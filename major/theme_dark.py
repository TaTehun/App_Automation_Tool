# Switch the DUT to dark mode and light mode
# -- adb shell cmd uimode night yes , adb shell cmd uimode night no
            # Turn darkmode on and off    
            d.app_start("com.android.settings")
            time.sleep(2)
            d(text="Display").click()
            time.sleep(2)
            dark_mode_toggle = d(text = "Dark Theme")
            if dark_mode_toggle.exists:
                if enable:    
            