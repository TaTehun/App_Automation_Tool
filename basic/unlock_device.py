import subprocess
import time
import uiautomator2 as u2
#(-32001, 'androidx.test.uiautomator.UiObjectNotFoundException', 
# ({'mask': 1, 'childOrSibling': [], 'childOrSiblingSelector': [], 'text': 'Open'},))


def is_device_unlocked(device):
    is_unlocked = subprocess.run(
        f"adb -s {device} shell dumpsys window | findstr mDreamingLockscreen",
        shell = True,
        capture_output = True,
        text = True,
    )   
                            
    if "mShowingDream=false" and "mDreamingLockscreen=false" in is_unlocked.stdout:
        return True
    return False

# screen on for 24 hours
def keep_screen_on(device):
    subprocess.run(
        ["adb","-s",f"{device}", "shell", "settings", "put", "system", "screen_off_timeout", "86400000"
    ], check = True) 

def unlock_device(device):
    try:
        attempt = 0
        d = u2.connect(device)
        screen_width, screen_height = d.window_size()
        center_x, center_y = screen_width //2 , screen_height // 2
        center_y2 = screen_width //8

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
                '''
                subprocess.run([
                    "adb","-s",f"{device}","shell",
                    "input","keyevent","82"
                ], check=True)
                '''
                subprocess.run([
                    "adb","-s",f"{device}","shell",
                    "input","touchscreen swipe", f"{center_x}", f"{center_y}", f"{center_x}", f"{center_y2}"
                ], check=True)
                attempt += 1
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")