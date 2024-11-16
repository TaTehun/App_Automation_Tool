# monkey? - Todo
# adb shell monkey -p your.app.package.name -c android.intent.category.LAUNCHER 1

import subprocess
import time
import uiautomator2 as u2
import re
from major.theme_dark import toggle_dark_mode
from major.multi_window import toggle_multi_window_mode

def test_app_run(device, package_names, app_names, df):
        d = u2.connect(device)
        
        for package_name, app_name in zip(package_names, app_names):
            for _ in range(3):
                subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_HOME'
                            ],check=True)
                subprocess.run([
                    "adb", "-s", f"{device}", "shell",
                    "am start -n com.android.vending/com.android.vending.AssetBrowserActivity",
                    "-a android.intent.action.VIEW",
                    "-d", f"market://details?id={package_name}"
                ], check=True)
                
                # Open the app
                if d(text = "Uninstall").exists:
                    if d(text = "Play").exists:
                        d(text = "Play").click()
                        time.sleep(2)
                        toggle_dark_mode()
                        time.sleep(2)
                        toggle_multi_window_mode()
                    elif d(text = "Open").exists:
                        d(text = "Open").click()
                        time.sleep(2)
                        toggle_dark_mode()
                        time.sleep(2)
                        toggle_multi_window_mode()
                    else: 
                        print(f"[Fail] {app_name} Failed to open")
                    time.sleep(3)
                print("App is Opened")
            

    
    # df['Result'] = test_result
    # df.to_csv('123tj_result.csv', index=False)