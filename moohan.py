import subprocess
import threading
import re
import time

def crash_detector(device,pack):
    crash_flag = threading.Event()  # Use an Event to signal a crash detection
    stop_flag = threading.Event()  # Use an Event to signal a crash detection


    def monitor_logcat():
        log_lock = threading.Lock()

        print("Monitoring logcat for crashes...")
        
        subprocess.run(
            ["adb", "-s", device, "logcat", "-c"],
            check=True
        )

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
        process_death = re.compile(rf"Process {pack} .* has died")
        crash_detected = False


        for line in logcat_process.stdout:
            line = line.strip()
            if stop_flag.is_set():
                logcat_process.terminate()
                print("END!")
            
            if crash_pattern.search(line):
                crash_detected = True
                with log_lock:
                    print("Crash detected!")
                    print(line)  # Print the crash log
                
            if crash_detected:

                if process_death.search(line):
                    print(line)
                    print("--- End of Crash ---\n")
                    crash_flag.set()
                    crash_detected = False
                    break
                
    def heyhey():
        time.sleep(5)
        if 1 + 1 == 2:
            print("YES!")
            stop_flag.set()
            return True
        return False
    
    ts = threading.Thread(target=monitor_logcat, daemon=True)
    
    ts.start()
    heyhey()
    while not stop_flag.is_set():
        crash_flag.wait()
        print("hey!")
    
if __name__ == "__main__":
    device = "R3CX80SY9ZR"  # Replace with your actual device ID
    pack = "com.female.inspire.workout.shefitness"
    crash_detector(device,pack)
