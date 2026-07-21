"""
This script automates navigation through the DB Insurance application menu 
and selects the 'Long Term' insurance type to perform a search.
"""
import win32api, win32con, win32gui, win32com.client, time

shell = win32com.client.Dispatch("WScript.Shell")

def get_hwnd():
    """
    Finds and returns the window handle (hwnd) of the DB Insurance application.
    Raises an exception if the window is not found.
    """
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

print('Started process: clicking...')

# Menu navigation
click(144, 264)
print('Clicked main menu')
time.sleep(0.5)

click(189, 267)
print('Clicked menu item 1')
time.sleep(0.5)

click(193, 355)
print('Clicked menu item 2')
time.sleep(0.5)

click(231, 540)
print('Clicked menu item 3')
time.sleep(0.5)

click(232, 601)
print('Clicked menu item 4')
time.sleep(3)

# Selection Box Insurance type
click(670, 172)
print('Clicked Selection Box Insurance type')
time.sleep(1)

click(638, 240)
print('Clicked Selection Item Long Term')
time.sleep(1)

# Selection Box 2
click(871, 175)
print('Clicked Selection Box 2')
time.sleep(0.5)

click(840, 220)
print('Clicked Selection Item 2')
time.sleep(1)

# Search
click(1361, 208)
print('Clicked Search button')
time.sleep(2)

print('DONE!')