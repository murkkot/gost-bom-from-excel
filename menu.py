import os, sys, time
from typing import Dict, Any, Tuple
import pandas as pd
from bom import combine_bom_components, sort_bom, concat_bom_and_docs, modify_bom_fields
from part_list import clean_part_list_non_des_fields, combine_part_list_consecutive_components, modify_part_list_fields
from excel import *
from auxiliary import get_input_file, check_dataframe, read_user_input
Menu = Dict[str, Any]

# ====================== Global variables ======================
found_files = [] # List of excel files in input dir
df_data = pd.DataFrame() # df_data - data from altium excel
df_params = pd.DataFrame() # df_params - parameters from altium excel
df_groups = pd.DataFrame() # df_groups - group names from excel
df_docs = pd.DataFrame() # df_docs - documents for bom from excel
df_part_list = pd.DataFrame() # df_part_list - sorted part list
df_part_list_templated = pd.DataFrame() # df_part_list_templated - modified part list for template
df_bom = pd.DataFrame() # df_bom - sorted bom
df_bom_templated = pd.DataFrame() # df_bom_templated - modified bom for template
input_directory = ""
templates_directory = ""
output_directory = ""
data_filepath = ""
docs_filepath = ""
part_list_file_name = ""
bom_file_name = ""
bom_designator_field_length = 11
bom_name_field_length = 35
part_list_designator_field_lenght = 15
part_list_name_field_lenght = 50

# ====================== Base functions ======================
def print_menu(menu, message):
    os.system("cls")
    for _, item in menu["data"].items():
        print(item["label"])
    if menu["hint"]:
        print(menu["hint"])
    if message:
        print("=> " + message + "\n")

def execute_menu_input(menu, choice) -> Tuple[Menu, str]:
    action = menu["data"][str(choice)]["action"]
    next_menu, message = action()
    return next_menu, message

def menu_exit():
    sys.exit(0)

def menu_back() -> Tuple[Menu, str]:
    message = ""
    return main_menu, message

# ====================== Main menu functions ======================
def menu_load_data() -> Tuple[Menu, str]:
    global input_directory, templates_directory, output_directory, found_files, df_groups
    message = ""
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
        message = f"ОШИБКА! Папка '{input_directory}' не обнаружена"
        return main_menu, message
    # Check if list is empty
    if not found_files:
        message = f"ОШИБКА! Не найдены excel файлы в папке input"
        return main_menu, message
    
    # Read groups.xlsx from templates directory to dataframe
    filepath = os.path.join(templates_directory, "groups.xlsx")
    if os.path.exists(filepath):
        df_groups, message = read_excel_file(filepath)
        if message:
            return main_menu, message
    else:
        message = f"ОШИБКА! Файл groups.xlsx не найден: {filepath}"
        return main_menu, message
    
    return load_menu, message

def menu_generate_data() -> Tuple[Menu, str]:
    global df_data, df_params, df_docs, df_groups, data_filepath, docs_filepath, \
        part_list_file_name, bom_file_name, PART_LIST_CONFIG, BOM_CONFIG, \
        templates_directory, output_directory
    message = ""

    # Check that dataframes have valid data
    if df_groups.empty or df_data.empty:
        message = "ОШИБКА! Сначала загрузите данные!"
        return main_menu, message
    columns_list = ['Key', 'Value']
    filepath = os.path.join(templates_directory, "groups.xlsx")
    message = check_dataframe(df_groups, columns_list, filepath)
    if message:
        return main_menu, message   
    columns_list = ['Designator', 'Name', 'Quantity', 'Decimal Number']
    message = check_dataframe(df_data, columns_list, data_filepath)
    if message:
        return main_menu, message   
    if not df_docs.empty: # optional dataframe
        columns_list = ['Format', 'Zone', 'Position', 'Decimal Number', 'Name', 'Quantity', 'Designator']
        message = check_dataframe(df_docs, columns_list, docs_filepath)
        if message:
            return main_menu, message
    
    # Create file name for part list
    part_list_file_name = create_document_filename(df_params, PART_LIST_CONFIG)
    # Create file name for bom
    bom_file_name = create_document_filename(df_params, BOM_CONFIG)

    # Copy part list template
    message = copy_rename_template(templates_directory, output_directory, part_list_file_name, PART_LIST_CONFIG)
    if message:
        return main_menu, message
    # Copy bom template
    message = copy_rename_template(templates_directory, output_directory, bom_file_name, BOM_CONFIG)
    if message:
        return main_menu, message

    return gen_menu, message

