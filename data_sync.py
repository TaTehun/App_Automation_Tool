import pandas as pd
from basic.csv_handler import process_csv
from basic.connect_devices import connect_devices

def data_sync():
    
    data_file = 'Book.csv'
    new_data_file = 'new_Book.csv'
    df = pd.read_csv(data_file)
    nf = pd.read_csv(new_data_file)
    df['Acccct'] = df['Acccct'].str.strip()
    df['Device'] = df['Device'].str.strip()
    nf['Accct'] = nf['Accct'].str.strip()
    nf['Device'] = nf['Device'].str.strip()
    df['Promo Start'] = pd.to_datetime(df['Promo Start'], format = '%m/%d/%Y')
    df['Promo End'] = pd.to_datetime(df['Promo End'], format = '%m/%d/%Y')

    #print (account_sync)
    #print (account_sync_nf)
    #print (nf.head())
    
    nf = nf.fillna(0)
    #print(nf)

    try:
        device_match, account_match, start_date_match, end_date_match, p_no_match = [], [], [], [], []
        unit_total = []
        
        new_date = [col for col in nf.columns if isinstance(col, str) and '/' in col]
        nf[new_date] = nf[new_date].apply(pd.to_datetime, format = '%m/%d/%Y')
        
        for i, row in df.iterrows():
            promo_start = row.get('Promo Start'),
            promo_end = row.get('Promo End'),
            device_list = row.get('Device'),
            acct_list = row.get('Acccct'),
            p_no = row.get('Condition')
            
            #print (device_list)
            #print (nf[(nf['Accct'])])

            #if pd.isna(promo_start) or pd.isna(promo_end) or pd.isna(device_list) or (acct_list):
                #continue

            nf['Device'] = nf['Device'].notna()
            nf['Accct'] = nf['Accct'].notna()
            nf.columns = nf.columns.str.strip()
            
            #matched_rows = nf[(nf['Device'] == device_list) & (nf['Accct'] == acct_list)]
            matched_rows = nf[(nf['Device'] == device_list) & (nf['Accct'] == acct_list)]
            
            #if matched_rows.empty:
                #continue
            
            total_sum = 0
            
            for _, match_row in matched_rows.iterrows():
            
                filtered_new_dates = match_row[new_date]
                
                for new_d, value in filtered_new_dates.items():
                    if pd.notna(value) and isinstance(value, (int, float)):
                        date_column_as_date = pd.to_datetime(new_d, format = '%m/%d/%Y')
                        if promo_start <= date_column_as_date <= promo_end:
                            unit_total += value
            unit_total = filtered_new_dates.values.sum()
            print (matched_rows)

            #print (f"p_no : {p_no_match}, device: {device_match}, account: {account_match}, start: {start_date_match}, end: {end_date_match}, unit = {unit_total}")

    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    data_sync()