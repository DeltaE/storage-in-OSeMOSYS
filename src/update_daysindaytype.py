import pandas as pd
import numpy as np
from collections import Counter

def daysindaytype(representative_days, chronological_sequence, output_file):
    season_vector = np.repeat('1', len(representative_days))
    daytype_vector = np.arange(1, len(representative_days) + 1)
    year_vector = np.repeat('2010', len(representative_days))
    

    # Contar a frequência de cada dia representativo no vetor chronological_sequence
    count = Counter(chronological_sequence)
    value_vector = [count[day] for day in representative_days]

    # Criar o DataFrame
    df = pd.DataFrame({
        'SEASON': season_vector,
        'DAYTYPE':daytype_vector,
        'YEAR': year_vector,
        'VALUE': value_vector
    })

    # Salvar o DataFrame em um arquivo CSV
    df.to_csv(output_file, index=False)

    return output_file
