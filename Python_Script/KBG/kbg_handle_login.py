"""
This script handles the login and verification process for the KB browser application.
IMPORTANT: This script works in tandem with `ocr_check.py`. It calls `ocr_check.py` 
as a subprocess to take a screenshot and perform Optical Character Recognition (OCR) 
to verify if the main page has successfully loaded or if it needs to be reloaded.
"""
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
SAVE_DIR = Path(r"C:\Users\RPA02\Documents\UiPath\RPA\Python_Script\Log")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = SAVE_DIR / f"ocr_log_kbg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
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
    """
    Finds and returns the window handle (hwnd) for the KB Smart Secretary GA browser.
    """
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'KB스마트비서' in title or 'KB라이프' in title or 'KB손보' in title:
                result.append((hwnd, title))
    win32gui.EnumWindows(callback, None)
    return result

def wait_for_kb(timeout=30):
    """
    Waits for the KB browser to appear within the specified timeout.
    """
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
    """
    Forces the specified window to the foreground by attaching to the current foreground thread.
    """
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
    """
    Executes the external `ocr_check.py` script in a separate subprocess.
    The external script takes a screenshot and performs OCR to extract text.
    This function captures its stdout and returns the extracted text to verify page loading.
    """
    print("Started process: Running ocr_check.py...")
    
    # Step 1: Run the OCR script synchronously and capture its standard output and errors
    result = subprocess.run(
        [PYTHON_EXE, OCR_SCRIPT],
        capture_output=True,
        text=True
    )
    
    # Step 2: Strip whitespace from the captured OCR text
    text = result.stdout.strip()
    
    # Step 3: Log any standard errors emitted by the OCR script for debugging purposes
    if result.stderr:
        log.warning(f"[OCR STDERR] {result.stderr.strip()}")
        
    # Step 4: Log the final parsed text or indicate failure if empty
    log.info(f"[OCR TEXT] '{text if text else '(Cannot recognize text)'}'")
    
    return text

# ─────────────────────────────────────────
# RELOAD + RETRY LOGIC
# ─────────────────────────────────────────
def reload_page(hwnd):
    """
    Reloads the browser page and handles any 'Resubmit' popup that might appear.
    """
    print("Reloading page (F5)...")
    force_foreground(hwnd)
    import win32com.client
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys("{F5}")
    time.sleep(3)  # Wait for "Resubmit the form?" dialog to appear
    print("Accepting Resubmit dialog...")
    shell.SendKeys("{ENTER}")
    time.sleep(15)  # Wait for page reload to finish

def check_main_loaded_and_retry(hwnd_main, max_retry=MAX_RETRY):
    """
    Uses OCR to check if the main page has loaded correctly.
    If it returns empty (e.g. blank page), it triggers a reload and tries again.
    """
    for attempt in range(1, max_retry + 1):
        print(f"[OCR] Checking main page (attempt {attempt}/{max_retry})...")
        
        # Step 1: Wait a few seconds to let the page render before taking a screenshot
        time.sleep(3)

        # Step 2: Call the OCR subprocess to extract text from the targeted screen region
        text = run_ocr_check()

        if text:
            # Step 3a: If OCR found text, it means the page successfully loaded. Exit retry loop.
            print(f"[OK] Main page loaded successfully! Text: '{text}'")
            log.info(f"[SUCCESS] Loaded successfully on attempt {attempt}. Text: '{text}'")
            return True
        else:
            # Step 3b: If OCR is empty, it means the page might be blank or stuck.
            print(f"[RETRY] Blank page, reloading... (attempt {attempt}/{max_retry})")
            log.warning(f"[RETRY] Blank page on attempt {attempt}, reloading...")
            
            # Step 4: If we haven't reached the max retries, force a page reload via F5
            if attempt < max_retry:
                reload_page(hwnd_main)

    # Step 5: If the loop finishes without returning True, the maximum retries were reached.
    print(f"[FAIL] Tried {max_retry} times but page still didn't load.")
    log.error(f"[FAIL] Main page failed to load after {max_retry} attempts.")
    return False

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
print("Started process...")

# Minimize CMD window
hwnd_cmd = ctypes.windll.kernel32.GetConsoleWindow()
ctypes.windll.user32.ShowWindow(hwnd_cmd, 6)

# Wait for KB browser (which is already opened by UiPath)
hwnd_main = wait_for_kb(timeout=30)
if not hwnd_main:
    log.error("[EXIT] Cannot find KB browser.")
    exit()

force_foreground(hwnd_main)
time.sleep(2)

# Check loading main page using OCR
success = check_main_loaded_and_retry(hwnd_main, max_retry=MAX_RETRY)

if success:
    print("DONE! - Main page loaded successfully.")
    log.info("[END] Main page load complete.")
else:
    print("Process ended - Main page failed after retries.")
    log.error("[END] Main page could not be loaded.")