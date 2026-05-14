import win32api, win32con, win32gui, win32com.client, time
import easyocr
import numpy as np
from PIL import ImageGrab
import cv2
import re

shell = win32com.client.Dispatch("WScript.Shell")

# ===== INIT OCR =====
reader = easyocr.Reader(['en'])

# =========================
# WINDOW HANDLE
# =========================
def get_hwnd():
    """Tìm hwnd của cửa sổ 메리츠화재 động"""
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if '메리츠화재' in title:
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    if not result:
        raise Exception("Không tìm thấy cửa sổ 메리츠화재!")
    print(f"Tim thay cua so: hwnd={result[0]}")
    return result[0]

# =========================
# CLICK
# =========================
def click(x, y):
    hwnd = get_hwnd()
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.3)

    win32api.SetCursorPos((x, y))
    time.sleep(0.2)

    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    time.sleep(0.5)

# =========================
# OCR FROM REGION
# =========================
def get_ocr_from_region():
    import numpy as np
    import cv2
    import re
    from PIL import ImageGrab

    # ===== TỌA ĐỘ ABSOLUTE (UPDATED) =====
    left = 711
    top = 676
    right = 776
    bottom = 688

    print("Capture:", left, top, right, bottom)

    # ===== CAPTURE =====
    img = ImageGrab.grab(bbox=(left, top, right, bottom))
    img_np = np.array(img)

    # ===== DEBUG =====
    cv2.imwrite("debug_crop.png", img_np)

    # ===== PREPROCESS =====
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

    # upscale giúp OCR tốt hơn
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    cv2.imwrite("debug_processed.png", gray)

    # ===== OCR (2 lần cho chắc) =====
    result1 = reader.readtext(gray, detail=0, allowlist='0123456789,')
    result2 = reader.readtext(img_np, detail=0, allowlist='0123456789,')

    text = " ".join(result1 + result2)

    print("Raw OCR:", text)

    # ===== EXTRACT NUMBER =====
    numbers = re.findall(r'[\d,]+', text)

    if numbers:
        return numbers[0]

    return text.strip()

# =========================
# MAIN FLOW
# =========================
print('Bat dau click...')
time.sleep(3)

# ===== OCR =====
ocr_text = get_ocr_from_region()
print("OCR result:", ocr_text)

print('DONE!')