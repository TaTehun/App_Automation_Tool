import subprocess
import pandas as pd
from basic.csv_handler import process_csv

def plm_checker():
    try:
        new_rows = []  # To store the new rows for issues

        for i, package_name in enumerate(package_names):
            # PLM checker
            for index, row in sf.iterrows():
                if row['App ID'] == package_name:
                    if row['Issue Status'] in ["Open", "Closed - Not Fixed"]:
                        new_row = {
                            'Issue Originator': row.get('Issue Originator', ''),
                            'Registered Date': row.get('Registered Date', ''),
                            'Source of Issue': row.get('Source of Issue', ''),
                            'Play Store App Category': row.get('Play Store App Category', ''),
                            'PLM Folder': row.get('PLM Folder', ''),
                            'Main Issue ID': row.get('Main Issue ID', ''),
                            '3rd Party Issue ID': row.get('3rd Party Issue ID', ''),
                            'Issue Description': row.get('Issue Description', ''),
                            'Application': row.get('Application', ''),
                            'Developer': row.get('Developer', ''),
                            'App ID': row.get('App ID', ''),
                            'App ver.': row.get('App ver.', ''),
                            'Model': row.get('Model', ''),
                            'Reproducible on Ref. Model': row.get('Reproducible on Ref. Model', ''),
                            'Issue Type': row.get('Issue Type', ''),
                            'Issue Status': row.get('Issue Status', ''),
                        }
                        new_rows.append(new_row)

        if new_rows:
            new_df = pd.DataFrame(new_rows)
            new_df.to_csv(f"{csv_file}_plm.csv", index=False)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    package_names, app_names, df, sf, csv_file = process_csv()
    plm_checker()
