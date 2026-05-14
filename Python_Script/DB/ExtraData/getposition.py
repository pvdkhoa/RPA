import pyautogui
import time

print("Di chuột vào vị trí cần lấy tọa độ...")

time.sleep(3)

while True:
    x, y = pyautogui.position()
    print(f"X={x}, Y={y}")
    time.sleep(0.5)