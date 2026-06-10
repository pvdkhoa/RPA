import win32api, win32con, win32gui, win32com.client, time
import requests
import logging

log = logging.getLogger(__name__)

# ===== ORCHESTRATOR CONFIG =====
CLIENT_ID     = "f03a6679-36df-4e04-987e-b73d8a905970"
CLIENT_SECRET = "!ys?YRKf6^e4Lbapq6SN0cq?GwNSO_#Q7s*~VwNt!BqDElg$F$srGJpiP7v8k$XS"
ORG_UNIT_ID   = "946773"
BASE_URL      = "https://cloud.uipath.com/rpacaxjvjr/DefaultTenant/orchestrator_"

TOGGLE_MANUAL_DOWNLOAD = "TOGGLE_MANUAL_DOWNLOAD"  # Value: "ON" / "OFF"
END_DATE_ASSET_NAME    = "END_DATE_DOWNLOAD"
START_DATE_ASSET_NAME  = "START_DATE_DOWNLOAD"

# ===== WIN32 SETUP =====
shell = win32com.client.Dispatch("WScript.Shell")

def get_hwnd():
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
    time.sleep(0.3)
    
    # Xóa sạch bằng cách bấm End rồi Backspace nhiều lần
    shell.SendKeys("{END}")
    time.sleep(0.1)
    for _ in range(20):  # 20 lần đủ cho date field yyyy-mm-dd (10 ký tự)
        shell.SendKeys("{BACKSPACE}")
        time.sleep(0.05)
    
    type_text(text)

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
    return str(asset.get("Value", asset.get("StringValue", ""))).strip()

def convert_date(date_str):
    """Chuyển format yyyy-mm-dd → yyyymmdd"""
    return date_str.replace("-", "")

# ===== CHECK TOGGLE_MANUAL_DOWNLOAD & SET DATE =====
def check_and_apply_manual_date():
    """
    Gọi API lấy TOGGLE_MANUAL_DOWNLOAD.
    - Nếu ON  → lấy START_DATE_DOWNLOAD, END_DATE_DOWNLOAD,
                 convert từ yyyy-mm-dd → yyyymmdd, rồi type vào UI.
    - Nếu OFF → không làm gì, giữ default của app.
    """
    try:
        token = get_access_token()

        toggle_asset = get_asset_by_name(token, TOGGLE_MANUAL_DOWNLOAD)
        if toggle_asset is None:
            print("[TOGGLE] Asset không tồn tại, giữ nguyên default.")
            return

        toggle_value = get_asset_value(toggle_asset).upper()
        print(f"[TOGGLE] TOGGLE_MANUAL_DOWNLOAD = {toggle_value}")

        if toggle_value == "ON":
            start_asset = get_asset_by_name(token, START_DATE_ASSET_NAME)
            end_asset   = get_asset_by_name(token, END_DATE_ASSET_NAME)

            if not start_asset or not end_asset:
                print("[TOGGLE] Thiếu asset ngày tháng, giữ nguyên default.")
                return

            START_DATE = convert_date(get_asset_value(start_asset))  # yyyymmdd
            END_DATE   = convert_date(get_asset_value(end_asset))    # yyyymmdd

            print(f"[TOGGLE] START_DATE={START_DATE}, END_DATE={END_DATE}")
            print("[TOGGLE] ON → Applying manual date range...")
            clear_and_type(328, 171, START_DATE)
            time.sleep(2)
            clear_and_type(458, 172, END_DATE)

        elif toggle_value == "OFF":
            print("[TOGGLE] OFF → Giữ nguyên date default của app.")

        else:
            print(f"[TOGGLE] Giá trị không hợp lệ: '{toggle_value}'. Giữ nguyên default.")

    except Exception as e:
        print(f"[TOGGLE] Lỗi khi kiểm tra asset: {e}")
        print("[TOGGLE] Fallback: giữ nguyên date default.")

# ===== MAIN FLOW =====
print('Bat dau click...')

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

# ===== CHECK TOGGLE_MANUAL_DOWNLOAD =====
check_and_apply_manual_date()
# ===== END CHECK =====

click(670, 172)
print('Da click Selection Box Insurance type')
time.sleep(1)
click(638, 240)
print('Da click Selection Item Long Term')
time.sleep(1)
click(871, 175)
print('Da click Selection Box 2')
time.sleep(0.5)
click(840, 220)
print('Da click Selection Item 2')
time.sleep(1)
click(1361, 208)
print('Da click Search button')
time.sleep(2)
print('DONE!')