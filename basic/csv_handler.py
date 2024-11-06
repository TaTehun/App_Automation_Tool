import pandas as pd

def process_csv():
    csv_file = '123tj.csv'
    
    df = pd.read_csv(csv_file, encoding='unicode_escape')
    
    package_names = df['App ID'].tolist()
    app_names = df['App Name'].tolist()
    
    return package_names, app_names, df