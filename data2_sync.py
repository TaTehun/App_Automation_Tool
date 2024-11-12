import pandas as pd

def data_sync():
    data_file = 'Book.csv'
    new_data_file = 'new_Book.csv'
    
    # Load data files
    df = pd.read_csv(data_file)
    nf = pd.read_csv(new_data_file)
    
    # Clean and strip columns
    df['Acccct'] = df['Acccct'].str.strip()
    df['Device'] = df['Device'].str.strip()
    nf['Accct'] = nf['Accct'].str.strip()
    nf['Device'] = nf['Device'].str.strip()

    # Convert Promo Start and End to datetime
    df['Promo Start'] = pd.to_datetime(df['Promo Start'], format='%m/%d/%Y')
    df['Promo End'] = pd.to_datetime(df['Promo End'], format='%m/%d/%Y')

    nf = nf.fillna(0)  # Replace NaNs with 0

    try:
        # Prepare lists for matched values and totals
        device_match, account_match, start_date_match, end_date_match, p_no_match = [], [], [], [], []
        unit_total = []

        # Identify date columns
        new_date = [col for col in nf.columns if isinstance(col, str) and '/' in col]
        
        # Convert date columns in nf to datetime
        nf[new_date] = nf[new_date].apply(pd.to_datetime, format='%m/%d/%Y', errors='coerce')

        # Iterate through each row in df
        for i, row in df.iterrows():
            promo_start = row.get('Promo Start')
            promo_end = row.get('Promo End')
            device_list = row.get('Device')
            acct_list = row.get('Acccct')
            p_no = row.get('Condition')
            
            # Check if promo_start, promo_end, device_list, and acct_list are valid
            if pd.isna(promo_start) or pd.isna(promo_end) or pd.isna(device_list) or pd.isna(acct_list):
                continue  # Skip if any of these are missing

            # Match rows in nf based on Device and Accct columns
            matched_rows = nf[(nf['Device'] == device_list) & (nf['Accct'] == acct_list)]
            
            if matched_rows.empty:
                continue  # Skip if no rows match
            
            total_sum = 0
            
            # Iterate over matched rows
            for _, match_row in matched_rows.iterrows():
                # Filter values in the date columns
                filtered_new_dates = match_row[new_date]
                
                # Iterate over the date columns and their corresponding values
                for new_d, value in filtered_new_dates.items():
                    if pd.notna(value) and isinstance(value, (int, float)):
                        date_column_as_date = pd.to_datetime(new_d, format='%m/%d/%Y', errors='coerce')
                        
                        # Check if the date is within the promo start and end range
                        if promo_start <= date_column_as_date <= promo_end:
                            total_sum += value  # Add the value to the running total

            # Store or print the result for this row
            print(f"p_no: {p_no}, Total sum for Device={device_list} and Account={acct_list} between {promo_start.date()} and {promo_end.date()}: {total_sum}")
            # You can also store results in lists if needed (e.g., device_match, account_match, etc.)

    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    data_sync()