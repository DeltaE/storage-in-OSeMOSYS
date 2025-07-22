import pandas as pd
import numpy as np

def conversionlh(timeslices, blocksperday, output_file):
 
    timeslice_vector = np.arange(1, timeslices + 1)

    dailytimebracket_vector = np.tile(np.arange(1, blocksperday + 1), timeslices // blocksperday + 1)[:timeslices]

    value_vector = np.ones(timeslices)

    df = pd.DataFrame({
        'TIMESLICE': timeslice_vector,
        'DAILYTIMEBRACKET': dailytimebracket_vector,
        'VALUE': value_vector
    })

    df.to_csv(output_file, index=False)

    return output_file