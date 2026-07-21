"""
This script performs Optical Character Recognition (OCR) on a specific region of the screen.
IMPORTANT: This is a standalone helper script designed to be executed as a subprocess by 
`kbg_handle_login.py` (and potentially other scripts like `ssl_handle_login_v3.py`).
It takes a screenshot of the coordinates (135, 110) to (210, 150), extracts Korean/English text 
using `easyocr`, and prints the result to standard output, which is then captured by the caller.
"""
import pyautogui
import numpy as np
import cv2
import easyocr
from pathlib import Path
from datetime import datetime

SAVE_DIR = Path(r"C:\Users\RPA02\Documents\UiPath\RPA\Python_Script\Log")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

reader = easyocr.Reader(["en", "ko"], gpu=False)

# Step 1: Define the region coordinates to capture (x1, y1, x2, y2)
x1, y1, x2, y2 = 135, 110, 210, 150
width  = x2 - x1
height = y2 - y1

# Step 2: Take a screenshot of the specific region
screenshot = pyautogui.screenshot(region=(x1, y1, width, height))

# Save debug image
save_path = SAVE_DIR / f"ocr_raw_kbg_{datetime.now().strftime('%H%M%S')}.png"
screenshot.save(str(save_path))

# Step 3: Convert the PIL screenshot object to a numpy array for OpenCV processing
img = np.array(screenshot)

# Step 4: Resize the image to 200% using cubic interpolation to improve OCR accuracy on small text
img_resized = cv2.resize(img, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)

# Step 5: Read the text from the resized image. detail=0 returns only the text list (no bounding boxes)
result = reader.readtext(img_resized, detail=0)

# Step 6: Join the list of detected text snippets into a single string and strip leading/trailing spaces
text = " ".join(result).strip()

# Step 7: Print the final text to stdout and force flush so the parent process captures it immediately
print(text, flush=True)