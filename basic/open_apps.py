# monkey? - Todo
# adb shell monkey -p your.app.package.name -c android.intent.category.LAUNCHER 1


def open_apps():
    if d(text = "Uninstall").exists:
        if d(text = "Play").exists:
            d(text = "Play").click()
        elif d(text = "Open").exists:
            d(text = "Open").click()
        else: 
            print(f"[Fail] {app_name} Failed to open")
        time.sleep(3)

    print("App is Opened")