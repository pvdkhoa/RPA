import sys
import pyautogui
import numpy as np
import cv2
import easyocr
from pathlib import Path
from datetime import datetime

"""
This script uses easyocr to extract text from a screen region.
Region can be passed as CLI args: x1 y1 x2 y2
If not provided, defaults to the login-status area.
Called as a subprocess by login handlers (like ssl_handle_login.py)
to verify page state (e.g. login success, popup detection).
"""

SAVE_DIR = Path(r"C:\Users\RPA02\Documents\UiPath\RPA\Python_Script\Log")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

reader = easyocr.Reader(["en", "ko"], gpu=False, verbose=False)

# ── Screen region: default = login-status area, override via CLI args ──
if len(sys.argv) >= 5:
    x1, y1, x2, y2 = map(int, sys.argv[1:5])
else:
    x1, y1, x2, y2 = 14, 100, 105, 140

width  = x2 - x1
height = y2 - y1
screenshot = pyautogui.screenshot(region=(x1, y1, width, height))

# Save debug image
save_path = SAVE_DIR / f"ocr_raw_ssl_{datetime.now().strftime('%H%M%S')}.png"
screenshot.save(str(save_path))

img = np.array(screenshot)
img_resized = cv2.resize(img, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
result = reader.readtext(img_resized, detail=0)
text = " ".join(result).strip()
print(text, flush=True)