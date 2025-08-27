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
    else:  # Multiple files found
        print("Found excel files in the input dir:")
        for i, filename in enumerate(found_files, 1): # Print all filenames
            print(f"{i}. {filename}")
        # Prompt for file number
        while True:
            try:
                choice = int(input("Enter altium data file number: "))
                if 1 <= choice <= len(found_files):
                    break
                print(f"Please enter a number between 1 and {len(found_files)}")
            except ValueError:
                print("Please enter a valid number.")
        filepath = os.path.join(input_directory, found_files[choice-1])
        print(f"Reading altium data file: {found_files[choice-1]}")
        # Read data and parameters from excel file
        df_data, df_params = read_altium_excel_file(filepath)
        while True:
            try:
                choice = int(input("Enter bom docs file number: "))
                if 1 <= choice <= len(found_files):
                    break
                print(f"Please enter a number between 1 and {len(found_files)}")
            except ValueError:
                print("Please enter a valid number.")
        filepath = os.path.join(input_directory, found_files[choice-1])
        print(f"Reading docs file: {found_files[choice-1]}")
        # Read data and parameters from excel file
        df_docs = read_excel_file(filepath)

    # Read groups.xlsx to dataframe
    filepath = os.path.join("templates", "groups.xlsx")
    if os.path.exists(filepath):
        df_groups = read_excel_file(filepath)
    else:
        print(f"File does not exist: {filepath}")

    # df_data - data from altium excel
    # df_params - parameters from altium excel
    # df_groups - group names from excel
    # df_docs - documents for bom from excel
    # df_part_list - sorted part list
    # df_part_list_templated - modified part list for template
    # df_bom - sorted bom
    # df_bom_templated - modified bom for template
        
    # Sort part list
    df_part_list = combine_part_list_consecutive_components(df_data)
    # Modify part list for template
    df_part_list_templated = modify_part_list_fields(df_part_list)

    # Combine bom components
    df_bom = combine_bom_components(df_data)
    # Sort bom
    df_bom = sort_bom(df_bom, df_groups)
    # Concat docs and bom
    df_bom = concat_bom_and_docs(df_bom, df_docs)
    # Modify bom for template
    df_bom_templated = modify_bom_fields(df_bom)

    # Write part list to excel
    write_to_excel(df_part_list_templated, "part_list_pe3")
    # Write bom to excel
    write_to_excel(df_bom_templated, "bom_sp")

    # Create file name for part list
    part_list_file_name = create_document_filename(df_params, PART_LIST_CONFIG)
    # Create file name for bom
    bom_file_name = create_document_filename(df_params, BOM_CONFIG)
    # Copy part list template
    copy_rename_template(part_list_file_name, PART_LIST_CONFIG)
    # Copy bom template
    copy_rename_template(bom_file_name, BOM_CONFIG)

    # Write part list to excel
    #write_part_list_to_template(df_params, df_part_list_templated, part_list_file_name)
    #write_bom_to_template(df_params, df_bom_templated, bom_file_name)

    write_document_to_template(df_params, df_part_list_templated, part_list_file_name, PART_LIST_CONFIG)
    write_document_to_template(df_params, df_bom_templated, bom_file_name, BOM_CONFIG)