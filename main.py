import sys

from excel import *
from part_list import *
from bom import *

if __name__ == "__main__":
    # Define the static input folder inside the program directory
    input_directory = os.path.join(os.path.dirname(__file__), "input")

    # Check that dir exists
    if os.path.isdir(input_directory):
        # Find excel files in the directory
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
        # Read data and parameters from excel file
        df_data, df_params = read_altium_excel_file(filepath)
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
        # Read data and parameters from excel file
        df_data, df_params = read_altium_excel_file(filepath)

    # Read groups.xlsx to dataframe
    filepath = os.path.join("templates", "groups.xlsx")
    if os.path.exists(filepath):
        df_groups = read_groups_excel_file(filepath)
    else:
        print(f"File does not exist: {filepath}")

    # df_data - data from altium excel
    # df_params - parameters from altium excel
    # df_groups - group names from excel
    # df_part_list - sorted part list
    # df_part_list_templated - modified part list for template
    # df_bom - sorted bom
    # df_bom_templated - modified bom for template
        
    # Sort part list
    df_part_list = combine_part_list_consecutive_components(df_data)
    # Modify part list for template
    df_part_list_templated = modify_part_list(df_part_list)
    # Write part list to excel
    #write_to_excel(df_part_list, "part_list_pe3")

    df_bom = combine_bom_components(df_data)
    df_bom = sort_bom(df_bom, df_groups)
    # Write bom to excel
    write_to_excel(df_bom, "bom_sp")

    
    # Print the head of the dataset
    #print("\nParameters preview:")
    #print(df_params.head(n=13))
    # print("\nBom preview:")
    # print(df_bom.head(n=21))

 
    #print(df_bom.head(n=21))

    # print("\nGroups preview:")
    # print(df_groups.head(n=10))
    
    # print("\nData sorted:")
    # print(df_result.head(n=20))

    #print("\nDataset modified:")
    #print(df_newdata.head(n=10))
    # Write part list to excel
    #write_to_excel(df_newdata, "part_list_pe3")

    # Create file name for part list
    # part_list_file_name = create_part_list_filename(df_params)
    # # Create file name for bom
    # bom_file_name = create_bom_filename(df_params)
    # # Copy part list template
    # copy_rename_part_list_template(part_list_file_name)
    # # Copy bom template
    # copy_rename_bom_template(bom_file_name)

    # # Write part list to excel
    # write_part_list_to_template(df_params, df_part_list_templated, part_list_file_name)