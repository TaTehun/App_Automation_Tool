import subprocess
import time

def in_device_unlocked(device):
    is_unlocked = subprocess.run(
        ["adb","-s",f"{device}", "shell", "dumpsys", "window | grep 'mDreamingLockscreen'"],
        capture_output = True,
        text = True,
    )   
                        
    if "mShowingDream=false" and "mDreamingLockscreen=false" in is_unlocked.stdout:
        return True
    return False

def unlock_device(device):
    try:
        attempt = 0
        while True and attempt <= 5:
            is_device_unlocked(device)
                attempt += 1
                
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