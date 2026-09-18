import win32api
import win32con
import time


def click(x, y):
    """Click at a fixed screen coordinate."""
    print(f"Clicking at ({x}, {y})...")

    # Move mouse to the target position
    win32api.SetCursorPos((x, y))
    time.sleep(0.3)

    # Left mouse button down
    win32api.mouse_event(
        win32con.MOUSEEVENTF_LEFTDOWN,
        x,
        y,
        0,
        0
    )

    # Left mouse button up
    win32api.mouse_event(
        win32con.MOUSEEVENTF_LEFTUP,
        x,
        y,
        0,
        0
    )

    time.sleep(0.5)


# ===== MAIN =====

click(954, 528)

print("DONE!")