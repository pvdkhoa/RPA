import win32api, win32con, win32gui, win32com.client, time, sys
from datetime import datetime
shell = win32com.client.Dispatch("WScript.Shell")
# ====== Get current date in yyyyMMdd format ======
today = datetime.now().strftime("%Y%m%d")
def get_hwnd():
    """
    Finds and returns the window handle (hwnd) of the Meritz Fire & Marine Insurance application.
    Raises an exception if the window is not found.
    """
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if '\uba54\ub9ac\uce20\ud654\uc7ac' in title:
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    if not result:
        raise Exception("Cannot find the Meritz Fire & Marine Insurance window!")
    print(f"Found window: hwnd={result[0]}")
    return result[0]
def get_hwnd_folder():
    """
    Finds and returns the window handle (hwnd) of the folder or save dialog window.
    """
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if any(keyword in title for keyword in ['Save As', 'Save', 'FileSave']):
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    return result[0] if result else None
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
print('Click Selection Box')
click(204,261)
time.sleep(0.5)
print('Click Download button')
click(1316,259)
time.sleep(1)
print('Type Into')
clear_and_type(739,410,6412301932814)
time.sleep(1)
print('Click Apply button')
click(728,459)
time.sleep(1)
print('Click Confirm popup')
click(772,460)
time.sleep(8)
print('Check Folder Dialog...')
folder_hwnd = get_hwnd_folder()
if folder_hwnd is None:
    print('Cannot find folder window!')
    raise Exception("Cannot find folder/save dialog window.")
print(f'Found folder window: hwnd={folder_hwnd}')
print('Click enter')
click(952,232)
time.sleep(1)
print('Click Save button')
click(1028,621)
time.sleep(6)
print('Click Completed button')
click(788,503)
time.sleep(1)
print('DONE!')