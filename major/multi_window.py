import subprocess
import uiautomator2 as u2
import time

def toggle_multi_window_mode(device):
    d = u2.connect(device)
    
    # initialize the screen size & duration
    screen_width, screen_height = d.window_size()
    center_x, center_y = screen_width //2 , screen_height // 2
    
    # click recents button
    subprocess.run(['adb', "-s", f"{device}", 'shell', 'input', 'keyevent', 'KEYCODE_APP_SWITCH'
                    ],check=True)
        
    time.sleep(2)
        
    d.long_click(screen_width -1, center_y, duration = 3)
    toast_text = d.toast.get_message(5.0, 5.0)
    if toast_text and "t use this app in Multi" in toast_text:
        mw_result = "Not supportive"
    elif d.xpath("//*[contains(@text,'Select app')]").exists:
        mw_result = "Pass"
    else:
        mw_result = "Fail"
    # click home button
    subprocess.run(['adb', "-s", f"{device}", 'shell', 'input', 'keyevent', 'KEYCODE_HOME'
                    ],check=True)
    time.sleep(1)
    subprocess.run(['adb', "-s", f"{device}", 'shell', 'input', 'keyevent', 'KEYCODE_APP_SWITCH'
                    ],check=True)
    time.sleep(2)
    d.click(center_x, center_y)
    time.sleep(2)
    
    return mw_result