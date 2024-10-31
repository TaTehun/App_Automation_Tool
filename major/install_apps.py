import subprocess
import time
import uiautomator2 as u2
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from threading import Lock 

def connect_devices():
    # Get connected devices
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True)
    lines = result.stdout.split('\n')[1:]  # Skip the first line which is a header
    device_list = [line.split('\t')[0] for line in lines if '\tdevice' in line]

    return device_list
        
def process_csv():
    
    df = pd.read_csv('App_List_US.csv', encoding='unicode_escape')
    
    # convert all column names to lowercase
    # df.columns = df.columns.str.lower()
    
    package_names = df['App ID'].tolist()
    app_names = df['App Name'].tolist()
    
    return package_names, app_names


def unlock_device(device):
    
    try:
        # call process_csv for the package_name - Todo 

        # Waking up and unlock the devices
        subprocess.run([
            "adb","-s",f"{device}","shell",
            "input","keyevent","224"
        ], check=True)
        
        time.sleep(1)
            
        subprocess.run([
            "adb","-s",f"{device}","shell",
            "input","keyevent","82"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    

def test_installation(device, package_names, app_names):
    try:
        # call process_csv for the package_name - Todo 
        
        
            
        # Navigate to the app page in google playstore
        for package_name,app_name in package_names, app_names:
            subprocess.run([
                "adb", "-s", f"{device}", "shell",
                "am start -n com.android.vending/com.android.vending.AssetBrowserActivity",
                "-a android.intent.action.VIEW",
                "-d", f"market://details?id={package_name}"
            ], check=True)
        
            # Click install button
            d = u2.connect(device)
            start_time = time.time()
            time_out = 5000
            
            if d(text = "Uninstall").exists(timeout = 10):
                if d(text = "Update").wait(timeout = 10):
                    d(text = "Update").click()
                    print(f"[Pass] app {app_name} has been Updated")
                else: print(f"[Pass] app {app_name} has been installed")
                
            elif d.xpath("//*[contains(@text,'t compatible') or contains(@text,'t available') or contains(@text,'t found')]").exists:
                print("[NT/NA] App is not available or compatible for this device")
            
            elif d.xpath("//*[contains(@text,'usd')]").exists:
                print("[NT/NA] Paid App")
            
            elif d(text = "Install").wait(timeout = 10):
                d(text = "Install").click()
                while time.time() - start_time < time_out:
                    if d(text = "Uninstall").exists(timeout= 10):
                        print(f"[Pass] app {app_name} has been installed")
            else:
                print("[Fail] Install button is not found")
                    
                # Click open button
    #            if d(text = "Open").wait(timeout = 10.0):
    #                d(text = "Open").click()
    #            else:
    #                print("Open button is not found")
                
            
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        

def execute_command(): 
    lock = Lock()
    devices = connect_devices()
    package_names, app_names = process_csv()

    try:
        with ThreadPoolExecutor() as executor:
            for device in devices:
                lock.acquire()
                unlock_device(device)
                executor.submit( 
                                test_installation(device, package_names, app_names), 
                                device)
                
                lock.release()
    except Exception as e:
        print(e)
                
# Log for the installation fails

if __name__ == "__main__":
    execute_command()
    
    