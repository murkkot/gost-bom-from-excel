import os
import sys
import pandas as pd
import re
from pathlib import Path

# Find excel files in named folder
def find_excel_files(input_dir):
    excel_files = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.xls', '.xlsx')):
            excel_files.append(filename)
    return excel_files

# Read excel file to dataset
def read_excel_file(filepath):
    try:
        # Read the Excel file (handles both .xls and .xlsx)
        return pd.read_excel(filepath)
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        sys.exit(1)

# Write dataset to excel file
def write_to_excel(result_df, filename):
    # Define output directory and filename
    output_dir = 'output'
    filename_with_ext = f"{filename}.xlsx"
    
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        # Construct full file path
        file_path = os.path.join(output_dir, filename_with_ext)
        # Write to Excel file
        result_df.to_excel(file_path, index=False, engine='openpyxl')
        print(f"Successfully wrote {result_df.shape[0]} records to {file_path}")
        return file_path
    
    except PermissionError:
        print(f"ERROR: Permission denied - cannot write to {filename_with_ext}")
        print("Please check:")
        print("1. If the file is open in another program (close it)")
        print("2. If you have write permissions in the output folder")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error writing Excel file: {str(e)}")
        sys.exit(1)

# Sort dataset for parts list (PE3)
def combine_consecutive_components(df):
    if df.empty:
        return pd.DataFrame(columns=['Designator', 'Name', 'Quantity'])
    
    combined_data = []
    current_name = df.iloc[0]['Name']
    current_designators = [str(df.iloc[0]['Designator'])]
    current_quantity = df.iloc[0]['Quantity']
    
    for i in range(1, len(df)):
        if df.iloc[i]['Name'] == current_name:
            current_designators.append(str(df.iloc[i]['Designator']))
            current_quantity += df.iloc[i]['Quantity']
        else:
            processed_designators = process_designator_sequence(current_designators)
            combined_data.append({
                'Designator': processed_designators,
                'Name': current_name,
                'Quantity': current_quantity
            })
            current_name = df.iloc[i]['Name']
            current_designators = [str(df.iloc[i]['Designator'])]
            current_quantity = df.iloc[i]['Quantity']
    
    processed_designators = process_designator_sequence(current_designators)
    combined_data.append({
        'Designator': processed_designators,
        'Name': current_name,
        'Quantity': current_quantity
    })
    
    return pd.DataFrame(combined_data)

# Process designator sequences according to GOST
def process_designator_sequence(designators):
    if len(designators) == 1:
        return designators[0]
    
    # Parse all designators into (prefix, number) tuples
    parsed = []
    for d in designators:
        match = re.match(r'([^\d]*)(\d+)', d)
        if match:
            prefix, num = match.groups()
            parsed.append((prefix, int(num)))
        else:
            return ', '.join(designators)
    
    # Group into consecutive sequences
    groups = []
    current_group = [designators[0]]
    
    for i in range(1, len(designators)):
        prev_prefix, prev_num = parsed[i-1]
        curr_prefix, curr_num = parsed[i]
        
        if (curr_prefix == prev_prefix) and (curr_num == prev_num + 1):
            current_group.append(designators[i])
        else:
            groups.append(current_group)
            current_group = [designators[i]]
    
    groups.append(current_group)
    
    # Format each group appropriately
    formatted_groups = []
    for group in groups:
        if len(group) >= 3:
            formatted_groups.append(f"{group[0]}...{group[-1]}")
        else:
            formatted_groups.append(", ".join(group))
    
    return ", ".join(formatted_groups)

if __name__ == "__main__":
    # Define the static input folder inside the program directory
    input_directory = os.path.join(os.path.dirname(__file__), "input")

    # Check that dir exists
    if os.path.isdir(input_directory):
        found_files = find_excel_files(input_directory)
    else:
        print(f"The directory '{input_directory}' does not exist.")
        sys.exit(1)
    
    if not found_files:  # Check if list is empty
        print("No excel files found in the directory.")
        sys.exit(1)
    elif len(found_files) == 1:  # Only one file found
        print(f"Reading file: {found_files[0]}")  # Print just the filename
        filepath = os.path.join(input_directory, found_files[0])
        df = read_excel_file(filepath)
    else:  # Multiple files found
        print("Multiple Excel files found:")
        for i, filename in enumerate(found_files, 1): # Print all filenames
            print(f"{i}. {filename}")
        # Prompt for file number
        while True:
            try:
                choice = int(input("Enter file number: "))
                if 1 <= choice <= len(found_files):
                    break
                print(f"Please enter a number between 1 and {len(found_files)}")
            except ValueError:
                print("Please enter a valid number.")

        filepath = os.path.join(input_directory, found_files[choice-1])
        print(f"Reading file: {found_files[choice-1]}")
        df = read_excel_file(filepath)

    # Print the head of the dataset
    print("\nData preview:")
    print(df.head(n=21))
    result_df = combine_consecutive_components(df)
    print("\nData sorted:")
    print(result_df.head(n=10))
    # Write part list to excel
    write_to_excel(result_df, "part_list_pe3")