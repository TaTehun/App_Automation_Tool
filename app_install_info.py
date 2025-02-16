from basic.unlock_device import unlock_device
from google_play_scraper import app
from basic.csv_handler import process_csv
from basic.connect_devices import connect_devices
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import subprocess
import uiautomator2 as u2
import subprocess
import time

# device -> run.py
# package_names, app_names -> csv_handler.py

def test_app_install(device, package_names, app_names, df, install_attempt):
        
    d = u2.connect(device)
    total_count, attempt = 0, 0
    remark_list, test_result = [], []
    t_result_list = ["Pass","Fail","NT/NA"]
                    
    # Initialize columns
    if 'Install Result' not in df.columns:
        df['Install Result'] = ""
    if 'Remarks' not in df.columns:
        df['Remarks'] = "" 
    if 'App Category' not in df.columns:
        df['App Category'] = ""
    if 'Developer' not in df.columns:
        df['Developer'] = ""
    if 'App Version' not in df.columns:
        df['App Version'] = ""
    if 'Updated Date' not in df.columns:
        df['Updated Date'] = ""
    if 'TargetSdk' not in df.columns:
        df['TargetSdk'] = "" 

    def is_app_installed():
        #no_cancel = not d(text = "Cancel").exists
        yes_cancel = d(text = "Cancel").exists
        timeout = 180
        timeout_start = time.time()
        
        #Checking if cancel button is activated for 180 sec
        while yes_cancel:
            if time.time() - timeout_start > timeout:
                break
            
        if d(text = "Uninstall").exists:
            test_result.append(t_result_list[0]) # Pass
            remark_list.append("App is successfully Installed")
                            
        elif d(text = "Open").exists:
            test_result.append(t_result_list[2]) # NT/NA
            remark_list.append("App needs to be verified again")
                            
        elif d(text = "Play").exists:
            test_result.append(t_result_list[2]) # NT/NA
            remark_list.append("App needs to be verified again")
            
        else:
            test_result.append(t_result_list[1]) #Fail
            remark_list.append("Timeout")
            
    def handle_popup():  
        screen_width, screen_height = d.window_size()    
        # Popup variables
        if d.xpath("//*[contains(@text,'t now')]").exists:
            d(text = "Not now").click(10)
        elif d.xpath("//*[contains(@text,'When Wi')]").wait(timeout = 5):
            d(text = "OK").click(10)
        elif d.xpath("//*[contains(@text,'t add')]").exists:
            d.xpath("//*[contains(@text,'t add')]").click(10)
        elif d.xpath("//*[contains(@text,'alert') and contains(@text,'OK')]").exists:
            d(text = "OK").click(10)
        elif d.xpath("//*[contains(@text,'Want to see local')]").wait(timeout = 5):
            d(text = "No thanks").click(10)
        else:
            d.click(screen_width //2, screen_height // 2)
            
    # Navigate to the app page in google playstore
    for i, (package_name, app_name) in enumerate(zip(package_names, app_names)):
        for attempt in range(install_attempt):
            attempt += 1
                
            unlock_device(device)
                
            subprocess.run([
                "adb", "-s", device, "shell",
                "am start -n com.android.vending/com.android.vending.AssetBrowserActivity",
                "-a android.intent.action.VIEW",
                "-d", f"market://details?id={package_name}"
            ], check=True)
            
            # Verify if the app is pre-installed
            if d(text = "Uninstall").wait(timeout = 10):
                if d(text = "Update").exists:
                    d(text = "Update").click(10)
                    
                    is_app_installed()
                            
                elif d.xpath("//*[contains(@text,'Update from')]").exists:
                    d(text = "Uninstall").click(10)
                    if d(text = "Uninstall").exists:
                        d(text = "Uninstall").click(10)
                        if d(text = "Install").wait(10):
                            d(text = "Install").click(10)
                            continue
                            
                        else:
                            test_result.append(t_result_list[1]) # Fail
                            remark_list.append("Install button is not found")
                                    
                    # wait until open
                    is_app_installed()
                else: 
                    test_result.append(t_result_list[0]) #Pass
                    remark_list.append("App has already been installed")
                    
            # Verify if the app is updatable
            elif d(text = "Update").exists:
                if d(text = "Open").exists:
                    d(text = "Update").click(10)
                        
                    is_app_installed()
                    
            # Verify the app's compatibility and availability  
            elif d.xpath("//*[contains(@text,'t compatible')]").exists:
                test_result.append(t_result_list[2]) # NT/NA
                remark_list.append("App is not compatible for this device")
                        
            elif d.xpath("//*[contains(@text,'t available')]").exists:
                test_result.append(t_result_list[2]) # NT/NA
                remark_list.append("App is not available for this device")
                        
            elif d.xpath("//*[contains(@text,'t found')]").exists:
                test_result.append(t_result_list[2]) # NT/NA
                remark_list.append("App is not found")
                    
            elif d.xpath("//*[contains(@text,'re offline')]").exists:
                test_result.append(t_result_list[2]) # NT/NA
                remark_list.append("Internet is not connected")
                
            # Verify if the app is Paid-app
            elif d.xpath("//*[contains(@text,'$')]").wait(timeout = 5) and not d(text = "Install").exists:
                test_result.append(t_result_list[2]) # NT/NA
                remark_list.append("App is a Paid App")
                        
            # Verify if the app is installable
            elif d(text = "Install").exists and not d(text = "Open").exists:
                d(text = "Install").click(10)

                if d.xpath("//*[contains(@text,'When Wi')]").wait(timeout = 5):
                    d(text = "OK").click(10)
                        
                is_app_installed()
                
            else:
                test_result.append(t_result_list[1]) # Fail
                remark_list.append("App is failed to install within the timeout")
                
            #attempt to reload the page and repeat the installation
            if test_result[-1] == t_result_list[0]: #Pass
                print(f"{app_name} installation status: {test_result[-1]}, attempt: {attempt}/3")
                break               
            elif attempt <= install_attempt -1:
                print(f"{app_name} installation status: {test_result[-1]}, attempt: {attempt}/3")
                handle_popup()
                test_result.pop()
                remark_list.pop()
                    
        # save the result to csv file
        df.at[i, 'Install Result'] = test_result[-1]
        df.at[i, 'Remarks'] = remark_list[-1]
        
        total_count += 1
        
        try:
            app_info = app(package_name)
                        
            # Sync category
            is_category = app_info.get('categories', [])
            if is_category:
                if not is_category[0].get('id') is None:
                    category_id = is_category[0].get('id', 'No category ID found').strip()
            else:
                category_id = "Unknown"
            df.at[i, 'App Category'] = category_id

            # Sync developer
            is_developer = app_info.get('developer', 'No developer found').strip()
                    
            df.at[i, 'Developer'] = is_developer if is_developer else "Unknown"
                    
            # Sync updated date
            is_updated = app_info.get('lastUpdatedOn', 'No lastUpdatedOn found').strip()
            df.at[i, 'Updated Date'] = is_updated if is_updated else "Unknown"
            
            app_version_finder = subprocess.run([
                "adb", "-s", device, "shell", "dumpsys", "package", f"{package_name}"
            ], capture_output=True, text=True, shell=True, encoding='utf-8')
                    
            is_version = False
            for line in app_version_finder.stdout.splitlines():
                if "versionCode=" in line:
                    target_sdk = line.split()
                    d_target = dict(item.split("=") for item in target_sdk)

                    # target_sdk = ['versionCode=10910200', 'minSdk=27', 'targetSdk=35']
                    # d_target = {'versionCode': '10910200', 'minSdk': '27', 'targetSdk': '35'}
                            
                    if "targetSdk" in d_target:
                        df.at[i, 'TargetSdk'] = d_target['targetSdk']
                    else:
                        df.at[i, 'App Version'] = "No data"

                if "versionName=" in line:
                    app_version = line.split("=")[1].strip()
                    df.at[i, 'App Version'] = app_version
                    is_version = True
                    break
            if not is_version:
                # Sync app version
                is_version_info = app_info.get('version', 'No version found').strip()
                df.at[i, 'App Version'] = is_version_info if is_version_info else "Unknown"
            
        except Exception:
            df.at[i, 'Developer'] = "App is not found"
            df.at[i, 'App Category'] = "App is not found"
            df.at[i, 'App Version'] = "App is not found"
            df.at[i, 'Updated Date'] = "App is not found"
            df.at[i, 'TargetSdk'] = "App is not found"
                
        df.to_csv(f'Install_result_{device}.csv', index=False)
    print(f"Total {total_count} app testing is completed")
    

    """
    # Installation Test result
    actual_test_count = p_count + f_count + na_count 
    if total_count == actual_test_count:
        print(f"Total {total_count} app testing is completed"
            f"\n{f_count} Fails, {na_count} NT/NAs, {p_count} Passes!!")
    else:
        ##numbers keep not matching
        print("Number of tested app doesn't match.."
            f"\nTotal number of app run : {total_count}"
            f"\nTest result is recorded : {actual_test_count} : {p_count}, {f_count}, {na_count}")

    # Filter only Pass status
    result_df = pd.read_csv(f'Install_result_{device}.csv')
    result_df['Result'] = result_df['Result'].astype(str)
    result_df.columns = result_df.columns.str.strip()
    pass_df = result_df[result_df['Result'] == 'Pass']
    pass_df.to_csv(f'pass_only_{device}_result.csv', index=False)
    """  
    
def execute_command(): 
    lock = Lock()
    device_list = connect_devices()
    package_names, app_names, df, sf, csv_file = process_csv()
    install_attempt = install_attempt = int(input("Enter the number of times to repeat the app installation test: "))

    try:
        with ThreadPoolExecutor() as executor: # source code from Hyeonjun An.
            for device in device_list:
                print(f"Device {device} is processing...")

                lock.acquire()
                
                executor.submit(
                test_app_install(device, package_names, app_names, df, install_attempt), device)

                lock.release()
    except Exception as e:
        print(e)
                
# Log for the installation fails

if __name__ == "__main__":
    execute_command()
    