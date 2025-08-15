import sys

from excel import *
from part_list import *

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