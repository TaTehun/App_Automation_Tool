import subprocess
import re
import threading

def app_crash_detector():
    """Continuously monitor logcat and print crash-related logs."""
    def monitor_crashes():
        try:
            logcat_process = subprocess.Popen(
                "adb logcat -v time",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            crash_start = re.compile(r"FATAL EXCEPTION")  # Start of a crash
            caused_by = re.compile(r"Caused by:")         # Exception type and cause
            process_death = re.compile(r"Process .* has died")  # Process termination message
            stack_trace_line = re.compile(r"\tat .*")     # Stack trace lines

            crash_detected = False

            while True:
                line = logcat_process.stdout.readline().decode('utf-8', errors='replace').strip()

                # Detect start of a crash log
                if crash_start.search(line):
                    crash_detected = True
                    print("\n--- Crash Detected ---")
                    #print(line)

                # Detect the cause of the crash
                elif crash_detected and caused_by.search(line):
                    #print(line)
                    print("!")

                # Detect stack trace or process death lines
                elif crash_detected and (stack_trace_line.search(line) or process_death.search(line)):
                    #print(line)
                    print("!")
                    if process_death.search(line):  # If process death is logged, end current crash
                        print("--- End of Crash ---\n")
                        crash_detected = False

        except Exception as e:
            print(f"Error while monitoring logcat: {e}")

    # Start crash monitoring in a separate thread
    crash_thread = threading.Thread(target=monitor_crashes, daemon=True)
    crash_thread.start()
