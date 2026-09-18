import os
import sys
import win32api, win32con, win32gui, win32com.client, win32clipboard, time
import ctypes
import base64
import requests
import json
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────
SAVE_DIR = Path(r"C:\Users\RPA02\Documents\UiPath\RPA\Python_Script\Log")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = SAVE_DIR / f"ocr_log_mrf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
import logging
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
# PARSE ARGUMENTS (EXACT SSL PATTERN + LABEL STRIPPING)
# ─────────────────────────────────────────
raw_tokens = []
for a in sys.argv[1:]:
    for token in a.strip().split():
        # Remove label prefixes if present (e.g. "username:", "password:")
        if token.lower() in ("username:", "user:", "password:", "pw:", "otp:"):
            continue
        raw_tokens.append(token)

ARG_USERNAME = raw_tokens[0] if len(raw_tokens) > 0 else ""
ARG_PASSWORD = ""
if len(raw_tokens) > 1:
    try:
        ARG_PASSWORD = base64.b64decode(raw_tokens[1]).decode("utf-8")
    except Exception:
        ARG_PASSWORD = raw_tokens[1]

ARG_OTP = raw_tokens[2] if len(raw_tokens) > 2 else ""

# ─────────────────────────────────────────
# UIPATH ORCHESTRATOR API CONFIG & FETCH (SSL PATTERN)
# SSL gets Username/Password from sys.argv, and OTP/URL from Orchestrator Assets
# ─────────────────────────────────────────
CLIENT_ID     = "a864297e-5ec8-4ca0-a456-3e8cbe0c2d95"
CLIENT_SECRET = "GG_Y9OPAKtiVfgML*de*B0_Xvv1Q?Bic@Gu2$PA31icIJ%dnt4(dDm5hEnY?Tx(v"
ORG_UNIT_ID   = "8773"
BASE_URL      = "https://cloud.uipath.com/miraeassetfp/DefaultTenant/orchestrator_"

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

def fetch_mrf_assets():
    """Fetch MRF OTP Asset from Orchestrator (Same as SSL_AST_OTP in SSL)"""
    global ARG_OTP
    try:
        log.info("[ASSETS] Attempting to fetch MRF Assets from Orchestrator...")
        token = get_access_token()
        url = f"{BASE_URL}/odata/Assets"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitId": ORG_UNIT_ID,
        }
        params = {"$filter": "startswith(Name,'MRF_AST')"}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        assets = response.json().get("value", [])

        for asset in assets:
            name = asset.get("Name", "")
            if name == "MRF_AST_OTP" and not ARG_OTP:
                ARG_OTP = asset.get("StringValue", "")
                log.info(f"[PARSE] MRF_AST_OTP -> otp='{ARG_OTP}'")
    except Exception as e:
        log.warning(f"[ASSETS] Failed to fetch assets via API: {e}")

# If OTP is missing, fetch from Orchestrator API
if not ARG_OTP:
    fetch_mrf_assets()

# Ghi rõ Username, Password, OTP thu thập được ra Log để kiểm tra
log.info(f"[CHECK] Target Username: '{ARG_USERNAME}'")
log.info(f"[CHECK] Target Password: '{ARG_PASSWORD}'")
log.info(f"[CHECK] Target OTP: '{ARG_OTP}'")

shell = win32com.client.Dispatch("WScript.Shell")

def focus_window():
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if '메리츠화재' in title or 'meritz' in title.lower():
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    
    if not result:
        def callback_edge(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if 'edge' in title.lower() or 'msedge' in title.lower():
                    result.append(hwnd)
        win32gui.EnumWindows(callback_edge, None)

    if result:
        hwnd = result[0]
        fgwin = ctypes.windll.user32.GetForegroundWindow()
        fgthread = ctypes.windll.user32.GetWindowThreadProcessId(fgwin, None)
        curthread = ctypes.windll.kernel32.GetCurrentThreadId()
        ctypes.windll.user32.AttachThreadInput(fgthread, curthread, True)
        ctypes.windll.user32.BringWindowToTop(hwnd)
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        ctypes.windll.user32.AttachThreadInput(fgthread, curthread, False)
        time.sleep(0.3)
        return hwnd
    return None

def click(x, y):
    """Hàm click chuột đơn giản"""
    log.info(f"[CLICK] Click at ({x}, {y})")
    win32api.SetCursorPos((x, y))
    time.sleep(0.3)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(0.5)

def type_text(text):
    """Copy chữ vào Clipboard và Dán (Ctrl + V) kết hợp SendKeys để đảm bảo gõ chuẩn 100%"""
    if not text:
        return
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(str(text), win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        time.sleep(0.1)
        # Paste via Ctrl + V
        shell.SendKeys("^v")
        time.sleep(2)
    except Exception as e:
        log.warning(f"[TYPE] Clipboard paste warning: {e}, fallback to SendKeys")
        shell.SendKeys(str(text))
        time.sleep(2)

def do_login(uid, pw, otp):
    focus_window()
    time.sleep(0.5)

    # BƯỚC 1: Click 2 lần vào ô ID theo tọa độ (1118, 403) để đảm bảo bôi đen / Focus
    click(1118, 403)
    time.sleep(0.3)
    click(1118, 403)

    # BƯỚC 2: Nhập ID (Dùng Clipboard Paste Ctrl+V)
    if uid:
        log.info(f"[LOGIN] Typing Username: {uid}")
        time.sleep(1)
        type_text(uid)
        time.sleep(1)

    # BƯỚC 3: Nhấn phím TAB để nhảy sang ô Mật khẩu
    log.info("[LOGIN] Pressing TAB to move to Password field...")
    shell.SendKeys("{TAB}")
    time.sleep(0.5)

    # BƯỚC 4: Nhập Mật khẩu (Dùng Clipboard Paste Ctrl+V)
    if pw:
        log.info(f"[LOGIN] Typing Password: {pw}")
        shell.SendKeys("^a")
        time.sleep(1)
        type_text(pw)
        time.sleep(2)

    # BƯỚC 5: Nhấn phím TAB để nhảy sang ô OTP (Nếu có)
    if otp:
        log.info("[LOGIN] Pressing TAB to move to OTP field...")
        shell.SendKeys("{TAB}")
        time.sleep(0.5)
        log.info(f"[LOGIN] Typing OTP: {otp}")
        type_text(otp)
        time.sleep(2)

    # BƯỚC 6: Click chuột vào Nút Đăng nhập theo tọa độ (1262, 713)
    log.info("[LOGIN] Clicking Login Button at (1262, 713)...")
    click(1262, 713)
    time.sleep(1)
    log.info("[LOGIN] Login Submitted Successfully!")

if __name__ == "__main__":
    log.info("========== START MRF LOGIN SCRIPT ==========")
    do_login(ARG_USERNAME, ARG_PASSWORD, ARG_OTP)
    log.info("========== END MRF LOGIN SCRIPT ==========")
