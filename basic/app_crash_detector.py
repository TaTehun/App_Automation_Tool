import subprocess
import re
import threading
import subprocess
import re
import threading
import time

def get_app_pid(device, package_names):
    """Fetch the running process ID (PID) of the target app."""
    try:
        result = subprocess.run(
            f"adb -s {device} shell pidof {package_names}",
            shell=True, capture_output=True, text=True
        )
        pid = result.stdout.strip()
        return pid if pid else None
    except Exception as e:
        print(f"Error getting PID: {e}")
        return None

def app_crash_detector(device, package_names):
    crash_flag = threading.Event()  # Use an Event to signal a crash detection
    crash_log = []

    def monitor_crashes():
        try:
            print("Start monitoring...")
            pid = get_app_pid(device, package_names)
            print(pid)
            if not pid:
                return
            logcat_process = subprocess.Popen(
                f"adb -s {device} logcat -v time --pid={pid}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            crash_start = re.compile(r"FATAL EXCEPTION|ANR in|Abort message:|signal \d+ \(SIG[A-Z]+\)")
            process_death = re.compile(r"Process .* has died")
            crash_detected = False

            for line in iter(logcat_process.stdout.readline, ''):
                line = line.strip()

                if crash_start.search(line):
                    crash_detected = True
                    crash_log.append("\n--- Crash Detected ---")
                    crash_log.append(line)

                if crash_detected and process_death.search(line):
                        crash_log.append("--- End of Crash ---\n")
                        crash_flag.set()  # Set the flag to indicate a crash
                        crash_detected = False  # Reset flag after full crash log is captured

        except Exception as e:
            print(f"Error while monitoring logcat: {e}")

    # Start monitoring in a separate thread
    crash_thread = threading.Thread(target=monitor_crashes, daemon=True)
    crash_thread.start()

    return crash_flag, crash_log  # Return flag to check crash status
