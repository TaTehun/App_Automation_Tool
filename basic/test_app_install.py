import subprocess
import uiautomator2 as u2
from basic.unlock_device import unlock_device
import pandas as pd

# device -> run.py
# package_names, app_names -> csv_handler.py

def test_app_install(device, package_names, app_names, df, csv_file):
    try:
        p_count, f_count, na_count, total_count, attempt = 0, 0, 0, 0, 0
        remark_list, test_result = [], []
        t_result_list = ["Pass","Fail","NT/NA"]
        d = u2.connect(device)
        
        # Initialize columns
        if 'Result' not in df.columns:
            df['Result'] = ""
        else:
            df['Result'] = ""
        if 'Remarks' not in df.columns:
            df['Remarks'] = "" 
        else:
            df['Remarks'] = "" 

        # Navigate to the app page in google playstore
        for i, (package_name, app_name) in enumerate(zip(package_names, app_names)):
            for attempt in range(3):
                attempt += 1
                
                unlock_device(device)
                
                subprocess.run([
                    "adb", "-s", f"{device}", "shell",
                    "am start -n com.android.vending/com.android.vending.AssetBrowserActivity",
                    "-a android.intent.action.VIEW",
                    "-d", f"market://details?id={package_name}"
                ], check=True)
                
                # Verify if the app is pre-installed
                if d(text = "Uninstall").wait(timeout = 15):
                    if d(text = "Update").exists:
                        d(text = "Update").click()
                        
                    elif d.xpath("//*[contains(@text,'Update from')]").exists:
                        d(text = "Uninstall").click()
                        if d(text = "Uninstall").exists:
                            d(text = "Uninstall").click()
                            if d(text = "Install").wait(15):
                                d(text = "Install").click()
                                continue
                            else:
                                test_result.append(t_result_list[1]) # Fail
                                remark_list.append("Install button is not found")
                                f_count += 1 
                                    
                        # wait until open
                        if d(text = "Uninstall").wait(timeout = 600):
                            test_result.append(t_result_list[0]) #Pass
                            remark_list.append("App has been Updated")
                            p_count += 1
                        else:
                            test_result.append(t_result_list[1]) # Fail
                            remark_list.append("App is failed to install within the timeout")
                            f_count += 1
                    else: 
                        test_result.append(t_result_list[0]) #Pass
                        remark_list.append("App has already been installed")
                        p_count += 1
                        
                # Verify the app's compatibility and availability  
                elif d.xpath("//*[contains(@text,'t compatible')]").exists:
                    test_result.append(t_result_list[2]) # NT/NA
                    remark_list.append("App is not compatible for this device")
                    na_count += 1
                    
                elif d.xpath("//*[contains(@text,'t available')]").exists:
                    test_result.append(t_result_list[2]) # NT/NA
                    remark_list.append("App is not available for this device")
                    na_count += 1
                    
                elif d.xpath("//*[contains(@text,'t found')]").exists:
                    test_result.append(t_result_list[2]) # NT/NA
                    remark_list.append("App is not found")
                    na_count += 1
                
                elif d.xpath("//*[contains(@text,'re offline')]").exists:
                    test_result.append(t_result_list[2]) # NT/NA
                    remark_list.append("Internet is not connected")
                    na_count += 1
                
                # Verify if the app is Paid-app
                elif d.xpath("//*[contains(@text,'$')]").wait(timeout = 5) and not d(text = "Install").exists:
                    test_result.append(t_result_list[2]) # NT/NA
                    remark_list.append("App is a Paid App")
                    na_count += 1
                
                # Verify if the app is installable
                elif d(text = "Install").exists and not d(text = "Open").exists:
                    d(text = "Install").click()

                    if d.xpath("//*[contains(@text,'When Wi')]").wait(timeout = 5):
                        d(text = "OK").click()
                        
                    if d(text = "Uninstall").wait(timeout = 180):
                        test_result.append(t_result_list[0]) # Pass
                        remark_list.append("App is successfully Installed")
                        p_count += 1
                    
                    elif d(text = "Open").wait(timeout = 10) and not d(text = "Cancel").exists:
                        test_result.append(t_result_list[2]) # NT/NA
                        remark_list.append("App needs to be verified again")
                        na_count += 1
                        
                    elif d(text = "Play").wait(timeout = 10) and not d(text = "Cancel").exists:
                        test_result.append(t_result_list[2]) # NT/NA
                        remark_list.append("App needs to be verified again")
                        na_count += 1
                        
                    else:
                        test_result.append(t_result_list[1]) # Fail
                        remark_list.append("App is failed to install within the timeout")
                        f_count += 1
                else:
                    test_result.append(t_result_list[1]) # Fail
                    remark_list.append("Install button is not found")
                    f_count += 1 

                # Popup variables
                if d.xpath("//*[contains(@text,'t now')]").exists:
                    d(text = "Not now").click()
                elif d.xpath("//*[contains(@text,'t add')]").exists:
                    d.xpath("//*[contains(@text,'t add')]").click()
                elif d.xpath("//*[contains(@text,'alert') and contains(@text,'OK')]").exists:
                    d(text = "OK").click()

                #attempt to reload the page and repeat the installation
                if test_result[-1] == t_result_list[0]:                    
                    break               
                elif attempt <= 2:
                    if test_result[-1] == t_result_list[1]:
                        f_count -= 1
                    else:
                        na_count -= 1
                    test_result.pop()
                    remark_list.pop()
                
            print(f"{app_name} installation status: {test_result[-1]}, attempt: {attempt}/3")
                    
            # save the result to csv file
            df.at[i, 'Result'] = test_result[-1]
            df.at[i, 'Remarks'] = remark_list[-1]
            df.to_csv(f'result_{device}.csv', index=False)

            total_count += 1
            
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
            f"\nTest result is recorded : {actual_test_count} : {p_count}, {f_count}, {na_count}")

    # Filter only Pass status
    result_df = pd.read_csv(f'result_{device}.csv')
    result_df['Result'] = result_df['Result'].astype(str)
    result_df.columns = result_df.columns.str.strip()
    pass_df = result_df[result_df['Result'] == 'Pass']
    pass_df.to_csv(f'pass_{device}_result.csv', index=False)
    
    
# Test bench
'''
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from basic.test_app_install import test_app_install
from basic.test_app_run import test_app_run
from basic.connect_devices import connect_devices
from basic.csv_handler import process_csv

def execute_command(): # source code from Hyeonjun An.
    lock = Lock()
    device_list = connect_devices()
    package_names, app_names, df, csv_file = process_csv()

    try:
        with ThreadPoolExecutor() as executor:
            for device in device_list:
                print(f"Device {device} is processing...")
                lock.acquire()
                executor.submit( 
                    test_app_install(device, package_names, app_names, df, csv_file), device)
                lock.release()
    except Exception as e:
        print(e)
                
# Log for the installation fails

if __name__ == "__main__":
    execute_command()
'''