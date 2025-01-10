# monkey? - Todo
# adb shell monkey -p your.app.package.name -c android.intent.category.LAUNCHER 1

import subprocess
import time
import uiautomator2 as u2
from major.theme_dark import toggle_dark_mode
from major.multi_window import toggle_multi_window_mode
from basic.unlock_device import unlock_device
import pandas as pd
import platform

def is_app_open(package_name, device):
    #Check if the app is running
    samsung_setting = "com.android.settings/com.samsung.android.settings.wifi"
    android_permission = "com.android.permissioncontroller"
    d = u2.connect(device)
    attempt = 0
    os_name = platform.system()
    
    try:
        for attempt in range(3):
            if os_name in ["Linux", "Darwin"]:  # macOS and Linux
                result = subprocess.check_output(
                    f"adb -s {device} shell dumpsys activity activities | grep ResumedActivity",
                    shell=True,
                    text=True
                ).strip()
            elif os_name == "Windows":
                result = subprocess.check_output(
                    f"adb -s {device} shell dumpsys activity activities | findstr ResumedActivity",
                    shell=True,
                    text=True
                ).strip()
            else:
                print(f"Unsupported OS: {os_name}")
                
            if package_name in result:
                return True
            elif samsung_setting in result:
                if d(text = "Not now").exists:
                    d(text = "Not now").click(10)
                    time.sleep(1)
            elif android_permission in result:
                if d(text = "While using the app").exists:
                    d(text = "While using the app").click()
                elif d(text = "Allow").exists:
                    d(text = "Allow").click()
            else:
                print("is app running? : ", result)
                if d(text = "Allow").exists:
                    d(text = "Allow").click()
                elif d(text = "Cancel").exists:
                    d(text = "Cancel").click()
                elif d(text = "OK").exists:
                    d(text = "OK").click()
                elif d(text = "Not now").exists:
                    d(text = "Not now").click()
                elif d(text = "Close").exists:
                    d(text = "Close").click()
                else:
                    subprocess.run(['adb', "-s", f"{device}", 'shell', 'input', 'keyevent', 'KEYCODE_BACK'
                                    ],check=True) 
                
        attempt += 1
    except subprocess.CalledProcessError:
        return False  # Continue if there's an issue with the adb command

def test_app_run(device, package_names, app_names, df, crash_flag, crash_log,launch_attempt):
        d = u2.connect(device)
        attempt = 0
        
        test_result = []
        mw_results = []
        if 'Running Result' not in df.columns:
            df['Running Result'] = ""
        else:
            df['Running Result'] = ""
        if 'MW_Result' not in df.columns:
            df['MW_Result'] = ""
        else:
            df['MW_Result'] = ""
        if 'Final_MW_Result' not in df.columns:
            df['Final_MW_Result'] = ""
        else:
            df['Final_MW_Result'] = ""
        t_result_list = ["Pass","NT/NA","Crash"]
        

        for i, (package_name, app_name) in enumerate(zip(package_names, app_names)):
            for attempt in range(launch_attempt):
                attempt += 1
                
                unlock_device(device)
                
                # Press home button
                subprocess.run(['adb', "-s", f"{device}", 'shell', 'input', 'keyevent', 'KEYCODE_HOME'
                            ],check=True)
                
                # open the app from google playstore
                subprocess.run([
                    "adb", "-s", f"{device}", "shell",
                    "am start -n com.android.vending/com.android.vending.AssetBrowserActivity",
                    "-a android.intent.action.VIEW",
                    "-d", f"market://details?id={package_name}"
                ], check=True)
                
                print (f"Testing {app_name}...")
                # Open the app
                if crash_flag.is_set():
                    test_result.append(t_result_list[2]) # Crash
                    print(crash_log)
                    crash_flag.clear() # Clear the flag when the crash ends
                    break

                if d(text = "Uninstall").wait(5):
                    if d(text = "Update").exists:
                        d(text = "Update").click(10)
                        if d(text = "Uninstall").wait(timeout = 180):
                            continue
                        else: 
                            print(f"{app_name} has no open or play button")
                            test_result.append(t_result_list[1]) # NA
                                                        
                        
                    if d(text = "Play").exists:
                        d(text = "Play").click(10)
                        time.sleep(2)
                        if is_app_open(package_name, device):
                            toggle_dark_mode(device)
                            time.sleep(2)
                            mw_results.append(toggle_multi_window_mode(device))
                            test_result.append(t_result_list[0]) # PASS
                            print("test done")
                        else:
                            print("app is not opened")
                            test_result.append(t_result_list[1]) # NA

                    elif d(text = "Open").exists:
                        d(text = "Open").click(10)
                        time.sleep(2)
                        if is_app_open(package_name, device):
                            toggle_dark_mode(device)
                            time.sleep(2)
                            mw_results.append(toggle_multi_window_mode(device))
                            test_result.append(t_result_list[0]) # PASS
                            print ("test done")
                        else:
                            print("app is not opened")
                            test_result.append(t_result_list[1]) # NA
                    else: 
                        print(f"{app_name} has no open or play button")
                        test_result.append(t_result_list[1]) # NA
                else:
                    print(f"app is not installed")
                    test_result.append(t_result_list[1]) # NA
                    if d(text = "Allow").exists:
                        d(text = "Allow").click()
                    elif d(text = "Cancel").exists:
                        d(text = "Cancel").click()
                    elif d(text = "OK").exists:
                        d(text = "OK").click()
                    elif d(text = "Not now").exists:
                        d(text = "Not now").click()
                    elif d(text = "Close").exists:
                        d(text = "Close").click()
                    else:
                        subprocess.run(['adb', "-s", f"{device}", 'shell', 'input', 'keyevent', 'KEYCODE_BACK'
                                        ],check=True)                    
                #attempt to reload the page and repeat the installation
                if test_result[-1] == t_result_list[2]:
                    print(f"{app_name} launch status: {test_result[-1]}, attempt: {attempt}/{launch_attempt}")
                    break               
                elif attempt <= launch_attempt -1:
                    print(f"{app_name} launch status: {test_result[-1]}, attempt: {attempt}/{launch_attempt}")
                    test_result.pop()
            
            if mw_results:
                df.at[i,'MW_Result'] = ', '.join(mw_results)
                final_mw_result = max(set(mw_results), key=mw_results.count)
                df.at[i,'Final_MW_Result'] = final_mw_result
            mw_results.clear()
            
            df.at[i, 'Running Result'] = test_result[-1]
            df.to_csv(f'launch_result_{device}.csv', index=False)
    
