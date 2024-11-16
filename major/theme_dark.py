import subprocess


# Function to enable or disable dark mode
def toggle_dark_mode():
    is_dark_mode = subprocess.run(['adb', 'shell', 'cmd', 'uimode', 'night'
                                ],capture_output=True, text=True, check=True)
    current_status = is_dark_mode.stdout.strip()
    for _ in range(3):
        if current_status == "Night mode: no":
            # Enabling dark mode
            subprocess.run(['adb', 'shell', 'cmd', 'uimode', 'night', 'yes'
                        ],capture_output=True, text=True, check=True)
        else:
            # Disabling dark mode
            subprocess.run(['adb', 'shell', 'cmd', 'uimode', 'night', 'no'
                        ],capture_output=True, text=True, check=True)


            

    
    
    '''
        while time.time() - start_time < duration_time:
        press_recents
        
        time.sleep(2)
        
        d.long_click(screen_width -1, center_y, duration = 3)
        if d.xpath("//*[contains(@text,'t use this')]").exists:
            print ("MW is not supportive for this app")
            break   
        elif d.xpath("//*[contains(@text,'Drop here')]").exists:
            print ("MW tested")
            break
        else:
            press_home
            time.sleep(1)
            press_recents
            time.sleep(1)
            press_recents
            time.sleep(1)
    '''