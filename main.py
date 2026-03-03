import sys
import logging
import argparse

import config
from excel import *
from part_list import *
from bom import *
from menu import *
from _version import __version__

def setup_logging(debug=False):
    """Configure logging based on debug flag"""
    log_level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger = logging.getLogger(__name__)
    
    return logger


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=f"gost-bom-from-excel v.{__version__}")
                                     
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    config.DEBUG = args.debug
    
    # Setup logging with debug flag
    logger = setup_logging(args.debug)
    #logger.debug("Entering main function")

    current_menu = main_menu
    if config.DEBUG:
        message = f"gost-bom-from-excel v.{__version__} >>> DEBUG mode"
    else:
        message = f"gost-bom-from-excel v.{__version__}"
    while True:
        print_menu(current_menu, message)
        choice = read_user_input("Введите номер пункта меню: ", 1, current_menu["menu_max"])
        new_menu, message = execute_menu_input(current_menu, choice)
        if new_menu is not None:
            current_menu = new_menu