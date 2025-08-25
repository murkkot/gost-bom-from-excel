import pandas as pd
import numpy as np
import re
from auxiliary import *
from typing import List

def natural_sort_key(s: str) -> List:

    # Create a sort key for natural sorting. 
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def combine_bom_components(df):
    if df.empty:
        return pd.DataFrame(columns=['Decimal Number', 'Name', 'Quantity', 'Designator'])
    
    # Combine components with the same name by summing quantities and concatenating designators with comma separator.

    # Group by Name and aggregate
    result = df.groupby('Name').agg({
        'Designator': lambda x: ','.join(sorted(x, key=natural_sort_key)),  # sorted for consistent order
        'Quantity': 'sum',
        'Decimal Number': lambda x: x.iloc[0] if x.notna().any() else pd.NA
    }).reset_index()  
    # Reorder columns
    result = result[['Decimal Number', 'Name', 'Quantity', 'Designator']]
    return result

def sort_bom(df_data, df_groups):

    # Create a copy to avoid modifying the original dataframe
    df_mid = df_data.copy()
    # Append new columnd with group letter
    df_mid['Group'] = df_mid['Designator'].apply(extract_group)
    # Create a mapping from key-value dataframe
    key_value_map = dict(zip(df_groups['Key'], df_groups['Value']))
    # Replace the Group column with values from the mapping
    df_mid['Group'] = df_mid['Group'].map(key_value_map).fillna(df_mid['Group'])
    # Change group to "Сборочные единицы" if Decimal Number has a value
    # Check if Decimal Number is not NaN and not empty string
    df_mid.loc[df_mid['Decimal Number'].notna() & (df_mid['Decimal Number'] != ''), 'Group'] = 'Сборочные единицы'
    # Separate assembly units and other components
    assembly_df = df_mid[df_mid['Group'] == 'Сборочные единицы'].sort_values(by='Name')
    other_df = df_mid[df_mid['Group'] != 'Сборочные единицы'].sort_values(by=['Group', 'Name'])
    # Concatenate with assembly units first
    df_mid = pd.concat([assembly_df, other_df]).reset_index(drop=True)
    
    # Create empty dataframe
    df_result = pd.DataFrame(columns=['Decimal Number', 'Name', 'Quantity', 'Designator', 'Group'])
    # Change the column's dtype to 'object'
    df_result['Name'] = df_result['Name'].astype(object)
    # # Use a list to collect rows for the final DataFrame
    result_rows = []
    seen_groups = set() # Using set() for faster lookup
    # Iterate over dataframe
    for _, row in df_mid.iterrows():
        # Reformat designators according to GOST
        # row['Designator'] = process_designator_sequence(row['Designator'])
        if row['Group'] not in seen_groups:
            # Add empty rows and the group header
            result_rows.append([np.nan, np.nan, np.nan, np.nan])
            result_rows.append([np.nan, row['Group'], np.nan, np.nan])
            seen_groups.add(row['Group'])
        # Process designator sequence in row
        current_designators = row['Designator']
        designator_list = current_designators.split(',')
        processed_designators = process_designator_sequence(designator_list)
        row['Designator'] = processed_designators
        # Append the current row's data
        result_rows.append(row[['Decimal Number', 'Name', 'Quantity', 'Designator']].tolist())

    # Create the final DataFrame from the list of rows
    df_result = pd.DataFrame(result_rows, columns=['Decimal Number', 'Name', 'Quantity', 'Designator'])

    return df_result

# Extract the first two letters from Designator to identify groups
def extract_group(designator):
    if pd.isna(designator):
        return None
    # Get the first letters (like 'VD', 'XP', 'L')
    designators = designator.split(',')
    first_designator = designators[0].strip()
    result = re.match(r"^[A-Za-z]+", first_designator).group()
    return result

# Modify dataframe's field with according lenght to fit the template
def modify_bom_fields(dataset):

    DEGIGNATOR_FIELD_LENGTH = 11
    NAME_FIELD_LENGTH = 23

    new_data = []
    
    for _, row in dataset.iterrows():
        designator = row['Designator']
        name = row['Name']

        # If designator is not a string, treat it as an empty one
        if isinstance(designator, str) and pd.notna(designator):
            designator_parts = modify_designator_field_length(designator, DEGIGNATOR_FIELD_LENGTH)
        else:
            designator_parts = ['']

        # If name is not a string, treat it as an empty one
        if isinstance(name, str) and pd.notna(name):
            name_parts = modify_name_field_length(name, NAME_FIELD_LENGTH)
        else:
            name_parts = ['']

        num_rows = max(len(designator_parts), len(name_parts))
        
        for i in range(num_rows):
            new_row = row.copy()
            
            # Designator: Use current part or empty if no more splits
            new_row['Designator'] = designator_parts[i] if i < len(designator_parts) else ''
            
            # Name: Use current part or empty if no more splits
            new_row['Name'] = name_parts[i] if i < len(name_parts) else ''
            
            # Quantity: Keep only for the first row, empty for others
            new_row['Quantity'] = row['Quantity'] if i == 0 else ''

            # Decimal Number: Keep only for the first expanded row
            new_row['Decimal Number'] = row['Decimal Number'] if i == 0 else ''
            
            new_data.append(new_row)

    # Reconstruct the DataFrame from the list of new rows
    if not new_data:
        return pd.DataFrame(columns=dataset.columns)
    
    return pd.DataFrame(new_data)[dataset.columns.tolist()]
    
    #return pd.DataFrame(new_data, columns=dataset.columns)