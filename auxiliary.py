import re
import sys

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
        print(f"В файле {filename} отсутствуют столбцы: {missing}")
        input("Нажмите ENTER для выхода")
        sys.exit(1)