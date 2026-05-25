import win32api, win32con, win32gui, win32com.client, time

shell = win32com.client.Dispatch("WScript.Shell")

def get_hwnd():
    """Tìm hwnd của cửa sổ DB손보 động"""
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'DB손해보험' in title:
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    if not result:
        raise Exception("Không tìm thấy cửa sổ DB손해보험!")
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

print('Bat dau click...')

# Menu navigation
click(144, 264)
print('Da click menu chinh')
time.sleep(0.5)

click(189, 267)
print('Da click menu item 1')
time.sleep(0.5)

click(193, 355)
print('Da click menu item 2')
time.sleep(0.5)

click(231, 540)
print('Da click menu item 3')
time.sleep(0.5)

click(232, 601)
print('Da click menu item 4')
time.sleep(3)

# Selection Box Insurance type
click(670, 172)
print('Da click Selection Box Insurance type')
time.sleep(1)

click(638, 240)
print('Da click Selection Item Long Term')
time.sleep(1)

# Selection Box 2
click(871, 175)
print('Da click Selection Box 2')
time.sleep(0.5)

click(840, 220)
print('Da click Selection Item 2')
time.sleep(1)

# Search
click(1361, 208)
print('Da click Search button')
time.sleep(2)

print('DONE!')