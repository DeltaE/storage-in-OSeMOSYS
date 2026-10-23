import pandas as pd

def intraday_kotzur(conversion_path, storage_path, storage_level_start, output_path):
    # Carregar os arquivos
    conversionlts_df = pd.read_csv(conversion_path)
    storagelevel_df = pd.read_csv(storage_path)

    # Ordenar por TIMESLICECRO e filtrar por VALUE = 1
    filtered_conversionlts = conversionlts_df[conversionlts_df['VALUE'] == 1].sort_values('TIMESLICECRO')

    # Mapear cada TIMESLICE de filtered_conversionlts para o VALUE correspondente em storagelevel_df
    values_from_storage = filtered_conversionlts['TIMESLICE'].map(
        storagelevel_df.set_index('TIMESLICE')['VALUE']
    )

    # Criar um novo DataFrame para salvar no Excel
    result_df = pd.DataFrame({
        'TIMESLICECRO': filtered_conversionlts['TIMESLICECRO'],
        'VALUE': values_from_storage
    })

    # Cria a coluna 'VALUEACCUMULATED' para iniciar com 0 e depois acumular os valores
    result_df['VALUEACCUMULATED'] = result_df['VALUE'].shift(1).fillna(0).cumsum() + storage_level_start

    # Salvar o DataFrame corrigido em um arquivo Excel
    result_df.to_csv(output_path, index=False)

    return output_path
