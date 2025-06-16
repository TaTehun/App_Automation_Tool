print("App Tester is starting... Please wait.")

import os
import sys
import time
import re
import threading
import subprocess
import platform
import uiautomator2 as u2
import pandas as pd
from PyQt5.QtWidgets import(QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QFileDialog, QMessageBox, QTextEdit, QSpinBox, QHBoxLayout, QLineEdit, QFrame, QProgressBar)
from PyQt5.QtCore import pyqtSignal, QObject
from threading import Lock, Event
from google_play_scraper import app, search, permissions

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

    if "mShowingDream=false" in is_unlocked.stdout and "mDreamingLockscreen=false" in is_unlocked.stdout:
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
    device_ids = [line.split('\t')[0] for line in lines if '\tdevice' in line]

    device_map = {}
    serial_device = {}
    
    for device_id in device_ids:
        serial = subprocess.check_output(
        ["adb", "-s", device_id, "shell", "getprop", "ro.serialno"]
        ).decode().strip()
            
        if serial not in serial_device:
            serial_device[serial] = device_id
        else:
            # USB connection preferred over Wireless
            c_id = serial_device[serial]
            if ":" in device_id and ":" not in c_id:
                continue
            elif ":" not in device_id and ":" in c_id:
                serial_device[serial] = device_id
    # Reverse mapping
    for serial, device_id in serial_device.items():
        device_map[device_id] = serial
                    
    return device_map
'''
def switch_navbar(device):
    d = u2.connect(device)

    for i in range(5):
        subprocess.run(['adb', "-s", f"{device}", 'shell', 'input', 'keyevent', 'KEYCODE_APP_SWITCH'
                        ],check=True)
        d(text = "Close all").click()
        
        subprocess.run(['adb', "-s", f"{device}", 'shell', 'am', 'start', '-a', 'android.settings.SETTINGS'
                    ],capture_output=True, text=True, check=True)
        d(text = "Display").click()
        d(text = "Navigation bar").click()
        d(text = "Swipe gestures").click()
        
        nav_status = subprocess.run(['adb', "-s", f"{device}", 'shell', 'settings', 'get', 'secure', 'navigation_mode'
                                ],capture_output=True, text=True, check=True)
        
        if nav_status.stdout == 2:
            break
            
'''    
def get_app_base_dir():
    if getattr(sys, 'frozen', False):  # Check if Pyinstaller is built 
        return os.path.dirname(sys.executable)  # .app location
    else:
        return os.path.dirname(os.path.abspath(__file__))
    
def process_csv(csv_filename):
    csv_file = os.path.abspath(csv_filename)
    
    df = pd.read_csv(csv_file, encoding='unicode_escape').rename(columns=lambda x: x.strip())
    app_names = df["App Name"].dropna().tolist() or "None"
    package_names = df['App ID'].tolist()
    
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
        time.sleep(3)
        mw_result = "Pass"
    elif toast_text and "t use this app in Multi" in toast_text:
        mw_result = "Not supportive"
    else:
        mw_result = "Fail"
    
    return mw_result

def toggle_monkey_test(device, package_name):
    d = u2.connect(device)
    event_count = 500
    throttle = 100
    
    subprocess.run([
        'adb', '-s', device, 'shell', 'monkey', '-p', package_name, 
        '--throttle', str(throttle), '--pct-touch', '100', str(event_count)
    ], stdout = subprocess.DEVNULL, stderr= subprocess.DEVNULL)
    '''
    screen_width, screen_height = d.window_size()    
    event_count = 1000
    th_height = screen_height // 2
    
    for _ in range(event_count):
        # Randomly generate X-coordinate within screen width
        x = random.randint(0, screen_width)
        # Generate Y-coordinate within the bottom half of the screen
        y = random.randint(0, screen_height)

        # Run the monkey command with touch event at (x, y)
        subprocess.run([
            'adb', '-s', device, 'shell', 'input', 'tap', str(x), str(y)
        ], capture_output=True, text=True)
    '''
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
                    d(text = "Not now").click()
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
                
    except subprocess.CalledProcessError:
        return False  # Continue if there's an issue with the adb command

