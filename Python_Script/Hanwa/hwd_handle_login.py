import win32api, win32con, win32gui, win32com.client, time
import win32process
import ctypes

shell = win32com.client.Dispatch("WScript.Shell")

def get_hwnd_popup():
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if '대리점 인증' in title:
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    return result[0] if result else None

def force_foreground(hwnd):
    # Trick để bypass Windows foreground lock
    ctypes.windll.user32.ShowWindow(hwnd, 9)        # SW_RESTORE
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    time.sleep(0.5)

def click(x, y):
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

print("Start")
time.sleep(5)

# Tìm popup và đưa lên foreground
hwnd = get_hwnd_popup()
if hwnd:
    force_foreground(hwnd)
    print(f"Found popup hwnd: {hwnd}, brought to foreground")
else:
    print("Popup not found!")

time.sleep(3)
clear_and_type(390, 189, 1208810829)
time.sleep(2)
click(464, 183)
print("End")