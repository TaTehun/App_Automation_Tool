from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from basic.app_crash_detector import app_crash_detector
from basic.test_app_install import test_app_install
from basic.test_app_run import test_app_run
from basic.connect_devices import connect_devices
from basic.csv_handler import process_csv
import time

def attempts():
    install_attempt = int(input("Enter the number of times to repeat the app installation test: "))
    launch_attempt = int(input("Enter the number of times to repeat the mw test: "))
    
    return install_attempt, launch_attempt

def execute_command(): 
    lock = Lock()
    device_list = connect_devices()
    package_names, app_names, df, sf, csv_file = process_csv()
    install_attempt, launch_attempt = attempts()

    try:
        with ThreadPoolExecutor() as executor: # source code from Hyeonjun An.
            for device in device_list:
                print(f"Device {device} is processing...")
                
                crash_flag, crash_log = app_crash_detector(device, package_names)                    
                lock.acquire()
                
                #executor.submit(
                #test_app_install(device, package_names, app_names, df, install_attempt), device)
            
                #time.sleep(1)
                executor.submit( 
                    test_app_run(device, package_names, app_names, df, crash_flag, crash_log,launch_attempt), device)
                lock.release()
    except Exception as e:
        print(e)
                
# Log for the installation fails

if __name__ == "__main__":
    execute_command()