def test_app_install(device, package_names, app_names, df, install_attempt, launch_attempt, serial, signals, test_stop_flag):

    base_dir = get_app_base_dir()
    crash_flag = threading.Event() # Use an Event to signal a crash detection
    stop_flag = threading.Event()
    
    d = u2.connect(device)
    total_count, attempt, l_attempt = 0, 0, 0
    remark_list, test_result, mw_results, launch_result = [], [], [], []
    t_result_list = ["Pass","Fail","NT/NA"]
    l_result_list = ["Pass","NT/NA","Crash"]
    
    #Checking if temp saved file exists
    temp_csv = os.path.join(base_dir, f'Test_result_{serial}_temp.csv')
    skip_app_mode = os.path.exists(temp_csv)
    temp_df = pd.read_csv(temp_csv, encoding='unicode_escape').rename(columns=lambda x: x.strip()) if skip_app_mode else None
    
    target_df = temp_df if skip_app_mode else df
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
    if 'Running Result' not in df.columns:
        df['Running Result'] = ""
    if 'Final Running Result' not in df.columns:
        df['Final Running Result'] = ""
    if 'Final MW Result' not in df.columns:
        df['Final MW Result'] = ""
    if 'MW Result' not in df.columns:
        df['MW Result'] = ""
    if 'Is Camera' not in df.columns:
        df['Is Camera'] = ""
    if 'Permissions' not in df.columns:
        df['Permissions'] = ""
        
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

                if not crash_detected and crash_start.search(line):
                    crash_detected = True
                    print("Crash Yes")
                    replace_package_name = package_name.replace(".", "_")
                    file_name = f"crashlog_{attempt}_{device}_{replace_package_name}.txt"
                    file_path = os.path.join(get_app_base_dir(), file_name)
                    log_file = open(file_path, "w", encoding = "utf-8")
                    with log_lock:
                        log_file.write("\n--- Crash Detected ---")

                if crash_detected:
                    if log_file:
                        with log_lock:
                            log_file.write(line + "\n")
                    
                    if process_death.search(line):
                        with log_lock:
                            log_file.write("--- End of Crash ---\n")
                        crash_flag.set()  # Set the flag to indicate a crash
                        crash_detected = False  # Reset flag after full crash log is captured
                        if log_file:
                            log_file.close()
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
        if is_app_already_installed():
            if d(text = "Uninstall").wait(timeout = 5):
                test_result.append(t_result_list[0]) # Pass
                remark_list.append("App is successfully Installed")
                    
            elif d(text = "Open").exists:
                test_result.append(t_result_list[2]) # NT/NA
                remark_list.append("App needs to be verified again")
                                
            elif d(text = "Play").exists:
                test_result.append(t_result_list[2]) # NT/NA
                remark_list.append("App needs to be verified again")
        else:
            test_result.append(t_result_list[1]) # Fail
            remark_list.append("App is failed to install")
    
    def is_app_already_installed():
        #no_cancel = not d(text = "Cancel").exists
        yes_cancel = d(text = "Cancel").exists
        
        #Checking if cancel button is activated for 180 sec
        for i in range(120):
            if not yes_cancel:
                break
            time.sleep(5)

        app_check = subprocess.run([
            "adb", "-s", device, "shell", "pm", "list", "packages", package_name], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return "package:" in app_check.stdout
            
    def handle_popup():
        screen_width, screen_height = d.window_size()    
        # Popup variables
        if d.xpath("//*[contains(@text,'t now')]").exists:
            d(text = "Not now").click()
        elif d.xpath("//*[contains(@text,'When Wi')]").wait(timeout = 5):
            d(text = "OK").click()
        elif d.xpath("//*[contains(@text,'t add')]").exists:
            d.xpath("//*[contains(@text,'t add')]").click()
        elif d.xpath("//*[contains(@text,'alert') and contains(@text,'OK')]").exists:
            d(text = "OK").click()
        elif d.xpath("//*[contains(@text,'Want to see local')]").wait(timeout = 5):
            d(text = "No thanks").click()
            #3app.test.mql
        elif d.xpath("//*[contains(@text,'Complete account setup')]").wait(timeout = 5):
            d(text = "Continue").click()
            if d.xpath("//*[contains(@text,'Payment method]')]").wait(timeout = 5):
                d(text = "Skip").click()
            else:
                d.click(screen_width //2, screen_height // 8)
                subprocess.run([
                    "adb","-s",f"{device}","shell",
                    "input","keyevent","KEYCODE_HOME"
                ], check=True)
                
        else:
            # Touch and hold the Home button, then circle or tap text or images to learn more and explore.
            d.click(screen_width //2, screen_height // 8)
            subprocess.run([
                "adb","-s",f"{device}","shell",
                "input","keyevent","KEYCODE_HOME"
            ], check=True)
            
    def info_scrapper():
        try:
            app_info = app(package_name)
            per_info = permissions(package_name)
            '''
            # Sync App name
            is_appname = app_info.get('title', [])
            if pd.isna(app_name) or str(app_name).strip() == "":
                if is_appname:
                    new_appname = is_appname
                else:
                    new_appname = "Unknown"
                target_df.at[i, 'App Name'] = new_appname
            '''
            # Sync category
            is_category = app_info.get('categories', [])
            if is_category:
                if not is_category[0].get('id') is None:
                    category_id = is_category[0].get('id', 'No category ID found').strip()
            else:
                category_id = "Unknown"
            target_df.at[i, 'App Category'] = category_id
            
            per_key = list(per_info.keys())
            per_key_l = ' , '.join(per_key)
            target_df.at[i, 'Permissions'] = per_key_l
            if "Camera" in per_key_l:
                target_df.at[i, 'Is Camera'] = "O"
            else:
                target_df.at[i, 'Is Camera'] = "X"

            # Sync developer
            is_developer = app_info.get('developer', 'No developer found').strip()
            target_df.at[i, 'Developer'] = is_developer if is_developer else "Unknown"
                    
            # Sync updated date
            is_updated = app_info.get('lastUpdatedOn', 'No lastUpdatedOn found').strip()
            target_df.at[i, 'Updated Date'] = is_updated if is_updated else "Unknown"
            
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
                        target_df.at[i, 'TargetSdk'] = int(d_target['targetSdk'])
                    else:
                        target_df.at[i, 'TargetSdk'] = "No data"

                if "versionName=" in line:
                    app_version = line.split("=")[1].strip()
                    target_df.at[i, 'App Version'] = app_version
                    is_version = True
                    break
            if not is_version:
                # Sync app version
                is_version_info = app_info.get('version', 'No version found').strip()
                target_df.at[i, 'App Version'] = is_version_info if is_version_info else "Unknown"
            
        except Exception as e:
            print(e)
            target_df.at[i, 'Developer'] = "App is not found"
            target_df.at[i, 'App Category'] = "App is not found"
            target_df.at[i, 'App Version'] = "App is not found"
            target_df.at[i, 'Updated Date'] = "App is not found"
            target_df.at[i, 'TargetSdk'] = "App is not found"

    def app_launcher():
        
        if crash_flag.is_set() or test_stop_flag.is_set():
            stop_flag.set()
            return
        
        subprocess.run([
                "adb", "-s", device, "shell",
                "am start -n com.android.vending/com.android.vending.AssetBrowserActivity",
                "-a android.intent.action.VIEW",
                "-d", f"market://details?id={package_name}"
                ], check=True)
        
        if d(text = "Play").wait(timeout = 10):
            d(text = "Play").click()
            time.sleep(2)
            toggle_dark_mode(device)
            time.sleep(2)
            mw_results.append(toggle_multi_window_mode(device,package_name))
            launch_result.append(l_result_list[0]) # PASS

        elif d(text = "Open").wait(timeout = 10):
            d(text = "Open").click()
            time.sleep(2)
            toggle_dark_mode(device)
            time.sleep(2)
            mw_results.append(toggle_multi_window_mode(device,package_name))
            launch_result.append(l_result_list[0]) # PASS

        else:
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
        
        if crash_flag.is_set() or test_stop_flag.is_set():
            stop_flag.set()
            return
        
        #time.sleep(1)
        toggle_monkey_test(device,package_name)
        time.sleep(2)
        
        if crash_flag.is_set() or test_stop_flag.is_set():
            stop_flag.set()
            return
        
        if l_attempt < launch_attempt / 2:
            subprocess.run([
                "adb", "-s", device, "uninstall", package_name
                ])
            
            subprocess.run([
                "adb", "-s", device, "shell",
                "am start -n com.android.vending/com.android.vending.AssetBrowserActivity",
                "-a android.intent.action.VIEW",
                "-d", f"market://details?id={package_name}"
                ], check=True)
            
            if d(text = "Install").wait(timeout= 10):
                print(f"{app_name} is Uninstalled")
                d(text = "Install").click()
            else: 
                print(f"{app_name} is not deleted")
                    
            for i in range(120): 
                if is_app_already_installed():
                    print(f"{app_name} installed again")
                    break
                elif d(text = "Install").wait(timeout= 10):
                    d(text = "Install").click()
                else:
                    print(f"Failed to re-install {app_name}")
                time.sleep(5)
                
        time.sleep(3)
        stop_flag.set()
        
    
    # Navigate to the app page in google playstore
    for i, (package_name, app_name) in enumerate(zip(package_names, app_names)):
        
        if test_stop_flag.is_set():
            break
        
        signals.progress_signal.emit(int((i + 1) / len(package_names) * 100))
        signals.progress_text_signal.emit(i + 1, len(package_names))
        
        if skip_app_mode:
            # set 0 index
            temp_df = temp_df.reset_index(drop=True)

            if i < len(temp_df): # In case the lenth of list are not matching
                temp_package_name = temp_df.at[i, 'App ID']
                install_result = temp_df.at[i, 'Install Result']
                app_info_result = temp_df.at[i, 'App Category']
                final_result = temp_df.at[i, 'Final MW Result']
                running_result = temp_df.at[i, 'Final Running Result']

                if temp_package_name == package_name:
                    if pd.notna(install_result) and str(install_result).strip() in ("Pass", "NT/NA") and str(final_result).strip() in ("Pass", "Not supportive") and str(running_result).strip() in ("Pass", "NT/NA"):
                        if pd.isna(app_info_result) or str(app_info_result).strip() == "App is not found":
                            info_scrapper()
                            saved_columns = ['App Name','App ID','Install Result','Remarks','Running Result', 'Final Running Result', 'MW Result', 'Final MW Result', 'App Category', 'Developer', 'App Version', 'Updated Date', 'TargetSdk', 'Is Camera', 'Permissions']
                            target_df[saved_columns].to_csv(temp_csv, index=False, encoding='utf-8')
                        continue
                    
        for attempt in range(install_attempt):
            attempt += 1
            
            if not unlock_device(device):
                print("Device is off")
                break
            
            if test_stop_flag.is_set():
                break
            
            subprocess.run([
                "adb", "-s", device, "shell",
                "am start -n com.android.vending/com.android.vending.AssetBrowserActivity",
                "-a android.intent.action.VIEW",
                "-d", f"market://details?id={package_name}"
            ], check=True)
            
            if is_app_already_installed():
            
                # Verify if the app is pre-installed
                if d(text = "Update").wait(timeout = 2):
                    d(text = "Update").click()
                    
                elif d(text = "Enable").exists:
                    d(text = "Enable").click()
                    if d(text = "Update").wait(timeout = 2):
                        d(text = "Update").click()
                            
                elif d.xpath("//*[contains(@text,'Update from')]").exists:
                    d(text = "Uninstall").click()
                    if d(text = "Uninstall").exists:
                        d(text = "Uninstall").click()
                        if d(text = "Install").wait(timeout = 10):
                            d(text = "Install").click()
                else: 
                    test_result.append(t_result_list[0]) #Pass
                    remark_list.append("App has already been installed")
                    
                is_app_installed()
                
            # Verify the app's compatibility and availability  
            elif d.xpath("//*[contains(@text,'t compatible')]").exists:
                test_result.append(t_result_list[2]) # NT/NA
                remark_list.append("App is not compatible for this device")

            elif d.xpath("//*[contains(@text,'available only')]").exists:
                test_result.append(t_result_list[2]) # NT/NA
                remark_list.append("App is not available for this device")
                        
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
                d(text = "Install").click()

                if d.xpath("//*[contains(@text,'When Wi')]").wait(timeout = 5):
                    d(text = "OK").click()
                        
                is_app_installed()
                
            else:
                test_result.append(t_result_list[1]) # Fail
                remark_list.append("App is failed to install within the timeout")
            
            if test_stop_flag.is_set():
                break
            
            if not test_result:
                print(f"{app_name} installation status: {test_result[-1]}, attempt: {attempt}/{install_attempt}, {remark_list}")
                if launch_result:
                    launch_result.pop()
                launch_result.append(l_result_list[1]) # NA
                test_result.append(t_result_list[1]) # Fail
                remark_list.append("App needs to be checked again")                
                break
            
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
                            crash_flag.wait(timeout = 5)
                            test_stop_flag.wait(timeout = 5)

                        if crash_flag.is_set():
                            launch_result.append(l_result_list[2])
                            print(f"{device},{app_name} launch status: {launch_result[-1]}, attempt: {l_attempt}/{launch_attempt}")
                            mw_results.clear()
                            crash_thread.join()
                            stop_flag.clear()
                            crash_flag.clear()
                            break
                        elif test_stop_flag.is_set():
                            break

                        #attempt to reload the page and repeat the installation    
                        elif l_attempt <= launch_attempt -1:
                            print(f"{device},{app_name} launch status: {launch_result[-1]}, attempt: {l_attempt}/{launch_attempt}")
                            launch_result.pop()
                            
                        elif launch_result[-1] == l_result_list[1]:
                            if not is_app_open(package_name, device):
                                launch_result[-1] = "App is not opened"
                        else:
                            print(f"{device},{app_name} launch status: {launch_result[-1]}, attempt: {l_attempt}/{launch_attempt}")
                        stop_flag.clear()
                        crash_flag.clear()

                    if mw_results:
                        target_df.at[i,'MW Result'] = ', '.join(mw_results)
                        final_mw_result = max(set(mw_results), key=mw_results.count)
                        target_df.at[i,'Final MW Result'] = final_mw_result
                        mw_results.clear()
                    break
                
            elif attempt < install_attempt -1:
                print(f"{app_name} installation status: {test_result[-1]}, attempt: {attempt}/{install_attempt}, {remark_list}")
                handle_popup()
                test_result.pop()
                remark_list.pop()
            else:
                print(f"{app_name} installation status: {test_result[-1]}, attempt: {attempt}/{install_attempt}, {remark_list}")
                if launch_result:
                    launch_result.pop()
                launch_result.append(l_result_list[1]) # NA
                
        info_scrapper()
        if test_stop_flag.is_set():
            break
        # save the result to csv file
        if launch_result:
            target_df.at[i, 'Running Result'] = ', '.join(launch_result)
            final_running_result = max(set(launch_result), key=launch_result.count)
            target_df.at[i, 'Final Running Result'] = final_running_result
            launch_result.clear()
        if test_result:
            target_df.at[i, 'Install Result'] = test_result[-1]
            test_result.clear()
        if remark_list:
            target_df.at[i, 'Remarks'] = remark_list[-1]
            remark_list.clear()

        saved_columns = ['App Name','App ID','Install Result','Remarks','Running Result', 'Final Running Result', 'MW Result', 'Final MW Result', 'App Category', 'Developer', 'App Version', 'Updated Date', 'TargetSdk', 'Is Camera', 'Permissions']
        target_df.to_csv(temp_csv, index=False, encoding='utf-8')
        total_count += 1
    final_csv = os.path.join(base_dir, f'Test_result_{serial}.csv')
    target_df.to_csv(final_csv, index=False, encoding='utf-8')
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

class SignalEmitter(QObject):
    progress_signal = pyqtSignal(int) 
    progress_text_signal = pyqtSignal(int, int)
    show_error_signal = pyqtSignal(str)
    show_info_signal = pyqtSignal(str)
    
class AppTesterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.test_stop_flag = threading.Event() # Stop testing
        self.signals.show_error_signal.connect(self.show_error)
        self.signals.show_info_signal.connect(self.show_info)
        
    def update_progress_text(self, current, total):
        progress_percent = int((current / total) * 100)
        self.progress_label.setText(f"{current} / {total} Apps, ({progress_percent}% processing)")

    def initUI(self):
        layout = QHBoxLayout()  # Main layout (horizontal)
        
        self.signals = SignalEmitter()

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
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        left_layout.addWidget(self.progress_bar)
        
        # Progress Label
        self.progress_label = QLabel("0 / 0")
        left_layout.addWidget(self.progress_label)

        self.signals.progress_text_signal.connect(self.update_progress_text)
        self.signals.progress_signal.connect(self.progress_bar.setValue)
        
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
        
        self.device_map = {}
        self.package_names = []
        self.app_names = []
        self.df = None
        
    def show_info(self, message):
        QMessageBox.information(self, "Info", message)
                
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def connect_devices(self):
        try:
            self.device_map = connect_devices()
            self.device_label.setText(f"Connected Devices: {', '.join(self.device_map.values())}")
        except Exception as e:
            self.show_error(str(e))
            
    def load_csv(self):
        try:
            base_dir = get_app_base_dir()
            self.automation_file_path = os.path.join(base_dir, "test1.csv")
            self.search_file_path = None
            self.resume_file_path = None

            self.package_names, self.app_names, self.df, _ = process_csv(self.automation_file_path)
            self.log_output.append(f"Loaded CSV file - {self.automation_file_path}")
            self.display_data(self.tableWidget)
        except Exception as e:
            self.show_error(str(e))

    def custom_csv(self): 
        try:
            # Open a file selection dialog to upload a CSV file
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.ExistingFile)
            file_path, _ = QFileDialog.getOpenFileName(self, "Upload CSV", get_app_base_dir(), "CSV Files (*.csv)")

            if not file_path:
                self.signals.show_error_signal.emit("Please select a CSV file to proceed.")
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
                
            base_dir = get_app_base_dir()
            self.search_file_path = os.path.join(base_dir, f'app_search_{self.keyword}_result.csv')
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
            self.signals.show_error_signal.emit("No file loaded. Please load a CSV file first.")
            return

        # Prioritize the most recent loaded CSV file
        base_dir = get_app_base_dir()
        file_path = self.automation_file_path if self.automation_file_path else self.search_file_path

        if not file_path:
            self.signals.show_error_signal.emit("No file loaded. Please load a CSV file first.")
            return
        
        if not os.path.isabs(file_path):
            file_path = os.path.join(base_dir, file_path)

        # Extract data from table widget
        updated_data = []
        for row in range(self.tableWidget.rowCount()):
            row_data = [self.tableWidget.item(row, col).text() if self.tableWidget.item(row, col) else ''
                        for col in range(self.tableWidget.columnCount())]
            updated_data.append(row_data)

        updated_df = pd.DataFrame(updated_data, columns=self.df.columns)
        updated_df.to_csv(file_path, index=False)
        self.signals.show_info_signal.emit(f"CSV file saved successfully to {file_path}")

    def save_as_csv(self):
        """Prompt for renaming every time and save the updated data."""
        if self.df is None:
            self.signals.show_error_signal.emit("No file loaded. Please load a CSV file first.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File As", get_app_base_dir(), "CSV Files (*.csv);;All Files (*)"
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
            self.signals.show_info_signal.emit(f"CSV file saved successfully as:\n{file_path}")

            self.file_path = file_path

    def start_testing(self):
        try:
            self.test_stop_flag.clear()
            
            if not self.device_map:
                self.log_output.append("Error: Devices not connected")
                return
            
            elif not self.package_names:
                self.log_output.append("Error: CSV not loaded.")
                return
            
            install_attempt = self.install_attempt_input.value()
            launch_attempt = self.launch_attempt_input.value()
            
            self.log_output.append("Starting tests...")
            
            self.stop_button.setEnabled(True)
            self.start_all_button.setEnabled(False)
            self.start_button.setEnabled(False)
            self.search_button.setEnabled(False)
            self.load_search_data.setEnabled(False)
            self.load_csv_button.setEnabled(False)
            self.custom_csv_button.setEnabled(False)
            
            def run_tests():
                for device in self.device_map:
                    serial = self.device_map[device]
                    self.log_output.append(f"Processing device {serial}...")
                    test_app_install (device, self.package_names, self.app_names, self.df, install_attempt, launch_attempt, serial, self.signals, self.test_stop_flag)
                self.log_output.append("Testing completed.")
                self.stop_button.setEnabled(False)
                self.start_all_button.setEnabled(True)
                self.start_button.setEnabled(True)
                self.search_button.setEnabled(True)
                self.load_search_data.setEnabled(True)
                self.load_csv_button.setEnabled(True)
                self.custom_csv_button.setEnabled(True)
                self.signals.show_info_signal.emit("Testing has been completed.")
            
            threading.Thread(target=run_tests, daemon=True).start()
            
        except Exception as e:
            self.show_error(str(e))

    def start_testing_all(self):
        try:
            self.test_stop_flag.clear()
            if not self.device_map:
                self.log_output.append("Error: Devices not connected")
                return
                
            elif not self.package_names:
                self.log_output.append("Error: CSV not loaded.")
                return
            
            install_attempt = self.install_attempt_input.value()
            launch_attempt = self.launch_attempt_input.value()
            
            self.log_output.append("Starting tests...")
            
            self.stop_button.setEnabled(True)
            self.start_all_button.setEnabled(False)
            self.start_button.setEnabled(False)
            self.search_button.setEnabled(False)
            self.load_search_data.setEnabled(False)
            self.load_csv_button.setEnabled(False)
            self.custom_csv_button.setEnabled(False)
            
            def run_tests_for_device(device, serial):
                self.log_output.append(f"Processing device {serial}...")
                local_df = self.df.copy()
                test_app_install(device, self.package_names, self.app_names, local_df, install_attempt, launch_attempt, serial, self.signals, self.test_stop_flag)

            def run_all_tests():
                threads = []
                for device in self.device_map:
                    serial = self.device_map[device]
                    t = threading.Thread(target=run_tests_for_device, args=(device,serial), daemon=True)
                    threads.append(t)
                    t.start()

                for t in threads:
                    t.join()

                self.log_output.append("Testing completed.")
                self.stop_button.setEnabled(False)
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
            self.test_stop_flag.set()
            self.stop_button.setEnabled(False)
            self.signals.show_info_signal.emit("Stopping the test... Please wait.")
        except Exception as e:
            self.show_error(str(e))

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    ex = AppTesterGUI()
    ex.show()
    print("App Tester is started. Please check the opened window.")
    sys.exit(qt_app.exec_())