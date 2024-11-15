import pandas as pd

def data_sync():
    data_file = 'Book.csv'
    new_data_file = 'new_Book1.csv'
    
    # Load data files
    df = pd.read_csv(data_file)
    nf = pd.read_csv(new_data_file)
    
    # Clean and strip columns
    df['Account'] = df['Account'].str.strip()
    df['Device'] = df['Device'].str.strip()
    nf['Account'] = nf['Account'].str.strip()
    nf['Device'] = nf['Device'].str.strip()

    # Convert Promo Start and End to datetime
    df['Promo Start'] = pd.to_datetime(df['Promo Start'], format='%Y-%m-%d')
    df['Promo End'] = pd.to_datetime(df['Promo End'], format='%Y-%m-%d')

    nf = nf.fillna(0)  # Replace NaNs with 0
    date_oct = pd.to_datetime('2024-10-01', format = '%Y-%m-%d')

    try:
        # Identify date columns
        new_date = [col for col in nf.columns if isinstance(col, str) and '-' in col]
        new_date_no = [col for col in nf.columns]
        df['Unit'] = 'no match'
        df['Matched Rows'] = 'no match'
        df['Unit Oct'] = 'no match'
        df['Matched Rows Oct'] = 'no match'
        
        # Iterate through each row in df
        for i, row in df.iterrows():
            promo_start = row.get('Promo Start')
            promo_start_date = promo_start.date()
            promo_end = row.get('Promo End')
            promo_end_date = promo_end.date()
            device_list = row.get('Device')
            acct_list = row.get('Account')
            p_no = row.get('Condition')

            # Check if promo_start, promo_end, device_list, and acct_list are valid
            if pd.isna(promo_start) or pd.isna(promo_end) or pd.isna(device_list) or pd.isna(acct_list):
                continue  # Skip if any of these are missing

            # Match rows in nf based on Device and Accct columns
            matched_rows = nf[(nf['Device'] == device_list) & (nf['Account'] == acct_list)]
            if not matched_rows.empty:
            
                total_sum = 0
                total_sum_oct = 0
                matched_row_number = []
                matched_row_oct = []

                promo_start_date_e = pd.to_datetime('2024-01-01', format = '%Y-%m-%d')
                promo_start_date_e = promo_start_date_e.date()
                promo_end_date_e = pd.to_datetime('2024-06-30', format = '%Y-%m-%d')
                promo_end_date_e = promo_end_date_e.date()

                
                for _, match_row in matched_rows.iterrows():
                    filtered_new_dates = match_row[new_date]
                    unfiltered_new_dates = match_row[new_date_no]
                    #print(filtered_new_dates.items())

                    for new_d, value in filtered_new_dates.items():
                        if pd.notna(value) and isinstance(value, (int, float)):
                            date_column_as = pd.to_datetime(new_d, format='%Y-%m-%d', errors='coerce')
                            date_column_as_date = date_column_as.date()
                            #print(date_column_as_date, value)
                            if promo_start_date_e <= date_column_as_date <= promo_end_date_e:
                                #print(promo_start_date_e, date_column_as_date, promo_end_date_e, value)
                                total_sum += value
                            #print(value)
                    matched_row_number.append(str(int(match_row.name)+2))
                    '''    
                    for new_d, value in filtered_new_dates.items():
                        
                        if pd.notna(value) and isinstance(value, (int, float)):
                            date_column_as_date = pd.to_datetime(new_d, format='%Y-%m-%d', errors='coerce')
                            if date_oct <= promo_start <= date_column_as_date <= promo_end:
                                total_sum_oct += value
                                
                    matched_row_oct.append(str(match_row.name))
                    '''
                df.at[i, 'Unit'] = total_sum
                df.at[i, 'Matched Rows'] = ', '.join(matched_row_number)
                #df.at[i, 'Unit Oct'] = total_sum_oct
                #df.at[i, 'Matched Rows Oct'] = ', '.join(matched_row_number)
            else:
                df.at[i,'Unit'] = 'no match'
                df.at[i,'Matched Rows'] = 'no match'
                #df.at[i,'Unit Oct'] = 'no match'
                #df.at[i,'Matched Rows Oct'] = 'no match'
                
        df.to_csv('updated_book.csv', index=False)
                            


    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    data_sync()