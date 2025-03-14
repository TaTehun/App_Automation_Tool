import sys
import os
import threading
import subprocess
import uiautomator2 as u2
import time
import pandas as pd
import os
import platform
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QSpinBox, QMessageBox
)
from threading import Lock, Event
from google_play_scraper import app

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
                break
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
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def connect_devices(): # source code from Hyeonjun An.
    # Get connected devices
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True)
    lines = result.stdout.split('\n')[1:]  # Skip the first line which is a header
    device_list = [line.split('\t')[0] for line in lines if '\tdevice' in line]

    return device_list

def process_csv():
    csv_file = os.path.abspath('test1.csv')
    
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
        print("dark mode!")
    else:
        # Disabling dark mode
        subprocess.run(['adb', "-s", f"{device}", 'shell', 'cmd', 'uimode', 'night', 'no'
                    ],capture_output=True, text=True, check=True)
        time.sleep(1)
        print("Light mode!")
        
def toggle_multi_window_mode(device):
    d = u2.connect(device)
    
    # initialize the screen size & duration
    screen_width, screen_height = d.window_size()
    center_x, center_y = screen_width //2 , screen_height // 2
    
    # click recents button
    subprocess.run(['adb', "-s", f"{device}", 'shell', 'input', 'keyevent', 'KEYCODE_APP_SWITCH'
                    ],check=True)
        
    time.sleep(2)
        
    d.long_click(screen_width -1, center_y, duration = 3)
    toast_text = d.toast.get_message(5.0, 5.0)
    if d.xpath("//*[contains(@text,'Select app')]").wait(2):
        time.sleep(5)
        mw_result = "Pass"
    elif toast_text and "t use this app in Multi" in toast_text:
        mw_result = "Not supportive"
    else:
        mw_result = "Fail"
    # click home button
    subprocess.run(['adb', "-s", f"{device}", 'shell', 'input', 'keyevent', 'KEYCODE_HOME'
                    ],check=True)
    time.sleep(1)
    subprocess.run(['adb', "-s", f"{device}", 'shell', 'input', 'keyevent', 'KEYCODE_APP_SWITCH'
                    ],check=True)
    time.sleep(2)
    d.click(center_x, center_y)
    time.sleep(2)
    
    return mw_result
