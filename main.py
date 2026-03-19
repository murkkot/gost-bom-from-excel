import sys
import logging
import argparse

import config
from excel import *
from part_list import *
from bom import *
from menu import *
from auxiliary import hide_cursor, show_cursor
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

    hide_cursor()
    try:
        current_menu = main_menu
        if config.DEBUG:
            message = f"gost-bom-from-excel v.{__version__} >>> DEBUG mode"
        else:
            message = f"gost-bom-from-excel v.{__version__}\nИспользуйте ↑/↓ для навигации, Enter для выбора"

        first_clear = True
        while True:
            index = 1
            confirm = False
            while not confirm:
                print_menu(current_menu, message, index, first_clear)
                first_clear = False
                index, confirm = read_user_input(index, 1, current_menu["menu_max"])
            new_menu, message = execute_menu_input(current_menu, index)
            if new_menu is not None:
                current_menu = new_menu
                first_clear = True
    finally:
        sys.stdout.write('\033[2J\033[H\033[0m')  # clear + home + reset (one write)
        show_cursor()
        sys.stdout.flush()