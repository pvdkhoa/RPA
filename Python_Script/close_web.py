"""
close_web.py
-----------------
Kill browser/RPA/Nexacro processes using taskkill.
Compatible with Windows Korean OS (CP949) and international environments.
Requires: Python 3.6+, pyautogui (pip install pyautogui) for the Ctrl+W step.
"""

import subprocess
import sys
import time

try:
    import pyautogui
except ImportError:
    pyautogui = None

PROCESS_NAMES = [
    "msedge.exe",
    "chrome.exe",
    "chromedriver.exe",
    "msedgedriver.exe",
    "XPlatform.exe",
    "nexacro.exe",
    "nexacroplatform.exe",
    "MatrixBrowser.exe",
]


def kill_via_taskkill(process_name: str) -> bool:
    """Kill process using standard Windows taskkill command."""
    try:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", process_name, "/T"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
        # returncode == 0 indicates successful termination
        return result.returncode == 0
    except Exception as e:
        print(f"Error killing {process_name}: {e}")
        return False


def send_ctrl_w(times: int = 2, delay: float = 1.0):
    """Send Ctrl+W keystroke 'times' times."""
    if pyautogui is None:
        print("  [!] pyautogui not installed, skipping Ctrl+W step.")
        return
    for i in range(1, times + 1):
        try:
            pyautogui.hotkey("ctrl", "w")
            print(f"  [OK] Ctrl+W sent ({i}/{times})")
        except Exception as e:
            print(f"  [!] Error sending Ctrl+W: {e}")
        time.sleep(delay)


def main():
    print("=" * 50)
    print("Kill Browser & Nexacro Processes (Taskkill)")
    print("=" * 50)

    for name in PROCESS_NAMES:
        success = kill_via_taskkill(name)
        if success:
            print(f"  [OK] Killed: {name}")
        else:
            print(f"  [--] Not found or already closed: {name}")

    # Extra: send Ctrl+W x2 at the end
    send_ctrl_w(times=2, delay=1.0)

    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())