import subprocess
import threading
import re

def monitor_logcat(device):
    print("Monitoring logcat for crashes...")

    logcat_process = subprocess.Popen(
        f"adb -s {device} logcat -v time",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",  # Force UTF-8 decoding
        errors="replace"  # Replace invalid characters
    )

    crash_pattern = re.compile(r"FATAL EXCEPTION|ANR in|Abort message:|signal \d+ \(SIG[A-Z]+\)")
    process_death = re.compile(r"Process .* has died")
    crash_detected = False


    for line in logcat_process.stdout:
        line = line.strip()
        
        if crash_pattern.search(line):
            crash_detected = True
            print("Crash detected!")
            print(line)  # Print the crash log
            
        if crash_detected:
            print(line)
            
        if process_death.search(line):
            print(line)
            print("--- End of Crash ---\n")
            crash_detected = False


if __name__ == "__main__":
    device_id = "R3CX80SY9ZR"  # Replace with your actual device ID
    monitor_logcat(device_id)
