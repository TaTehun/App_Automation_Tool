import pandas as pd

def data_sync():
    
# Load CSV files
    a_df = pd.read_csv('Book.csv')
    b_df = pd.read_csv('new_Book.csv')

# Convert 'start_date' and 'end_date' columns in a_df to datetime
    a_df['Promo Start'] = pd.to_datetime(a_df['Promo Start'], format='%m/%d/%Y')
    a_df['Promo End'] = pd.to_datetime(a_df['Promo End'], format='%m/%d/%Y')

# Iterate over rows in a_df and calculate the sum
    for index, row in a_df.iterrows():
        device_name = row['Device']
        account = row['Account']
        start_date = row['Promo Start']
        end_date = row['Promo End']

        # Filter all matching rows in b_df, including duplicates
        matching_rows = b_df[(b_df['Device'] == device_name) & (b_df['Account'] == account)]

        if not matching_rows.empty:
            # Create a date range and convert it to the required string format
            date_range = pd.date_range(start=start_date, end=end_date).to_series().dt.strftime('%-m/%-d/%Y')

            # Initialize total_sum
            total_sum = 0

            # Iterate over each matching row to accumulate the sum
            for _, match in matching_rows.iterrows():
                total_sum += match[date_range].sum()

            # Output or store the total sum
            print(f"Total sum for device '{device_name}' and account '{account}': {total_sum}")
        
if __name__ == "__main__":
    data_sync()