import re, os, sys, logging
import config
import keyboard

logger = logging.getLogger(__name__)

# Process designator sequences according to GOST
def process_designator_sequence(designators):
    if len(designators) == 1:
        return designators[0]
    
    # Parse all designators into (prefix, number) tuples
    parsed = []
    for d in designators:
        match = re.match(r'([^\d]*)(\d+)', d)
        if match:
            prefix, num = match.groups()
            parsed.append((prefix, int(num)))
        else:
            return ',  '.join(designators)
    
    # Group into consecutive sequences
    groups = []
    current_group = [designators[0]]
    
    for i in range(1, len(designators)):
        prev_prefix, prev_num = parsed[i-1]
        curr_prefix, curr_num = parsed[i]
        
        if (curr_prefix == prev_prefix) and (curr_num == prev_num + 1):
            current_group.append(designators[i])
        else:
            groups.append(current_group)
            current_group = [designators[i]]
    
    groups.append(current_group)
    
    # Format each group appropriately
    formatted_groups = []
    for group in groups:
        if len(group) >= 3:
            formatted_groups.append(f"{group[0]}...{group[-1]}")
        else:
            formatted_groups.append(",".join(group))
    
    return ",".join(formatted_groups)

# Modify fields length to fit in template
# ПЭ3 Поз. обозн. <= 10
# СП Примечание (поз. обозн.) <= 11
def modify_designator_field_length(field, length):
    result = []
    current_segment = ""
    fields = field.split(',')
   
    for i, part in enumerate(fields):
        # Check if adding this part would exceed length
        if current_segment:
            test_segment = current_segment + "," + part
        else:
            test_segment = part
            
        if len(test_segment) <= length:
            current_segment = test_segment
        else:
            if current_segment:  # Only add if not empty
                result.append(current_segment + ",")
            current_segment = part
            
    # Add the last segment if it exists
    if current_segment:
        result.append(current_segment)
        
    return result

# ПЭ3 Наименование <= 38
# СП Наименование <= 23
def modify_name_field_length(field, length):
    result = []
    current_segment = ""
    fields = field.split(' ')
    fields = reformat_names_list(fields)
    
    for part in fields:
        # Check if adding this part would exceed length
        if current_segment:
            test_segment = current_segment + " " + part
        else:
            test_segment = part
            
        if len(test_segment) <= length:
            current_segment = test_segment
        else:
            if current_segment:  # Only add if not empty
                result.append(current_segment)
            current_segment = part
            
    # Add the last segment if it exists
    if current_segment:
        result.append(current_segment)
        
    return result

# Check if a string is a number, allowing for a comma as a decimal separator
def is_numeric_with_comma(s):
    # Pattern to match an integer or a number with a single comma decimal.
    numeric_pattern = re.compile(r'^\d+(,\d+)?$')
    
    if numeric_pattern.match(s):
        return True
    
    # Check for percentage format like '5%'
    if s.endswith('%'):
        # Check if the part before '%' is a valid number (with comma)
        return bool(numeric_pattern.match(s[:-1]))
        
    return False


# Reformat names list to exclude units from numbers separation
def reformat_names_list(string_list):
    if not string_list:
        return []

    result = [] 
    i = 0
    while i < len(string_list):
        current_item = string_list[i]
        
        # Check if there is a next item to look at
        if (i + 1) < len(string_list):
            next_item = string_list[i + 1]   
            # Condition: Glue items if the current one is a number AND the next one is NOT a number
            if is_numeric_with_comma(current_item) and not is_numeric_with_comma(next_item):
                # Join the number and its unit
                result.append(f"{current_item} {next_item}")
                i += 2 
                continue
        # If the condition is not met, or it's the last item, append the current item as is
        result.append(current_item)
        i += 1
        
    return result

# Check if df contains needed columns
def check_dataframe(df, column_list, filename):
    missing = set(column_list) - set(df.columns)
    if missing:
        message = f"ОШИБКА! В файле {filename} отсутствуют столбцы: {missing}"
    else:
        message = ""
    return message

# Get input file from user input
def get_input_file(files):
    # Print header (3 lines) - fixed to use write for consistency
    sys.stdout.write("\033[1m Главное меню - Загрузки - Загрузить excel файлы\033[0m\n")
    sys.stdout.write("----------------------------------------------------\n")
    sys.stdout.write("Найдены следующие excel файлы:\n")
    
    # Print a blank line for spacing
    sys.stdout.write("\n")
    
    min_val = 1
    max_val = len(files)
    index = 1
    width = max(len(f) for f in files) + 10
    
    # Menu starts at line 5
    menu_start_line = 5
    
    sys.stdout.flush()
    
    while True:
        # Go to menu start (no save/restore needed)
        sys.stdout.write(f'\033[{menu_start_line};1H')
        
        # Print all filenames with current selection
        for idx, filename in enumerate(files, 1):
            sys.stdout.write('\033[2K')  # Clear the current line
            if index == idx:
                sys.stdout.write(f"\033[7m {filename.ljust(width)}\033[0m\n")
            else:
                sys.stdout.write(f" {filename.ljust(width)}\n")
        
        sys.stdout.flush()
        
        event = keyboard.read_event(suppress=False)
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'up':
                if index == min_val:
                    index = max_val
                else:
                    index -= 1
            elif event.name == 'down':
                if index == max_val:
                    index = min_val
                else:
                    index += 1
            elif event.name == 'enter':
                sys.stdout.write(f'\033[{menu_start_line};1H')
                return index

# Read user input
def read_user_input(index, min, max):
    confirm = False
    while True:
        event = keyboard.read_event(suppress=False)
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'up':
                if index == min:
                    index = max
                else:
                    index -= 1
                return index, confirm
            elif event.name == 'down':
                if index == max:
                    index = min
                else:
                    index += 1
                return index, confirm
            elif event.name == 'enter':
                confirm = True
                return index, confirm

def export_pdf(excel_path, pdf_path):
    message = ""
    # Check target path permissions
    if os.path.exists(pdf_path) and not os.access(pdf_path, os.W_OK):
        message = f"Нет прав на перезапись {pdf_path}"
        return message
    elif not os.access(os.path.dirname(pdf_path), os.W_OK):
        message = f"Нет прав на запись в папку {pdf_path}"
        return message
    # Check for windows platform
    if sys.platform != "win32":
        message = f"PDF export skipped on {sys.platform}"
        return message
    
    try:
        import win32com.client
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False

        workbook = excel.Workbooks.Open(excel_path)

        # Export all printable sheets
        print(f"Записываю {pdf_path}")
        workbook.ExportAsFixedFormat(
            Type=0,              # 0 = PDF
            Filename=pdf_path,
            Quality=0,           # 0 = standard, 1 = minimum
            IncludeDocProperties=True,
            IgnorePrintAreas=False,
        )

        workbook.Close(SaveChanges=False)
        excel.Quit()

        return message
    except Exception as e:
        message = f"Ошибка экспорта: {e}"
        return message
    
def _is_filename(filename):
    # Invalid Windows filename characters
    invalid_chars = '<>:"/\\|?*'
    
    # Replace each invalid character with "-"
    for char in invalid_chars:
        filename = filename.replace(char, "-")
    
    # Replace multiple consecutive dashes with a single dash
    filename = re.sub(r'-+', '-', filename)
    
    # Remove leading/trailing dashes and spaces
    filename = filename.strip('-').strip()
    
    # Ensure filename is not empty after sanitization
    if not filename:
        filename = "unnamed"
    
    return filename

def hide_cursor():
    """Hide the terminal cursor"""
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()

def show_cursor():
    """Show the terminal cursor"""
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()