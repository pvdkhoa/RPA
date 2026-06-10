import win32gui, win32con
import ctypes
import subprocess
import logging
import time
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
# CONFIG
# ─────────────────────────────────────────
PYTHON_EXE = r"C:\Users\RPA02\AppData\Local\Programs\Python\Python311\python.exe"
OCR_SCRIPT = r"ocr_check.py"
MAX_RETRY  = 3

# ─────────────────────────────────────────
# BROWSER FUNCTIONS
# ─────────────────────────────────────────
def get_hwnd_kb():
    """Lấy hwnd browser KB스마트비서 GA전용"""
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'KB스마트비서' in title or 'KB라이프' in title or 'KB손보' in title:
                result.append((hwnd, title))
    win32gui.EnumWindows(callback, None)
    return result

def wait_for_kb(timeout=30):
    """Chờ browser KB xuất hiện"""
    print("Waiting for KB browser...")
    start = time.time()
    while time.time() - start < timeout:
        windows = get_hwnd_kb()
        if windows:
            print(f"Browser ready: {windows[0][1]}")
            return windows[0][0]
        time.sleep(1)
    print("Timeout! KB browser not found.")
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

# ─────────────────────────────────────────
# OCR CHECK
# ─────────────────────────────────────────
def run_ocr_check():
    """Gọi ocr_check.py trong process riêng"""
    print("[OCR] Running ocr_check.py...")
    result = subprocess.run(
        [PYTHON_EXE, OCR_SCRIPT],
        capture_output=True,
        text=True
    )
    text = result.stdout.strip()
    if result.stderr:
        log.warning(f"[OCR STDERR] {result.stderr.strip()}")
    log.info(f"[OCR TEXT] '{text if text else '(Khong nhan dien duoc)'}'")
    return text

# ─────────────────────────────────────────
# RELOAD + RETRY LOGIC
# ─────────────────────────────────────────
def reload_page(hwnd):
    print("Reload page (F5)...")
    force_foreground(hwnd)
    import win32com.client
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys("{F5}")
    time.sleep(3)  # chờ dialog "Resubmit the form?" xuất hiện
    print("Accepting Resubmit dialog...")
    shell.SendKeys("{ENTER}")
    time.sleep(15)  # chờ page reload xong

def check_main_loaded_and_retry(hwnd_main, max_retry=MAX_RETRY):
    for attempt in range(1, max_retry + 1):
        print(f"[OCR] Kiểm tra trang main (lần {attempt}/{max_retry})...")
        time.sleep(3)

        text = run_ocr_check()

        if text:
            print(f"[OK] Trang main đã load xong! Text: '{text}'")
            log.info(f"[SUCCESS] Load thành công lần {attempt}. Text: '{text}'")
            return True
        else:
            print(f"[RETRY] Trang trắng, reload... (lần {attempt}/{max_retry})")
            log.warning(f"[RETRY] Trang trắng lần {attempt}, reload...")
            if attempt < max_retry:
                reload_page(hwnd_main)

    print(f"[FAIL] Đã thử {max_retry} lần nhưng trang vẫn không load.")
    log.error(f"[FAIL] Trang main không load sau {max_retry} lần.")
    return False

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
print("Start")

# Minimize CMD
hwnd_cmd = ctypes.windll.kernel32.GetConsoleWindow()
ctypes.windll.user32.ShowWindow(hwnd_cmd, 6)

# Chờ browser KB (UiPath đã mở sẵn)
hwnd_main = wait_for_kb(timeout=30)
if not hwnd_main:
    log.error("[EXIT] Không tìm thấy KB browser.")
    exit()

force_foreground(hwnd_main)
time.sleep(2)

# Check loading main page
success = check_main_loaded_and_retry(hwnd_main, max_retry=MAX_RETRY)

if success:
    print("End - Main page loaded!")
    log.info("[END] Main page load hoàn tất.")
else:
    print("End - Main page failed after retries.")
    log.error("[END] Main page không load được.")