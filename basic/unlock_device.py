import subprocess
import time

def unlock_device(device):
    try:
        # Waking up and unlock the devices
        subprocess.run([
            "adb","-s",f"{device}","shell",
            "input","keyevent","224"
        ], check=True)
        
        time.sleep(1)
            
        subprocess.run([
            "adb","-s",f"{device}","shell",
            "input","keyevent","82"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")