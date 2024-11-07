# monkey? - Todo
# adb shell monkey -p your.app.package.name -c android.intent.category.LAUNCHER 1

import subprocess
import time
import uiautomator2 as u2
import re

def test_app_run(device, package_names, app_names):
    try:
        for package_name, app_name in zip(package_names, app_names):
            subprocess.run([
                "adb", "-s", f"{device}", "shell",
                "am start -n com.android.vending/com.android.vending.AssetBrowserActivity",
                "-a android.intent.action.VIEW",
                "-d", f"market://details?id={package_name}"
            ], check=True)

            d = u2.connect(device)
            
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
    
    
'''
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

                        #category
                        category = re.findall(r'android.intent.category\.(\w+)', app_output)
                        if category:
                            print(f"Category: {category}")
                    
                
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
            
        df['App Version'] = app_version
        
'''