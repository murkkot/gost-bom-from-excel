import os
import sys
import math
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import range_boundaries
from openpyxl.styles import Border, Side
from pathlib import Path
import shutil
from itertools import chain

# Find excel files in named folder
def find_excel_files(input_dir):
    excel_files = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.xls', '.xlsx')):
            excel_files.append(filename)
    return excel_files

# Read altium excel file to dataset
def read_altium_excel_file(filepath):
    try:
        # Read Excel file once and get sheet names
        xls = pd.ExcelFile(filepath)
        if not {'Sheet1', 'Sheet2'}.issubset(xls.sheet_names):
            missing = {'Sheet1', 'Sheet2'} - set(xls.sheet_names)
            print(f"Missing sheets: {', '.join(missing)}")
            sys.exit(1)

        # Read both sheets using the ExcelFile object
        list1_df = pd.read_excel(xls, sheet_name='Sheet1')
        list2_df = pd.read_excel(xls, sheet_name='Sheet2')
        return list1_df, list2_df

    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        sys.exit(1)

# Read groups escel file to dataset
def read_groups_excel_file(filepath):
    try:
        # Read Excel file once and get sheet names
        xls = pd.ExcelFile(filepath)
        if not {'Sheet1'}.issubset(xls.sheet_names):
            print("Missing Sheet1")
            sys.exit(1)

        # Read sheet using the ExcelFile object
        df = pd.read_excel(xls, sheet_name='Sheet1')
        return df

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

# Create filename for part list
def create_part_list_filename(df):
    result = df.loc[df["Key"] == "Децимальный номер", "Value"].values[0] \
    + " ПЭ3 (" \
    + df.loc[df["Key"] == "Наименование 2", "Value"].values[0] \
    + ") v." \
    + df.loc[df["Key"] == "Версия", "Value"].values[0] \
    + "." + df.loc[df["Key"] == "Ревизия ПЭ3", "Value"].values[0] + ".xlsx"
    return result

# Create filename for bom
def create_bom_filename(df):
    result = df.loc[df["Key"] == "Децимальный номер", "Value"].values[0] \
    + " СП (" \
    + df.loc[df["Key"] == "Наименование 2", "Value"].values[0] \
    + ") v." \
    + df.loc[df["Key"] == "Версия", "Value"].values[0] \
    + "." + df.loc[df["Key"] == "Ревизия СП", "Value"].values[0] + ".xlsx"
    return result

# Copy and rename part list template
def copy_rename_part_list_template(filename):
    input_path = Path('templates') / 'part_list_template.xlsx'
    output_path = Path('output') / f"{filename}"
    print(output_path)
    try:
        shutil.copy2(input_path, output_path)
        print("File copied and renamed successfully!")
    except FileNotFoundError:
        print("Error: File or directory not found")
    except PermissionError:
        print("Error: Permission denied")
    except Exception as e:
        print(f"An error occurred: {e}")

# Copy and rename bom template
def copy_rename_bom_template(filename):
    input_path = Path('templates') / 'bom_template.xlsx'
    output_path = Path('output') / f"{filename}"
    print(output_path)
    try:
        shutil.copy2(input_path, output_path)
        print("File copied and renamed successfully!")
    except FileNotFoundError:
        print("Error: File or directory not found")
    except PermissionError:
        print("Error: Permission denied")
    except Exception as e:
        print(f"An error occurred: {e}")

