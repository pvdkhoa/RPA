"""
This script handles the login process for Hanwha by finding the agency certification popup 
and entering the necessary credentials.
"""
import win32api, win32con, win32gui, win32com.client, time
import win32process
import ctypes

shell = win32com.client.Dispatch("WScript.Shell")

def get_hwnd_popup():
    """
    Finds and returns the window handle (hwnd) of the Hanwha agency certification popup.
    """
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if '대리점 인증' in title:
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    return result[0] if result else None

def force_foreground(hwnd):
    """
    Forces the specified window to the foreground.
    """
    # Trick to bypass Windows foreground lock
    ctypes.windll.user32.ShowWindow(hwnd, 9)        # SW_RESTORE
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    time.sleep(0.5)

def click(x, y):
    """
    Simulates a left mouse click at the specified (x, y) coordinates.
    """
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

print("Started process...")
time.sleep(5)

# Find popup and bring to foreground
hwnd = get_hwnd_popup()
if hwnd:
    force_foreground(hwnd)
    print(f"Found popup hwnd: {hwnd}, brought to foreground")
else:
    print("Popup not found!")
    raise Exception("Cannot find the Hanwha popup window!")

time.sleep(3)
clear_and_type(390, 189, 1208810829)
print("Entered value: 1208810829")
time.sleep(2)
click(464, 183)
print("Clicked login button")
print("DONE!")