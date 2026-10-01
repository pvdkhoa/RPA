import win32api, win32con, win32gui
import ctypes
import time

# List of 14 companies
COMPANY_TITLES = [
    '삼성생명', '라이나생명', 'DB생명', '메트라이프', 'KB라이프',
    '카디프생명', '현대해상', '메리츠화재', 'DB손보', 'KB손보','KB생명',
    '삼성화재', '한화손보', '흥국화재', '롯데손보','한화손해','롯데손해']

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

import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime
from PIL import ImageGrab, ImageDraw

# Thư mục lưu ảnh debug
DEBUG_DIR = Path(tempfile.gettempdir()) / "openga_debug"
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

def force_foreground(hwnd):
    try:
        ctypes.windll.user32.SystemParametersInfoW(0x2001, 0, 0, 0)
    except Exception:
        pass
    fgwin = ctypes.windll.user32.GetForegroundWindow()
    fgthread = ctypes.windll.user32.GetWindowThreadProcessId(fgwin, None)
    curthread = ctypes.windll.kernel32.GetCurrentThreadId()
    if fgthread != curthread and fgthread != 0:
        ctypes.windll.user32.AttachThreadInput(fgthread, curthread, True)
    ctypes.windll.user32.ShowWindow(hwnd, 3)
    ctypes.windll.user32.BringWindowToTop(hwnd)
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    if fgthread != curthread and fgthread != 0:
        ctypes.windll.user32.AttachThreadInput(fgthread, curthread, False)
    time.sleep(0.8)

def capture_and_mark_click(screen_x, screen_y, label, rel_x, rel_y):
    """Chụp màn hình và vẽ hồng tâm đỏ đánh dấu điểm click vào thư mục Temp"""
    try:
        # Chụp toàn màn hình
        img = ImageGrab.grab()
        draw = ImageDraw.Draw(img)
        
        # Vẽ vòng tròn đỏ tại điểm click
        r = 15
        draw.ellipse((screen_x - r, screen_y - r, screen_x + r, screen_y + r), outline="red", width=3)
        # Vẽ dấu thập (crosshair)
        draw.line((screen_x - 30, screen_y, screen_x + 30, screen_y), fill="red", width=2)
        draw.line((screen_x, screen_y - 30, screen_x, screen_y + 30), fill="red", width=2)
        
        # Ghi thông tin tọa độ lên ảnh
        text = f"[{label}] Rel: ({rel_x}, {rel_y}) -> Screen: ({screen_x}, {screen_y})"
        draw.text((screen_x + 20, screen_y - 20), text, fill="red")
        
        # Lưu file vào thư mục temp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
        file_path = DEBUG_DIR / f"click_{label}_{timestamp}.png"
        img.save(file_path)
        print(f"[DEBUG_IMAGE] Screenshot saved to: {file_path}")
    except Exception as e:
        print(f"[DEBUG_IMAGE] Warning: Could not save screenshot: {e}")

def click(hwnd, x, y, label="click"):
    # Chuyển tọa độ tương đối bên trong cửa sổ (client area) sang tọa độ màn hình thực tế
    screen_x, screen_y = win32gui.ClientToScreen(hwnd, (int(x), int(y)))
    print(f"[{label}] Rel: ({x}, {y}) -> Screen: ({screen_x}, {screen_y})")
    
  
    
    win32api.SetCursorPos((screen_x, screen_y))
    time.sleep(0.3)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, screen_x, screen_y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, screen_x, screen_y, 0, 0)
    time.sleep(0.5)

# ── Main ──
print(f"Start (Debug Folder: {DEBUG_DIR})")

# Minimize CMD
hwnd_cmd = ctypes.windll.kernel32.GetConsoleWindow()
if hwnd_cmd:
    ctypes.windll.user32.ShowWindow(hwnd_cmd, 6)

# Find browser
windows = get_hwnd_by_company()
if not windows:
    print("Cannot find any browser!")
    exit()

hwnd, title, company = windows[0]
print(f"Found: [{company}] {title}")

# Focus cửa sổ trước khi click
force_foreground(hwnd)
time.sleep(1)

# Click Tab / Active
click(hwnd, 104, 6, label="Active_Tab")
print("Active Done!")

time.sleep(2)
# Click Upload Icon (tọa độ tương đối bên trong cửa sổ)
click(hwnd, 138, 131, label="Upload_Icon")
print("Click Upload Icon!")

time.sleep(2)