import pandas as pd
import numpy as np
import re

def combine_bom_components(df):
    if df.empty:
        return pd.DataFrame(columns=['Decimal Number', 'Name', 'Quantity', 'Designator'])
    
    # Combine components with the same name by summing quantities and concatenating designators with comma separator.

    # Group by Name and aggregate
    result = df.groupby('Name').agg({
        'Designator': lambda x: ','.join(sorted(x)),  # sorted for consistent order
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
    # Create uniq list
    uniq_groups = []
    seen_groups = set() # Using set() for faster lookup
    # Iterate over dataframe
    for idx, row in df_mid.iterrows():
        if row['Group'] not in seen_groups:
            # Append empty row
            df_result.loc[df_result.shape[0]] = np.nan
            # Append another empty row
            df_result.loc[df_result.shape[0]] = np.nan
            # Add group name to the Name field
            df_result.loc[df_result.index[-1], 'Name'] = row['Group']
            # Add group name to uniq_groups
            uniq_groups.append(row['Group'])
            seen_groups.add(row['Group'])
            # Append current row to df_result
            df_result.loc[df_result.shape[0]] = row
        else:
            # Append current row to df_result
            df_result.loc[df_result.shape[0]] = row
    # Drop column Group
    df_result.drop(columns=['Group'], inplace=True)
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