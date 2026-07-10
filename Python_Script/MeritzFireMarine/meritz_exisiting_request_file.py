import win32api, win32con, win32gui, win32com.client, time, sys
from datetime import datetime
shell = win32com.client.Dispatch("WScript.Shell")

# ====== Get current date in yyyyMMdd format ======
today = datetime.now().strftime("%Y%m%d")

def get_hwnd():
    """
    Finds and returns the window handle (hwnd) of the Meritz Fire & Marine Insurance application.
    Raises an exception if the window is not found.
    """
    result = []
    
    # Step 1: Define a callback function to evaluate each enumerated window
    def callback(hwnd, _):
        # Step 2: Check if the window is currently visible to the user
        if win32gui.IsWindowVisible(hwnd):
            # Step 3: Extract the title text of the window
            title = win32gui.GetWindowText(hwnd)
            # Step 4: Check if the application name '메리츠화재' is in the title
            if '메리츠화재' in title:
                result.append(hwnd)
                
    # Step 5: Enumerate all top-level windows on the screen, passing each to the callback
    win32gui.EnumWindows(callback, None)
    
    # Step 6: If no matching window is found, raise an exception to halt the script
    if not result:
        raise Exception("Cannot find the Meritz Fire & Marine Insurance window!")
        
    print(f"Found window: hwnd={result[0]}")
    # Step 7: Return the first matching window handle
    return result[0]

def get_hwnd_folder():
    """
    Finds and returns the window handle (hwnd) of the Windows Save As dialog.
    """
    result = []
    # Step 1: Define a callback to evaluate each window
    def callback(hwnd, _):
        # Step 2: Check if window is visible
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            # Step 3: Match common titles for Windows Save As dialogs in various languages
            if any(keyword in title for keyword in ['다른 이름으로 저장', 'Save As', 'Save', '저장']):
                result.append(hwnd)
    # Step 4: Enumerate all windows and pass them to the callback
    win32gui.EnumWindows(callback, None)
    # Step 5: Return the first matched handle, or None if not found
    return result[0] if result else None

def click(x, y):
    """
    Brings the application window to the foreground and simulates a left mouse click 
    at the specified (x, y) coordinates.
    """
    # Step 1: Retrieve the window handle of the main application
    hwnd = get_hwnd()
    
    # Step 2: Force the application window to the foreground so it can receive input
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    
    # Step 3: Move the physical mouse cursor to the target (x, y) coordinates
    win32api.SetCursorPos((x, y))
    time.sleep(0.3)
    
    # Step 4: Simulate pressing down the left mouse button
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    
    # Step 5: Simulate releasing the left mouse button to complete the click
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(0.5)

def type_text(text):
    """
    Simulates typing text using WScript.Shell SendKeys.
    """
    shell.SendKeys(str(text))
    time.sleep(0.3)

def clear_and_type(x, y, text):
    """
    Clicks on a specified (x, y) input field, clears its existing content, 
    and types the new text.
    """
    click(x, y)
    # Select all text inside the input field (Ctrl+A)
    shell.SendKeys("^a")
    time.sleep(0.1)
    # Delete the selected text
    shell.SendKeys("{DELETE}")
    time.sleep(0.1)
    # Type the new text
    type_text(text)

print('Click Close popup search data')
click(788,495)
time.sleep(2)

print('Click Close popup search data')
click(788,495)
time.sleep(2)

print('Click New Request')
click(1312,758)
time.sleep(2)

print('Click Include Maturity')
click(924,412)
time.sleep(1)

print('Click Apply')
click(736,478)
time.sleep(1)

print('Click Completed Popup')
click(784,497)
time.sleep(2)
