import os
import sys
import time
import re
import threading
import subprocess
import platform
import uiautomator2 as u2
import pandas as pd
import random
from PyQt5.QtWidgets import(QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QFileDialog, QMessageBox, QTextEdit, QSpinBox, QHBoxLayout, QLineEdit, QFrame)
from threading import Lock, Event
from google_play_scraper import app, search

# device -> run.py
# package_names, app_names -> csv_handler.py

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
            f"adb -s {device} shell dumpsys window | findstr mDreamingLockscreen",
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
                return True
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
        if not is_device_unlocked(device):
            return False
        
    except subprocess.CalledProcessError as e:
        return False  # Continue if there's an issue with the adb command
    return True

def connect_devices(): # source code from Hyeonjun An.
    # Get connected devices
    result = subprocess.run(
        ['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True)
    lines = result.stdout.split('\n')[1:]  # Skip the first line which is a header
    device_list = [line.split('\t')[0] for line in lines if '\tdevice' in line]

    return device_list

def process_csv(csv_filename):
    csv_file = os.path.abspath(csv_filename)
    
    df = pd.read_csv(csv_file, encoding='unicode_escape').rename(columns=lambda x: x.strip())
    
    package_names = df['App ID'].tolist()
    app_names = df['App Name'].tolist()    
    
    return package_names, app_names, df, csv_file
    
def toggle_dark_mode(device):
    is_dark_mode = subprocess.run(['adb', "-s", f"{device}", 'shell', 'cmd', 'uimode', 'night'
                                ],capture_output=True, text=True, check=True)
    current_status = is_dark_mode.stdout.strip()
    if current_status == "Night mode: no":
        # Enabling dark mode
        subprocess.run(['adb', "-s", f"{device}", 'shell', 'cmd', 'uimode', 'night', 'yes'
                    ],capture_output=True, text=True, check=True)
        time.sleep(1)
    else:
        # Disabling dark mode
        subprocess.run(['adb', "-s", f"{device}", 'shell', 'cmd', 'uimode', 'night', 'no'
                    ],capture_output=True, text=True, check=True)
        time.sleep(1)
        
def toggle_multi_window_mode(device,package_name):
    os_name = platform.system()
    d = u2.connect(device)
    horizontal = "mCurrentRotation=ROTATION_0"
    
    # initialize the screen size & duration
    screen_width, screen_height = d.window_size()
    center_x, center_y = screen_width //2 , screen_height // 2

    # click recents button
    subprocess.run(['adb', "-s", f"{device}", 'shell', 'input', 'keyevent', 'KEYCODE_APP_SWITCH'
                    ],check=True)
        
    time.sleep(1)
    if os_name == "Windows":
        crotation = subprocess.check_output(
                        f"adb -s {device} shell dumpsys window | findstr mCurrentRotation",
                        shell=True,
                        text=True
                    ).strip()
        
    elif os_name in ["Linux", "Darwin"]:
        crotation = subprocess.check_output(
                        f"adb -s {device} shell dumpsys window | grep mCurrentRotation",
                        shell=True,
                        text=True
                    ).strip()
        
    if horizontal in crotation:
        d.long_click(screen_width -1, center_y -1, duration = 3)            
    else:
        # click home button
        subprocess.run(['adb', "-s", f"{device}", 'shell', 'input', 'keyevent', 'KEYCODE_HOME'
                        ],check=True)
        time.sleep(1)
        subprocess.run(['adb', "-s", f"{device}", 'shell', 'input', 'keyevent', 'KEYCODE_APP_SWITCH'
                        ],check=True)
        time.sleep(1)
        d.long_click(center_x // 2, center_y, duration = 3)
        
    toast_text = d.toast.get_message(5.0, 5.0)
    if d.xpath("//*[contains(@text,'Select app')]").wait(2):
        time.sleep(5)
        mw_result = "Pass"
    elif toast_text and "t use this app in Multi" in toast_text:
        mw_result = "Not supportive"
    else:
        mw_result = "Fail"
    
    #toggle_monkey_test(device,package_name)
    return mw_result

def toggle_monkey_test(device, package_name):
    d = u2.connect(device)
    screen_width, screen_height = d.window_size()    
    event_count = 100
    th_height = screen_height // 2
    
    for _ in range(event_count):
        # Randomly generate X-coordinate within screen width
        x = random.randint(0, screen_width)
        # Generate Y-coordinate within the bottom half of the screen
        y = random.randint(0, th_height)

        # Run the monkey command with touch event at (x, y)
        subprocess.run([
            'adb', '-s', device, 'shell', 'input', 'tap', str(x), str(y)
        ], capture_output=True, text=True)

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
                    subprocess.run(['adb', "-s", f"{device}", 'shell', 'input', 'keyevent', 'KEYCODE_HOME'
                                    ],check=True) 
                
        attempt += 1
    except subprocess.CalledProcessError:
        return False  # Continue if there's an issue with the adb command

def test_app_install(device, package_names, app_names, df, install_attempt, launch_attempt):
    
    crash_flag = threading.Event() # Use an Event to signal a crash detection
    stop_flag = threading.Event()
    
    d = u2.connect(device)
    total_count, attempt, l_attempt = 0, 0, 0
    remark_list, test_result, mw_results, launch_result, crash_log = [], [], [], [], []
    t_result_list = ["Pass","Fail","NT/NA"]
    l_result_list = ["Pass","NT/NA","Crash"]
                    
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
    if 'App Version2' not in df.columns:
        df['App Version2'] = ""
    if 'Updated Date' not in df.columns:
        df['Updated Date'] = ""
    if 'TargetSdk' not in df.columns:
        df['TargetSdk'] = "" 
    if 'Running Result' not in df.columns:
        df['Running Result'] = ""
    if 'Final MW Result' not in df.columns:
        df['Final MW Result'] = ""
    if 'MW Result' not in df.columns:
        df['MW Result'] = ""
    if 'Crash log' not in df.columns:
        df['Crash log'] = ""
    
        
    def monitor_crashes():
        log_lock = threading.Lock()
        try:
            subprocess.run(
            ["adb", "-s", device, "logcat", "-c"],
            check=True
            )
            
            logcat_process = subprocess.Popen(
                f"adb -s {device} logcat -v time",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            crash_start = re.compile(r"FATAL EXCEPTION|ANR in|Abort message:|signal \d+ \(SIG[A-Z]+\)")
            process_death = re.compile(rf"Process {package_name} .* has died")
            crash_detected = False

            for line in logcat_process.stdout:
                line = line.strip()
                if stop_flag.is_set():
                    logcat_process.terminate()
                    break

                if crash_start.search(line):
                    crash_detected = True
                    with log_lock:
                        crash_log.append("\n--- Crash Detected ---")
                        crash_log.append(line)

                if crash_detected:
                    with log_lock:
                        crash_log.append(line)
                    
                    if process_death.search(line):
                        with log_lock:
                            crash_log.append(line)
                            crash_log.append("--- End of Crash ---\n")
                        crash_flag.set()  # Set the flag to indicate a crash
                        crash_detected = False  # Reset flag after full crash log is captured
                        break
                    
        except Exception as e:
            print(f"Error while monitoring logcat: {e}")
    '''        
    def skip_tested_apps():
        result_csv = f'Install_result_{device}.csv'  # Add .csv extension
        
        if os.path.exists(result_csv):
            # Load the result CSV file
            df = pd.read_csv(result_csv, encoding='unicode_escape').rename(columns=lambda x: x.strip())
    '''        

    def is_app_installed():
        #no_cancel = not d(text = "Cancel").exists
        yes_cancel = d(text = "Cancel").exists
        timeout = 180
        timeout_start = time.time()
        
        #Checking if cancel button is activated for 180 sec
        while time.time() - timeout_start < timeout:
            if not yes_cancel:
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
            #3app.test.mql
        elif d.xpath("//*[contains(@text,'Complete account setup')]").wait(timeout = 5):
            d(text = "Continue").click(10)
            if d.xpath("//*[contains(@text,'Payment method]')]").wait(timeout = 5):
                d(text = "Skip").click(10)
            else:
                d.click(screen_width //2, screen_height // 2)
                subprocess.run([
                    "adb","-s",f"{device}","shell",
                    "input","keyevent","KEYCODE_HOME"
                ], check=True)
                
        else:
            # Touch and hold the Home button, then circle or tap text or images to learn more and explore.
            d.click(screen_width //2, screen_height // 2)
            subprocess.run([
                "adb","-s",f"{device}","shell",
                "input","keyevent","KEYCODE_HOME"
            ], check=True)
            
    def info_scrapper():
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
                "adb", "-s", device, "shell", "dumpsys", "package", package_name
            ], capture_output=True, text=True) #shell=True, encoding='utf-8'
            #print(app_version_finder)
            
            # App version        
            is_version = False
            for line in app_version_finder.stdout.splitlines():
                if "versionCode=" in line:
                    target_sdk = line.split()
                    d_target = dict(item.split("=") for item in target_sdk)

                    # target_sdk = ['versionCode=10910200', 'minSdk=27', 'targetSdk=35']
                    # d_target = {'versionCode': '10910200', 'minSdk'com.waze: '27', 'targetSdk': '35'}
                            
                    if "targetSdk" in d_target:
                        df.at[i, 'TargetSdk'] = d_target['targetSdk']
                    else:
                        df.at[i, 'TargetSdk'] = "No data"

                if "versionName=" in line:
                    app_version = line.split("=")[1].strip()
                    df.at[i, 'App Version'] = app_version
                    is_version = True
                    break
            if not is_version:
                # Sync app version
                is_version_info = app_info.get('version', 'No version found').strip()
                df.at[i, 'App Version'] = is_version_info if is_version_info else "Unknown"
            
        except Exception as e:
            df.at[i, 'Developer'] = "App is not found"
            df.at[i, 'App Category'] = "App is not found"
            df.at[i, 'App Version'] = "App is not found"
            df.at[i, 'Updated Date'] = "App is not found"
            df.at[i, 'TargetSdk'] = "App is not found"
        
    def app_launcher():
        if crash_flag.is_set():
            return
        if d(text = "Play").wait(timeout = 5):
            d(text = "Play").click(10)
            time.sleep(2)
            toggle_dark_mode(device)
            time.sleep(2)
            mw_results.append(toggle_multi_window_mode(device,package_name))
            #toggle_monkey_test(device,package_name)
            launch_result.append(l_result_list[0]) # PASS

        elif d(text = "Open").wait(timeout = 5):
            d(text = "Open").click(10)
            time.sleep(2)
            toggle_dark_mode(device)
            time.sleep(2)
            mw_results.append(toggle_multi_window_mode(device,package_name))
            #toggle_monkey_test(device,package_name)
            launch_result.append(l_result_list[0]) # PASS

        else: 
            print(f"app is not installed")
            launch_result.append(l_result_list[1]) # NA
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
        time.sleep(2)
        stop_flag.set()
    
    # Navigate to the app page in google playstore
    for i, (package_name, app_name) in enumerate(zip(package_names, app_names)):
        
        if 'Install Result' in df.columns:
            if pd.notna(df.at[i, 'Install Result']) and df.at[i, 'Install Result'].strip():
                continue 
        
        for attempt in range(install_attempt):
            attempt += 1

            if not unlock_device(device):
                break
                
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
                elif d(text = "Enable").exists:
                    d(text = "Enable").click(10)
                    if d(text = "Update").wait(timeout = 5):
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
                    
            elif d(text = "Enable").exists:
                d(text = "Enable").click(10)
                if d(text = "Update").wait(timeout = 5):
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
                print(f"{app_name} installation status: {test_result[-1]}, attempt: {attempt}/{install_attempt}")
                if launch_attempt >= 1:
                    for l_attempt in range(launch_attempt):
                        l_attempt += 1
                        crash_thread = threading.Thread(target=monitor_crashes, daemon=True)
                        crash_thread.start()
                        app_launcher()
                        while not stop_flag.is_set():
                            crash_flag.wait()
                        if crash_flag.is_set():
                            launch_result.append(l_result_list[2])
                            break
                    crash_thread.join()
                    crash_flag.clear()
                    stop_flag.clear()
                        
                    #attempt to reload the page and repeat the installation    
                    if launch_result[-1] == l_result_list[2]:
                        print(f"{app_name} launch status: {launch_result[-1]}, attempt: {l_attempt}/{launch_attempt}")
                        mw_results.clear()
                        df.at[i, 'Crash log'] = "\n".join(crash_log)
                        crash_log.clear()
                        break

                    elif l_attempt <= launch_attempt -1:
                        print(f"{app_name} launch status: {launch_result[-1]}, attempt: {l_attempt}/{launch_attempt}")
                        launch_result.pop()
                        
                    elif launch_result[-1] == l_result_list[1]:
                        if not is_app_open(package_name, device):
                            launch_result[-1] == "App is not opened"
                        else:
                            launch_result[-1] == l_result_list[1]
                    else:
                        print(f"{app_name} launch status: {launch_result[-1]}, attempt: {l_attempt}/{launch_attempt}")
                
                if mw_results:
                    df.at[i,'MW Result'] = ', '.join(mw_results)
                    final_mw_result = max(set(mw_results), key=mw_results.count)
                    df.at[i,'Final MW Result'] = final_mw_result
                    mw_results.clear()
                break

            elif attempt <= install_attempt -1:
                print(f"{app_name} installation status: {test_result[-1]}, attempt: {attempt}/{install_attempt}")
                handle_popup()
                test_result.pop()
                remark_list.pop()
            else:
                print(f"{app_name} installation status: {test_result[-1]}, attempt: {attempt}/{install_attempt}")
                if launch_result:
                    launch_result.pop()
                launch_result.append(l_result_list[1]) # NA
        
        info_scrapper()
        
        # save the result to csv file
        df.at[i, 'Running Result'] = launch_result[-1] if launch_result else None
        df.at[i, 'Install Result'] = test_result[-1] if test_result else None
        df.at[i, 'Remarks'] = remark_list[-1] if remark_list else None
        test_result_df = df[['App Name','App ID','Install Result','Running Result', 'MW Result', 'Final MW Result', 'Remarks', 'App Category', 'Developer', 'App Version', 'Updated Date', 'TargetSdk', 'Crash log']]
        test_result_df.to_csv(f'Test_result_{device}.csv', index=False)
        total_count += 1
        
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
    
class AppTesterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()  # Main layout (horizontal)

        # ===== Left Layout (Device Connection, Testing Controls) =====
        left_layout = QVBoxLayout()

        self.device_label = QLabel("Connected Devices: None")
        left_layout.addWidget(self.device_label)

        self.connect_button = QPushButton("Connect Devices")
        self.connect_button.clicked.connect(self.connect_devices)
        left_layout.addWidget(self.connect_button)

        self.install_attempt_label = QLabel("Installation Attempts:")
        left_layout.addWidget(self.install_attempt_label)

        self.install_attempt_input = QSpinBox()
        self.install_attempt_input.setMinimum(1)
        self.install_attempt_input.setValue(3)
        left_layout.addWidget(self.install_attempt_input)

        self.launch_attempt_label = QLabel("Launch test Attempts:")
        left_layout.addWidget(self.launch_attempt_label)

        self.launch_attempt_input = QSpinBox()
        self.launch_attempt_input.setMinimum(0)
        self.launch_attempt_input.setValue(3)
        left_layout.addWidget(self.launch_attempt_input)

        self.start_button = QPushButton("Start Testing")
        self.start_button.clicked.connect(self.start_testing)
        left_layout.addWidget(self.start_button)

        self.start_all_button = QPushButton("Start Testing all")
        self.start_all_button.clicked.connect(self.start_testing_all)
        left_layout.addWidget(self.start_all_button)

        self.stop_button = QPushButton("Stop Testing")
        self.stop_button.clicked.connect(self.stop_testing)
        self.stop_button.setEnabled(False)
        left_layout.addWidget(self.stop_button)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        left_layout.addWidget(self.log_output)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        
        # ===== Divider between Left and Middle =====
        left_divider = QFrame()
        left_divider.setFrameShape(QFrame.VLine)
        left_divider.setFrameShadow(QFrame.Sunken)
        left_divider.setFixedWidth(1)
        left_divider.setStyleSheet("border: 1px dotted black;")
        
        # ===== Middle Layout (CSV Table and Controls) =====
        mid_layout = QVBoxLayout()

        self.app_search_label = QLabel("App Search")
        mid_layout.addWidget(self.app_search_label)
        
        self.keyword_input = QLineEdit(self)
        self.keyword_input.setPlaceholderText("Trending social media apps")
        mid_layout.addWidget(self.keyword_input)
        
        self.search_button = QPushButton("Search (Max: 30 apps)")
        self.search_button.clicked.connect(self.app_searcher)
        mid_layout.addWidget(self.search_button)

        self.load_search_data = QPushButton("Load searched data CSV File")
        self.load_search_data.clicked.connect(self.search_data)
        mid_layout.addWidget(self.load_search_data)
        
        # Horizontal dotted divider
        mid_divider = QFrame()
        mid_divider.setFrameShape(QFrame.HLine)  # Horizontal line
        mid_divider.setFrameShadow(QFrame.Sunken)
        mid_divider.setFixedHeight(1)  # Use fixed height for horizontal line
        mid_divider.setStyleSheet("border: 1px solid black;")
        mid_layout.addWidget(mid_divider)  # Add the divider between buttons

        self.automation_label = QLabel("Automation")
        mid_layout.addWidget(self.automation_label)
        
        self.load_csv_button = QPushButton("Load Automation CSV File")
        self.load_csv_button.clicked.connect(self.load_csv)
        mid_layout.addWidget(self.load_csv_button)
        
        self.custom_csv_button = QPushButton('Select CSV file')
        self.custom_csv_button.clicked.connect(self.custom_csv)
        mid_layout.addWidget(self.custom_csv_button)

        # Horizontal dotted divider
        mid_divider = QFrame()
        mid_divider.setFrameShape(QFrame.HLine)  # Horizontal line
        mid_divider.setFrameShadow(QFrame.Sunken)
        mid_divider.setFixedHeight(1)  # Use fixed height for horizontal line
        mid_divider.setStyleSheet("border: 1px solid black;")
        mid_layout.addWidget(mid_divider)  # Add the divider between buttons
                
        # Horizontal layout for Add Row buttons
        self.automation_label = QLabel("Table Control")
        mid_layout.addWidget(self.automation_label)
        add_row_layout = QHBoxLayout()
        self.add_row_above_button = QPushButton("Add Row ⬆")
        self.add_row_above_button.clicked.connect(self.add_row_above)
        add_row_layout.addWidget(self.add_row_above_button)

        self.add_row_below_button = QPushButton("Add Row ⬇")
        self.add_row_below_button.clicked.connect(self.add_row_below)
        add_row_layout.addWidget(self.add_row_below_button)

        mid_layout.addLayout(add_row_layout)

        self.delete_row_button = QPushButton("Delete Row")
        self.delete_row_button.clicked.connect(self.delete_row)
        mid_layout.addWidget(self.delete_row_button)
    
        self.save_csv_button = QPushButton("Save CSV")
        self.save_csv_button.clicked.connect(self.save_csv)
        mid_layout.addWidget(self.save_csv_button)

        self.save_as_csv_button = QPushButton("Save as")
        self.save_as_csv_button.clicked.connect(self.save_as_csv)
        mid_layout.addWidget(self.save_as_csv_button)
        
        mid_widget = QWidget()
        mid_widget.setLayout(mid_layout)
        
        # ===== Divider between Middle and Right =====
        right_divider = QFrame()
        right_divider.setFrameShape(QFrame.VLine)
        right_divider.setFrameShadow(QFrame.Sunken)
        right_divider.setFixedWidth(1)
        right_divider.setStyleSheet("border: 1px dotted black;")

        # ===== Right Layout (CSV Table and Controls) =====
        right_layout = QVBoxLayout()
        
        self.display_table_label = QLabel("Table")
        right_layout.addWidget(self.display_table_label)
        
        # CSV Table Widget
        self.tableWidget = QTableWidget()
        right_layout.addWidget(self.tableWidget)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # Add left and right sections to the main horizontal layout
        layout.addWidget(left_widget, 30)   # Left takes 25% width
        layout.addWidget(left_divider)  # Divider between Left and Middle

        layout.addWidget(mid_widget, 30)   # mid takes 25% width
        layout.addWidget(right_divider)  # Divider between Left and Middle
        layout.addWidget(right_widget, 40)  # Right takes 50% width

        self.setLayout(layout)
        self.setWindowTitle("App Installation Tester")
        self.setGeometry(300, 300, 1000, 400) 
        
        self.device_list = []
        self.package_names = []
        self.app_names = []
        self.df = None
        
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def connect_devices(self):
        try:
            self.device_list = connect_devices()
            self.device_label.setText(f"Connected Devices: {', '.join(self.device_list)}")
        except Exception as e:
            self.show_error(str(e))
            
    def load_csv(self):
        try:
            self.automation_file_path = "test1.csv"
            self.search_file_path = None
            self.resume_file_path = None

            self.package_names, self.app_names, self.df, _ = process_csv(self.automation_file_path)
            self.log_output.append(f"Loaded CSV file - {self.automation_file_path}")
            self.display_data(self.tableWidget)
        except Exception as e:
            self.show_error(str(e))
    '''        
    def resume_csv(self):
        try:
            self.resume_file_path = "test_result_{device}.csv"
            self.search_file_path = None
            self.resume_file_path = None

            self.package_names, self.app_names, self.df, _ = process_csv(self.resume_file_path)
            self.log_output.append(f"Loaded CSV file - {self.resume_file_path}")
            self.display_data(self.tableWidget)
        except Exception as e:
            self.show_error(str(e))
    '''
    def custom_csv(self): 
        try:
            # Open a file selection dialog to upload a CSV file
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.ExistingFile)
            file_path, _ = file_dialog.getOpenFileName(self, "Upload Test Result CSV", "", "CSV Files (*.csv)")

            if not file_path:
                QMessageBox.warning(self, "No File Selected", "Please select a CSV file to proceed.")
                return  # User canceled selection

            # Store the selected file path
            self.resume_file_path = file_path
            self.automation_file_path = None
            self.search_file_path = None

            # Process the selected file
            self.package_names, self.app_names, self.df, _ = process_csv(self.resume_file_path)
            self.display_data(self.tableWidget)
            
        except Exception as e:
            self.show_error(str(e))
    
    def app_searcher(self):
        app_names, app_ids, free_apps,prices,num_of_installs = [],[],[],[],[]
        
        self.keyword = self.keyword_input.text().strip()  # Get the keyword from the user input
        if not self.keyword:
            self.keyword = "Trending social media apps"
        
        results = search(
        self.keyword
    )
        for app in results:
            try:
                app_names.append(app['title'])
                app_ids.append(app['appId'])
                free_apps.append(app['free'])
                prices.append(app['price'])
                num_of_installs.append(app['installs'])
                
            except Exception as e:
                app_names.append('Unknown')
                app_ids.append('Unknown')
                free_apps.append('Unknown')
                prices.append('Unknown')
                num_of_installs.append('Unknown')
                
            self.search_file_path = f'app_search_{self.keyword}_result.csv'
            self.automation_file_path = None  # Reset search file path to avoid interference
            self.resume_file_path = None


            df = pd.DataFrame({
                'App Name': app_names,
                'App ID' : app_ids,
                'Free app' : free_apps,
                'Price' : prices,
                'Installation' : num_of_installs
            })
            
            df.to_csv(self.search_file_path, index=False)
            
    def search_data(self):
        try:
            csv = f'app_search_{self.keyword}_result.csv'
            self.package_names, self.app_names, self.df, _ = process_csv(csv)
            self.log_output.append(f"Loaded CSV file - {csv}")
            self.display_data(self.tableWidget)
        except Exception as e:
            self.show_error(str(e))

    def display_data(self, target_table):
        """Display DataFrame in QTableWidget."""
        if self.df is not None:
            target_table.setRowCount(self.df.shape[0])
            target_table.setColumnCount(self.df.shape[1])
            target_table.setHorizontalHeaderLabels(self.df.columns)

            for row in range(self.df.shape[0]):
                for col in range(self.df.shape[1]):
                    item = QTableWidgetItem(str(self.df.iat[row, col]))
                    target_table.setItem(row, col, item)

    def add_row_above(self):
        """Insert an empty row above the selected row."""
        if self.df is not None:
            selected_row = self.tableWidget.currentRow()
            if selected_row == -1:  # If no row is selected, add at the top
                selected_row = 0  
            self.tableWidget.insertRow(selected_row)

            # Add an empty row to the DataFrame at the same index
            new_row = pd.Series([""] * len(self.df.columns), index=self.df.columns)
            self.df = pd.concat([self.df.iloc[:selected_row], new_row.to_frame().T, self.df.iloc[selected_row:]], ignore_index=True)

    def add_row_below(self):
        """Insert an empty row below the selected row."""
        if self.df is not None:
            selected_row = self.tableWidget.currentRow()
            if selected_row == -1:  # If no row is selected, add at the bottom
                selected_row = self.tableWidget.rowCount()
            else:
                selected_row += 1  # Move to the next row
            
            self.tableWidget.insertRow(selected_row)

            # Add an empty row to the DataFrame at the same index
            new_row = pd.Series([""] * len(self.df.columns), index=self.df.columns)
            self.df = pd.concat([self.df.iloc[:selected_row], new_row.to_frame().T, self.df.iloc[selected_row:]], ignore_index=True)

    def delete_row(self):
        """Delete selected row from the table."""
        selected_rows = set(index.row() for index in self.tableWidget.selectedIndexes())
        for row in sorted(selected_rows, reverse=True):
            self.tableWidget.removeRow(row)
            
    def save_csv(self):
        """Save the updated table data back to the most recently used file."""
        if self.df is None:
            QMessageBox.warning(self, "Error", "No file loaded. Please load a CSV file first.")
            return

        # Prioritize the most recent loaded CSV file
        file_path = self.automation_file_path if self.automation_file_path else self.search_file_path

        if not file_path:
            QMessageBox.warning(self, "Error", "No file loaded. Please load a CSV file first.")
            return

        # Extract data from table widget
        updated_data = []
        for row in range(self.tableWidget.rowCount()):
            row_data = [self.tableWidget.item(row, col).text() if self.tableWidget.item(row, col) else ''
                        for col in range(self.tableWidget.columnCount())]
            updated_data.append(row_data)

        updated_df = pd.DataFrame(updated_data, columns=self.df.columns)
        updated_df.to_csv(file_path, index=False)
        QMessageBox.information(self, "Success", f"CSV file saved successfully to {file_path}")

    def save_as_csv(self):
        """Prompt for renaming every time and save the updated data."""
        if self.df is None:
            QMessageBox.warning(self, "Error", "No file loaded. Please load a CSV file first.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File As", "", "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            updated_data = []
            for row in range(self.tableWidget.rowCount()):
                row_data = [
                    self.tableWidget.item(row, col).text() if self.tableWidget.item(row, col) else ''
                    for col in range(self.tableWidget.columnCount())
                ]
                updated_data.append(row_data)

            updated_df = pd.DataFrame(updated_data, columns=self.df.columns)
            updated_df.to_csv(file_path, index=False)
            QMessageBox.information(self, "Success", f"CSV file saved successfully as:\n{file_path}")

            self.file_path = file_path

    def start_testing(self):
        try:
            if not self.device_list:
                self.log_output.append("Error: Devices not connected")
                
            elif not self.package_names:
                self.log_output.append("Error: CSV not loaded.")
                return
            
            install_attempt = self.install_attempt_input.value()
            launch_attempt = self.launch_attempt_input.value()
            self.stop_testing_event.clear()
            
            self.log_output.append("Starting tests...")
            
            self.stop_button.setEnabled(True)
            self.start_all_button.setEnabled(False)
            self.start_button.setEnabled(False)
            self.search_button.setEnabled(False)
            self.load_search_data.setEnabled(False)
            self.load_csv_button.setEnabled(False)
            self.custom_csv_button.setEnabled(False)
            
            def run_tests():
                for device in self.device_list:
                    self.log_output.append(f"Processing device {device}...")
                    test_app_install (device, self.package_names, self.app_names, self.df, install_attempt, launch_attempt)
                self.log_output.append("Testing completed.")
                self.stop_button.setEnabled(False)
                self.start_all_button.setEnabled(True)
                self.start_button.setEnabled(True)
                self.search_button.setEnabled(True)
                self.load_search_data.setEnabled(True)
                self.load_csv_button.setEnabled(True)
                self.custom_csv_button.setEnabled(True)
            
            threading.Thread(target=run_tests, daemon=True).start()
            
        except Exception as e:
            self.show_error(str(e))

    def start_testing_all(self):
        try:
            if not self.device_list:
                self.log_output.append("Error: Devices not connected")
                
            elif not self.package_names:
                self.log_output.append("Error: CSV not loaded.")
                return
            
            install_attempt = self.install_attempt_input.value()
            launch_attempt = self.launch_attempt_input.value()
            self.stop_testing_event.clear()
            
            self.log_output.append("Starting tests...")
            
            self.stop_button.setEnabled(True)
            self.start_all_button.setEnabled(False)
            self.start_button.setEnabled(False)
            self.search_button.setEnabled(False)
            self.load_search_data.setEnabled(False)
            self.load_csv_button.setEnabled(False)
            self.custom_csv_button.setEnabled(False)
            
            def run_tests_for_device(device):
                self.log_output.append(f"Processing device {device}...")
                test_app_install(device, self.package_names, self.app_names, self.df, install_attempt, launch_attempt)

            def run_all_tests():
                threads = []
                for device in self.device_list:
                    t = threading.Thread(target=run_tests_for_device, args=(device,), daemon=True)
                    threads.append(t)
                    t.start()

                for t in threads:
                    t.join()

                self.log_output.append("Testing completed.")
                self.stop_button.setEnabled(False)
                self.start_all_button.setEnabled(True)
                self.start_button.setEnabled(True)
                self.start_all_button.setEnabled(True)
                self.start_button.setEnabled(True)
                self.search_button.setEnabled(True)
                self.load_search_data.setEnabled(True)
                self.load_csv_button.setEnabled(True)
                self.custom_csv_button.setEnabled(True)

            threading.Thread(target=run_all_tests, daemon=True).start()
        except Exception as e:
            self.show_error(str(e))

    def stop_testing(self):
        try:
            os._exit(0)
            #self.log_output.append("Testing stopped by user.")
            self.stop_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.start_all_button.setEnabled(True)
            self.start_button.setEnabled(True)
            self.start_all_button.setEnabled(True)
            self.start_button.setEnabled(True)
            self.search_button.setEnabled(True)
            self.load_search_data.setEnabled(True)
            self.load_csv_button.setEnabled(True)
            self.custom_csv_button.setEnabled(True)
        except Exception as e:
            self.show_error(str(e))

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    ex = AppTesterGUI()
    ex.show()
    sys.exit(qt_app.exec_())
