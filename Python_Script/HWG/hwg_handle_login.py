import win32api, win32con, win32com.client, time

shell = win32com.client.Dispatch("WScript.Shell")

def click(x, y, delay=0.5):
    """Di chuyển chuột đến (x, y) và click chuột trái"""
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, int(x), int(y), 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, int(x), int(y), 0, 0)
    time.sleep(delay)

def type_text(text):
    """Gõ chuỗi ký tự"""
    shell.SendKeys(str(text))
    time.sleep(0.3)

def clear_and_type(x, y, text):
    """Click vào ô, xóa nội dung và nhập mã mới"""
    click(x, y, delay=0.2)
    shell.SendKeys("^a")
    time.sleep(0.1)
    shell.SendKeys("{DELETE}")
    time.sleep(0.1)
    type_text(text)

# ─────────────────────────────────────────
# THỰC THI CHÍNH
# ─────────────────────────────────────────
print("Bắt đầu thực hiện...")

# 1. Chờ popup xuất hiện ổn định trên màn hình
time.sleep(5)
# click button sms
click(374, 181)
# click button ok
time.sleep(5)
click(430, 194)
print("DONE!")
