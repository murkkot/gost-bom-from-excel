import os
import sys

def find_excel_files(input_dir):
    excel_files = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.xls', '.xlsx')):
            excel_files.append(filename)
    return excel_files

if __name__ == "__main__":
    # Define the static input folder inside the program directory
    input_directory = os.path.join(os.path.dirname(__file__), "input")

    if os.path.isdir(input_directory):
        found_files = find_excel_files(input_directory)
    else:
        print(f"The directory '{input_directory}' does not exist.")
        sys.exit(1)
    
    if not found_files:  # Check if list is empty
        print("No excel files found in the directory.")
        sys.exit(1)
    elif len(found_files) == 1:  # Only one file found
        print(found_files[0])  # Print just the filename
    else:  # Multiple files found
        print("choose file")
        for i, filename in enumerate(found_files, 1):
            print(f"{i}. {filename}")