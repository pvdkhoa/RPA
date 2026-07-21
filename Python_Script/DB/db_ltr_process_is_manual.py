"""
This script automates Long Term insurance processing in DB Insurance application,
with additional capabilities to interact with UiPath Orchestrator API to check for 
manual date overrides and apply them if toggled on.
"""
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
    Finds and returns the window handle (hwnd) of the DB Insurance application.
    """
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'DB손해보험' in title:
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    if not result:
        raise Exception("Cannot find the DB Insurance window!")
    print(f"Found window: hwnd={result[0]}")
    return result[0]

def click(x, y):
    """
    Brings the application window to the foreground and simulates a left mouse click 
    at the specified (x, y) coordinates.
    """
    hwnd = get_hwnd()
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    win32api.SetCursorPos((x, y))
    time.sleep(0.3)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
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
    Clicks a field, clears its content by pressing {END} and {BACKSPACE} multiple times, 
    and types the new text. Specifically useful for date fields.
    """
    click(x, y)
    time.sleep(0.3)
    
    # Clear the field completely by pressing End and then Backspace multiple times
    shell.SendKeys("{END}")
    time.sleep(0.1)
    for _ in range(20):  # 20 times is enough for yyyy-mm-dd date field (10 chars)
        shell.SendKeys("{BACKSPACE}")
        time.sleep(0.05)
    
    type_text(text)

clear_and_click = clear_and_type

# ===== ORCHESTRATOR FUNCTIONS =====
def get_access_token():
    """
    Authenticates with UiPath Cloud using Client Credentials and retrieves an access token.
    """
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
    """
    Queries the UiPath Orchestrator API to get the asset object by its name.
    """
    url = f"{BASE_URL}/odata/Assets"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-UIPATH-OrganizationUnitId": ORG_UNIT_ID,
    }
    params = {"$filter": f"Name eq '{asset_name}'"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    assets = response.json().get("value", [])
    if not assets:
        log.warning(f"[ASSET] Cannot find asset '{asset_name}'")
        return None
    log.info(f"[ASSET] Found asset '{asset_name}'")
    return assets[0]

def get_asset_value(asset):
    """
    Extracts the string value from the given UiPath asset dictionary.
    """
    return str(asset.get("Value", asset.get("StringValue", ""))).strip()

def convert_date(date_str):
    """
    Converts a date string from 'yyyy-mm-dd' format to 'yyyymmdd' format.
    """
    return date_str.replace("-", "")

# ===== CHECK TOGGLE_MANUAL_DOWNLOAD & SET DATE =====
def check_and_apply_manual_date():
    """
    Fetches TOGGLE_MANUAL_DOWNLOAD asset from Orchestrator.
    - If ON: fetches START_DATE_DOWNLOAD and END_DATE_DOWNLOAD, 
             converts them from yyyy-mm-dd to yyyymmdd, and types them into UI date fields.
    - If OFF: does nothing, relying on the application's default dates.
    """
    try:
        token = get_access_token()

        toggle_asset = get_asset_by_name(token, TOGGLE_MANUAL_DOWNLOAD)
        if toggle_asset is None:
            print("[TOGGLE] Asset does not exist, keeping default.")
            return

        toggle_value = get_asset_value(toggle_asset).upper()
        print(f"[TOGGLE] TOGGLE_MANUAL_DOWNLOAD = {toggle_value}")

        if toggle_value == "ON":
            start_asset = get_asset_by_name(token, START_DATE_ASSET_NAME)
            end_asset   = get_asset_by_name(token, END_DATE_ASSET_NAME)

            if not start_asset or not end_asset:
                print("[TOGGLE] Missing date asset, keeping default.")
                return

            START_DATE = convert_date(get_asset_value(start_asset))  # yyyymmdd
            END_DATE   = convert_date(get_asset_value(end_asset))    # yyyymmdd

            print(f"[TOGGLE] START_DATE={START_DATE}, END_DATE={END_DATE}")
            print("[TOGGLE] ON → Applying manual date range...")
            clear_and_type(328, 171, START_DATE)
            time.sleep(2)
            clear_and_type(458, 172, END_DATE)

        elif toggle_value == "OFF":
            print("[TOGGLE] OFF → Keeping default date of the app.")

        else:
            print(f"[TOGGLE] Invalid value: '{toggle_value}'. Keeping default.")

    except Exception as e:
        print(f"[TOGGLE] Error checking asset: {e}")
        print("[TOGGLE] Fallback: keeping default date.")

# ===== MAIN FLOW =====
print('Started process: clicking...')

click(144, 264)
print('Clicked main menu')
time.sleep(0.5)
click(189, 267)
print('Clicked menu item 1')
time.sleep(0.5)
click(193, 355)
print('Clicked menu item 2')
time.sleep(0.5)
click(231, 540)
print('Clicked menu item 3')
time.sleep(0.5)
click(232, 601)
print('Clicked menu item 4')
time.sleep(3)

# ===== CHECK TOGGLE_MANUAL_DOWNLOAD =====
check_and_apply_manual_date()
# ===== END CHECK =====

click(670, 172)
print('Clicked Selection Box Insurance type')
time.sleep(1)
click(638, 240)
print('Clicked Selection Item Long Term')
time.sleep(1)
click(871, 175)
print('Clicked Selection Box 2')
time.sleep(0.5)
click(840, 220)
print('Clicked Selection Item 2')
time.sleep(1)
click(1361, 208)
print('Clicked Search button')
time.sleep(2)
print('DONE!')