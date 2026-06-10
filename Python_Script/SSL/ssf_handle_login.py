import shutil
import os
import sys
import win32api, win32con, win32gui, win32com.client, time
import ctypes
import subprocess
import logging
import requests
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────
SAVE_DIR = Path.home() / "Downloads"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = SAVE_DIR / f"ocr_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────
# PARSE ARGUMENTS
# username = sys.argv[1]
# password = sys.argv[2]
# Pass password as base64 to avoid special character issues
# ─────────────────────────────────────────
import base64

if len(sys.argv) < 3:
    log.error("[ARGS] Missing arguments. Usage: ssl_handle_login.py <username> <base64_password>")
    sys.exit(1)

ARG_USERNAME = sys.argv[1]

# Decode base64 password to handle special characters: !! @@ ## $$ &&
try:
    ARG_PASSWORD = base64.b64decode(sys.argv[2]).decode("utf-8")
    log.info(f"[ARGS] Username: '{ARG_USERNAME}'")
    log.info(f"[ARGS] Password decoded successfully")
except Exception as e:
    log.error(f"[ARGS] Failed to decode password: {e}")
    sys.exit(1)

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
shell = win32com.client.Dispatch("WScript.Shell")

PYTHON_EXE  = r"C:\Users\RPA02\AppData\Local\Programs\Python\Python311\python.exe"
OCR_SCRIPT  = r"ocr_check.py"
MAX_RETRY   = 5   # Number of OCR retries before restarting browser
MAX_RESTART = 2   # Number of browser restarts if still failing

CLIENT_ID     = "f03a6679-36df-4e04-987e-b73d8a905970"
CLIENT_SECRET = "!ys?YRKf6^e4Lbapq6SN0cq?GwNSO_#Q7s*~VwNt!BqDElg$F$srGJpiP7v8k$XS"
ORG_UNIT_ID   = "946773"
BASE_URL      = "https://cloud.uipath.com/rpacaxjvjr/defaulttenant/orchestrator_"

# ─────────────────────────────────────────
# UIPATH API
# ─────────────────────────────────────────
def get_access_token():
    url = "https://cloud.uipath.com/identity_/connect/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "OR.Assets.Read OR.Assets.Write OR.Folders.Read",
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    token = response.json()["access_token"]
    log.info("[AUTH] Access token retrieved successfully")
    return token

