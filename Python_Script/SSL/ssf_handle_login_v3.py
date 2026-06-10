import shutil
import os
import win32api, win32con, win32gui, win32com.client, time
import ctypes
import subprocess
import logging
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
shell = win32com.client.Dispatch("WScript.Shell")

PYTHON_EXE  = r"C:\Users\RPA02\AppData\Local\Programs\Python\Python311\python.exe"
OCR_SCRIPT  = r"ocr_check.py"
MAX_RETRY   = 5  # Số lần reload + OCR trước khi restart
MAX_RESTART = 2  # Số lần restart browser nếu vẫn fail

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
    print("Opening Edge...")
    time.sleep(20)

def close_edge():
    """Đóng Edge đúng cách: WM_CLOSE trước, taskkill sau"""
    print("[RESTART] Closing Edge gracefully...")
    log.info("[RESTART] Closing Edge...")

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            cls = win32gui.GetClassName(hwnd)
            if cls == 'Chrome_WidgetWin_1':
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    win32gui.EnumWindows(callback, None)
    time.sleep(3)

    os.system("taskkill /f /im msedge.exe 2>nul")
    time.sleep(2)

def clear_edge_data():
    """Xóa cache/cookies/session data của Edge"""
    base = Path(r"C:\Users\RPA02\AppData\Local\Microsoft\Edge\User Data\Default")
    targets = [
        base / "Cache",
        base / "Code Cache",
        base / "GPUCache",
        base / "Cookies",
        base / "Cookies-journal",
        base / "Session Storage",
        base / "Local Storage",
        base / "IndexedDB",
        base / "Sessions",
        base / "Current Session",
        base / "Current Tabs",
        base / "Last Session",
        base / "Last Tabs",
    ]
    for target in targets:
        try:
            if target.is_dir():
                shutil.rmtree(target)
                print(f"[CLEAR] Deleted folder: {target.name}")
            elif target.is_file():
                os.remove(target)
                print(f"[CLEAR] Deleted file: {target.name}")
        except Exception as e:
            print(f"[WARN] Could not delete {target.name}: {e}")
    print("[CLEAR] Edge data cleared.")
    log.info("[CLEAR] Edge browser data cleared.")

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
    print("Checking for popup...")
    start = time.time()
    while time.time() - start < timeout:
        popups = get_hwnd_popup_edge()
        if popups:
            for hwnd, title in popups:
                print(f"Closing popup: {title}")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                time.sleep(0.5)
            return True
        time.sleep(1)
    print("No popup found.")
    return False

def wait_for_samsunglife(timeout=30):
    print("Waiting for Samsung Life browser...")
    start = time.time()
    while time.time() - start < timeout:
        windows = get_hwnd_samsunglife()
        if windows:
            print(f"Browser ready: {windows[0][1]}")
            return windows[0][0]
        time.sleep(1)
    print("Timeout! Samsung Life browser not found.")
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
    print("Close Popup 1..")
    click(hwnd_main, 773, 538)
    time.sleep(2)
    print("Close Popup 2..")
    click(hwnd_main, 770, 471)
    time.sleep(2)
    print("Close Popup 3.")
    click(hwnd_main, 786, 478)
    time.sleep(2)
    print("Close Popup 4.")
    click(hwnd_main, 1013, 589)
    time.sleep(2)
    

# ─────────────────────────────────────────
# OCR CHECK
# ─────────────────────────────────────────
def run_ocr_check():
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
def reload_and_close_popups(hwnd_main):
    """F5 reload → chờ → close all popups"""
    print("Reload page (F5)...")
    force_foreground(hwnd_main)
    shell.SendKeys("{F5}")
    time.sleep(15)
    close_all_popups(hwnd_main)

