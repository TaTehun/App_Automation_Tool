# monkey? - Todo
# adb shell monkey -p your.app.package.name -c android.intent.category.LAUNCHER 1

import subprocess
import time
import uiautomator2 as u2
import re

def test_app_run(device, package_names, app_names, df):
    try:
        d = u2.connect(device)
        
        for package_name, app_name in zip(package_names, app_names):
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
                elif d(text = "Open").exists:
                    d(text = "Open").click()
                else: 
                    print(f"[Fail] {app_name} Failed to open")
                time.sleep(3)
            print("App is Opened")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        
    
    # df['Result'] = test_result
    # df.to_csv('123tj_result.csv', index=False)