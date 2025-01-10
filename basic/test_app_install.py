import subprocess
import uiautomator2 as u2
from basic.unlock_device import unlock_device
import pandas as pd
import time

# device -> run.py
# package_names, app_names -> csv_handler.py

def test_app_install(device, package_names, app_names, df, csv_file, crash_flag, crash_log, install_attempt):
        
    d = u2.connect(device)
    p_count, f_count, na_count, total_count, attempt = 0, 0, 0, 0, 0
    remark_list, test_result = [], []
    t_result_list = ["Pass","Fail","NT/NA"]
                    
    # Initialize columns
    if 'Result' not in df.columns:
        df['Result'] = ""
    else:
        df['Result'] = ""
    if 'Remarks' not in df.columns:
        df['Remarks'] = "" 
    else:
        df['Remarks'] = "" 
    if 'Crash' not in df.columns:
        df['Crash'] = "" 
    else:
        df['Crash'] = ""
            

    def is_app_installed(p_count,f_count,na_count):
        
        no_cancel = not d(text = "Cancel").exists
        yes_cancel = d(text = "Cancel").exists
        
        while yes_cancel:
            pass
        
        if d(text = "Uninstall").wait(timeout = 180):
            test_result.append(t_result_list[0]) # Pass
            remark_list.append("App is successfully Installed")
            p_count += 1
                            
        elif d(text = "Open").exists:
            test_result.append(t_result_list[2]) # NT/NA
            remark_list.append("App needs to be verified again")
            na_count += 1
                            
        elif d(text = "Play").exists:
            test_result.append(t_result_list[2]) # NT/NA
            remark_list.append("App needs to be verified again")
            na_count += 1
                
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
                    
                    is_app_installed(p_count,f_count,na_count)
                            
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
                            f_count += 1 
                                    
                    # wait until open
                    is_app_installed(p_count,f_count,na_count)
                else: 
                    test_result.append(t_result_list[0]) #Pass
                    remark_list.append("App has already been installed")
                    p_count += 1
                    
            # Verify if the app is updatable
            elif d(text = "Update").exists:
                if d(text = "Open").exists:
                    d(text = "Update").click(10)
                        
                    is_app_installed(p_count,f_count,na_count)
                    
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
                d(text = "Install").click(10)

                if d.xpath("//*[contains(@text,'When Wi')]").wait(timeout = 5):
                    d(text = "OK").click(10)
                        
                is_app_installed(p_count,f_count,na_count)
                
            else:
                test_result.append(t_result_list[1]) # Fail
                remark_list.append("App is failed to install within the timeout")
                f_count += 1
                
                
            #attempt to reload the page and repeat the installation
            if test_result[-1] == t_result_list[0]: #Pass
                print(f"{app_name} installation status: {test_result[-1]}, attempt: {attempt}/3")
                break               
            elif attempt <= install_attempt -1:
                if test_result[-1] == t_result_list[1]: #Fail
                    f_count -= 1
                else:
                    na_count -= 1
                print(f"{app_name} installation status: {test_result[-1]}, attempt: {attempt}/3")
                handle_popup()
                test_result.pop()
                remark_list.pop()
                    
        # save the result to csv file
        df.at[i, 'Crash'] = "Crash" if crash_flag.is_set() else "Pass"
        df.at[i, 'Result'] = test_result[-1]
        df.at[i, 'Remarks'] = remark_list[-1]
        df.to_csv(f'Install_result_{device}.csv', index=False)

        total_count += 1

    # Installation Test result
    actual_test_count = f_count + p_count + na_count 
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