import subprocess
import time
import uiautomator2 as u2

# device -> run.py
# package_names, app_names -> csv_handler.py

def test_installation(device, package_names, app_names):
    try:
        # Navigate to the app page in google playstore
        for package_name, app_name in zip(package_names, app_names):
            subprocess.run([
                "adb", "-s", f"{device}", "shell",
                "am start -n com.android.vending/com.android.vending.AssetBrowserActivity",
                "-a android.intent.action.VIEW",
                "-d", f"market://details?id={package_name}"
            ], check=True)
        
            # Click install button
            d = u2.connect(device)
            start_time = time.time()
            time_out = 5000
            
            # Verify if the app is pre-installed
            if d(text = "Uninstall").exists(timeout = 10):
                if d(text = "Update").wait(timeout = 10):
                    d(text = "Update").click()
                    print(f"[Pass] {app_name} has been Updated")
                else: print(f"[Pass] {app_name} has already been installed")
            
            # Verify the app's compatibility and availability    
            elif d.xpath("//*[contains(@text,'t compatible') or contains(@text,'t available') or contains(@text,'t found')]").exists:
                print(f"[NT/NA] {app_name} is not available or compatible for this device")
            
            # Verify if the app is Paid-app
            elif d.xpath("//*[contains(@text,'usd')]").exists:
                print(f"[NT/NA] {app_name} is a Paid App")
            
            # Verify if the app is installable
            elif d(text = "Install").wait(timeout = 10):
                d(text = "Install").click()
                while time.time() - start_time < time_out:
                    if d(text = "Uninstall").exists(timeout= 10):
                        print(f"[Pass] {app_name} is successfully installed")
            else:
                print("[Fail] Install button is not found")    
                
            # Open the app
            if d(text = "Uninstall").exists(timeout = 10):
                if d(text = "Play").wait(timeout = 10):
                    d(text = "Play").click()
                elif d(text = "Open").wait(timeout = 10):
                    d(text = "Open").click()
                    
                    time.sleep(3)
                    
                    print(f"[Pass] {app_name} is Opened")
                else: print(f"[Fail] {app_name} Failed to open")

            
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        

# Test bench
'''
from basic.install_apps import test_installation
from basic.connect_devices import connect_devices
from basic.unlock_device import unlock_device
from basic.csv_handler import process_csv
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

def execute_command(): 
    lock = Lock()
    devices = connect_devices()
    package_names, app_names = process_csv()

    try:
        with ThreadPoolExecutor() as executor:
            for device in devices:
                print(f"Device {device} is processing...")
                unlock_device(device)
                lock.acquire()
                executor.submit( 
                                test_installation(device, package_names, app_names), 
                                device)
                lock.release()
    except Exception as e:
        print(e)
                
# Log for the installation fails

if __name__ == "__main__":
    execute_command()
'''