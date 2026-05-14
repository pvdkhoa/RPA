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

print('Click Long Term Insurance Type')
click(284,219)
time.sleep(0.5)

print('Click automobile insurance type')
click(471,216)
time.sleep(0.5)

print('Click Joint Property insurance type')
click(587,219)
time.sleep(0.5)

print('Click Search Button')
click(1342,187)
time.sleep(4)

print('Click Download button')
click(1271,253)
time.sleep(10)

print('DONE!')