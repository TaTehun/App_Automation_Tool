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
            
            #if matched_rows.empty:
                #continue  # Skip if no rows match
            

                # Iterate over the date columns and their corresponding values
            matched_num = df.select_dtypes(include=[int, float])
            matched_num = matched_num.fillna(0)
            matched_rows = matched_rows.matched_num.sum(axis=1)
            
            print(matched_rows)
            # Store or print the result for this row
            #print(f"p_no: {p_no}, Total sum for Device={device_list} and Account={acct_list} between {promo_start.date()} and {promo_end.date()}: {total_sum}")
            # You can also store results in lists if needed (e.g., device_match, account_match, etc.)
            
    def data_syn():
        import pandas as pd

# Load CSV files
a_df = pd.read_csv('a.csv')
b_df = pd.read_csv('b.csv')

# Convert 'start_date' and 'end_date' columns in a_df to datetime
a_df['start_date'] = pd.to_datetime(a_df['start_date'], format='%m/%d/%Y')
a_df['end_date'] = pd.to_datetime(a_df['end_date'], format='%m/%d/%Y')

# Iterate over rows in a_df and calculate the sum
for index, row in a_df.iterrows():
    device_name = row['device name']
    account = row['account']
    start_date = row['start_date']
    end_date = row['end_date']

    # Filter all matching rows in b_df, including duplicates
    matching_rows = b_df[(b_df['device name'] == device_name) & (b_df['account'] == account)]

    if not matching_rows.empty:
        # Create a date range and convert it to the required string format
        date_range = pd.date_range(start=start_date, end=end_date).strftime('%-m/%-d/%Y')

        # Initialize total_sum
        total_sum = 0

        # Iterate over each matching row to accumulate the sum
        for _, match in matching_rows.iterrows():
            total_sum += match[date_range].sum()

        # Output or store the total sum
        print(f"Total sum for device '{device_name}' and account '{account}': {total_sum}")


    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    data_sync()