def menu_settings() -> Tuple[Menu, str]:
    message = ""
    return set_menu, message

# ====================== Load menu functions ======================
def menu_load_bom() -> Tuple[Menu, str]:
    global input_directory, data_filepath, found_files, df_data, df_params
    message = ""
    choice = get_input_file(found_files)
    data_filepath = os.path.join(input_directory, found_files[choice-1])
    print(f"Читаю файл c данными из Altium: {found_files[choice-1]}")
    # Read data and parameters from excel file
    df_data, df_params, message = read_altium_excel_file(data_filepath)
    if not message:
        message = "Файл прочитан успешно"    
    return load_menu, message        

def menu_load_docs() -> Tuple[Menu, str]:
    global input_directory, docs_filepath, found_files, df_docs
    message = ""
    choice = get_input_file(found_files)
    docs_filepath = os.path.join(input_directory, found_files[choice-1])
    print(f"Читаю файл с документацией для спецификации: {found_files[choice-1]}")
    df_docs, message = read_excel_file(docs_filepath)
    if not message:
        message = "Файл прочитан успешно"    
    return load_menu, message 

# ====================== Gen menu functions ======================
def menu_gen_excel_all() -> Tuple[Menu, str]:
    global df_data, df_docs, df_groups, df_params, part_list_file_name, bom_file_name, PART_LIST_CONFIG, BOM_CONFIG, \
         part_list_designator_field_lenght, part_list_name_field_lenght, bom_designator_field_length, bom_name_field_length
    # Clean part list line with empty Designator field
    df_clean_data = clean_part_list_non_des_fields(df_data)  
    # Sort part list
    df_part_list = combine_part_list_consecutive_components(df_clean_data)
    # Modify part list for template
    df_part_list_templated = modify_part_list_fields(df_part_list, part_list_designator_field_lenght, part_list_name_field_lenght)

    # Combine bom components
    df_bom = combine_bom_components(df_data)
    # Sort bom
    df_bom = sort_bom(df_bom, df_groups)
    # Concat docs and bom
    df_bom = concat_bom_and_docs(df_bom, df_docs)
    # Modify bom for template
    df_bom_templated = modify_bom_fields(df_bom, bom_designator_field_length, bom_name_field_length)

    # Write part list to template
    message = write_document_to_template(df_params, df_part_list_templated, part_list_file_name, PART_LIST_CONFIG)
    if message:
        return gen_menu, message
    # Write bom to template
    message = write_document_to_template(df_params, df_bom_templated, bom_file_name, BOM_CONFIG)
    if message:
        return gen_menu, message
    message = "Книги сохранены успешно"
    return gen_menu, message

def menu_gen_pdf_all():
    message = "Очень хочется, но еще не готово =)"
    return gen_menu, message

# ====================== Set menu functions ======================
def menu_set_designator_bom() -> Tuple[Menu, str]:
    global bom_designator_field_length
    choice = read_user_input("Введите количетсво символов для поля Примечание (спецификация): ", 1, 50)
    bom_designator_field_length = choice
    message = f"Новое количество символов для поля Примечание (спецификация) - {choice}"
    return set_menu, message
def menu_set_name_bom() -> Tuple[Menu, str]:
    global bom_name_field_length
    choice = read_user_input("Введите количетсво символов для поля Наименование (спецификация): ", 1, 100)
    bom_name_field_length = choice
    message = f"Новое количество символов для поля Наименование (спецификация) - {choice}"
    return set_menu, message
