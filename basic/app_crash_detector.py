import subprocess
import re
import threading

def app_crash_detector(device):
    crash_flag = threading.Event()  # Use an Event to signal a crash detection
    crash_log = []

    def monitor_crashes():
        try:
            logcat_process = subprocess.Popen(
                f"adb -s {device} logcat -v time",
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

            for line in logcat_process.stdout:
                line = line.strip()

                if crash_start.search(line):
                    crash_detected = True
                    crash_log.append("\n--- Crash Detected ---")
                    crash_log.append(line)

                if crash_detected:
                    crash_log.append(line)
                    
                    if process_death.search(line):
                        crash_log.append(line)
                        crash_log.append("--- End of Crash ---\n")
                        crash_flag.set()  # Set the flag to indicate a crash
                        crash_detected = False  # Reset flag after full crash log is captured

        except Exception as e:
            print(f"Error while monitoring logcat: {e}")

    # Start monitoring in a separate thread
    crash_thread = threading.Thread(target=monitor_crashes, daemon=True)
    crash_thread.start()

    return crash_flag, crash_log  # Return flag to check crash status
