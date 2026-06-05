import win32api, win32con, win32gui
import ctypes
import time

# Danh sách 14 công ty
COMPANY_TITLES = [
    '삼성생명', '라이나생명', 'DB생명', '메트라이프', 'KB라이프',
    '카디프생명', '현대해상', '메리츠화재', 'DB손보', 'KB손보',
    '삼성화재', '한화손보', '흥국화재', '롯데손보', '영업 홈', 'BNP 파리바 카디프생명'
]

def get_hwnd_by_company():
    """Lấy hwnd browser có title chứa tên 1 trong 14 công ty"""
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            for company in COMPANY_TITLES:
                if company in title:
                    result.append((hwnd, title, company))
                    break
    win32gui.EnumWindows(callback, None)
    return result

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

# ── Main ──
print("Start")

# Minimize CMD
hwnd_cmd = ctypes.windll.kernel32.GetConsoleWindow()
ctypes.windll.user32.ShowWindow(hwnd_cmd, 6)

# Tìm browser
windows = get_hwnd_by_company()
if not windows:
    print("Không tìm thấy browser nào!")
    exit()

hwnd, title, company = windows[0]
print(f"Found: [{company}] {title}")

# Click vào tọa độ 278, 145
click(hwnd, 98, 24)
print("Click done!")