# Write part list to template
def write_part_list_to_template(df_params, df_data, filename):
    SHEET1_ROWS_NUMBER = 29
    SHEETN_ROWS_NUMBER = 32
    # Compute number of sheets in template
    num_rows = df_data.shape[0]
    #print("Num rows: ", num_rows)
    if num_rows <= SHEET1_ROWS_NUMBER:
        num_sheets = 1
    else:
        num_sheets = math.ceil((num_rows - SHEET1_ROWS_NUMBER) / SHEETN_ROWS_NUMBER) + 1
    # print("Num sheets: ", num_sheets)

    # Write parameters to title block
    output_path = Path('output') / f"{filename}"
    print(output_path)
    try:
        # Load the workbook with openpyxl
        wb = load_workbook(output_path)
        
        # Write to Sheet1
        # Set target sheet
        target_sheet='Sheet1'
        if target_sheet not in wb.sheetnames:
            raise ValueError(f"Sheet '{target_sheet}' not found in workbook")
        ws = wb[target_sheet]

        # Write parameters to Sheet1
        value = df_params.loc[df_params["Key"] == "Разработал", "Value"].values[0]
        write_to_merged_cell(ws, 'E37', value)
        value = df_params.loc[df_params["Key"] == "Проверил", "Value"].values[0]
        write_to_merged_cell(ws, 'E38', value)
        value = df_params.loc[df_params["Key"] == "Нормоконтролёр", "Value"].values[0]
        write_to_merged_cell(ws, 'E40', value)
        value = df_params.loc[df_params["Key"] == "Утвердил", "Value"].values[0]
        write_to_merged_cell(ws, 'E41', value)
        value = df_params.loc[df_params["Key"] == "Утвердил", "Value"].values[0]
        write_to_merged_cell(ws, 'E41', value)
        value = df_params.loc[df_params["Key"] == "Дата", "Value"].values[0]
        write_to_merged_cell(ws, 'H37', value)
        value = df_params.loc[df_params["Key"] == "Дата", "Value"].values[0]
        write_to_merged_cell(ws, 'H38', value)
        value = df_params.loc[df_params["Key"] == "Дата", "Value"].values[0]
        write_to_merged_cell(ws, 'H40', value)
        value = df_params.loc[df_params["Key"] == "Дата", "Value"].values[0]
        write_to_merged_cell(ws, 'H41', value)
        value = df_params.loc[df_params["Key"] == "Наименование 1", "Value"].values[0]
        write_to_merged_cell(ws, 'I38', value)
        value = df_params.loc[df_params["Key"] == "Наименование 2", "Value"].values[0]
        write_to_merged_cell(ws, 'I39', value)
        value =  'Версия ' + df_params.loc[df_params["Key"] == "Версия", "Value"].values[0] + '.' \
        + df_params.loc[df_params["Key"] == "Ревизия ПЭ3", "Value"].values[0]
        write_to_merged_cell(ws, 'I40', value)
        value = df_params.loc[df_params["Key"] == "Децимальный номер", "Value"].values[0] + ' ПЭ3'
        write_to_merged_cell(ws, 'I34', value)
        # Write total sheet number
        write_to_merged_cell(ws, 'P38', num_sheets)

        # Write data to Sheet1 cells C2:J17, C19:J26, C28:J30, C32:J33

        row_idx = 0
        for excel_row in chain(range(2, 18), range(19, 27), range(28, 31), range(32, 34)):
            col_idx = 0
            # Cells C, F, J            
            for excel_col in [3, 6, 10]:
                cell_ref = f"{chr(64 + excel_col)}{excel_row}"
                cell_value = df_data.iloc[row_idx, col_idx]
                col_idx += 1
                write_to_merged_cell(ws, cell_ref, cell_value)
            row_idx += 1
            if row_idx >= num_rows:
                break
        
        # Set border thickness for broken cells
        set_border_thickness(ws, 'Q2:Q33')
        
        # Write data and parameters to SheetN
        if num_sheets > 1:
            for i in range(2, num_sheets + 1):
                # Select current sheet
                target_sheet = f"Sheet{i}"
                if i > 2:
                    # Add sheet
                    ws = wb['Sheet2']
                    target = wb.copy_worksheet(ws)
                    target.title = target_sheet
                if target_sheet not in wb.sheetnames:
                    raise ValueError(f"Sheet '{target_sheet}' not found in workbook")
                ws = wb[target_sheet]
                # Write decimal number to title block
                write_to_merged_cell(ws, 'I38', value)
                # Write page number to title block
                write_to_merged_cell(ws, 'P40', i)
                # Write data to SheetN cells C2:J17, C19:J22, C24:J30, C32:J35, C37
                row_idx = 29 + (i - 2) * 32
                for excel_row in chain(range(2, 18), range(19, 23), range(24, 31), range(32, 36), range(37, 38)):
                    col_idx = 0
                    # Cells C, F, J            
                    for excel_col in [3, 6, 10]:
                        cell_ref = f"{chr(64 + excel_col)}{excel_row}"
                        cell_value = df_data.iloc[row_idx, col_idx]
                        col_idx += 1
                        write_to_merged_cell(ws, cell_ref, cell_value)
                    row_idx += 1
                    if row_idx >= num_rows:
                        break
                # Set border thickness for broken cells
                set_border_thickness(ws, 'Q2:Q37')
        else:
            # If only one sheet, delete Sheet2
            sheet_name = "Sheet2"
            if sheet_name in wb.sheetnames:
            # Remove the sheet
                del wb[sheet_name]
                print(f"Sheet '{sheet_name}' deleted successfully.")
            else:
                print(f"Sheet '{sheet_name}' not found in the workbook.")
          
        # Save workbook
        wb.save(output_path)
 
    except FileNotFoundError:
        print("Error: File or directory not found")
    except PermissionError:
        print("Error: Permission denied")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

# Write to merged cell
def write_to_merged_cell(ws, cell_ref, value):
    # Writes to the top-left cell of a merged range
    for merged_range in ws.merged_cells.ranges:
        if cell_ref in merged_range:
            # Get top-left cell of merged range
            min_col, min_row, _, _ = range_boundaries(str(merged_range))
            top_left_cell = ws.cell(row=min_row, column=min_col)
            top_left_cell.value = value
            return
    
    # If not in merged range, write normally
    ws[cell_ref] = value

def set_border_thickness(ws, range):
    # Create bold left border
    bold_left = Side(style='medium')

    # Apply to the entire range Q2:Q33
    for row in ws[range]:
        for cell in row:
            # Preserve existing borders and only modify left border
            current_border = cell.border
            cell.border = Border(
                left=bold_left,
                top=current_border.top,
                right=current_border.right,
                bottom=current_border.bottom
            )