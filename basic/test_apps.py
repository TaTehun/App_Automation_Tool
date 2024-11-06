import subprocess
import time
import uiautomator2 as u2
import re

# device -> run.py
# package_names, app_names -> csv_handler.py

def test_installation(device, package_names, app_names, df):
    try:
        p_count, f_count, na_count, total_count = 0, 0, 0, 0
        p_list, f_list, na_list, total_list = [], [], [], []
        # Navigate to the app page in google playstore
        for package_name, app_name in zip(package_names, app_names):
            subprocess.run([
                "adb", "-s", f"{device}", "shell",
                "am start -n com.android.vending/com.android.vending.AssetBrowserActivity",
                "-a android.intent.action.VIEW",
                "-d", f"market://details?id={package_name}"
            ], check=True)

            d = u2.connect(device)
            
            # Verify if the app is pre-installed
            if d(text = "Uninstall").wait(timeout = 15):
                if d(text = "Update").exists:
                    d(text = "Update").click()
                    p_list.append(f"[Pass] {app_name} has been Updated")
                    total_list.append("App has been Updated")
                    p_count += 1
                else: 
                    p_list.append(f"[Pass] {app_name} has already been installed")
                    total_list.append("App has already been installed")
                    p_count += 1
                    
            # Verify the app's compatibility and availability  
            elif d.xpath("//*[contains(@text,'t compatible')]").exists:
                na_list.append(f"[NT/NA] {app_name} is not compatible for this device")
                total_list.append("App not compatible for this device")
                na_count += 1
                
            elif d.xpath("//*[contains(@text,'t available')]").exists:
                na_list.append(f"[NT/NA] {app_name} is not available for this device")
                total_list.append("App not compatible for this device")
                na_count += 1
                
            elif d.xpath("//*[contains(@text,'t found')]").exists:
                na_list.append(f"[NT/NA] {app_name} is not found")
                total_list.append("App not compatible for this device")
                na_count += 1
            
            # Verify if the app is Paid-app
            elif not d(text = "Install").exists and d.xpath("//*[contains(@text,'$')]").wait(timeout = 10):
                na_list.append(f"[NT/NA] {app_name} is a Paid App")
                total_list.append("App not compatible for this device")
                na_count += 1
            
            # Verify if the app is installable
            elif d(text = "Install").exists and not d(text = "Open").exists:
                d(text = "Install").click()

                if d.xpath("//*[contains(@text,'When Wi')]").wait(timeout = 10):
                    d(text = "OK").click()
                    
                if d(text = "Uninstall").wait(timeout = 600):
                    p_list.append(f"[Pass] {app_name} is successfully installed")
                    total_list.append("App is successfully instae")
                    p_count += 1
                else:
                    f_list.append(f"[Fail] {app_name} failed to install within the timeout")
                    total_list.append("App is Fail instae")
                    f_count += 1
            else:
                f_list.append("[Fail] Install button is not found")
                total_list.append("no bytton")
                f_count += 1
                
        
            # Get App version
            app_version = subprocess.run([
                "adb", "shell", "dumpsys", "package", f"{package_name}"],
                                        capture_output=True, text=True)
            
            for line in app_version.stdout.splitlines():
                if "versionName=" in line:
                    version = line.split("=")[1].strip()
                    print(f"Version: {version}") 
                
                '''
                    category = re.findall(r'android.intent.category\.(\w+)', app_output)
                    if category:
                        print(f"Category: {category}")
                '''
            # Get App categories
            total_count += 1
        
                
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        
    if total_count == f_count + p_count + na_count:
        print(f"Total {total_count} app testing is completed \n {f_count} Fails, {na_count} NT/NAs, {p_count} Passes!!")
    else:
        print("Total number doesn't match..")
    
    print("Fail:", f_list if f_list else f_count, 
          "\n NT/NA:", na_list if na_list else na_count, 
          "\n Pass:", p_list if p_list else p_count)
    
    df['Result'] = total_list
    df.to_csv('123tj.csv', index=False)
'''            
            # Open the app
            if d(text = "Uninstall").exists:
                if d(text = "Play").exists:
                    d(text = "Play").click()
                elif d(text = "Open").exists:
                    d(text = "Open").click()
                else: 
                    print(f"[Fail] {app_name} Failed to open")
                time.sleep(3)
            
                print(f"[Pass] {app_name} is Opened")
            '''

        
        

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