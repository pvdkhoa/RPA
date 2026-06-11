import os
import sys
import shutil
from pathlib import Path

def find_latest_no_extension_file(folder: str):
    all_files = [f for f in Path(folder).iterdir() if f.is_file() and f.suffix == ""]
    
    if not all_files:
        print(" Không tìm thấy file phù hợp. Kết thúc chương trình.")
        return None
    
    latest = max(all_files, key=lambda f: f.stat().st_mtime)
    print(f" Tìm thấy file: {latest.name}")
    return latest

# ===================== MAIN =====================
src_folder = r"C:\Users\RPA02\Downloads"
dst_folder = r"C:\RPA\TempDownload"

file = find_latest_no_extension_file(src_folder)

if file:
    new_name = f"MRF_EXT_LTR_{file.name}"
    dst_path = Path(dst_folder) / new_name
    
    # Đổi tên + move sang thư mục đích
    shutil.move(str(file), str(dst_path))
    print(f"Đã đổi tên và chuyển file tới: {dst_path}")

print("🎉 DONE!")