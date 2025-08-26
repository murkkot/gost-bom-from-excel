import re
import pandas as pd
from auxiliary import *

# Sort dataset for parts list (PE3)
def combine_part_list_consecutive_components(df):
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

# Modify dataframe's field with according lenght to fit the template
def modify_part_list_fields(dataset):

    DEGIGNATOR_FIELD_LENGTH = 15
    NAME_FIELD_LENGTH = 50

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
    
    df_result = pd.DataFrame(new_data, columns=dataset.columns)
    # Replace all NaN values with an empty string
    df_result = df_result.fillna('')
    return df_result