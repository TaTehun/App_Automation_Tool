from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from basic.test_apps import test_installation
from basic.connect_devices import connect_devices
from basic.unlock_device import unlock_device
from basic.csv_handler import process_csv


def execute_command(): # source code from Hyeonjun An.
    lock = Lock()
    devices = connect_devices()
    package_names, app_names, df = process_csv()

    try:
        with ThreadPoolExecutor() as executor:
            for device in devices:
                print(f"Device {device} is processing...")
                unlock_device(device)
                lock.acquire()
                executor.submit( 
                                test_installation(device, package_names, app_names, df), 
                                device)
                lock.release()
    except Exception as e:
        print(e)
                
# Log for the installation fails

if __name__ == "__main__":
    execute_command()