
import numpy as np
import pandas as pd

def conversionlts(blocks_per_day, chronological_timeslices, timeslices, chronological_sequence, representative_days, output_file):

    # 3 VECTOR CREATION #
    # Tile: [1, 2,..., timeslice, 1, 2, ..., timeslice ... ] repeated (Chronological timeslice) times
    timeslice_vector = np.tile(np.arange(1, timeslices + 1), chronological_timeslices)
    
    # A sequência CHRONOLOGICAL_TIME contém strings como 'D1HB1', 'D1HB2', ..., repetidas para o total de timeslices. Esse formato da pau no otoole.
    #chronological_time = np.repeat([f"D{day:03d}HB{block:02d}" for day in range(1, days_in_year + 1)
    #                                for block in range(1, blocks_per_day + 1)], timeslices)
    
    # Repeat: [1, 1, 1, 1, ... (timeslice) times, 2, 2, 2, 2, ... (timeslice) times, ... (Chronological timeslices), (Chronological timeslices), ... (timeslice) times]
    chronological_time_vector = np.repeat(np.arange(1, chronological_timeslices + 1), timeslices)
    
    # Vector (days_in_year * blocks_per_day * timeslices) with zeros
    values_vector = np.zeros(chronological_timeslices * timeslices, dtype=int)
    
    # Loops #
    # Mapeia cada dia em chronological_sequence para o seu correspondente bloco de timeslices
    for day_idx, rep_day in enumerate(chronological_sequence):
        # O índice em representative_days determina o bloco de timeslices
        timeslice_block_start = representative_days.index(rep_day) * blocks_per_day
        
        # Define '1' nos timeslices correspondentes para o dia específico em chronological_time
        for block in range(blocks_per_day):
            timeslice_number = timeslice_block_start + block
            index = (day_idx * blocks_per_day + block) * timeslices + timeslice_number
            values_vector[index] = 1  # Marca com '1' a posição correta
    
    # Cria o DataFrame com as colunas corretas
    df = pd.DataFrame({
        'TIMESLICE': timeslice_vector,
        'TIMESLICECRO': chronological_time_vector,
        'VALUE': values_vector
    })

    # Ordena o DataFrame baseado na coluna TIMESLICE_NUMBER e reordena o índice
    df = df.sort_values(by=['TIMESLICE', 'TIMESLICECRO']).reset_index(drop=True)

    # Save to CSV
    df.to_csv(output_file, index=False)

    return output_file
