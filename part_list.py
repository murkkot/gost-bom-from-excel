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
            return ', '.join(designators)
    
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
            formatted_groups.append(", ".join(group))
    
    return ", ".join(formatted_groups)