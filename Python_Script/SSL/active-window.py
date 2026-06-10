import win32api, win32con, win32gui
import ctypes
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

KEYEVENTF_KEYUP = 0x0002

COMPANY_TITLES = [
    '삼성생명', '라이나생명', 'DB생명', '메트라이프', 'KB라이프',
    '카디프생명', '현대해상', '메리츠화재', 'DB손보', 'KB손보',
    '삼성화재', '한화손보', '흥국화재', '롯데손보', '영업 홈',
    'BNP 파리바 카디프생명', 'NGS - 영업지원시스템'
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

def force_foreground_safe(hwnd):
    # Step 1: Cho phép bất kỳ process nào set foreground
    user32.AllowSetForegroundWindow(-1)

    # Step 2: ALT key trick — unlock foreground restriction
    user32.keybd_event(0x12, 0, 0, 0)
    user32.keybd_event(0x12, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)

    # Step 3: SW_RESTORE trước — tránh black screen
    user32.ShowWindow(hwnd, 9)
    time.sleep(0.2)

    # Step 4: SwitchToThisWindow
    user32.SwitchToThisWindow(hwnd, True)
    time.sleep(0.1)

    # Step 5: AttachThreadInput + SetForegroundWindow
    fgwin = user32.GetForegroundWindow()
    fgthread = user32.GetWindowThreadProcessId(fgwin, None)
    curthread = kernel32.GetCurrentThreadId()

    if fgthread != curthread:
        user32.AttachThreadInput(fgthread, curthread, True)
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
        user32.AttachThreadInput(fgthread, curthread, False)
    else:
        user32.SetForegroundWindow(hwnd)

    # Step 6: Verify foreground loop
    for _ in range(30):
        if user32.GetForegroundWindow() == hwnd:
            break
        time.sleep(0.1)
    else:
        # Fallback nếu sau 3s vẫn chưa foreground
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.5)

    # Step 7: SW_MAXIMIZE sau khi đã là foreground — không black screen
    user32.ShowWindow(hwnd, 3)
    time.sleep(0.3)

def click(hwnd, x, y):
    force_foreground_safe(hwnd)
    time.sleep(0.3)
    win32api.SetCursorPos((x, y))
    time.sleep(0.2)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(0.5)

# ── Main ──
print("Start")

# Minimize CMD
hwnd_cmd = kernel32.GetConsoleWindow()
user32.ShowWindow(hwnd_cmd, 6)

# Tìm browser
windows = get_hwnd_by_company()
if not windows:
    print("Không tìm thấy browser nào!")
    exit()

hwnd, title, company = windows[0]
print(f"Found: [{company}] {title} | hwnd={hwnd}")

# Click vào tọa độ
click(hwnd, 98, 24)
print("Click done!")