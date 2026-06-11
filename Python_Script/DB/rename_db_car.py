import os
import shutil
from datetime import datetime

def process_downloaded_file():
    src_folder = r'C:\Users\RPA02\Documents'
    dst_folder = r'C:\RPA\TempDownload'
    prefix = 'DBG_NEW_CAR_'

    os.makedirs(dst_folder, exist_ok=True)

    # Bước 1: Tìm file .xls/.xlsx mới nhất trong Documents
    files = [
        f for f in os.listdir(src_folder)
        if f.endswith('.xls') or f.endswith('.xlsx')
    ]
    if not files:
        raise Exception("Không tìm thấy file .xls/.xlsx trong Documents!")

    latest_file = max(
        files,
        key=lambda f: os.path.getctime(os.path.join(src_folder, f))
    )
    print(f"File moi nhat: {latest_file}")

    # Bước 2: Đổi tên file với timestamp tránh trùng
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(latest_file)
    new_name = f"{prefix}{name}_{timestamp}{ext}"

    src_path     = os.path.join(src_folder, latest_file)
    renamed_path = os.path.join(src_folder, new_name)
    os.rename(src_path, renamed_path)
    print(f"Da doi ten: {latest_file} -> {new_name}")

    # Bước 3: Chuyển file đến TempDownload
    dst_path = os.path.join(dst_folder, new_name)
    shutil.move(renamed_path, dst_path)
    print(f"Da chuyen file den: {dst_path}")

    return dst_path

process_downloaded_file()