import win32api, win32con, win32gui, win32com.client, time
import ctypes
import subprocess

shell = win32com.client.Dispatch("WScript.Shell")

def open_edge(url):
    """Mở Microsoft Edge với URL chỉ định"""
    subprocess.Popen([
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "--start-maximized",
        url
    ])
    print("Opening Edge...")
    time.sleep(12)  # Chờ browser load xong

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
    """Lấy hwnd popup Edge browser Samsung Life"""
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if '엣지브라우저' in title or 'gapopup' in title or ('삼성생명' in title and 'GA영업포털시스템' in title):
                result.append((hwnd, title))
    win32gui.EnumWindows(callback, None)
    return result

def close_popup_if_exists(timeout=10):
    """Chờ popup xuất hiện rồi đóng"""
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

def force_foreground(hwnd):
    fgwin = ctypes.windll.user32.GetForegroundWindow()
    fgthread = ctypes.windll.user32.GetWindowThreadProcessId(fgwin, None)
    curthread = ctypes.windll.kernel32.GetCurrentThreadId()
    ctypes.windll.user32.AttachThreadInput(fgthread, curthread, True)
    ctypes.windll.user32.ShowWindow(hwnd, 3)   # SW_MAXIMIZE
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

def wait_for_samsunglife(timeout=30):
    """Chờ browser Samsung Life xuất hiện, tối đa timeout giây"""
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

print("Start")

# Minimize CMD
hwnd_cmd = ctypes.windll.kernel32.GetConsoleWindow()
ctypes.windll.user32.ShowWindow(hwnd_cmd, 6)

# Mở Edge
open_edge("https://ga.samsunglife.com/")

# Đóng popup trước
close_popup_if_exists(timeout=10)

# Chờ main browser
hwnd_main = wait_for_samsunglife(timeout=30)
if not hwnd_main:
    exit()

force_foreground(hwnd_main)
time.sleep(2)


# ── Login ──────────────────────────────────────────────────────
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
time.sleep(15)

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

print("End")