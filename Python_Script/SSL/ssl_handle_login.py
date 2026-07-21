import shutil
import os
import sys
import win32api, win32con, win32gui, win32com.client, time
import ctypes
import subprocess
import logging
import requests
import json
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────
SAVE_DIR = Path(r"C:\Users\RPA02\Documents\UiPath\RPA\Python_Script\Log")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = SAVE_DIR / f"ocr_log_ssl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
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
# password = sys.argv[2]  (base64 encoded)
# ─────────────────────────────────────────
import base64

if len(sys.argv) < 3:
    log.error("[ARGS] Missing arguments. Usage: ssl_handle_login.py <username> <base64_password> [checkID]")
    sys.exit(1)

ARG_USERNAME = sys.argv[1]

try:
    ARG_PASSWORD = base64.b64decode(sys.argv[2]).decode("utf-8")
    log.info(f"[ARGS] Username: '{ARG_USERNAME}'")
    log.info(f"[ARGS] Password decoded successfully: {ARG_PASSWORD}")
except Exception as e:
    log.error(f"[ARGS] Failed to decode password: {e}")
    sys.exit(1)

ARG_CHECK_ID = sys.argv[3] if len(sys.argv) > 3 else ""
if ARG_CHECK_ID:
    log.info(f"[ARGS] CheckID provided: '{ARG_CHECK_ID}'")

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
shell = win32com.client.Dispatch("WScript.Shell")

PYTHON_EXE  = r"C:\Users\RPA02\AppData\Local\Programs\Python\Python311\python.exe"
OCR_SCRIPT  = r"ocr_check.py"
MAX_RETRY   = 6   # Number of reload + OCR attempts before restarting the browser
MAX_RESTART = 2   # Number of browser restarts if still failing

# Wait time for local security agent (K-Defense / MaWebDRM) to complete handshake.
# This is the real bottleneck causing blank pages: WebSquare only renders after
# the agent at 127.0.0.1 reports READY. Extra time added to avoid race condition.
SECURITY_WARMUP_SEC = 8
POST_LOGIN_SETTLE   = 12   # Wait for security handshake to stabilize after clicking login

CLIENT_ID     = "a864297e-5ec8-4ca0-a456-3e8cbe0c2d95"
CLIENT_SECRET = "GG_Y9OPAKtiVfgML*de*B0_Xvv1Q?Bic@Gu2$PA31icIJ%dnt4(dDm5hEnY?Tx(v"
ORG_UNIT_ID   = "8773"
BASE_URL      = "https://cloud.uipath.com/miraeassetfp/DefaultTenant/orchestrator_"

# Security agent process names (verify against Task Manager on RPA02 and adjust if needed).
# Used to wait for the agent to be alive before opening Edge.
SECURITY_PROCESSES = ["MaWebDRM", "MarkAny", "KStdWeb", "KGenia", "KSecureWeb", "kos"]

