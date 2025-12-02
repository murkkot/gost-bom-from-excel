import sys

from excel import *
from part_list import *
from bom import *
from menu import *
from _version import __version__

if __name__ == "__main__":
    # Print version
    print(f"gost-bom-from-excel v.{__version__}")
    print("--------------------------------------")

    current_menu = main_menu
    message = ""
    while True:
        print_menu(current_menu, message)
        choice = read_user_input("Введите номер пункта меню: ", 1, current_menu["menu_max"])
        new_menu, message = execute_menu_input(current_menu, choice)
        if new_menu is not None:
            current_menu = new_menu