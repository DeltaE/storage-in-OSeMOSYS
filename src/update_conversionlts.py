
import numpy as np
import pandas as pd

def conversionlts(blocks_per_day, chronological_timeslices, timeslices, chronological_sequence, representative_days, output_file):

    # 3 VECTOR CREATION #
    # Tile: [1, 2,..., timeslice, 1, 2, ..., timeslice ... ] repeated (Chronological timeslice) times
    timeslice_vector = np.tile(np.arange(1, timeslices + 1), chronological_timeslices)
    
    
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


def conversionlts_sparse(blocks_per_day, chronological_sequence, representative_days, output_file):
    """Write only the non-zero entries (VALUE == 1) of the Conversionlts mapping.

    Equivalent input for intraday_kotzur(), which keeps only VALUE == 1 rows, but avoids the
    dense (365*b) x (k*b) table (about 77 million rows at k365h1). This also removes the
    dependency of the Kotzur reconstruction on running Model_Cluster first.
    """
    rows = []
    for day_idx, rep_day in enumerate(chronological_sequence):
        start = representative_days.index(rep_day) * blocks_per_day
        for block in range(blocks_per_day):
            rows.append((start + block + 1, day_idx * blocks_per_day + block + 1, 1))
    df = pd.DataFrame(rows, columns=['TIMESLICE', 'TIMESLICECRO', 'VALUE'])
    df.to_csv(output_file, index=False)
    return output_file