# ─────────────────────────────────────────
# UIPATH ORCHESTRATOR API
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
    url = f"{BASE_URL}/odata/Assets"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-UIPATH-OrganizationUnitId": ORG_UNIT_ID,
    }
    params = {"$filter": "startswith(Name,'SSL_AST')"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    assets = response.json().get("value", [])
    log.info(f"[ASSETS] Retrieved {len(assets)} SSL asset(s)")
    return assets

def parse_ssl_credentials(assets):
    result = {"username": ARG_USERNAME, "password": ARG_PASSWORD, "otp": "", "url": ""}
    for asset in assets:
        name = asset.get("Name", "")
        if name == "SSL_AST_OTP":
            result["otp"] = asset.get("StringValue", "")
            log.info(f"[PARSE] SSL_AST_OTP -> otp='{result['otp']}'")
        elif name == "SSL_AST_URL":
            result["url"] = asset.get("StringValue", "")
            log.info(f"[PARSE] SSL_AST_URL -> url='{result['url']}'")

    if not result["username"] or not result["password"]:
        raise ValueError("[ERROR] Username or password argument is empty!")
    if not result["url"]:
        raise ValueError("[ERROR] SSL_AST_URL is empty!")
    if not result["otp"]:
        raise ValueError("[ERROR] SSL_AST_OTP is empty!")
    return result

# ─────────────────────────────────────────
# UPDATE SSL LOGIN STATUS ASSET
# Using for checking Alive SSL Y/N
# For checking SSL activation status (Y/N)
# ─────────────────────────────────────────
def update_ssl_login_status(status: str):
    """Update SSL_LOGIN_STATUS asset value to 'Y' (success) or 'N' (failed)."""
    # Step 1: Get fresh token (same pattern as ocr_script)
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "X-UIPATH-OrganizationUnitId": ORG_UNIT_ID,
        "Content-Type": "application/json",
    }

    # Step 2: Get asset by name (same as get_asset_by_name in ocr_script)
    url = f"{BASE_URL}/odata/Assets"
    params = {"$filter": "Name eq 'SSL_LOGIN_STATUS'"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    assets = response.json().get("value", [])

    if not assets:
        log.error("[STATUS] SSL_LOGIN_STATUS asset not found in Orchestrator!")
        return False

    asset = assets[0]
    asset_id = asset["Id"]
    log.info(f"[STATUS] SSL_LOGIN_STATUS asset ID: {asset_id}")

    # Step 3: Update asset (same as update_asset in ocr_script)
    update_url = f"{BASE_URL}/odata/Assets({asset_id})"
    body = {
        "Id": asset_id,
        "Name": "SSL_LOGIN_STATUS",
        "ValueType": "Text",
        "StringValue": status,
    }
    response = requests.put(update_url, headers=headers, json=body)
    response.raise_for_status()
    log.info(f"[STATUS] SSL_LOGIN_STATUS updated to '{status}' successfully")
    return True

# ─────────────────────────────────────────
# SECURITY AGENT WARM-UP
# WebSquare only renders when the security agent (K-Defense/MaWebDRM) reports READY.
# Wait for the agent process to be alive + warm-up before opening Edge to avoid race condition.
# ─────────────────────────────────────────
def is_process_running(name_part):
    try:
        out = subprocess.run(
            ["tasklist"], capture_output=True, text=True,
            encoding="utf-8", errors="replace"
        ).stdout.lower()
        return name_part.lower() in out
    except Exception:
        return False

def wait_security_agents(timeout=20):
    log.info("[AGENT] Waiting for local security agents...")
    start = time.time()
    found = []
    while time.time() - start < timeout:
        found = [p for p in SECURITY_PROCESSES if is_process_running(p)]
        if found:
            log.info(f"[AGENT] Security agent(s) detected: {found}")
            break
        time.sleep(1)
    if not found:
        log.warning("[AGENT] No known security agent detected "
                    "(please verify process names in SECURITY_PROCESSES).")
    log.info(f"[AGENT] Warming up for {SECURITY_WARMUP_SEC}s to complete handshake...")
    time.sleep(SECURITY_WARMUP_SEC)

# ─────────────────────────────────────────
# BROWSER FUNCTIONS
# ─────────────────────────────────────────
def open_edge(url):
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
    log.info("[BROWSER] Closing Edge gracefully...")
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            if win32gui.GetClassName(hwnd) == 'Chrome_WidgetWin_1':
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    win32gui.EnumWindows(callback, None)
    time.sleep(3)
    os.system("taskkill /f /im msedge.exe 2>nul")
    time.sleep(2)
    log.info("[BROWSER] Edge closed")

def clear_edge_data():
    """
    Clear Edge cache & cookies for a clean login session.

    IMPORTANT: Do NOT delete Local Storage / IndexedDB / Session Storage.
    The security agent (MaWebDRM / K-Defense) likely caches its handshake
    state there. Deleting them forces a cold-start handshake from scratch,
    which races with WebSquare rendering and causes blank pages requiring
    many reloads. This is one of the main root causes of 'many reloads needed'.
    """
    base = Path(r"C:\Users\RPA02\AppData\Local\Microsoft\Edge\User Data\Default")
    targets = [
        base / "Cache", base / "Code Cache", base / "GPUCache",
        base / "Cookies", base / "Cookies-journal",
        base / "Sessions", base / "Current Session", base / "Current Tabs",
        base / "Last Session", base / "Last Tabs",
        # ── REMOVED (preserving security agent state) ──
        # base / "Session Storage", base / "Local Storage", base / "IndexedDB",
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
    log.info("[CLEAR] Edge browser data cleared (agent state preserved)")

def get_hwnd_samsunglife():
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if '삼성생명' in title or 'GA영업포털' in title:
                result.append((hwnd, title))
    win32gui.EnumWindows(callback, None)
    return result

def get_hwnd_popup_edge():
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

def update_json_is_openned(status):
    if not ARG_CHECK_ID:
        return
    json_path = os.path.join(r"C:\RPA\CheckAvailableComp", f"result_{ARG_CHECK_ID}.json")
    if not os.path.exists(json_path):
        log.warning(f"[JSON] JSON file not found: {json_path}")
        return
    try:
        with open(json_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        for item in data:
            if str(item.get("compCode")) == "SSL":
                item["isOpenned"] = status
                item["processTime"] = datetime.now().strftime("%Y%m%d %H:%M:%S")
                break
        with open(json_path, 'w', encoding='utf-8-sig') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        log.info(f"[JSON] Successfully updated isOpenned to '{status}' for SSL")
    except Exception as e:
        log.error(f"[JSON] Failed to update JSON file: {e}")

def wait_for_samsunglife(timeout=30):
    log.info("[BROWSER] Waiting for Samsung Life browser...")
    start = time.time()
    while time.time() - start < timeout:
        windows = get_hwnd_samsunglife()
        if windows:
            log.info(f"[BROWSER] Browser ready: {windows[0][1]}")
            update_json_is_openned("Y")
            return windows[0][0]
        time.sleep(1)
    log.error("[BROWSER] Timeout! Samsung Life browser not found")
    update_json_is_openned("N")
    return None

# ─────────────────────────────────────────
# WINDOW CONTROL
# ─────────────────────────────────────────
def force_foreground(hwnd):
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
    force_foreground(hwnd)
    win32api.SetCursorPos((x, y))
    time.sleep(0.3)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(0.5)

def clear_and_type(hwnd, x, y, text):
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
# OCR CHECK  (HARDENED - prevents false positives)
# Old bug: easyocr progress bar / download messages written to stdout,
# crashed cp949 encoding, but garbage strings leaked through -> counted as 'loaded'.
# This version: forces UTF-8, checks exit code, filters out all noise.
# ─────────────────────────────────────────
def run_ocr_check():
    """
    Executes the external ocr_check.py script as a subprocess to extract text from the screen.
    This is used to verify if the main page has fully loaded after login.
    """
    log.info("[OCR] Running ocr_check.py...")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"   # prevent cp949 crash from subprocess

    result = subprocess.run(
        [PYTHON_EXE, OCR_SCRIPT],
        capture_output=True, text=True,
        encoding="utf-8", errors="replace",
        env=env,
    )

    if result.stderr:
        log.warning(f"[OCR] STDERR: {result.stderr.strip()[:300]}")

    # If ocr_check.py crashes -> must NOT be counted as loaded
    if result.returncode != 0:
        log.error(f"[OCR] ocr_check.py exit code {result.returncode} -> treat as blank")
        return ""

    # Filter out easyocr noise (progress bars, download messages, etc.)
    NOISE = ("Progress:", "Downloading", "Using CPU", "Using GPU",
             "CUDA", "This may take", "Complete")
    clean = []
    for ln in (result.stdout or "").splitlines():
        s = ln.strip()
        if not s:
            continue
        if "|" in s and any(n in s for n in NOISE):   # progress bar line
            continue
        if any(s.startswith(n) for n in NOISE):
            continue
        clean.append(s)

    text = "\n".join(clean).strip()
    log.info(f"[OCR] Result: '{text if text else '(empty)'}'")
    return text

# ─────────────────────────────────────────
# RELOAD + RETRY LOGIC  (proven working reload method)
# Note: Do NOT use bare URL / new ticket anymore.
#   - websquare.html (no ticket) -> empty ticket -> blank page (confirmed).
#   - https://ga.samsunglife.com/ (request new ticket) -> still blank (confirmed).
#   => Correct recovery = F5 reload the current tab with existing ?ticket=... URL.
# ─────────────────────────────────────────
def reload_and_close_popups(hwnd_main, wait_load=15):
    log.info("[RELOAD] Reloading page (F5)...")
    force_foreground(hwnd_main)
    shell.SendKeys("{F5}")
    time.sleep(wait_load)
    close_all_popups(hwnd_main)

def check_main_loaded_and_retry(hwnd_main, max_retry=MAX_RETRY):
    """Run OCR; if blank -> F5 reload -> close popups -> OCR again, up to max_retry times."""
    for attempt in range(1, max_retry + 1):
        log.info(f"[OCR] Checking main page (attempt {attempt}/{max_retry})...")
        time.sleep(3)
        text = run_ocr_check()
        if text:
            log.info(f"[OCR] Page loaded on attempt {attempt}. Text: '{text}'")
            return True
        log.warning(f"[OCR] Blank page on attempt {attempt}/{max_retry}")
        if attempt < max_retry:
            reload_and_close_popups(hwnd_main)
    log.error(f"[OCR] Failed to load page after {max_retry} attempts")
    return False

# ─────────────────────────────────────────
# LOGIN FLOW
# ─────────────────────────────────────────
def do_login(hwnd, creds):
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

    # Wait for page loading + security handshake (race condition prone -> keep generous)
    time.sleep(25)
    log.info(f"[LOGIN] Settling {POST_LOGIN_SETTLE}s for security handshake...")
    time.sleep(POST_LOGIN_SETTLE)

    close_all_popups(hwnd)
    log.info("[LOGIN] Login flow completed")

# ─────────────────────────────────────────
# RESTART BROWSER (last resort fallback)
# Restart does NOT wipe Local Storage/IndexedDB (preserves agent state).
# ─────────────────────────────────────────
def restart_and_open(creds):
    log.info("[RESTART] Starting browser restart...")
    close_edge()
    time.sleep(3)
    wait_security_agents()
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

# Step 1: Fetch OTP and URL from Orchestrator
log.info("[INIT] Fetching OTP and URL from Orchestrator...")
try:
    token = get_access_token()
    assets = get_ssl_assets(token)
    creds = parse_ssl_credentials(assets)
    log.info(f"[INIT] Credentials OK -> URL: {creds['url']}")
except Exception as e:
    log.error(f"[INIT] Failed to fetch credentials: {e}")
    sys.exit(1)

# Step 2: Clear (cache + cookies, preserve agent state) -> warm-up agent -> open -> login
clear_edge_data()
time.sleep(3)
wait_security_agents()          # wait for security agent to be alive before opening Edge
open_edge(creds["url"])
close_popup_if_exists(timeout=10)

hwnd_main = wait_for_samsunglife(timeout=30)
if not hwnd_main:
    log.error("[EXIT] Browser not found after open")
    sys.exit(1)

do_login(hwnd_main, creds)

# Step 3: OCR + reload retry (proven working method; bare URL/new ticket has been ruled out)
success = check_main_loaded_and_retry(hwnd_main, max_retry=MAX_RETRY)

# Step 4: If still failing -> restart browser (preserve agent state) up to MAX_RESTART times
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
        log.warning(f"[RESTART] Attempt {restart_num}: Still failed after 3 OCR retries")

# Final result
if success:
    log.info("[END] Login completed successfully!")
    try:
        update_ssl_login_status("Y")
    except Exception as e:
        log.error(f"[STATUS] Failed to update SSL_LOGIN_STATUS to Y: {e}")
else:
    log.error(f"[END] Failed after {MAX_RETRY} retries + {MAX_RESTART} restarts")
    try:
        update_ssl_login_status("N")
    except Exception as e:
        log.error(f"[STATUS] Failed to update SSL_LOGIN_STATUS to N: {e}")

log.info("========== END ==========")