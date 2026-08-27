"""
This script automates the process of selecting the 'General' insurance type 
and executing a search on the DB Insurance application.
"""
import win32api, win32con, win32gui, win32com.client, time
import ctypes

shell = win32com.client.Dispatch("WScript.Shell")

def get_hwnd():
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'DB손해보험' in title:
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    if not result:
        raise Exception("Cannot find the DB Insurance window!")
    print(f"Found window: hwnd={result[0]}")
    return result[0]

def force_foreground(hwnd):
    """
    Bring window lên foreground mà không thay đổi size/state.
    """
    # Lấy thread của foreground window hiện tại và thread của target window
    foreground_hwnd = win32gui.GetForegroundWindow()
    foreground_tid = ctypes.windll.user32.GetWindowThreadProcessId(foreground_hwnd, None)
    target_tid = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)

    # Attach thread input để bypass Windows restriction
    if foreground_tid != target_tid:
        ctypes.windll.user32.AttachThreadInput(foreground_tid, target_tid, True)
        win32gui.BringWindowToTop(hwnd)
        win32gui.SetForegroundWindow(hwnd)
        ctypes.windll.user32.AttachThreadInput(foreground_tid, target_tid, False)
    else:
        win32gui.SetForegroundWindow(hwnd)

    # Verify foreground
    for _ in range(10):
        time.sleep(0.1)
        if win32gui.GetForegroundWindow() == hwnd:
            print("Window is now in foreground.")
            return True

    print("Warning: Could not bring window to foreground!")
    return False

def click(x, y):
    hwnd = get_hwnd()
    force_foreground(hwnd)
    time.sleep(0.3)
    win32api.SetCursorPos((x, y))
    time.sleep(0.2)
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


# Minimize CMD
hwnd_cmd = ctypes.windll.kernel32.GetConsoleWindow()
ctypes.windll.user32.ShowWindow(hwnd_cmd, 6)  # SW_MINIMIZE = 6
time.sleep(5)

# Bring app to foreground trước khi bắt đầu
hwnd = get_hwnd()
force_foreground(hwnd)

print('Started process: clicking...')
time.sleep(5)
# Selection Box Insurance type
click(670, 172)
print('Clicked Selection Box Insurance type')
time.sleep(3)

click(640, 257)
print('Clicked Selection Item General')
time.sleep(3)

# Search
click(1361, 208)
print('Clicked Search button')
time.sleep(3)

print('DONE!')