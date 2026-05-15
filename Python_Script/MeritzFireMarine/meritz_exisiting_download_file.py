import win32api, win32con, win32gui, win32com.client, time, sys
from datetime import datetime
shell = win32com.client.Dispatch("WScript.Shell")
# ====== Lay ngay hien tai format yyyyMMdd ======
today = datetime.now().strftime("%Y%m%d")
def get_hwnd():
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if '\uba54\ub9ac\uce20\ud654\uc7ac' in title:
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    if not result:
        raise Exception("Khong tim thay cua so \uba54\ub9ac\uce20\ud654\uc7ac!")
    print(f"Tim thay cua so: hwnd={result[0]}")
    return result[0]
def get_hwnd_folder():
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if any(keyword in title for keyword in ['Save As', 'Save', 'FileSave']):
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
    print('Khong tim thay cua so folder!')
    raise Exception("Khong tim thay cua so folder/save dialog.")
print(f'Tim thay cua so folder: hwnd={folder_hwnd}')
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