import re
import pandas as pd

# Sort dataset for parts list (PE3)
def combine_consecutive_components(df):
    if df.empty:
        return pd.DataFrame(columns=['Designator', 'Name', 'Quantity'])
    
    combined_data = []
    current_name = df.iloc[0]['Name']
    current_designators = [str(df.iloc[0]['Designator'])]
    current_quantity = df.iloc[0]['Quantity']
    
    for i in range(1, len(df)):
        if df.iloc[i]['Name'] == current_name:
            current_designators.append(str(df.iloc[i]['Designator']))
            current_quantity += df.iloc[i]['Quantity']
        else:
            processed_designators = process_designator_sequence(current_designators)
            combined_data.append({
                'Designator': processed_designators,
                'Name': current_name,
                'Quantity': current_quantity
            })
            current_name = df.iloc[i]['Name']
            current_designators = [str(df.iloc[i]['Designator'])]
            current_quantity = df.iloc[i]['Quantity']
    
    processed_designators = process_designator_sequence(current_designators)
    combined_data.append({
        'Designator': processed_designators,
        'Name': current_name,
        'Quantity': current_quantity
    })
    
    return pd.DataFrame(combined_data)

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
            test_segment = current_segment + "," + part + ","
        else:
            test_segment = part + ","
            
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

# ПЭ3 Наименование <= 38
# СП Наименование <= 23
def modify_name_field_length(field, length):
    result = []
    current_segment = ""
    fields = field.split(' ')
    
    for i, part in enumerate(fields):
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

# Modify dataframe's field with according lenght to fit the template
def modify_part_list(dataset):

    DEGIGNATOR_FIELD_LENGTH = 10
    NAME_FIELD_LENGTH = 38

    new_data = []
    
    for _, row in dataset.iterrows():
        designator = row['Designator']
        designator_parts = modify_designator_field_length(designator, DEGIGNATOR_FIELD_LENGTH)
        name = row['Name']
        name_parts = modify_name_field_length(name, NAME_FIELD_LENGTH)

        num_rows = max(len(designator_parts), len(name_parts))
        
        for i in range(num_rows):
            new_row = row.copy()
            
            # Designator: Use current part or empty if no more splits
            new_row['Designator'] = designator_parts[i] if i < len(designator_parts) else ''
            
            # Name: Use current part or empty if no more splits
            new_row['Name'] = name_parts[i] if i < len(name_parts) else ''
            
            # Quantity: Keep only for the first row, empty for others
            new_row['Quantity'] = row['Quantity'] if i == 0 else ''
            
            new_data.append(new_row)
    
    return pd.DataFrame(new_data, columns=dataset.columns)