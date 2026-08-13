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

# Titles of the MAIN application windows - these must NEVER be closed.
# Add more names here if additional systems are involved.
MAIN_WINDOW_TITLES = ['메리츠화재', 'DB손해보험-통합']

def close_popups():
    """
    Closes any visible child/owned popup window that is not one of the
    main application windows. No longer relies on a specific keyword like
    '팝업공지', since the portal can spawn various types of popups
    (surveys, ads, system notices, etc.) with unpredictable titles.
    """
    count = 0

    def callback(hwnd, _):
        nonlocal count
        # Step 1: Skip windows that aren't currently visible
        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd)
        owner = win32gui.GetWindow(hwnd, win32con.GW_OWNER)

        # Step 2: This is a MAIN window (no owner AND title matches whitelist)
        # -> leave it alone
        if owner == 0 and any(name in title for name in MAIN_WINDOW_TITLES):
            return

        # Step 3: Everything else visible (owned windows, or ownerless
        # windows not in the whitelist) is treated as a popup/ad -> close it
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        print(f"Closed popup: hwnd={hwnd} owner={owner} title={title!r}")
        count += 1

    # Step 4: Enumerate all top-level windows and apply the callback
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
close_popups()
time.sleep(1)

print('Closed popup')
click(997,261)
time.sleep(0.5)

print('DONE!')