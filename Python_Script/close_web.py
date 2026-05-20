"""
kill_processes.py
-----------------
Kill browser/RPA processes dùng wmic.
Yêu cầu: Python 3.6+, không cần cài thêm thư viện.
"""

import subprocess
import sys

PROCESS_NAMES = [
    "msedge.exe",
    "msedgewebview2.exe",
    "chrome.exe",
    "chromedriver.exe",
    "msedgedriver.exe",
    "XPlatform.exe",
    "nexacro.exe",
    "ChromeNativeMessaging.exe",
]


def get_pids_by_name(process_name: str) -> list[int]:
    """Lấy danh sách PID theo tên process dùng tasklist."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {process_name}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            encoding="cp949",
        )
        pids = []
        for line in result.stdout.strip().splitlines():
            parts = line.strip('"').split('","')
            if len(parts) >= 2:
                try:
                    pids.append(int(parts[1]))
                except ValueError:
                    pass
        return pids
    except Exception:
        return []


def kill_via_wmic(pid: int) -> tuple[bool, str]:
    """Kill process bằng wmic."""
    try:
        result = subprocess.run(
            ["wmic", "process", "where", f"processid={pid}", "delete"],
            capture_output=True,
            text=True,
            encoding="cp949",
        )
        success = result.returncode == 0 and "삭제했습니다" in result.stdout
        return success, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 50)
    print("Kill Browser Processes (wmic)")
    print("=" * 50)

    # Bước 1: Thu thập tất cả PID
    print("\n[Step 1] Scanning processes...")
    all_pids = {}
    for name in PROCESS_NAMES:
        pids = get_pids_by_name(name)
        for pid in pids:
            all_pids[pid] = name
            print(f"  Found: {name} PID={pid}")

    if not all_pids:
        print("  No target processes found. Nothing to kill.")
        return 0

    # Bước 2: Kill từng PID bằng wmic
    print(f"\n[Step 2] Killing {len(all_pids)} process(es) via wmic...")
    for pid, name in all_pids.items():
        success, msg = kill_via_wmic(pid)
        if success:
            print(f"  [OK]   PID {pid} ({name})")
        else:
            print(f"  [FAIL] PID {pid} ({name}) - {msg}")

    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())