import win32gui, win32con
import ctypes
import time
import os

# List of 14 companies
COMPANY_TITLES = [
    '삼성생명', '라이나생명', 'DB생명', '메트라이프', 'KB라이프',
    '카디프생명', '현대해상', '메리츠화재', 'DB손보', 'KB손보',
    '삼성화재', '한화손보', '흥국화재', '롯데손보', '영업 홈', 'BNP 파리바 카디프생명', 'NGS - 영업지원시스템','Open GA'
]

def get_hwnd_by_company():
    """Gets the browser hwnd that contains the name of one of the 14 companies in its title."""
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

def close_browser_by_hwnd(hwnd, title):
    """Close browser window gracefully by hwnd, fallback to taskkill if needed."""
    print(f"Closing browser: {title}")

    # Step 1: Graceful close via WM_CLOSE
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    time.sleep(2)

    # Step 2: Check if window still exists → force close via taskkill
    if win32gui.IsWindow(hwnd):
        print(f"Window still alive after WM_CLOSE → force closing via taskkill...")
        _, pid = win32gui.GetWindowThreadProcessId(hwnd)
        os.system(f"taskkill /f /pid {pid} 2>nul")
        time.sleep(1)

    # Step 3: Verify
    if not win32gui.IsWindow(hwnd):
        print(f"Browser closed successfully!")
    else:
        print(f"Warning: Could not close browser!")

# ── Main ──
print("Start")

# Minimize CMD
hwnd_cmd = ctypes.windll.kernel32.GetConsoleWindow()
ctypes.windll.user32.ShowWindow(hwnd_cmd, 6)

# Find browser
windows = get_hwnd_by_company()
if not windows:
    print("Cannot find any browser!")
    exit()

hwnd, title, company = windows[0]
print(f"Found: [{company}] {title}")

# Close browser
close_browser_by_hwnd(hwnd, title)