import pandas as pd
import pandas.testing as pdt
from part_list import combine_part_list_consecutive_components, modify_part_list_fields

def test_combine_part_list_consecutive_components():
    # Tests the combine_part_list_consecutive_components function with a sample BOM
    input_data = {
    'Designator': ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 
                   'C11', 'C12', 'C13', 'C14', 'C16', 'C18', 'C19', 'C20', 'C21'],
    'Name': [
        'Конденсатор чип 0805 0,1 мкФ 50В X7R',
        'Конденсатор чип 1210 4,7 мкФ 50В X7R',
        'Конденсатор чип 1210 4,7 мкФ 50В X7R',
        'Конденсатор чип 1210 4,7 мкФ 50В X7R',
        'Конденсатор чип 0805 0,1 мкФ 50В X7R',
        'Конденсатор чип 0805 220 пФ 50В X7R',
        'Конденсатор чип 0805 220 пФ 50В X7R',
        'Конденсатор чип 0805 2200 пФ 50В X7R',
        'Конденсатор чип 0805 2200 пФ 50В X7R',
        'Конденсатор танталовый D 10 мкФ 50В',
        'Конденсатор танталовый D 10 мкФ 50В',
        'Конденсатор чип 0805 0,1 мкФ 50В X7R',
        'Конденсатор чип 0805 0,1 мкФ 50В X7R',
        'Конденсатор чип 0805 0,1 мкФ 50В X7R',
        'Конденсатор чип 0805 0,1 мкФ 50В X7R',
        'Конденсатор чип 0805 0,1 мкФ 50В X7R',
        'Конденсатор чип 0805 0,1 мкФ 50В X7R',
        'Конденсатор чип 0805 0,1 мкФ 50В X7R',
        'Конденсатор чип 0805 0,1 мкФ 50В X7R'
    ],
    'Quantity': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
}  
    expected_data = {
    'Designator': [
        'C1', 
        'C2...C4', 
        'C5', 
        'C6,C7', 
        'C8,C9', 
        'C10,C11', 
        'C12...C14,C16,C18...C21'
    ],
    'Name': [
        'Конденсатор чип 0805 0,1 мкФ 50В X7R',
        'Конденсатор чип 1210 4,7 мкФ 50В X7R',
        'Конденсатор чип 0805 0,1 мкФ 50В X7R',
        'Конденсатор чип 0805 220 пФ 50В X7R',
        'Конденсатор чип 0805 2200 пФ 50В X7R',
        'Конденсатор танталовый D 10 мкФ 50В',
        'Конденсатор чип 0805 0,1 мкФ 50В X7R'
    ],
    'Quantity': [1, 3, 1, 2, 2, 2, 8]
}
    input_df = pd.DataFrame(input_data)
    expected_df = pd.DataFrame(expected_data)

    actual_df = combine_part_list_consecutive_components(input_df)
    
    pdt.assert_frame_equal(actual_df, expected_df)

def test_combine_part_list_consecutive_components_empty_dataframe():
    # Tests the function with an empty DataFrame
    input_df = pd.DataFrame(columns=['Designator', 'Name', 'Quantity'])
    expected_df = pd.DataFrame(columns=['Designator', 'Name', 'Quantity'])
    
    actual_df = combine_part_list_consecutive_components(input_df)

    pdt.assert_frame_equal(actual_df, expected_df)

def test_modify_part_list_fields():
    # Tests the modify_part_list_fields function with sample BOM
    input_data = {
        'Designator': [
            'C1', 'C2...C4', 'C5', 'C6,C7', 'C8,C9', 'C10,C11', 
            'C12...C14,C16,C18...C21'
        ],
        'Name': [
            'Конденсатор чип 0805 0,1 мкФ 50В X7R', 
            'Конденсатор чип 1210 4,7 мкФ 50В X7R',
            'Конденсатор чип 0805 0,1 мкФ 50В X7R', 
            'Конденсатор чип 0805 220 пФ 50В X7R',
            'Конденсатор чип 0805 2200 пФ 50В X7R', 
            'Конденсатор танталовый D 10 мкФ 50В',
            'Конденсатор чип 0805 0,1 мкФ 50В X7R'
        ],
        'Quantity': [1, 3, 1, 2, 2, 2, 8]
    }
    expected_data = {
        'Designator': [
            'C1', 'C2...C4', 'C5', 'C6,C7', 'C8,C9', 'C10,C11', 
            'C12...C14,C16,', 'C18...C21'
        ],
        'Name': [
            'Конденсатор чип 0805 0,1 мкФ 50В X7R', 
            'Конденсатор чип 1210 4,7 мкФ 50В X7R',
            'Конденсатор чип 0805 0,1 мкФ 50В X7R', 
            'Конденсатор чип 0805 220 пФ 50В X7R',
            'Конденсатор чип 0805 2200 пФ 50В X7R', 
            'Конденсатор танталовый D 10 мкФ 50В',
            'Конденсатор чип 0805 0,1 мкФ 50В X7R',
            ''
        ],
        'Quantity': [1, 3, 1, 2, 2, 2, 8, '']
    }
    input_df = pd.DataFrame(input_data)
    expected_df = pd.DataFrame(expected_data)

    actual_df = modify_part_list_fields(input_df)
    
    pdt.assert_frame_equal(actual_df.reset_index(drop=True), expected_df.reset_index(drop=True))