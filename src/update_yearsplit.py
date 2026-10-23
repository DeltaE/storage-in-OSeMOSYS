import pandas as pd
import numpy as np
from collections import Counter

def yearsplit(timeslices, representative_days, chronological_sequence, days_in_year, output_file):
    timeslice_vector = np.arange(1, timeslices + 1)
    year_vector = np.repeat('2010', timeslices)

    # Contar a frequência de cada dia representativo no vetor chronological_sequence
    count = Counter(chronological_sequence)
    count_representative_days = {day: count[day] for day in representative_days}
    
    # Calcular o número de repetições por dia representativo
    blocks_per_day = timeslices // len(representative_days)
    value_vector = []

    # para cada dia representativo, o year_split -é = (repetição do dia representativo * 24/blocks_per_day) / (365*24)
    # como 24 corta com 24, fica = (repetição do dia representativo / blocks_per_day) / (365) 
    for day in representative_days:
        year_split = count_representative_days[day] / blocks_per_day / days_in_year
        value_vector.extend([year_split] * blocks_per_day)
    
    value_vector = np.array(value_vector)

    # Criar o DataFrame
    df = pd.DataFrame({
        'TIMESLICE': timeslice_vector,
        'YEAR': year_vector,
        'VALUE': value_vector
    })

    # Salvar o DataFrame em um arquivo CSV
    df.to_csv(output_file, index=False)

    return output_file
