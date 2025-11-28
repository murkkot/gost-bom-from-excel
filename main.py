import sys

from excel import *
from part_list import *
from bom import *
from _version import __version__

if __name__ == "__main__":
    # Print version
    print(f"gost-bom-from-excel v.{__version__}")
    print("--------------------------------------")

    # Determine the base path, works for both development and PyInstaller
    if getattr(sys, 'frozen', False):
        # If run as a bundle, the base path is the directory of the executable
        base_path = os.path.dirname(sys.executable)
    else:
        # If run as a script, the base path is the script's directory
        base_path = os.path.dirname(os.path.abspath(__file__))


    # Define the static input folder inside the program directory
    input_directory = os.path.join(base_path, "input")
    templates_directory = os.path.join(base_path, "templates")
    output_directory = os.path.join(base_path, "output")

    # Check that dir exists
    if os.path.isdir(input_directory):
        # Find excel files in the directory
        found_files = find_excel_files(input_directory)
    else:
        print(f"Папка '{input_directory}' не обнаружена")
        input("Нажмите ENTER для выхода")
        sys.exit(1)
    
    if not found_files:  # Check if list is empty
        print("Не найдены excel файлы в папке input")
        input("Нажмите ENTER для выхода")
        sys.exit(1)
    else:  # Multiple files found
        print("Найдены следующие excel файлы:")
        for i, filename in enumerate(found_files, 1): # Print all filenames
            print(f"{i}. {filename}")
        # Prompt for file number
        while True:
            try:
                choice = int(input("Введите номер файла c данными из Altium: "))
                if 1 <= choice <= len(found_files):
                    break
                print(f"Введите число между 1 и {len(found_files)}")
            except ValueError:
                print(f"Введите число между 1 и {len(found_files)}")
        data_filepath = os.path.join(input_directory, found_files[choice-1])
        print(f"Читаю файл c данными из Altium: {found_files[choice-1]}")
        # Read data and parameters from excel file
        df_data, df_params = read_altium_excel_file(data_filepath)
        while True:
            try:
                choice = int(input("Введите номер файла с документацией для спецификации: "))
                if 1 <= choice <= len(found_files):
                    break
                print(f"Введите число между 1 и {len(found_files)}")
            except ValueError:
                print(f"Введите число между 1 и {len(found_files)}")
        docs_filepath = os.path.join(input_directory, found_files[choice-1])
        print(f"Читаю файл с документацией для спецификации: {found_files[choice-1]}")
        df_docs = read_excel_file(docs_filepath)

    # Read groups.xlsx to from templates directory dataframe
    filepath = os.path.join(templates_directory, "groups.xlsx")
    if os.path.exists(filepath):
        df_groups = read_excel_file(filepath)
    else:
        print(f"Файл groups.xlsx не найден: {filepath}")

    # df_data - data from altium excel
    # df_params - parameters from altium excel
    # df_groups - group names from excel
    # df_docs - documents for bom from excel
    # df_part_list - sorted part list
    # df_part_list_templated - modified part list for template
    # df_bom - sorted bom
    # df_bom_templated - modified bom for template

    # Check df_data
    columns_list = ['Designator', 'Name', 'Quantity', 'Decimal Number']
    check_dataframe(df_data, columns_list, data_filepath)
    columns_list = ['Format', 'Zone', 'Position', 'Decimal Number', 'Name', 'Quantity', 'Designator']
    check_dataframe(df_docs, columns_list, docs_filepath)
        
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
    # write_to_excel(df_part_list, "part_list_pe3")
    # Write bom to excel
    # write_to_excel(df_bom, "bom_sp")

    # Create file name for part list
    part_list_file_name = create_document_filename(df_params, PART_LIST_CONFIG)
    # Create file name for bom
    bom_file_name = create_document_filename(df_params, BOM_CONFIG)
    # Copy part list template
    copy_rename_template(templates_directory, output_directory, part_list_file_name, PART_LIST_CONFIG)
    # Copy bom template
    copy_rename_template(templates_directory, output_directory, bom_file_name, BOM_CONFIG)

    # Write part list to template
    write_document_to_template(df_params, df_part_list_templated, part_list_file_name, PART_LIST_CONFIG)
    # Write bom to template
    write_document_to_template(df_params, df_bom_templated, bom_file_name, BOM_CONFIG)
    print("--------------------------------------")
    print("Программа завершилась успешно")
    input("Нажмите ENTER для выхода")