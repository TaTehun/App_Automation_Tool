import subprocess

def app_crash_detector():
    """Monitor logcat for crash logs (e.g., exceptions, FATAL, ANR)."""
    try:
        # Start logcat to monitor for crash logs
        print("Monitoring logcat for crashes...")
        logcat_process = subprocess.Popen("adb logcat -v time", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Continuously monitor the logcat output
        while True:
            line = logcat_process.stdout.readline().decode('utf-8')
            if 'Exception' in line or 'FATAL' in line or 'ANR' in line:
                print(f"Crash detected: {line.strip()}")  # Print crash details
            if line == '' and logcat_process.poll() is not None:
                break

    except Exception as e:
        print(f"Error while monitoring logcat: {e}")