import win32api, win32con, win32gui, win32com.client, time
import requests
import logging

log = logging.getLogger(__name__)

# ===== ORCHESTRATOR CONFIG =====
CLIENT_ID     = "a864297e-5ec8-4ca0-a456-3e8cbe0c2d95"
CLIENT_SECRET = "GG_Y9OPAKtiVfgML*de*B0_Xvv1Q?Bic@Gu2$PA31icIJ%dnt4(dDm5hEnY?Tx(v"
ORG_UNIT_ID   = "8773"
BASE_URL      = "https://cloud.uipath.com/miraeassetfp/DefaultTenant/orchestrator_"

TOGGLE_MANUAL_DOWNLOAD = "TOGGLE_MANUAL_DOWNLOAD"  # Value: "ON" / "OFF"
END_DATE_ASSET_NAME    = "END_DATE_DOWNLOAD"
START_DATE_ASSET_NAME  = "START_DATE_DOWNLOAD"

# ===== WIN32 SETUP =====
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
    and types the new text. (This version includes extra delays and refocusing).
    """
    # Step 1: Click the target field to focus it
    click(x, y)
    time.sleep(0.5)
    
    # Step 2: Ensure the window remains in the foreground after the click
    hwnd = get_hwnd()
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    
    # Step 3: Select all text (Ctrl+A)
    shell.SendKeys("^a")
    time.sleep(0.2)
    
    # Step 4: Delete the selected text
    shell.SendKeys("{DELETE}")
    time.sleep(0.2)
    
    # Step 5: Type the newly provided text
    type_text(text)

# ===== ORCHESTRATOR FUNCTIONS =====
def get_access_token():
    url = "https://cloud.uipath.com/identity_/connect/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "OR.Assets.Read OR.Assets.Write OR.Folders.Read",
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    token = response.json()["access_token"]
    log.info("[AUTH] Access token OK")
    return token

def get_asset_by_name(token, asset_name):
    url = f"{BASE_URL}/odata/Assets"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-UIPATH-OrganizationUnitId": ORG_UNIT_ID,
    }
    # Step 3: Filter assets by the specified name
    params = {"$filter": f"Name eq '{asset_name}'"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    # Step 4: Extract the asset list from the response JSON
    assets = response.json().get("value", [])
    # Step 5: Check if the asset was found, return None if missing
    if not assets:
        log.warning(f"[ASSET] Cannot find asset '{asset_name}'")
        return None
    # Step 6: Log success and return the first matching asset
    log.info(f"[ASSET] Found asset '{asset_name}'")
    return assets[0]

def get_asset_value(asset):
    return str(asset.get("Value", asset.get("StringValue", ""))).strip()

def convert_date(date_str):
    """Converts format yyyy-mm-dd → yyyymmdd"""
    return date_str.replace("-", "")

# ===== CHECK TOGGLE_MANUAL_DOWNLOAD & SET DATE =====
def check_and_apply_manual_date():
    """
    Calls the API to retrieve TOGGLE_MANUAL_DOWNLOAD.
    - If ON  → fetches START_DATE_DOWNLOAD, END_DATE_DOWNLOAD,
                 converts them from yyyy-mm-dd → yyyymmdd, and types them into UI.
    - If OFF → does nothing, keeps the app's default date.
    """
    try:
        # Step 1: Obtain the API authorization token
        token = get_access_token()

        # Step 2: Retrieve the toggle setting from Orchestrator
        toggle_asset = get_asset_by_name(token, TOGGLE_MANUAL_DOWNLOAD)
        if toggle_asset is None:
            print("[TOGGLE] Asset does not exist, keeping default.")
            return

        toggle_value = get_asset_value(toggle_asset).upper()
        print(f"[TOGGLE] TOGGLE_MANUAL_DOWNLOAD = {toggle_value}")

        # Step 3: If toggle is ON, fetch dates and update UI
        if toggle_value == "ON":
            start_asset = get_asset_by_name(token, START_DATE_ASSET_NAME)
            end_asset   = get_asset_by_name(token, END_DATE_ASSET_NAME)

            if not start_asset or not end_asset:
                print("[TOGGLE] Missing date asset, keeping default.")
                return

            # Step 4: Format date strings and input them into the UI fields
            START_DATE = convert_date(get_asset_value(start_asset))  # yyyymmdd
            END_DATE   = convert_date(get_asset_value(end_asset))    # yyyymmdd

            print(f"[TOGGLE] START_DATE={START_DATE}, END_DATE={END_DATE}")
            print("[TOGGLE] ON → Applying manual date range...")
            clear_and_type(423, 161, START_DATE)
            time.sleep(2)
            clear_and_type(542, 160, END_DATE)

        elif toggle_value == "OFF":
            print("[TOGGLE] OFF → Keeping default date of the app.")

        else:
            print(f"[TOGGLE] Invalid value: '{toggle_value}'. Keeping default.")

    except Exception as e:
        # Step 5: Handle potential errors by printing to log/console
        print(f"[TOGGLE] Error checking asset: {e}")
        print("[TOGGLE] Fallback: keeping default date.")

# ===== MAIN FLOW =====
check_and_apply_manual_date()

print('Click Payment Type: New Contract')
click(1195, 160)
time.sleep(0.5)
print('Click New Contract Item')
click(1152, 204)
time.sleep(0.5)
print('Click Remove all Insurance Type')
click(200, 220)
time.sleep(0.5)
print('Click Long Term Insurance Type')
click(284, 219)
time.sleep(0.5)
print('Click Search Button')
click(1342, 187)
time.sleep(4)
print('Click Download button')
click(1271, 253)
time.sleep(10)
print('DONE!')