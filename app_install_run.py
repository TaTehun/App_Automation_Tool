from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from basic.app_crash_detector import app_crash_detector
from basic.test_app_install import test_app_install
from basic.test_app_run import test_app_run
from basic.connect_devices import connect_devices
from basic.csv_handler import process_csv
import time

'''
class AppTester:
    def __init__(self, device_list, package_names, app_names, csv_file):
        self.device_list = device_list
        self.package_names = package_names
        self.app_names = app_names
        self.csv_file = csv_file
        package_names, app_names, csv_file = process_csv
'''        

def execute_command(): 
    lock = Lock()
    device_list = connect_devices()
    package_names, app_names, df, sf, csv_file = process_csv()

    try:
        with ThreadPoolExecutor() as executor: # source code from Hyeonjun An.
            for device in device_list:
                print(f"Device {device} is processing...")
                crash_flag, crash_log = app_crash_detector(device)

                lock.acquire()
                #executor.submit( 
                    #test_app_install(device, package_names, app_names, df, csv_file, crash_flag, crash_log), device)
                #time.sleep(10)
                executor.submit( 
                    test_app_run(device, package_names, app_names, df, crash_flag, crash_log), device)
                lock.release()
    except Exception as e:
        print(e)
                
# Log for the installation fails

if __name__ == "__main__":
    execute_command()