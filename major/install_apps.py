import subprocess
import time
import uiautomator2 as u2


def install_app_direct(device_id: str, package_name: str) -> bool:
    """Install app by launching Play Store directly"""
    try:
        print(f"Installing {package_name}...")
        
        # Launch Play Store directly with the package
        subprocess.run([
            "adb", "-s", device_id, "shell",
            "am start -n com.android.vending/com.android.vending.AssetBrowserActivity",
            "-a android.intent.action.VIEW",
            "-d", f"market://details?id={package_name}"
        ], check=True)
        
        print("Launched Play Store, waiting for load...")
        time.sleep(3)
        
        return True
        
    except subprocess.SubprocessError as e:
        print(f"Unable to load the app: {e}")
        return False

def connect_devices():
    # Get connected device
    result = subprocess.run(
        ["adb", "devices"],
        capture_output=True,
        text=True,
        check=True
    )
    # Get first connected device
    lines = result.stdout.strip().split('\n')
    if len(lines) <= 1:
        print("No devices connected!")
    else:
        device_id = lines[1].split('\t')[0]
        print(f"Found device: {device_id}")
        return device_id
    
def click_install_button():
    d = u2.connect()
    if d(text = "Install").wait(timeout = 10.0):
        d(text = "Install").click()
    else:
        print("Install button is not found")

def test_installation():
    try:
        # Use the specific package name you want to test
        package_name = "com.hellosimply.simplysingdroid"
        device_id = connect_devices()
        
        print(f"Attempting to install {package_name}")
        
        if install_app_direct(device_id, package_name):            
            click_install_button()
            print("Installation process started successfully")
            
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_installation()