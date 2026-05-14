import win32api, win32con, win32gui, win32com.client, time
import requests
import logging

log = logging.getLogger(__name__)

# ===== ORCHESTRATOR CONFIG =====
CLIENT_ID     = "f03a6679-36df-4e04-987e-b73d8a905970"
CLIENT_SECRET = "!ys?YRKf6^e4Lbapq6SN0cq?GwNSO_#Q7s*~VwNt!BqDElg$F$srGJpiP7v8k$XS"
ORG_UNIT_ID   = "946773"
BASE_URL      = "https://cloud.uipath.com/rpacaxjvjr/DefaultTenant/orchestrator_"

IS_MANUAL_ASSET_NAME  = "IS_MANUAL"
END_DATE_ASSET_NAME   = "END_DATE_DOWNLOAD"
START_DATE_ASSET_NAME = "START_DATE_DOWNLOAD"

# ===== WIN32 SETUP =====
shell = win32com.client.Dispatch("WScript.Shell")

def get_hwnd():
    """Tìm hwnd của cửa sổ DB손보 động"""
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'DB손해보험' in title:
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    if not result:
        raise Exception("Không tìm thấy cửa sổ DB손해보험!")
    print(f"Tim thay cua so: hwnd={result[0]}")
    return result[0]

def click(x, y):
    hwnd = get_hwnd()
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    win32api.SetCursorPos((x, y))
    time.sleep(0.3)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(0.5)

def type_text(text):
    shell.SendKeys(str(text))
    time.sleep(0.3)

def clear_and_type(x, y, text):
    click(x, y)
    shell.SendKeys("^a")
    time.sleep(0.1)
    shell.SendKeys("{DELETE}")
    time.sleep(0.1)
    type_text(text)

# Alias để tương thích với tên hàm trong code gốc
clear_and_click = clear_and_type

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
    params = {"$filter": f"Name eq '{asset_name}'"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    assets = response.json().get("value", [])
    if not assets:
        log.warning(f"[ASSET] Không tìm thấy asset '{asset_name}'")
        return None
    log.info(f"[ASSET] Tìm thấy asset '{asset_name}'")
    return assets[0]

def get_asset_value(asset):
    """Extract string value từ asset object (Text/Bool/Integer...)"""
    return str(asset.get("Value", asset.get("StringValue", ""))).strip()

# ===== CHECK IS_MANUAL & SET DATE =====
def check_and_apply_manual_date():
    """
    Gọi API lấy IS_MANUAL.
    - Nếu TRUE  → lấy thêm START_DATE_DOWNLOAD, END_DATE_DOWNLOAD rồi type vào UI.
    - Nếu FALSE → không làm gì, giữ default của app.
    """
    try:
        token = get_access_token()

        is_manual_asset = get_asset_by_name(token, IS_MANUAL_ASSET_NAME)
        if is_manual_asset is None:
            print("[IS_MANUAL] Asset không tồn tại, giữ nguyên default.")
            return

        is_manual_value = get_asset_value(is_manual_asset).upper()
        print(f"[IS_MANUAL] Value = {is_manual_value}")

        if is_manual_value == "TRUE":
            start_asset = get_asset_by_name(token, START_DATE_ASSET_NAME)
            end_asset   = get_asset_by_name(token, END_DATE_ASSET_NAME)

            if not start_asset or not end_asset:
                print("[IS_MANUAL] Thiếu asset ngày tháng, giữ nguyên default.")
                return

            START_DATE = get_asset_value(start_asset)
            END_DATE   = get_asset_value(end_asset)

            print(f"[IS_MANUAL] START_DATE={START_DATE}, END_DATE={END_DATE}")
            print("Check is manual add time period")
            clear_and_click(328, 171, START_DATE)
            time.sleep(2)
            clear_and_click(458, 172, END_DATE)

        else:
            print("[IS_MANUAL] FALSE → Giữ nguyên date default của app.")

    except Exception as e:
        print(f"[IS_MANUAL] Lỗi khi kiểm tra asset: {e}")
        print("[IS_MANUAL] Fallback: giữ nguyên date default.")

# ===== MAIN FLOW =====
print('Bat dau click...')

# Menu navigation
click(144, 264)
print('Da click menu chinh')
time.sleep(0.5)
click(189, 267)
print('Da click menu item 1')
time.sleep(0.5)
click(193, 355)
print('Da click menu item 2')
time.sleep(0.5)
click(231, 540)
print('Da click menu item 3')
time.sleep(0.5)
click(232, 601)
print('Da click menu item 4')
time.sleep(3)

# ===== CHECK CONDITION IS MANUAL HERE =====
check_and_apply_manual_date()
# ===== END CHECK CONDITION IS MANUAL =====

# Selection Box Insurance type
click(670, 172)
print('Da click Selection Box Insurance type')
time.sleep(1)
click(638, 240)
print('Da click Selection Item Long Term')
time.sleep(1)
# Selection Box 2
click(871, 175)
print('Da click Selection Box 2')
time.sleep(0.5)
click(840, 220)
print('Da click Selection Item 2')
time.sleep(1)
# Search
click(1361, 208)
print('Da click Search button')
time.sleep(2)
print('DONE!')