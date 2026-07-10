import os
import shutil
import time

def process_downloaded_file():
    src_folder = r'C:\Users\RPA02\Documents'
    dst_folder = r'C:\RPA\TempDownload'
    prefix = 'MRF_NEW_GEN_'

    # Create destination folder if it does not exist
    os.makedirs(dst_folder, exist_ok=True)

    # Step 1: Find the latest .xls/.xlsx file in Documents
    files = [
        f for f in os.listdir(src_folder)
        if f.endswith('.xls') or f.endswith('.xlsx')
    ]

    if not files:
        raise Exception("Cannot find .xls/.xlsx file in Documents!")

    # Get the latest file based on creation time
    latest_file = max(
        files,
        key=lambda f: os.path.getctime(os.path.join(src_folder, f))
    )
    print(f"Latest file: {latest_file}")

    # Step 2: Rename the file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_name = prefix + timestamp + "_" + latest_file
    src_path = os.path.join(src_folder, latest_file)
    renamed_path = os.path.join(src_folder, new_name)
    os.rename(src_path, renamed_path)
    print(f"Renamed: {latest_file} -> {new_name}")

    # Step 3: Move the file to TempDownload
    dst_path = os.path.join(dst_folder, new_name)
    shutil.move(renamed_path, dst_path)
    print(f"Moved file to: {dst_path}")

    return dst_path


process_downloaded_file()