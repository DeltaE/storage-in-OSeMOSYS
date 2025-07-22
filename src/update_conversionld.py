import pandas as pd
import numpy as np

def conversionld(timeslices, representative_days, output_file, label='DAYTYPE'):
 
    timeslice_vector = np.arange(1, timeslices + 1)

    daytype_vector = np.repeat(np.arange(1, representative_days + 1), timeslices//representative_days)

    value_vector = np.ones(timeslices)

    df = pd.DataFrame({
        'TIMESLICE': timeslice_vector,
        label: daytype_vector,
        'VALUE': value_vector
    })

    df.to_csv(output_file, index=False)

    return output_file