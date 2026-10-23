import pandas as pd

#Generate a list from 1 to the length and save to a CSV file
#Used to update timeslice and daytype
def new_list(length, output_file):
    value = list(range(1, length + 1))
    
    df = pd.DataFrame({
        'VALUE': value
    })

    # Save to CSV
    df.to_csv(output_file, index=False)

    return output_file