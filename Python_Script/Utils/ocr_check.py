import pyautogui
import numpy as np
import cv2
import easyocr
from pathlib import Path
from datetime import datetime

"""
This script uses easyocr to extract text from a specific screen region (login status area).
It is intended to be called as a subprocess by login handlers (like ssf_handle_login.py) 
to verify if the login was successful or if the page is still loading.
"""

SAVE_DIR = Path.home() / "Downloads"

reader = easyocr.Reader(["en", "ko"], gpu=False, verbose=False)

x1, y1, x2, y2 = 14, 100, 105, 140 
width  = x2 - x1
height = y2 - y1

screenshot = pyautogui.screenshot(region=(x1, y1, width, height))

# Save debug image
save_path = SAVE_DIR / f"ocr_raw_{datetime.now().strftime('%H%M%S')}.png"
screenshot.save(str(save_path))

img = np.array(screenshot)
img_resized = cv2.resize(img, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)

result = reader.readtext(img_resized, detail=0)
text = " ".join(result).strip()

print(text, flush=True)