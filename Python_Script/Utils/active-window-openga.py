import win32api, win32con, win32gui
import ctypes
import time

# List of 14 companies
COMPANY_TITLES = [
    '삼성생명', '라이나생명', 'DB생명', '메트라이프', 'KB라이프',
    '카디프생명', '현대해상', '메리츠화재', 'DB손보', 'KB손보',
    '삼성화재', '한화손보', '흥국화재', '롯데손보']

def get_hwnd_by_company():
    """Gets the browser hwnd that contains the name of one of the 14 companies in its title."""
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            for company in COMPANY_TITLES:
                if company in title:
                    result.append((hwnd, title, company))
                    break
    win32gui.EnumWindows(callback, None)
    return result

def force_foreground(hwnd):
    fgwin = ctypes.windll.user32.GetForegroundWindow()
    fgthread = ctypes.windll.user32.GetWindowThreadProcessId(fgwin, None)
    curthread = ctypes.windll.kernel32.GetCurrentThreadId()
    ctypes.windll.user32.AttachThreadInput(fgthread, curthread, True)
    ctypes.windll.user32.ShowWindow(hwnd, 3)
    ctypes.windll.user32.BringWindowToTop(hwnd)
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    ctypes.windll.user32.AttachThreadInput(fgthread, curthread, False)
    time.sleep(0.8)

def click(hwnd, x, y):
    """Gửi lệnh click TRỰC TIẾP vào cửa sổ Chrome bằng PostMessage.
    x, y là tọa độ TƯƠNG ĐỐI so với góc trên-trái của vùng nội dung cửa sổ (client area).
    Không bị ảnh hưởng bởi DPI, RDP 50% hay 100%."""
    force_foreground(hwnd)
    
    # Tạo tọa độ dạng lParam cho Windows Message
    lParam = win32api.MAKELONG(x, y)
    
    # Gửi lệnh click trực tiếp vào Chrome (không cần di chuyển chuột trên màn hình)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    time.sleep(0.1)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
    time.sleep(0.5)

# ── Main ──
print("Start")

# Minimize CMD
hwnd_cmd = ctypes.windll.kernel32.GetConsoleWindow()
ctypes.windll.user32.ShowWindow(hwnd_cmd, 6)

# Find browser
windows = get_hwnd_by_company()
if not windows:
    print("Cannot find any browser!")
    exit()

hwnd, title, company = windows[0]
print(f"Found: [{company}] {title}")

# Click at coordinates (Tọa độ tương đối bên trong cửa sổ Chrome)
time.sleep(3)
click(hwnd, 98, 24)
print("Active Done!")

time.sleep(3)
click(hwnd, 230, 134)
print("Click Upload Icon!")

time.sleep(3)