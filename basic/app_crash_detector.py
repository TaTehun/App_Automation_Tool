import subprocess
import re
import threading


def app_crash_detector(device):
    crash_flag = threading.Event()  # Use an Event to signal a crash detection
    crash_log = []
    
    def monitor_crashes():
        try:
            print("Start monitoring")
            logcat_process = subprocess.run(
                f"adb -s {device} logcat -v time",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            crash_start = re.compile(r"FATAL EXCEPTION|ANR in|Abort message:|signal \d+ \(SIG[A-Z]+\)")  # Start of a crash
            process_death = re.compile(r"Process .* has died")  # Process termination message
            crash_detected = False
            
            while True:
                line = logcat_process.stdout.readline().decode('utf-8', errors='replace').strip()

                # Detect start of a crash log
                if crash_start.search(line):
                    crash_detected = True
                    crash_log.append("\n--- Crash Detected ---")
                    crash_log.append(line)
                    
                    # Detect end of a crash log
                    if crash_detected and process_death.search(line):
                        crash_log.append(line)
                        crash_log.append("--- End of Crash ---\n")
                        crash_flag.set()  # Set the flag to indicate a crash
                    crash_detected = False # Clear the detect when the crash ends
                else:
                    continue
                    
        except Exception as e:
            print(f"Error while monitoring logcat: {e}")

    # Start crash monitoring in a separate thread
    crash_thread = threading.Thread(target=monitor_crashes, daemon=True)
    crash_thread.start()

    return crash_flag, crash_log  # Return the flag to check crash status

