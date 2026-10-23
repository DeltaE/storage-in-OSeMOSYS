import pandas as pd
import numpy as np

def intraday_welsch(storage_path, blocksperday, timeslices, representative_days, output_path):
    # Carregar os arquivos
    storagelevel_df = pd.read_csv(storage_path)

    # Criar os vetores de controle
    dailytimebracket_vector = np.tile(np.arange(1, blocksperday + 1), (timeslices // blocksperday + 1))[:timeslices]
    daytype_vector = np.repeat(np.arange(1, representative_days + 1), (timeslices // representative_days))[:timeslices]

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

   # Calcular VALUEACCUMULATED somente a partir do segundo dia
    result_df['VALUEACCUMULATED'] = result_df['VALUE']
    last_value_day1 = result_df.loc[result_df['DAYTYPE'] == 1, 'VALUE'].iloc[-1]
    first_dailytimebracket_day2_index = result_df[(result_df['DAYTYPE'] == 2) & (result_df['DAILYTIMEBRACKET'] == 1)].index[0]
    result_df.loc[first_dailytimebracket_day2_index, 'VALUEACCUMULATED'] += last_value_day1
    result_df.loc[first_dailytimebracket_day2_index + 1:, 'VALUEACCUMULATED'] = result_df.loc[first_dailytimebracket_day2_index + 1:, 'VALUE'].cumsum() + result_df.loc[first_dailytimebracket_day2_index, 'VALUEACCUMULATED']


    # Salvar o DataFrame corrigido em um arquivo CSV
    result_df.to_csv(output_path, index=False)

    return output_path
