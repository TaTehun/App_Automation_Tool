import subprocess
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

    crash_pattern = re.compile(r"FATAL EXCEPTION")
    process_death = re.compile(r"Process .* has died")


    for line in iter(logcat_process.stdout.readline, ''):
        line = line.strip()
        
        if crash_pattern.search(line):
            print("Crash detected!")
            print(line)  # Print the crash log
            
        if process_death.search(line):
            print("--- End of Crash ---\n")

if __name__ == "__main__":
    device_id = "R3CX20PPY5K"  # Replace with your actual device ID
    monitor_logcat(device_id)