'''
def toggle_monkey_test(device, package_name):
    event_count = 3000
    result = subprocess.run([
        'adb', "-s", device, 'shell', 'monkey','-p',package_name, '--pct-touch 50', '--pct-motion 50', '-v', str(event_count)
                ],capture_output=True, text=True) 
    print(result.stdout)
    print(result.stderr)
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
        
    d = u2.connect(device)
    total_count, attempt, l_attempt = 0, 0, 0
    remark_list, test_result, mw_results, launch_result = [], [], [], []
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
    if 'MW_Result' not in df.columns:
        df['MW_Result'] = ""
    if 'Final_MW_Result' not in df.columns:
        df['Final_MW_Result'] = ""

    def is_app_installed():
        #no_cancel = not d(text = "Cancel").exists
        yes_cancel = d(text = "Cancel").exists
        timeout = 180
        timeout_start = time.time()
        
        #Checking if cancel button is activated for 180 sec
        while time.time() - timeout_start < timeout:
            if yes_cancel:
                pass
            else:
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
        if d(text = "Play").wait(timeout = 5):
            d(text = "Play").click(10)
            time.sleep(2)
            if is_app_open(package_name, device):
                toggle_dark_mode(device)
                time.sleep(2)
                mw_results.append(toggle_multi_window_mode(device))
                #toggle_monkey_test(device,package_name)
                launch_result.append(l_result_list[0]) # PASS
                print("test done")
            else:
                print("app is not opened")
                launch_result.append(l_result_list[1]) # NA

        elif d(text = "Open").wait(timeout = 5):
            d(text = "Open").click(10)
            time.sleep(2)
            if is_app_open(package_name, device):
                toggle_dark_mode(device)
                time.sleep(2)
                mw_results.append(toggle_multi_window_mode(device))
                #toggle_monkey_test(device,package_name)
                launch_result.append(l_result_list[0]) # PASS
                print ("test done")
            else:
                print("app is not opened")
                launch_result.append(l_result_list[1]) # NA
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
                        app_launcher()
                #attempt to reload the page and repeat the installation
                    if launch_result[-1] == l_result_list[2]:
                        print(f"{app_name} launch status: {launch_result[-1]}, attempt: {l_attempt}/{launch_attempt}")
                        break               
                    elif l_attempt <= launch_attempt -1:  
                        print(f"{app_name} launch status: {launch_result[-1]}, attempt: {l_attempt}/{launch_attempt}")
                        launch_result.pop()
                    else:
                        print(f"{app_name} launch status: {launch_result[-1]}, attempt: {l_attempt}/{launch_attempt}")

                if mw_results:
                    df.at[i,'MW_Result'] = ', '.join(mw_results)
                    final_mw_result = max(set(mw_results), key=mw_results.count)
                    df.at[i,'Final_MW_Result'] = final_mw_result
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
        df.at[i, 'Running Result'] = launch_result[-1]
        df.at[i, 'Install Result'] = test_result[-1]
        df.at[i, 'Remarks'] = remark_list[-1]
        install_result_df = df[['App Name','App ID','Install Result', 'Remarks', 'App Category', 'Developer', 'App Version', 'Updated Date', 'TargetSdk']]
        launch_result_df = df[['App Name','App ID','Running Result', 'MW_Result', 'Final_MW_Result']]
        launch_result_df.to_csv(f'launch_result_{device}.csv', index=False)
        install_result_df.to_csv(f'Install_result_{device}.csv', index=False)
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
        layout = QVBoxLayout()

        self.device_label = QLabel("Connected Devices: None")
        layout.addWidget(self.device_label)

        self.connect_button = QPushButton("Connect Devices")
        self.connect_button.clicked.connect(self.connect_devices)
        layout.addWidget(self.connect_button)

        self.load_csv_button = QPushButton("Load CSV File")
        self.load_csv_button.clicked.connect(self.load_csv)
        layout.addWidget(self.load_csv_button)

        self.install_attempt_label = QLabel("Installation Attempts:")
        layout.addWidget(self.install_attempt_label)

        self.install_attempt_input = QSpinBox()
        self.install_attempt_input.setMinimum(1)
        self.install_attempt_input.setMaximum(50)
        self.install_attempt_input.setValue(3)
        layout.addWidget(self.install_attempt_input)
        
        self.launch_attempt_label = QLabel("Launch test Attempts:")
        layout.addWidget(self.launch_attempt_label)
        
        self.launch_attempt_input = QSpinBox()
        self.launch_attempt_input.setMinimum(0)
        self.launch_attempt_input.setMaximum(50)
        self.launch_attempt_input.setValue(3)
        layout.addWidget(self.launch_attempt_input)
        
        self.start_button = QPushButton("Start Testing")
        self.start_button.clicked.connect(self.start_testing)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Testing")
        self.stop_button.clicked.connect(self.stop_testing)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        
        self.setLayout(layout)
        self.setWindowTitle("App Installation Tester")
        self.setGeometry(300, 300, 500, 400)
        
        self.device_list = []
        self.package_names = []
        self.app_names = []
        self.df = None
        self.stop_testing_event = Event()
        
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
            self.package_names, self.app_names, self.df, _ = process_csv()
            self.log_output.append("Loaded default CSV file: test1.csv")
        except Exception as e:
            self.show_error(str(e))
    def start_testing(self):
        try:
            if not self.device_list or not self.package_names:
                self.log_output.append("Error: Devices not connected or CSV not loaded.")
                return
            
            install_attempt = self.install_attempt_input.value()
            launch_attempt = self.launch_attempt_input.value()
            self.stop_testing_event.clear()
            
            self.log_output.append("Starting tests...")
            
            self.stop_button.setEnabled(True)
            self.start_button.setEnabled(False)
            
            def run_tests():
                for device in self.device_list:
                    self.log_output.append(f"Processing device {device}...")
                    test_app_install (device, self.package_names, self.app_names, self.df, install_attempt, launch_attempt)
                self.log_output.append("Testing completed.")
                self.stop_button.setEnabled(False)
                self.start_button.setEnabled(True)
            
            threading.Thread(target=run_tests, daemon=True).start()
        except Exception as e:
            self.show_error(str(e))

    def stop_testing(self):
        try:
            os._exit(0)
            #self.log_output.append("Testing stopped by user.")
            self.stop_button.setEnabled(False)
            self.start_button.setEnabled(True)
        except Exception as e:
            self.show_error(str(e))

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    ex = AppTesterGUI()
    ex.show()
    sys.exit(qt_app.exec_())
