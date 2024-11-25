import subprocess
import uiautomator2 as u2
import pandas as pd
from basic.unlock_device import unlock_device


class AutoAppInstaller:
    def __init__(self, device, package_names, app_names, csv_file):
        self.device = device
        self.package_names = package_names
        self.app_names = app_names
        self.csv_file = csv_file
        self.df = pd.read_csv(csv_file)
        self.d = u2.connect(device)

        # Initialize result columns
        if 'Result' not in self.df.columns:
            self.df['Result'] = ""
        else:
            self.df['Result'] = ""
        if 'Remarks' not in self.df.columns:
            self.df['Remarks'] = ""
        else:
            self.df['Remarks'] = ""

    def unlock_and_open_playstore(self, package_name):
        unlock_device(self.device)
        subprocess.run(
            [
                "adb", "-s", self.device, "shell",
                "am start -n com.android.vending/com.android.vending.AssetBrowserActivity",
                "-a android.intent.action.VIEW",
                "-d", f"market://details?id={package_name}"
            ],
            check=True
        )

    def handle_popups(self):
        if self.d.xpath("//*[contains(@text,'t now')]").exists:
            self.d(text="Not now").click()
        elif self.d.xpath("//*[contains(@text,'t add')]").exists:
            self.d.xpath("//*[contains(@text,'t add')]").click()
        elif self.d.xpath("//*[contains(@text,'alert') and contains(@text,'OK')]").exists:
            self.d(text="OK").click()
        elif self.d.xpath("//*[contains(@text,'Want to see local')]").wait(timeout=5):
            self.d(text="No thanks").click()

    def install_app(self, package_name, app_name):
        remark_list = []
        test_result = []
        t_result_list = ["Pass", "Fail", "NT/NA"]
        attempt = 0

        for attempt in range(3):  # Retry installation up to 3 times
            attempt += 1
            self.unlock_and_open_playstore(package_name)
            self.handle_popups()

            # Verify if app is pre-installed or needs an update
            if self.d(text="Uninstall").wait(timeout=15):
                if self.d(text="Update").exists:
                    self.d(text="Update").click()
                    if self.d.xpath("//*[contains(@text,'When Wi')]").wait(timeout=5):
                        self.d(text="OK").click()
                    if self.d(text="Uninstall").wait(timeout=180):
                        return "Pass", "App successfully installed"
                else:
                    return "Pass", "App already installed"
            elif self.d.xpath("//*[contains(@text,'t compatible')]").exists:
                return "NT/NA", "App not compatible for this device"
            elif self.d.xpath("//*[contains(@text,'t available')]").exists:
                return "NT/NA", "App not available for this device"
            elif self.d.xpath("//*[contains(@text,'t found')]").exists:
                return "NT/NA", "App not found"
            elif self.d.xpath("//*[contains(@text,'re offline')]").exists:
                return "NT/NA", "Internet not connected"
            elif self.d(text="Install").exists and not self.d(text="Open").exists:
                self.d(text="Install").click()
                if self.d(text="Uninstall").wait(timeout=180):
                    return "Pass", "App successfully installed"
                else:
                    return "Fail", "App failed to install within timeout"

            # Retry on failure
            if attempt < 3:
                continue

        return "Fail", "App installation failed after 3 attempts"

    def test_apps(self):
        p_count, f_count, na_count, total_count = 0, 0, 0, 0

        for i, (package_name, app_name) in enumerate(zip(self.package_names, self.app_names)):
            total_count += 1
            result, remark = self.install_app(package_name, app_name)

            # Update results
            self.df.at[i, 'Result'] = result
            self.df.at[i, 'Remarks'] = remark

            if result == "Pass":
                p_count += 1
            elif result == "Fail":
                f_count += 1
            else:
                na_count += 1

            print(f"{app_name} installation status: {result}, remark: {remark}")

        # Save results to CSV
        self.df.to_csv(f'result_{self.device}.csv', index=False)
        print(f"Total {total_count} app tests completed: {p_count} Pass, {f_count} Fail, {na_count} NT/NA.")

    def filter_passed_apps(self):
        result_df = pd.read_csv(f'result_{self.device}.csv')
        result_df['Result'] = result_df['Result'].astype(str)
        pass_df = result_df[result_df['Result'] == 'Pass']
        pass_df.to_csv(f'pass_{self.device}_result.csv', index=False)


# Example usage:
if __name__ == "__main__":
    device = "device_serial"
    package_names = ["com.example.app1", "com.example.app2"]
    app_names = ["Example App 1", "Example App 2"]
    csv_file = "apps.csv"

    installer = AutoAppInstaller(device, package_names, app_names, csv_file)
    installer.test_apps()
    installer.filter_passed_apps()
