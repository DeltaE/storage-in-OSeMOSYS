import pandas as pd

def read_csvfile(path):
    # Ler o arquivo CSV
    df = pd.read_csv(path)

    # Obter o valor na segunda linha e coluna 'VALUE'
    storagelevelstart = df.iloc[0]['VALUE']
    
    return storagelevelstart