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
    
    df = pd.read_csv('App_List_US_1.csv')
    
    # convert all column names to lowercase
    # df.columns = df.columns.str.lower()
    
    package_names = df['App ID'].tolist()
    
    return package_names


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
    

def test_installation(device, package_names):
    try:
        # call process_csv for the package_name - Todo 
        
        
            
        # Navigate to the app page in google playstore
        for package_name in package_names:
            subprocess.run([
                "adb", "-s", f"{device}", "shell",
                "am start -n com.android.vending/com.android.vending.AssetBrowserActivity",
                "-a android.intent.action.VIEW",
                "-d", f"market://details?id={package_name}"
            ], check=True)
        
            # Click install button
            d = u2.connect(device)

            if d(text = "Install" or "Update").wait(timeout = 10.0):
                d(text = "Install" or "Update").click()
                d(text = "cancel").exists(timeout=10)
                d(text = "Uninstall").exists(timeout= 10.0)
                print(f"app {package_name} has been installed")
                    
            elif d(text = "Uninstall").exists(timeout=10):
                print(f"app {package_name} has been installed")
            else:
                print("Install button is not found")
                    
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
    package_names = process_csv()

    try:
        with ThreadPoolExecutor() as executor:
            for device in devices:
                lock.acquire()
                unlock_device(device)
                executor.submit( 
                                test_installation(device, package_names), 
                                device)
                
                lock.release()
    except Exception as e:
        print(e)
                
# Log for the installation fails

if __name__ == "__main__":
    execute_command()
    
    