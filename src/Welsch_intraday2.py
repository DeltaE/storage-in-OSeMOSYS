import pandas as pd
import numpy as np
from collections import Counter

def intraday_welsch2(storage_path, blocksperday, timeslices, representative_days, chronological_sequence, storage_level_start, output_path):
    # Carregar os arquivos
    storagelevel_df = pd.read_csv(storage_path)

    # Criar os vetores de controle
    dailytimebracket_vector = np.tile(np.arange(1, blocksperday + 1), (timeslices // blocksperday + 1))[:timeslices]
    daytype_vector = np.repeat(np.arange(1, len(representative_days) + 1), (timeslices // len(representative_days)))[:timeslices]

    # Criar o DataFrame a partir dos vetores esperados
    expected_df = pd.DataFrame({
        'DAYTYPE': daytype_vector,
        'DAILYTIMEBRACKET': dailytimebracket_vector
    })

    # Inserir chave única para evitar problemas de repetição nos joins
    expected_df['Key'] = expected_df['DAYTYPE'].astype(str) + '-' + expected_df['DAILYTIMEBRACKET'].astype(str)
    storagelevel_df['Key'] = storagelevel_df['DAYTYPE'].astype(str) + '-' + storagelevel_df['DAILYTIMEBRACKET'].astype(str)

    # Juntar o DataFrame esperado com o DataFrame original baseado na chave
    result_df = pd.merge(expected_df, storagelevel_df.drop(columns=['DAYTYPE', 'DAILYTIMEBRACKET']), on='Key', how='left')
    result_df['VALUE'] = result_df['VALUE'].fillna(0)  # Preencher valores faltantes com 0

    # Remover a chave temporária
    result_df.drop(columns='Key', inplace=True)

    # Repetir os resultados das linhas dos mesmos dias típicos
    count = Counter(chronological_sequence)
    daysindaytype = [count[day] for day in representative_days]

    repeated_rows = []
    for day, repeat_count in zip(range(1, len(representative_days) + 1), daysindaytype):
        day_rows = result_df[result_df['DAYTYPE'] == day]
        repeated_rows.append(pd.concat([day_rows] * repeat_count, ignore_index=True))

    result_df = pd.concat(repeated_rows, ignore_index=True)

    # Cria a coluna 'VALUEACCUMULATED' para iniciar com 0 e depois acumular os valores
    result_df['VALUEACCUMULATED'] = result_df['VALUE'].shift(1).fillna(0).cumsum() + storage_level_start

    # Salvar o DataFrame corrigido em um arquivo CSV
    result_df.to_csv(output_path, index=False)

    return output_path

