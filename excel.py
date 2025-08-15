import os
import sys
import pandas as pd
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
        # Read Excel file once and get sheet names
        xls = pd.ExcelFile(filepath)
        if not {'List1', 'List2'}.issubset(xls.sheet_names):
            missing = {'List1', 'List2'} - set(xls.sheet_names)
            print(f"Missing sheets: {', '.join(missing)}")
            sys.exit(1)

        # Read both sheets using the ExcelFile object
        list1_df = pd.read_excel(xls, sheet_name='List1')
        list2_df = pd.read_excel(xls, sheet_name='List2')
        return list1_df, list2_df

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