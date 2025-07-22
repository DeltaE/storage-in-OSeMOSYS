import pandas as pd
from pathlib import Path
from . import utilities as utils

def new_list(length:int, output_file:str|Path):
    """
    Generates a list of integers from 1 to the specified length, saves it as a CSV file, and returns the output file path. Used to update timeslice and daytype.
    
    Parameters:
        length (int): The number of integers to include in the list.
        output_file (str): The file path where the CSV will be saved.
    Returns:
        str: The path to the output CSV file.
        
    The generated CSV will contain a single column named 'VALUE' with integers from 1 to 'length' (inclusive).
    
    """
    value = list(range(1, length + 1))
    
    df = pd.DataFrame({
        'VALUE': value
    })

    # Ensure the output directory exists
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    utils.print_update(level=2, message=f" {__file__} | New list created with {length} entries at {output_file}")
    # return output_file
    return df