def menu_set_designator_part_list() -> Tuple[Menu, str]:
    global part_list_designator_field_lenght
    choice = read_user_input("Введите количетсво символов для поля Поз. обозначение (перечень элементов): ", 1, 50)
    part_list_designator_field_lenght = choice
    message = f"Новое количество символов для поля Поз. обозначение (перечень элементов) - {choice}"
    return set_menu, message
def menu_set_name_part_list() -> Tuple[Menu, str]:
    global part_list_name_field_lenght
    choice = read_user_input("Введите количетсво символов для поля Наименование (перечень элементов): ", 1, 100)
    part_list_name_field_lenght = choice
    message = f"Новое количество символов для поля Наименование (перечень элементов) - {choice}"
    return set_menu, message

# ====================== Dictionaries ======================
main_menu = {
    "data": {
        "1": {"label": "1. Загрузить данные", "action": menu_load_data},
        "2": {"label": "2. Сгенерировать файлы", "action": menu_generate_data},
        "3": {"label": "3. Настройки", "action": menu_settings},
        "4": {"label": "4. Выход", "action": menu_exit},
    },
    "menu_max": 4,
    "hint": (
        "----------------------------------------------------\n"
    )
}

load_menu = {
    "data": {
        "1": {"label": "1. Загрузить файл c данными из Altium", "action": menu_load_bom},
        "2": {"label": "2. Загрузить файл с документацией для спецификации", "action": menu_load_docs},
        "3": {"label": "3. Назад", "action": menu_back},
        "4": {"label": "4. Выход", "action": menu_exit},
    },
    "menu_max": 4,
    "hint": (
        "----------------------------------------------------\n"
        "Загрузите файл с данными из Altium. Данные необходимо сгенерировать по шаблону.\n"
        "Шаблон находится в папке templates/altium_template.xlsx\n"
        "[Опционально] Загрузите файл с документацией для спецификации. Данные из этого файла будут вставлены в начало спецификации.\n"
        "Шаблон находится в папке examples/docs_for_sp.xlsx\n"
        "----------------------------------------------------\n"
    )
}

gen_menu = {
    "data": {
        "1": {"label": "1. Сгенерировать перечень элементов и спецификацию в excel", "action": menu_gen_excel_all},
        "2": {"label": "2. Сгенерировать перечень элементов и спецификацию в pdf", "action": menu_gen_pdf_all},
        "3": {"label": "3. Назад", "action": menu_back},
        "4": {"label": "4. Выход", "action": menu_exit},
    },
    "menu_max": 4,
    "hint": (
        "----------------------------------------------------\n"
        "Сгенерированные файлы находятся в папке output.\n"
        "Удалять существующие файлы не нужно, они перепишутся автоматически.\n"
        "----------------------------------------------------\n"
    )
}

set_menu = {
    "data": {
        "1": {"label": "1. Изменить количество символов в поле Примечание (спецификация)", "action": menu_set_designator_bom},
        "2": {"label": "2. Изменить количество символов в поле Наименование (спецификация)", "action": menu_set_name_bom},
        "3": {"label": "3. Изменить количество символов в поле Поз. обозначение (перечень элементов)", "action": menu_set_designator_part_list},
        "4": {"label": "4. Изменить количество символов в поле Наименование (перечень элементов)", "action": menu_set_name_part_list},
        "5": {"label": "5. Назад", "action": menu_back},
        "6": {"label": "6. Выход", "action": menu_exit},
    },
    "menu_max": 6,
    "hint": (
        "----------------------------------------------------\n"
        "Изменить количество символов в соответствующих полях можно, если неправильно формируются переносы:\n"
        "текст не влезает в поле или остается слишком много свободного места.\n"
        "[Количество символов по умолчанию]\n"
        "  Примечание (спецификация) - 11\n"
        "  Наименование (спецификация) - 35\n"
        "  Поз. обозначение (перечень элементов) - 15\n"
        "  Наименование (перечень элементов) - 50\n"
        "----------------------------------------------------\n"
    )
}
