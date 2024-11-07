import subprocess
import time

def unlock_device(device):
    try:
        for _ in range(3):
        # Waking up and unlock the devices
            subprocess.run([
                "adb","-s",f"{device}","shell",
                "input","keyevent","224"
            ], check=True)
            
            time.sleep(2)
            
            subprocess.run([
                "adb","-s",f"{device}","shell",
                "input","keyevent","82"
            ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")