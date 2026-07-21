"""
This script finds the latest downloaded Excel file for DB General insurance, 
appends a timestamp to its name to prevent duplication, and moves it to a temp folder.
"""
import os
import shutil
from datetime import datetime

def process_downloaded_file():
    """
    Locates the most recently downloaded .xls or .xlsx file in the Documents folder, 
    renames it using the prefix 'DBG_NEW_GEN_' and the current timestamp, 
    and finally moves it to 'C:\\RPA\\TempDownload'.
    Returns the new destination path.
    """
    src_folder = r'C:\Users\RPA02\Documents'
    dst_folder = r'C:\RPA\TempDownload'
    prefix = 'DBG_NEW_GEN_'

    os.makedirs(dst_folder, exist_ok=True)

    # Step 1: Find the latest .xls/.xlsx file in Documents
    files = [
        f for f in os.listdir(src_folder)
        if f.endswith('.xls') or f.endswith('.xlsx')
    ]
    if not files:
        print("Cannot find .xls/.xlsx file in Documents folder!")
        return None

    latest_file = max(
        files,
        key=lambda f: os.path.getctime(os.path.join(src_folder, f))
    )
    print(f"Latest file: {latest_file}")

    # Step 2: Rename file with timestamp to avoid duplicates
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(latest_file)
    new_name = f"{prefix}{name}_{timestamp}{ext}"

    src_path     = os.path.join(src_folder, latest_file)
    renamed_path = os.path.join(src_folder, new_name)
    os.rename(src_path, renamed_path)
    print(f"Renamed: {latest_file} -> {new_name}")

    # Step 3: Move file to TempDownload
    dst_path = os.path.join(dst_folder, new_name)
    shutil.move(renamed_path, dst_path)
    print(f"Moved file to: {dst_path}")

    return dst_path

process_downloaded_file()