import subprocess
import time
import uiautomator2 as u2
import re

# device -> run.py
# package_names, app_names -> csv_handler.py

def test_installation(device, package_names, app_names, df):
    try:
        p_count, f_count, na_count, total_count = 0, 0, 0, 0
        remark_list, test_result, app_version = [], [], []
        t_result_list = ["Pass","Fail","NT/NA"]
        
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
                    test_result.append(t_result_list[0]) #Pass
                    remark_list.append("App has been Updated")
                    p_count += 1
                else: 
                    test_result.append(t_result_list[0]) #Pass
                    remark_list.append("App has already been installed")
                    p_count += 1
                    
            # Verify the app's compatibility and availability  
            elif d.xpath("//*[contains(@text,'t compatible')]").exists:
                test_result.append(t_result_list[3]) # NT/NA
                remark_list.append("App is not compatible for this device")
                na_count += 1
                
            elif d.xpath("//*[contains(@text,'t available')]").exists:
                test_result.append(t_result_list[3]) # NT/NA
                remark_list.append("App is not available for this device")
                na_count += 1
                
            elif d.xpath("//*[contains(@text,'t found')]").exists:
                test_result.append(t_result_list[3]) # NT/NA
                remark_list.append("App is not found")
                na_count += 1
            
            # Verify if the app is Paid-app
            elif d.xpath("//*[contains(@text,'$')]").wait(timeout = 10) and not d(text = "Install").exists:
                test_result.append(t_result_list[3]) # NT/NA
                remark_list.append("App is a Paid App")
                na_count += 1
            
            # Verify if the app is installable
            elif d(text = "Install").exists and not d(text = "Open").exists:
                d(text = "Install").click()

                if d.xpath("//*[contains(@text,'When Wi')]").wait(timeout = 10):
                    d(text = "OK").click()
                    
                if d(text = "Uninstall").wait(timeout = 600):
                    test_result.append(t_result_list[0]) # Pass
                    remark_list.append("App is successfully Installed")
                    p_count += 1
                else:
                    test_result.append(t_result_list[1]) # Fail
                    remark_list.append("App is failed to install within the timeout")
                    f_count += 1
            else:
                test_result.append(t_result_list[1]) # Fail
                remark_list.append("Install button is not found")
                f_count += 1
                
        
            # Get App version
            app_version_finder = subprocess.run([
                "adb", "shell", "dumpsys", "package", f"{package_name}"],
                                        capture_output=True, text=True)
            
            found_version = False
            for line in app_version_finder.stdout.splitlines():
                if "versionName=" in line:
                    version = line.split("=")[1].strip()
                    app_version.append(f"{version}")
                    found_version = True
                    break
            if not found_version:
                app_version.append("no version")
                

                '''
                    category = re.findall(r'android.intent.category\.(\w+)', app_output)
                    if category:
                        print(f"Category: {category}")
                '''
            # Count tested app
            total_count += 1
            
            
            # Open the app
            if d(text = "Uninstall").exists:
                if d(text = "Play").exists:
                    d(text = "Play").click()
                elif d(text = "Open").exists:
                    d(text = "Open").click()
                else: 
                    print(f"[Fail] {app_name} Failed to open")
            
            time.sleep(3)
            print("App is opened!!")    
            

        
                
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    
    # Installation Test result
    actual_test_count = f_count + p_count + na_count 
    if total_count == actual_test_count:
        print(f"Total {total_count} app testing is completed"
              f"\n{f_count} Fails, {na_count} NT/NAs, {p_count} Passes!!")
    else:
        print("Number of tested app doesn't match.."
              f"\nTotal number of app run : {total_count}"
              f"\nTest result is recorded : {actual_test_count}")
    
    df['App Version'] = app_version
    df['Result'] = test_result
    df['Remarks'] = remark_list
    df.to_csv('123tj_result.csv', index=False)
    
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