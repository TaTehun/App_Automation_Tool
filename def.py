import pandas as pd

# Load a.csv and b.csv
a_csv = pd.read_csv('a.csv')
b_csv = pd.read_csv('b.csv')

# Replace NaN values in b.csv with 0 (empty values treated as 0)
b_csv = b_csv.fillna(0)

# Convert start_date and end_date in a_csv to datetime (assuming the format is MM/DD/YYYY)
a_csv['start_date'] = pd.to_datetime(a_csv['start_date'], format='%m/%d/%Y', errors='coerce')
a_csv['end_date'] = pd.to_datetime(a_csv['end_date'], format='%m/%d/%Y', errors='coerce')

# Identify date columns in b_csv (those that contain '/' in their name, assuming they represent dates)
date_columns = [col for col in b_csv.columns if isinstance(col, str) and '/' in col]

# Convert valid date columns in b_csv to datetime, skipping non-date values like '0'
def safe_convert_to_datetime(value):
    # If value is '0' or NaN, return NaT (Not a Time)
    if value == 0 or pd.isna(value):
        return pd.NaT
    try:
        # Try to convert the value to a datetime object, if it's a valid date string
        return pd.to_datetime(value, format='%m/%d/%Y', errors='coerce')
    except Exception as e:
        # If conversion fails, return NaT
        return pd.NaT

# Apply the safe conversion function to all date columns in b_csv
b_csv[date_columns] = b_csv[date_columns].applymap(safe_convert_to_datetime)

# Iterate through each row in a_csv
for index, row in a_csv.iterrows():
    abc_value = row.get('ABC')
    def_value = row.get('DEF')
    start_date = row.get('start_date')
    end_date = row.get('end_date')
    p_number = row.get('p_number')  # Get the p_number from the current row

    # Skip the row if ABC, DEF, or dates are missing in a.csv (just in case)
    if pd.isna(abc_value) or pd.isna(def_value) or pd.isna(start_date) or pd.isna(end_date):
        continue  # Skip this row if any required value is missing

    # Use parentheses to ensure logical operations are evaluated correctly
    matched_rows = b_csv[(b_csv['ABC'] == abc_value) & (b_csv['DEF'] == def_value)]

    # If there are matched rows, process the date columns within the range
    if matched_rows.empty:  # Skip if no match is found in b.csv
        continue

    # Iterate over matched rows and sum values within the date range
    total_sum = 0
    for _, match_row in matched_rows.iterrows():  # iterrows() is used to iterate row by row
        # Filter the date columns that fall within the start and end date range
        filtered_dates = match_row[date_columns]  # Get the values for date columns for this matched row
        
        # Iterate over the date columns and check if the date is within the range
        for date_column, value in filtered_dates.items():
            # Ensure value is a valid numeric value and it's within the date range
            if pd.notna(value) and isinstance(value, (int, float)):  # Ensure value is numeric
                date_column_as_date = pd.to_datetime(date_column, format='%m/%d/%Y', errors='coerce')  # Convert column name to date
                if start_date <= date_column_as_date <= end_date:
                    total_sum += value  # Add the corresponding value to the total sum

    # Print the result, including p_number
    print(f"p_number: {p_number}, Total sum for ABC={abc_value} and DEF={def_value} between {start_date.date()} and {end_date.date()}: {total_sum}")
