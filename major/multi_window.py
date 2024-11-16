import subprocess
import uiautomator2 as u2
import time

def toggle_multi_window_mode():
    d = u2.connect()
    start_time = time.time()
    
    # initialize the screen size & duration
    screen_width, screen_height = d.window_size()
    center_x, center_y = screen_width //2 , screen_height // 2
    duration_time = 20
    
    for _ in range(3):
        # click recents button
        subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_APP_SWITCH'
                        ],check=True)
        
        time.sleep(2)
        
        d.long_click(screen_width -1, center_y, duration = 3)
        toast_text = d.toast.get_message(5.0, 5.0)
        if toast_text and "t use this app in Multi" in toast_text:
            print ("MW is not supportive for this app")
            break   
        elif d.xpath("//*[contains(@text,'Select app')]").exists:
            print ("MW tested")
            break
        else:
            print("nothing happend")
        # click home button
        subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_HOME'
                        ],check=True)
        time.sleep(1)
        subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_APP_SWITCH'
                        ],check=True)
        time.sleep(2)
        d.click(center_x, center_y)
        time.sleep(2)