def get_ssl_assets(token):
    """Fetch SSL_AST_OTP and SSL_AST_URL assets from Orchestrator"""
    url = f"{BASE_URL}/odata/Assets"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-UIPATH-OrganizationUnitId": ORG_UNIT_ID,
    }
    params = {
        "$filter": "startswith(Name,'SSL_AST')"
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    assets = response.json().get("value", [])
    log.info(f"[ASSETS] Retrieved {len(assets)} SSL asset(s)")
    return assets

def parse_ssl_credentials(assets):
    """
    Parse credentials:
    - username/password: from command line arguments (base64 encoded)
    - otp/url: from Orchestrator assets
    """
    result = {
        "username": ARG_USERNAME,
        "password": ARG_PASSWORD,
        "otp": "",
        "url": ""
    }

    for asset in assets:
        name = asset.get("Name", "")
        if name == "SSL_AST_OTP":
            result["otp"] = asset.get("StringValue", "")
            log.info(f"[PARSE] SSL_AST_OTP -> otp='{result['otp']}'")
        elif name == "SSL_AST_URL":
            result["url"] = asset.get("StringValue", "")
            log.info(f"[PARSE] SSL_AST_URL -> url='{result['url']}'")

    # Validate
    if not result["username"] or not result["password"]:
        raise ValueError("[ERROR] Username or password argument is empty!")
    if not result["url"]:
        raise ValueError("[ERROR] SSL_AST_URL is empty!")
    if not result["otp"]:
        raise ValueError("[ERROR] SSL_AST_OTP is empty!")

    return result

# ─────────────────────────────────────────
# BROWSER FUNCTIONS
# ─────────────────────────────────────────
def open_edge(url):
    """Open Edge browser with no session restore"""
    subprocess.Popen([
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "--start-maximized",
        "--no-restore",
        "--disable-session-crashed-bubble",
        url
    ])
    log.info(f"[BROWSER] Opening Edge: {url}")
    time.sleep(20)

def close_edge():
    """Close Edge gracefully: WM_CLOSE first, then force kill"""
    log.info("[BROWSER] Closing Edge gracefully...")

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            cls = win32gui.GetClassName(hwnd)
            if cls == 'Chrome_WidgetWin_1':
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    win32gui.EnumWindows(callback, None)
    time.sleep(3)

    os.system("taskkill /f /im msedge.exe 2>nul")
    time.sleep(2)
    log.info("[BROWSER] Edge closed")

def clear_edge_data():
    """Clear Edge cache, cookies and session data"""
    base = Path(r"C:\Users\RPA02\AppData\Local\Microsoft\Edge\User Data\Default")
    targets = [
        base / "Cache", base / "Code Cache", base / "GPUCache",
        base / "Cookies", base / "Cookies-journal",
        base / "Session Storage", base / "Local Storage", base / "IndexedDB",
        base / "Sessions", base / "Current Session", base / "Current Tabs",
        base / "Last Session", base / "Last Tabs",
    ]
    for target in targets:
        try:
            if target.is_dir():
                shutil.rmtree(target)
                log.info(f"[CLEAR] Deleted folder: {target.name}")
            elif target.is_file():
                os.remove(target)
                log.info(f"[CLEAR] Deleted file: {target.name}")
        except Exception as e:
            log.warning(f"[CLEAR] Could not delete {target.name}: {e}")
    log.info("[CLEAR] Edge browser data cleared")

def get_hwnd_samsunglife():
    """Find Samsung Life browser window handle"""
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if '삼성생명' in title or 'GA영업포털' in title:
                result.append((hwnd, title))
    win32gui.EnumWindows(callback, None)
    return result

def get_hwnd_popup_edge():
    """Find Edge popup window handle"""
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if ('엣지브라우저' in title or
                'gapopup' in title or
                ('삼성생명' in title and 'GA영업포털시스템' in title)):
                result.append((hwnd, title))
    win32gui.EnumWindows(callback, None)
    return result

def close_popup_if_exists(timeout=10):
    """Wait for Edge popup and close it if found"""
    log.info("[POPUP] Checking for Edge popup...")
    start = time.time()
    while time.time() - start < timeout:
        popups = get_hwnd_popup_edge()
        if popups:
            for hwnd, title in popups:
                log.info(f"[POPUP] Closing popup: {title}")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                time.sleep(0.5)
            return True
        time.sleep(1)
    log.info("[POPUP] No popup found")
    return False

def wait_for_samsunglife(timeout=30):
    """Wait for Samsung Life browser to appear"""
    log.info("[BROWSER] Waiting for Samsung Life browser...")
    start = time.time()
    while time.time() - start < timeout:
        windows = get_hwnd_samsunglife()
        if windows:
            log.info(f"[BROWSER] Browser ready: {windows[0][1]}")
            return windows[0][0]
        time.sleep(1)
    log.error("[BROWSER] Timeout! Samsung Life browser not found")
    return None

# ─────────────────────────────────────────
# WINDOW CONTROL
# ─────────────────────────────────────────
def force_foreground(hwnd):
    """Force window to foreground using AttachThreadInput"""
    fgwin = ctypes.windll.user32.GetForegroundWindow()
    fgthread = ctypes.windll.user32.GetWindowThreadProcessId(fgwin, None)
    curthread = ctypes.windll.kernel32.GetCurrentThreadId()
    ctypes.windll.user32.AttachThreadInput(fgthread, curthread, True)
    ctypes.windll.user32.ShowWindow(hwnd, 3)
    ctypes.windll.user32.BringWindowToTop(hwnd)
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    ctypes.windll.user32.AttachThreadInput(fgthread, curthread, False)
    time.sleep(0.8)

def click(hwnd, x, y):
    """Hardware mouse click at coordinates"""
    force_foreground(hwnd)
    win32api.SetCursorPos((x, y))
    time.sleep(0.3)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(0.5)

def clear_and_type(hwnd, x, y, text):
    """Click field, select all, delete, then type text"""
    force_foreground(hwnd)
    click(hwnd, x, y)
    shell.SendKeys("^a")
    time.sleep(0.1)
    shell.SendKeys("{DELETE}")
    time.sleep(0.1)
    shell.SendKeys(str(text))
    time.sleep(0.3)

# ─────────────────────────────────────────
# POPUP CLOSE FLOW
# ─────────────────────────────────────────
def close_all_popups(hwnd_main):
    """Close all portal popups after login"""
    log.info("[POPUP] Closing portal popups...")
    click(hwnd_main, 773, 538)
    time.sleep(2)
    click(hwnd_main, 770, 471)
    time.sleep(2)
    click(hwnd_main, 786, 478)
    time.sleep(2)
    click(hwnd_main, 1013, 589)
    time.sleep(2)
    log.info("[POPUP] All popups closed")

# ─────────────────────────────────────────
# OCR CHECK
# ─────────────────────────────────────────
def run_ocr_check():
    """Run ocr_check.py as subprocess and return recognized text"""
    log.info("[OCR] Running ocr_check.py...")
    result = subprocess.run(
        [PYTHON_EXE, OCR_SCRIPT],
        capture_output=True,
        text=True
    )
    text = result.stdout.strip()
    if result.stderr:
        log.warning(f"[OCR] STDERR: {result.stderr.strip()}")
    log.info(f"[OCR] Result: '{text if text else '(empty)'}'")
    return text

# ─────────────────────────────────────────
# RELOAD + RETRY LOGIC
# ─────────────────────────────────────────
def reload_and_close_popups(hwnd_main):
    """F5 reload page, wait, then close all popups"""
    log.info("[RELOAD] Reloading page (F5)...")
    force_foreground(hwnd_main)
    shell.SendKeys("{F5}")
    time.sleep(15)
    close_all_popups(hwnd_main)

def check_main_loaded_and_retry(hwnd_main, max_retry=MAX_RETRY):
    """
    Retry OCR up to max_retry times.
    Each failure: reload -> close popups -> OCR again.
    Returns True if page loaded successfully.
    """
    for attempt in range(1, max_retry + 1):
        log.info(f"[OCR] Checking main page (attempt {attempt}/{max_retry})...")
        time.sleep(3)
        text = run_ocr_check()
        if text:
            log.info(f"[OCR] Page loaded on attempt {attempt}. Text: '{text}'")
            return True
        else:
            log.warning(f"[OCR] Blank page on attempt {attempt}/{max_retry}")
            if attempt < max_retry:
                reload_and_close_popups(hwnd_main)

    log.error(f"[OCR] Failed to load page after {max_retry} attempts")
    return False

# ─────────────────────────────────────────
# LOGIN FLOW
# ─────────────────────────────────────────
def do_login(hwnd, creds):
    """Perform login using credentials from arguments + Orchestrator assets"""
    force_foreground(hwnd)
    time.sleep(2)

    log.info("[LOGIN] Typing username...")
    clear_and_type(hwnd, 1160, 343, creds["username"])
    time.sleep(1)

    log.info("[LOGIN] Typing password...")
    clear_and_type(hwnd, 1145, 403, creds["password"])
    time.sleep(1)

    log.info("[LOGIN] Typing OTP...")
    clear_and_type(hwnd, 1150, 459, creds["otp"])
    time.sleep(1)

    log.info("[LOGIN] Clicking login button...")
    click(hwnd, 1110, 558)
    time.sleep(25)

    close_all_popups(hwnd)
    log.info("[LOGIN] Login flow completed")

# ─────────────────────────────────────────
# RESTART BROWSER
# ─────────────────────────────────────────
def restart_and_open(creds):
    """Close Edge -> reopen URL -> login -> close popups"""
    log.info("[RESTART] Starting browser restart...")
    close_edge()
    time.sleep(3)
    open_edge(creds["url"])
    close_popup_if_exists(timeout=10)

    hwnd = wait_for_samsunglife(timeout=30)
    if not hwnd:
        log.error("[RESTART] Browser not found after restart")
        return None

    do_login(hwnd, creds)
    return hwnd

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
log.info("========== START ==========")

# Minimize CMD window
hwnd_cmd = ctypes.windll.kernel32.GetConsoleWindow()
ctypes.windll.user32.ShowWindow(hwnd_cmd, 6)

# Step 1: Fetch OTP and URL from Orchestrator API
log.info("[INIT] Fetching OTP and URL from Orchestrator...")
try:
    token = get_access_token()
    assets = get_ssl_assets(token)
    creds = parse_ssl_credentials(assets)
    log.info(f"[INIT] Credentials OK -> URL: {creds['url']}")
except Exception as e:
    log.error(f"[INIT] Failed to fetch credentials: {e}")
    sys.exit(1)

# Step 2: Clear cache, open browser, login
clear_edge_data()
time.sleep(3)
open_edge(creds["url"])
close_popup_if_exists(timeout=10)

hwnd_main = wait_for_samsunglife(timeout=30)
if not hwnd_main:
    log.error("[EXIT] Browser not found after open")
    sys.exit(1)

do_login(hwnd_main, creds)

# Step 3: OCR retry up to MAX_RETRY times
success = check_main_loaded_and_retry(hwnd_main, max_retry=MAX_RETRY)

# Step 4: If still failing -> restart browser up to MAX_RESTART times
if not success:
    for restart_num in range(1, MAX_RESTART + 1):
        log.warning(f"[RESTART] Attempt {restart_num}/{MAX_RESTART}")

        hwnd_main = restart_and_open(creds)
        if not hwnd_main:
            log.error(f"[RESTART] Attempt {restart_num}: Browser not found")
            continue

        success = check_main_loaded_and_retry(hwnd_main, max_retry=3)
        if success:
            break
        else:
            log.warning(f"[RESTART] Attempt {restart_num}: Still failed after 3 OCR retries")

# Final result
if success:
    log.info("[END] Login completed successfully!")
else:
    log.error(f"[END] Failed after {MAX_RETRY} retries + {MAX_RESTART} restarts")

log.info("========== END ==========")