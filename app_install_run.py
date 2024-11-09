from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from basic.test_app_install import test_app_install
from basic.test_app_run import test_app_run
from basic.connect_devices import connect_devices
from basic.csv_handler import process_csv


def execute_command(): # source code from Hyeonjun An.
    lock = Lock()
    device_list = connect_devices()
    package_names, app_names, df, sf, csv_file = process_csv()

    try:
        with ThreadPoolExecutor() as executor:
            for device in device_list:
                print(f"Device {device} is processing...")
                lock.acquire()
                executor.submit( 
                    test_app_install(device, package_names, app_names, df, csv_file), device)
                #executor.submit( 
                    #test_app_run(device, package_names, app_names, df), device)
                lock.release()
    except Exception as e:
        print(e)
                
# Log for the installation fails

if __name__ == "__main__":
    execute_command()