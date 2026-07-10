import win32api, win32con, win32gui, win32com.client, time
shell = win32com.client.Dispatch("WScript.Shell")

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

def close_program():
    """
    Closes the main Meritz Fire & Marine Insurance application window.
    """
    try:
        # Step 1: Find the main application window handle
        hwnd = get_hwnd()
        # Step 2: Send a WM_CLOSE message to close the application gracefully
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        print(f"Closed program: hwnd={hwnd}")
    except Exception as e:
        print(f"Error closing program: {e}")

def close_popups():
    """
    Closes all 'ComShareMsiePopup' windows that might be blocking the main UI.
    """
    count = 0
    
    # Step 1: Define a callback function to check each window
    def callback(hwnd, _):
        nonlocal count
        # Step 2: Check if the window is visible
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            # Step 3: Identify the specific popup by its title
            if 'ComShareMsiePopup' in title:
                # Step 4: Send a WM_CLOSE message to gracefully close the popup
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                print(f"Closed popup: hwnd={hwnd}")
                count += 1
                
    # Step 5: Enumerate all windows to apply the callback
    win32gui.EnumWindows(callback, None)
    print(f"Total popups closed: {count}")

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

print('Started process: closing popup...')
close_program()

print('DONE!')