def check_main_loaded_and_retry(hwnd_main, max_retry=MAX_RETRY):
    """
    Retry OCR max_retry lần.
    Mỗi lần fail: reload → close popup → OCR lại.
    Trả về True nếu load được.
    """
    for attempt in range(1, max_retry + 1):
        print(f"[OCR] Kiểm tra trang main (lần {attempt}/{max_retry})...")
        time.sleep(3)
        text = run_ocr_check()
        if text:
            print(f"[OK] Load xong! Text: '{text}'")
            log.info(f"[SUCCESS] Load thành công lần {attempt}. Text: '{text}'")
            return True
        else:
            print(f"[RETRY] Trang trắng (lần {attempt}/{max_retry})")
            log.warning(f"[RETRY] Trang trắng lần {attempt}")
            if attempt < max_retry:
                reload_and_close_popups(hwnd_main)

    log.error(f"[FAIL] Không load được sau {max_retry} lần retry.")
    return False

# ─────────────────────────────────────────
# RESTART BROWSER
# ─────────────────────────────────────────
def restart_and_open():
    """Đóng Edge đúng cách → mở lại URL → login → close popup"""
    log.info("[RESTART] Bắt đầu restart browser...")
    close_edge()
    time.sleep(3)
    open_edge("https://ga.samsunglife.com/")
    close_popup_if_exists(timeout=10)

    hwnd = wait_for_samsunglife(timeout=30)
    if not hwnd:
        log.error("[RESTART] Không tìm thấy browser sau restart.")
        return None

    force_foreground(hwnd)
    time.sleep(2)

    # ── Login lại ──
    print("[RESTART] Typing ID...")
    clear_and_type(hwnd, 1160, 343, "0001930832")
    time.sleep(1)

    print("[RESTART] Typing Password...")
    clear_and_type(hwnd, 1145, 403, "asdf2626{!}{!}")
    time.sleep(1)

    print("[RESTART] Typing Birthday...")
    clear_and_type(hwnd, 1150, 459, "19740410")
    time.sleep(1)

    print("[RESTART] Clicking Login...")
    click(hwnd, 1110, 558)
    time.sleep(25)

    close_all_popups(hwnd)
    return hwnd

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
print("Start")

hwnd_cmd = ctypes.windll.kernel32.GetConsoleWindow()
ctypes.windll.user32.ShowWindow(hwnd_cmd, 6)

# ── Lần đầu: xóa cache + mở + login ──
clear_edge_data()
time.sleep(3)
open_edge("https://ga.samsunglife.com/")
close_popup_if_exists(timeout=10)

hwnd_main = wait_for_samsunglife(timeout=30)
if not hwnd_main:
    log.error("[EXIT] Không tìm thấy browser.")
    exit()

force_foreground(hwnd_main)
time.sleep(2)

print("Typing ID...")
clear_and_type(hwnd_main, 1160, 343, "0001930832")
time.sleep(1)
print("Typing Password...")
clear_and_type(hwnd_main, 1145, 403, "asdf2626{!}{!}")
time.sleep(1)
print("Typing Birthday...")
clear_and_type(hwnd_main, 1150, 459, "19740410")
time.sleep(1)
print("Clicking Login...")
click(hwnd_main, 1110, 558)
time.sleep(25)
close_all_popups(hwnd_main)

# ── OCR retry MAX_RETRY lần ──
success = check_main_loaded_and_retry(hwnd_main, max_retry=MAX_RETRY)

# ── Nếu fail → restart MAX_RESTART lần ──
if not success:
    for restart_num in range(1, MAX_RESTART + 1):
        print(f"\n===== RESTART {restart_num}/{MAX_RESTART} =====")
        log.warning(f"[RESTART] Lần {restart_num}/{MAX_RESTART}")

        hwnd_main = restart_and_open()
        if not hwnd_main:
            log.error(f"[RESTART] Lần {restart_num}: Không tìm thấy browser.")
            continue

        # OCR retry 3 lần sau mỗi restart
        success = check_main_loaded_and_retry(hwnd_main, max_retry=3)
        if success:
            break
        else:
            log.warning(f"[RESTART] Lần {restart_num}: Vẫn không load sau 3 lần.")

# ── Kết quả cuối ──
if success:
    print("\nEnd - Login thành công!")
    log.info("[END] Login hoàn tất.")
else:
    print(f"\nEnd - Thất bại sau {MAX_RETRY} retry + {MAX_RESTART} restart.")
    log.error(f"[END] Thất bại hoàn toàn sau {MAX_RETRY} retry + {MAX_RESTART} restart.")