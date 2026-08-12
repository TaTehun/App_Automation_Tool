# App Automation Tester

A GUI-based Android app testing automation tool that installs, launches, and stress-tests apps from Google Play across multiple connected devices simultaneously, with real-time crash detection, dark/multi-window mode testing, and CSV-driven reporting.

> **Visual overview:** [project-overview.html](project-overview.html)

---

## Overview

Testing app compatibility across Android devices is time-consuming and repetitive. This tool automates the full cycle: install from Google Play, launch the app, toggle dark mode, attempt multi-window mode, run a monkey test, detect crashes via logcat, and save structured results to CSV, all without manual interaction.

Multiple devices can run in parallel. A resume mode picks up where it left off if the session is interrupted.

---

## Project Structure

```
App_Automation_Tool/
├── main.py                  # Full GUI + automation pipeline
├── test1.csv                # Default app list (App Name, App ID)
├── Book1.csv                # Sample app list
├── requirements.txt         # Python dependencies
├── Readme_dev.md            # Dev environment setup notes
└── readme_files/            # Screenshots and demo images for README
```

---

## How It Works

### 1. Connect Devices
Click **Connect Devices** to detect all Android devices via ADB (USB or wireless). Devices can be individually selected from a checklist. Leaving them unchecked selects all devices.

### 2. Load App List
- **Load Automation CSV File**: loads the default `test1.csv`
- **Select CSV File**: opens a file picker for any CSV
- **Search (Max: 30 apps)**: queries Google Play by keyword and generates a CSV automatically

CSV format required:
```
App Name,App ID
Instagram,com.instagram.android
```

### 3. Set Test Parameters
- **Installation Attempts**: retries per app if install fails
- **Launch Test Attempts**: if pass rate < 50%, the app is uninstalled and reinstalled automatically

### 4. Run Tests
- **Run in Sequential**: one device at a time
- **Run in Parallel**: all selected devices simultaneously (multithreaded)

Each app goes through:
1. Open Google Play → Install
2. Launch app (via Play / Open button)
3. Toggle Dark Mode
4. Attempt Multi-Window mode
5. Run Monkey test (500 random touch events)
6. Monitor logcat for crashes (ANR / Fatal Exception / Tombstone)
7. Scrape app metadata (version, developer, category, permissions)
8. Save result to temp CSV (resume-safe)

### 5. Results
Results are saved as `Test_result_{serial}.csv` per device. Columns include:

| Column | Description |
|--------|-------------|
| Install Result | Pass / Fail / NT/NA |
| Running Result | Pass / NT/NA / Crash |
| Final Running Result | Most frequent launch result |
| MW Result | Multi-window test result per attempt |
| Final MW Result | Most frequent MW result |
| Crash log | Saved to `crashlog_{attempt}_{device}_{package}.txt` |
| App Version, Developer, Category, Updated Date, TargetSdk | Scraped from Google Play |
| Permissions, Is Camera | Permission list and camera flag |

---

## Resume Mode

If a session is interrupted, the tool resumes from the last saved temp CSV (`Test_result_{serial}_temp.csv`) on next run. Apps with a passing install + launch result are skipped automatically.

---

## Screen Recording

A screen recording is captured for each launch attempt via `adb screenrecord`. On crash, the recording is renamed with a `crash_` prefix and kept. On success, it is deleted.

---

## Requirements

```
PyQt5
pandas
uiautomator2
google-play-scraper
```

Also requires `adb` installed and available in system PATH.

---

## Running

```bash
# From source
pip install -r requirements.txt
python main.py
```

On first run with **Start Testing All**, the tool pushes `u2.jar` to each device automatically.

---

## Executable Build (archived)

Previously built with PyInstaller for Windows (`.exe`) and macOS (`.app`). Source-only going forward.

---

## Changelog

### v2.0 · 2026-05-07 · Crash Detection Overhaul + Device Selection UI
- Ring-buffer logcat monitoring (800-line buffer) captures crash context before detection is confirmed
- ANR / App Crash / Tombstone distinguished in crash log output
- Device checklist UI: run on selected devices only
- `test_settings()`: auto-configures swipe navigation and keyboard toolbar before test run
- Screen recording per launch attempt, preserved on crash
- `Updated Date` converted to `YYYYMMDD` format
- Resume logic tightened to skip only apps with both install and launch passing

### v1.0 · Initial Release
- Multi-device parallel testing via ADB
- Google Play install automation
- Dark mode / multi-window / monkey test
- Crash detection via logcat
- Google Play scraper for app metadata
- CSV-driven input/output with resume support
- PyQt5 GUI with progress bar and log output
