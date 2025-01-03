import pandas as pd

def process_csv():
    csv_file = 'App_List_US_1.csv'
    sync_issue_file = 'Book4.csv'
    
    df = pd.read_csv(csv_file, encoding='unicode_escape').rename(columns=lambda x: x.strip())
    sf = pd.read_csv(sync_issue_file, encoding='unicode_escape').rename(columns=lambda x: x.strip())
    
    package_names = df['App ID'].tolist()
    app_names = df['App ID'].tolist()    
    
    return package_names, app_names, df, sf, csv_file