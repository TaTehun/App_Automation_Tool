# App Installation Tester

**Version:** 1.0.0  
**Author:** Taehun Jang

## Introduction

`App Installation Tester` is a GUI-based automation tool for testing Android apps across multiple devices simultaneously.  
It provides automated app installation, UI testing, crash monitoring, and CSV-based reporting.  
The tool is built with Python and PyQt5, and requires no manual interaction during test execution.

---

## Features

- Multi-device parallel testing (ADB over USB or Wi-Fi)  
- Automated app installation from Google Play  
- Auto uninstall & reinstall if launch success < 50%  
- Dark/Light mode toggle before multi-window test  
- Multi-window compatibility check  
- Monkey test (random UI events)  
- Real-time crash detection via logcat  
- App info scraping (permissions, version, developer, category)  
- CSV-driven input/output with resume support  
- Fully GUI-based (no coding required)

---

## System Requirements

- Python 3.8 or higher (for source version)  
- ADB installed & working  
- OS: Windows or macOS (via PyInstaller build)

---

## Executable Build

| OS      | File Type | Run Command                      |
|---------|-----------|----------------------------------|
| Windows | `.exe`    | Run `app_tester_4_windows.exe` |
| macOS   | `.app`    | Run `app_tester_4_mac.app` *(allow in system preferences)*

## From Source

pip install PyQt5 pandas uiautomator2 google_play_scraper
python main.py

## How It Works
### Installation Flow
This flow determines how the tool behaves when installing apps from the Play Store.
<img src="/readme_files/Automated_App_Installer_Tester.png">

### Launch & Test Flow
<img src="/readme_files/app_test_workflow.png" width="600"/>
---

The tool automates the entire testing pipeline across connected Android devices:

1. Detect connected devices via ADB
2. Load the app list from a CSV file
3. Open Google Play and attempt to install each app
   ↳ If launch attempts < 50%, uninstall and reinstall the app
4. Launch the installed app
5. Toggle between Dark and Light mode
6. Attempt to enter Multi-Window mode
7. Run a Monkey test (random touch input events)
8. Monitor the device logcat for crash signals
9. Collect app metadata (permissions, version, developer, etc.)
10. Save all test results to a CSV file
🔴 Crash detection is active from step 4 to 7.

---

## GUI Overview

### Window:
<img src="/readme_files/main_window.png" width="720"/>

### Mac:
<img src="/readme_files/main_screen.png" width="720"/>

---

### Device Management
- **Connect Devices**  
  Scans for connected Android devices via ADB (USB or wireless) and displays their IDs.

---

### Test Parameters
- **Installation Attempts**  
  Number of times to retry installation if it fails.

- **Launch Test Attempts**  
  Number of times to retry launching the app.  
  If success rate is below 50%, the app will be uninstalled and reinstalled.

---

### ▶️ Test Controls
- **Start Testing**  
  Begins testing only on one selected device.

- **Start Testing All**  
  Runs the same test across all connected devices in parallel (multithreaded).

- **Stop Testing**  
  Cancels all currently running tests.

---

### App Search (Google Play)
- **Search (Max: 30 apps)**  
  Searches for apps on Google Play using a keyword and generates a CSV.

- **Load searched data CSV File**  
  Loads a previously saved CSV from the app search to use for testing.

---

### CSV Automation
- **Load Automation CSV File**  
  Loads a predefined list of apps (App Name & App ID) to automate testing.

- **Select CSV File**  
  Allows manual CSV file selection for loading app list.

---

### Table Control
- **Add Row (↑ / ↓)**  
  Adds a new row above or below the selected row.

- **Delete Row**  
  Removes the currently selected row(s) from the table.

- **Save CSV**  
  Saves changes to the currently loaded CSV file.

- **Save As**  
  Saves the table content as a new CSV file.

---

### CMD | Terminal Output
<img src="/readme_files/cmd.png" width="600"/>

<img src="/readme_files/terminal.png" width="600"/>

- **Log Output Window**  
  Displays real-time logs for each device.  
  Shows installation status, crash logs, Play Store actions, app compatibility, and result summaries.  
  Helps the user track progress and debug issues as they happen.

  ---

## How to Run in GUI

**(Optional) App Search on Google Play Store**
- Enter a keyword in the **App Search** input (e.g., `Trending social media apps`)  
- Click **Search (Max: 30 apps)**  
- A CSV file (e.g., `app_search_trending_social_apps_result.csv`) will be generated  
- Click **Load searched data CSV File** to import it into the app  

1. **Launch the App**  
   Run `app_tester_4_windows.exe` (on Windows) or `app_tester_4_mac.app` (on macOS).  
   > ⚠️ Ensure `test1.csv` is in the **same directory** as the executable.

2. **Connect Devices**  
   Click **Connect Devices** (top-left).  
   This detects all Android devices connected via ADB (USB or wireless).

3. **Load CSV File**  
   - Click **Load Automation CSV File** to load the default `test1.csv`,  
   - Or click **Select CSV File** to choose a custom app list.  
   The CSV must contain **App Name,App ID**
    example:
    **App Name,App ID**
    Instagram,com.instagram.android

4. **(Optional) Table Control**
You can edit the app list in the table:
- Use Add Row ↑ / ↓ or Delete Row to modify
- After editing, Save CSV
- Then click **Load Automation CSV File** or **Select CSV File** again to reflect changes in the app list

5. **Set Test Parameters**  
- **Installation Attempts**: How many times to retry installing if it fails  
- **Launch Test Attempts**: If launch success rate is below 50%, the app will be uninstalled & reinstalled automatically

6. **Start Testing**  
- Click **Start Testing** to run on one device  
- Or click **Start Testing All** to test **all connected devices in parallel**

7. **Monitor Progress**  
- Track real-time logs in the **log window** 
- View **progress bar** and count

8. **Stop Testing (Optional)**  
- Click **Stop Testing** to cancel all running tests at any time.

## Demo Video
[<img src="/readme_files/demo.png" width="300"/>](https://yourdomain.com/videos/demo.mp4)

---

## Test Result example

1. App Search
<img src="/readme_files/app_search.png" width="600"/>

2. Test Result
<img src="/readme_files/test_result.png" width="600"/>
