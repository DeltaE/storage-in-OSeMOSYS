import pandas as pd
import numpy as np

def conversionldc(chronological_sequence, representative_days, days_in_year, output_file):
    
    # 3 VECTOR CREATION #
    # Tile: [1, 2,..., timeslice, 1, 2, ..., timeslice ... ] repeated (Chronological timeslice) times
    Representative_days_vector = np.tile(np.arange(1, len(representative_days) + 1), days_in_year)
    
    # Repeat: [1, 1, 1, 1, ... (timeslice) times, 2, 2, 2, 2, ... (timeslice) times, ... (Chronological timeslices), (Chronological timeslices), ... (timeslice) times]
    chronological_days_vector = np.repeat(np.arange(1, days_in_year + 1), len(representative_days))
    
    # Vector (days_in_year * blocks_per_day * timeslices) with zeros
    values_vector = np.zeros(days_in_year * len(representative_days), dtype=int)

    # Loops #
    # Mapeia cada dia em chronological_sequence para o seu correspondente bloco de timeslices
    for day_idx, rep_day in enumerate(chronological_sequence):
        # O índice em representative_days determina o bloco de timeslices
        representative_days_index = representative_days.index(rep_day)
        index = representative_days_index + (day_idx * len(representative_days))
        values_vector[index] = 1
    
    # Cria o DataFrame com as colunas corretas
    df = pd.DataFrame({
        'DAYTYPE': Representative_days_vector,
        'DAYSCRO': chronological_days_vector,
        'VALUE': values_vector
    })

    # Ordena o DataFrame baseado na coluna TIMESLICE_NUMBER e reordena o índice
    df = df.sort_values(by=['DAYTYPE', 'DAYSCRO']).reset_index(drop=True)

    # Save to CSV
    df.to_csv(output_file, index=False)

    return output_file