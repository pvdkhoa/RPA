import win32api, win32con, win32gui, win32com.client, time
shell = win32com.client.Dispatch("WScript.Shell")

def get_hwnd():
    """
    Finds and returns the window handle (hwnd) of the Meritz Fire & Marine Insurance application.
    Raises an exception if the window is not found.
    """
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if '메리츠화재' in title:
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    if not result:
        raise Exception("Cannot find the Meritz Fire & Marine Insurance window!")
    print(f"Found window: hwnd={result[0]}")
    return result[0]

def close_popups():
    """
    Closes all 'ComShareMsiePopup' windows that might be blocking the main UI.
    """
    count = 0
    def callback(hwnd, _):
        nonlocal count
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'ComShareMsiePopup' in title:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                print(f"Closed popup: hwnd={hwnd}")
                count += 1
    win32gui.EnumWindows(callback, None)
    print(f"Total popups closed: {count}")

def click(x, y):
    """
    Brings the application window to the foreground and simulates a left mouse click 
    at the specified (x, y) coordinates.
    """
    hwnd = get_hwnd()
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    win32api.SetCursorPos((x, y))
    time.sleep(0.3)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(0.5)

def type_text(text):
    """
    Simulates typing text using WScript.Shell SendKeys.
    """
    shell.SendKeys(str(text))
    time.sleep(0.3)

def clear_and_type(x, y, text):
    """
    Clicks on a specified (x, y) input field, clears its existing content, 
    and types the new text.
    """
    click(x, y)
    shell.SendKeys("^a")
    time.sleep(0.1)
    shell.SendKeys("{DELETE}")
    time.sleep(0.1)
    type_text(text)

print('Started process...')

click(444,55)
time.sleep(1)

click(482,152)
time.sleep(1)

click(605,236)
time.sleep(10)

print('DONE!')