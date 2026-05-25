import win32api, win32con, win32gui, win32com.client, time, sys
from datetime import datetime
shell = win32com.client.Dispatch("WScript.Shell")

# ====== Lấy ngày hiện tại format yyyyMMdd ======
today = datetime.now().strftime("%Y%m%d")

def get_hwnd():
    """Tìm hwnd của cửa sổ 메리츠화재 động"""
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if '메리츠화재' in title:
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    if not result:
        raise Exception("Không tìm thấy cửa sổ 메리츠화재!")
    print(f"Tim thay cua so: hwnd={result[0]}")
    return result[0]

def get_hwnd_folder():
    """Tìm hwnd của cửa sổ folder Windows (Save As dialog)"""
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            # Các title phổ biến của Windows Save As dialog
            if any(keyword in title for keyword in ['다른 이름으로 저장', 'Save As', 'Save', '저장']):
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    return result[0] if result else None

def click(x, y):
    hwnd = get_hwnd()
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    win32api.SetCursorPos((x, y))
    time.sleep(0.3)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(0.5)

def type_text(text):
    shell.SendKeys(str(text))
    time.sleep(0.3)

def clear_and_type(x, y, text):
    click(x, y)
    shell.SendKeys("^a")
    time.sleep(0.1)
    shell.SendKeys("{DELETE}")
    time.sleep(0.1)
    type_text(text)

print('Click Menu 1')
click(867,47)
time.sleep(0.5)

print('Click Menu 2')
click(876,203)
time.sleep(0.5)

print('Click Menu 3')
click(1080,415)
time.sleep(5)

print('Close popup')
click(1011,191)
time.sleep(5)

print('Clear and type Start Date')
clear_and_type(353,159, today)
time.sleep(3)

print('Clear and type End Date')
clear_and_type(475,156, today)
time.sleep(3)

print('Click Search')
click(943,156)
time.sleep(3)
