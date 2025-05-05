import pandas as pd
from basic.csv_handler import process_csv
from basic.connect_devices import connect_devices

def plm_category(row):
    return{
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

def plm_checker():
    try:
        issue_list_total = []
                
        for package_name in package_names:
            # PLM checker
            for i, row in sf.iterrows():
                if str(row['App ID']).strip() == package_name:
                    if row['Issue Status'] in ["Open", "Closed - Not Fixed"]:
                        plm_cat = plm_category(row)
                        issue_list_total.append(plm_cat)
            if issue_list_total:
                new_df_total = pd.DataFrame(issue_list_total)
                new_df_total.to_csv(f"plm_list_total.csv", index=False)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    package_names, app_names, df, sf, csv_file = process_csv()
    plm_checker()
