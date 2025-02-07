import subprocess
from google_play_scraper import app, search
from basic.csv_handler import process_csv
from basic.connect_devices import connect_devices

def info_sync():
    try:
        # Connect to devices
        device_list = connect_devices()

        # Initialize columns
        if 'App Category' not in df.columns:
            df['App Category'] = ""
        if 'Developer' not in df.columns:
            df['Developer'] = ""
        if 'App Version' not in df.columns:
            df['App Version'] = ""
        if 'Updated Date' not in df.columns:
            df['Updated Date'] = ""
        if 'TargetSdk' not in df.columns:
            df['TargetSdk'] = ""
            
        df['App Category'] = df.get('App Category', '').astype(str)
        df['Developer'] = df.get('Developer', '').astype(str)
        df['App Version'] = df.get('App Version', '').astype(str)
        df['Updated Date'] = df.get('App Version', '').astype(str)
        df['TargetSdk'] = df.get('TargetSdk', '').astype(str)
        
        for i, package_name in enumerate(package_names):
            try:
                # Fetch app details for the current package name
                app_info = app(package_name)
                    
                # Sync category
                is_category = app_info.get('categories', [])
                if is_category:
                    if not is_category[0].get('id') is None:
                        category_id = is_category[0].get('id', 'No category ID found').strip()
                else:
                    category_id = "Unknown"

                df.at[i, 'App Category'] = category_id

                # Sync developer
                is_developer = app_info.get('developer', 'No developer found').strip()
                
                df.at[i, 'Developer'] = is_developer if is_developer else "Unknown"
                
                # Sync updated date
                is_updated = app_info.get('lastUpdatedOn', 'No lastUpdatedOn found').strip()
                df.at[i, 'Updated Date'] = is_updated if is_updated else "Unknown"
                
                # Get App version for each device
                for device in device_list:
                    app_version_finder = subprocess.run([
                        "adb", "-s", device, "shell", "dumpsys", "package", f"{package_name}"
                    ], capture_output=True, text=True, shell=True, encoding='utf-8')
                    
                    is_version = False
                    for line in app_version_finder.stdout.splitlines():
                        if "versionCode=" in line:
                            target_sdk = line.split()
                            d_target = dict(item.split("=") for item in target_sdk)
                            if "targetSdk" in d_target:
                                df.at[i, 'TargetSdk'] = d_target['targetSdk']
                            else:
                                df.at[i, 'App Version'] = "No data"

                        if "versionName=" in line:
                            app_version = line.split("=")[1].strip()
                            df.at[i, 'App Version'] = app_version
                            is_version = True
                            break
                    if not is_version:
                        # Sync app version
                        is_version_info = app_info.get('version', 'No version found').strip()
                        df.at[i, 'App Version'] = is_version_info if is_version_info else "Unknown"

                    # Save the result to CSV file for each device
                    df.to_csv(f'appInfo_result_{device}.csv', index=False)

            except Exception:
                df.at[i, 'Developer'] = "App is not found"
                df.at[i, 'App Category'] = "App is not found"
                df.at[i, 'App Version'] = "App is not found"
                df.at[i, 'Updated Date'] = "App is not found"
                df.at[i, 'TargetSdk'] = "App is not found"
                continue
                
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    package_names, app_names, df, sf, csv_file = process_csv()
    info_sync()
