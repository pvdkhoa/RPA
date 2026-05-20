"""
kill_processes.py
-----------------
Kill browser/RPA processes dùng wmic (bypass Access Denied tốt hơn taskkill)
Fallback sang Scheduled Task SYSTEM nếu wmic cũng fail.

Yêu cầu: Python 3.6+, không cần cài thêm thư viện

Dùng trong UiPath:
    Start Process: python kill_processes.py
"""

import subprocess
import time
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

TASK_NAME = "RPA_KillBrowsers"


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
    """Kill process bằng wmic — bypass được Access Denied mà taskkill không làm được."""
    try:
        result = subprocess.run(
            ["wmic", "process", "where", f"processid={pid}", "delete"],
            capture_output=True,
            text=True,
            encoding="cp949",
        )
        # wmic trả về "인스턴스를 삭제했습니다" nếu thành công
        success = result.returncode == 0 and "삭제했습니다" in result.stdout
        return success, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def kill_via_scheduled_task(pids: list[int]) -> str:
    """Fallback: Dùng SYSTEM Scheduled Task nếu wmic vẫn fail."""
    kill_cmds = " & ".join([f"wmic process where processid={pid} delete" for pid in pids])
    task_cmd = f'cmd /c "{kill_cmds}"'
    logs = []

    try:
        subprocess.run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"], capture_output=True)

        r = subprocess.run(
            ["schtasks", "/Create", "/TN", TASK_NAME, "/TR", task_cmd,
             "/SC", "ONCE", "/ST", "00:00", "/RU", "SYSTEM", "/F"],
            capture_output=True, text=True, encoding="cp949"
        )
        if r.returncode != 0:
            return f"[ERROR] Create task failed: {r.stderr.strip()}"

        subprocess.run(["schtasks", "/Run", "/TN", TASK_NAME], capture_output=True)
        logs.append(f"[SYSTEM TASK] Killing PIDs via wmic: {pids}")
        time.sleep(3)
        subprocess.run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"], capture_output=True)
        logs.append("[SYSTEM TASK] Done & cleaned up")

    except Exception as e:
        logs.append(f"[EXCEPTION] {str(e)}")

    return "\n".join(logs)


def main():
    print("=" * 60)
    print("Kill Browser Processes (wmic)")
    print("=" * 60)

    # Bước 1: Thu thập tất cả PID cần kill
    print("\n[Step 1] Scanning processes...")
    all_pids = {}  # pid -> name
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
    failed_pids = []

    for pid, name in all_pids.items():
        success, msg = kill_via_wmic(pid)
        if success:
            print(f"  [OK]   PID {pid} ({name})")
        else:
            print(f"  [FAIL] PID {pid} ({name}) - {msg}")
            failed_pids.append(pid)

    # Bước 3: Fallback SYSTEM task nếu còn fail
    if failed_pids:
        print(f"\n[Step 3] Escalating to SYSTEM for PIDs: {failed_pids}")
        result = kill_via_scheduled_task(failed_pids)
        print(result)
    else:
        print("\n[Step 3] Skipped - all killed successfully")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())