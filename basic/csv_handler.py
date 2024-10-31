import pandas as pd

def process_csv():
    
    df = pd.read_csv('App_List_US.csv', encoding='unicode_escape')
    
    package_names = df['App ID'].tolist()
    app_names = df['App Name'].tolist()
    
    return package_names, app_names