import win32api, win32con, time

def click(x, y, delay=0.5):
    """
    Di chuyển chuột đến tọa độ (x, y) và thực hiện click chuột trái.
    """
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, int(x), int(y), 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, int(x), int(y), 0, 0)
    time.sleep(delay)

if __name__ == "__main__":

    CLICK_COORDINATES = [
        (1008, 120),   # Tọa độ nút đóng 1
        (910, 122),    # Tọa độ nút đóng 2
        (908, 66),    # Tọa độ nút đóng 3
  	(789, 124),    # Tọa độ nút đóng 4
	(666, 382),    # Tọa độ nút đóng 5
  	(1055,390),
    ]

    for idx, (x, y) in enumerate(CLICK_COORDINATES, start=1):
        print(f"[{idx}] Đang click vào tọa độ: ({x}, {y})")
        click(x, y, delay=1.0)

    print("Finish close!")
