import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min

def cluster_data(capacity_factor_path, demand_profile_path, n_clusters):

    capacity_factor_data = pd.read_csv(capacity_factor_path)
    demand_profile_data = pd.read_csv(demand_profile_path)

    # Normalizar os dados de capacidade
    scaler_capacity = MinMaxScaler()
    capacity_factor_data['VALUE'] = scaler_capacity.fit_transform(capacity_factor_data[['VALUE']])

    # Normalizar os dados de demanda
    scaler_demand = MinMaxScaler()
    demand_profile_data['VALUE'] = scaler_demand.fit_transform(demand_profile_data[['VALUE']])

    # Combinar os dados usando a coluna TIMESLICE e YEAR
    combined_data = pd.merge(capacity_factor_data[['TIMESLICE', 'YEAR', 'VALUE']],
                            demand_profile_data[['TIMESLICE', 'YEAR', 'VALUE']],
                            on=['TIMESLICE', 'YEAR'], suffixes=('_capacity', '_demand'))

    # Converter TIMESLICE em DayOfYear
    combined_data['DayOfYear'] = (combined_data['TIMESLICE'] - 1) // 24 + 1
    combined_data['HourOfDay'] = (combined_data['TIMESLICE'] - 1) % 24 + 1

    #print(combined_data.head(30))

    # Pivotear os dados para VALUE_capacity e VALUE_demand separadamente
    pivot_capacity = combined_data.pivot(index='DayOfYear', columns='HourOfDay', values='VALUE_capacity')
    pivot_demand = combined_data.pivot(index='DayOfYear', columns='HourOfDay', values='VALUE_demand')

    # Renomear as colunas para refletir os nomes apropriados
    pivot_capacity.columns = [f'value_capacity_timeslice_{i}' for i in pivot_capacity.columns]
    pivot_demand.columns = [f'value_demand_timeslice_{i}' for i in pivot_demand.columns]

    # Concatenar as duas tabelas pivotadas horizontalmente
    final_data = pd.concat([pivot_capacity, pivot_demand], axis=1)

    # Visualizar os resultados
    #print(final_data.head())

    # Aplicar K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    clusters = kmeans.fit_predict(final_data)
    
    # Encontrar o dia mais próximo do centro de cada cluster
    closest, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, final_data)
    representative_days = final_data.iloc[closest].index.tolist()
    
    # Ordenar os dias representativos em ordem cronológica
    representative_days_sorted = sorted(representative_days)

    chronological_sequence = [representative_days[i] for i in clusters]
    
    return representative_days_sorted, chronological_sequence