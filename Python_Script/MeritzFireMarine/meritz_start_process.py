import win32api, win32con, win32gui, win32com.client, time
shell = win32com.client.Dispatch("WScript.Shell")

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

def close_popups():
    """Đóng tất cả popup ComShareMsiePopup"""
    count = 0
    def callback(hwnd, _):
        nonlocal count
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'ComShareMsiePopup' in title:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                print(f"Da dong popup: hwnd={hwnd}")
                count += 1
    win32gui.EnumWindows(callback, None)
    print(f"Tong so popup da dong: {count}")

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

print('Bat dau close popup...')
close_popups()
time.sleep(1)

print('Close popup')
click(997,261)
time.sleep(0.5)

print('DONE!')