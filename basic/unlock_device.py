import subprocess
import time

def is_device_unlocked(device):
    is_unlocked = subprocess.run(
        ["adb","-s",f"{device}", "shell", "dumpsys", "window | grep 'mDreamingLockscreen'"],
        capture_output = True,
        text = True,
    )   
                        
    if "mShowingDream=false" and "mDreamingLockscreen=false" in is_unlocked.stdout:
        return True
    return False

def keep_screen_on(device):
    subprocess.run(
        ["adb","-s",f"{device}", "shell", "settings", "put", "system", "screen_off_timeout", "86400000"
    ], check = True) # screen on for 24 hours

def unlock_device(device):
    try:
        attempt = 0
        while attempt <= 5: 
            if is_device_unlocked(device):
                break
            else:
                # Waking up and unlock the devices
                keep_screen_on(device)
                subprocess.run([
                    "adb","-s",f"{device}","shell",
                    "input","keyevent","224"
                ], check=True)
                
                time.sleep(2)
                
                subprocess.run([
                    "adb","-s",f"{device}","shell",
                    "input","keyevent","82"
                ], check=True)
                attempt += 1
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")