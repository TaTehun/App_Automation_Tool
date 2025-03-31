import subprocess
import time
import uiautomator2 as u2
import platform
#(-32001, 'androidx.test.uiautomator.UiObjectNotFoundException', 
# ({'mask': 1, 'childOrSibling': [], 'childOrSiblingSelector': [], 'text': 'Open'},))


def is_device_unlocked(device):
    os_name = platform.system()

    if os_name in ["Linux", "Darwin"]:  # macOS and Linux
        is_unlocked = subprocess.run(
            f"adb -s {device} shell dumpsys window | grep mDreamingLockscreen",
            shell = True,
            capture_output = True,
            text = True,)
    elif os_name == "Windows":
        is_unlocked = subprocess.run(
            f"adb -s {device} shell dumpsys window |  mDreamingLockscreen",
            shell = True,
            capture_output = True,
            text = True,)
    else:
        print(f"Unsupported OS: {os_name}")
   
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

        while attempt <= 5: 
            if is_device_unlocked(device):
                keep_screen_on(device)
                break
            else:
                # Waking up and unlock the devices
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
                    "input","touchscreen swipe", "0", f"{center_y}", f"{screen_width}", f"{center_y}"
                ], check=True)
                attempt += 1
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")