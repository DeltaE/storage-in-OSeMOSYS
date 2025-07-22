import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def graph(file_kotzur, file_cluster, file_base, representative_days, blocks_per_day):

    # Ler os dados
    data_kotzur = pd.read_csv(file_kotzur)
    data_cluster = pd.read_csv(file_cluster)
    data_base = pd.read_csv(file_base)

    # Preparar dados para o gráfico do arquivo "Cluster"
    # Pegando a primeira hora de cada dia nas simulações com 24h (8760 pontos -> 365 dias, cada dia tem 24 pontos)
    cluster_storage_level = data_cluster['StorageLevelTSStart'][::blocks_per_day]

    # Índices dos dias especificados (ajustados para índice baseado em zero)
    indices = np.array(representative_days) - 1
    # Valores dos dias especificados
    values = [data_base['StorageLevelTSStart'][i * blocks_per_day] for i in range(len(representative_days))]

    # Configurar os gráficos combinados para Kotzur, Cluster e Base
    fig, axs = plt.subplots(3, 1, figsize=(12, 18))

    # Gráfico para Kotzur
    axs[0].plot(data_kotzur['StorageLevelChronoDayStart'], label='Kotzur', color='blue')
    axs[0].set_title('Kotzur Storage Level')
    axs[0].set_xlim(0, 365)
    axs[0].set_xlabel('Days')
    axs[0].set_ylabel('Storage Level')
    axs[0].grid(True)

    # Gráfico para Cluster
    axs[1].plot(range(365), cluster_storage_level, label='Cluster', color='green')
    axs[1].set_title('Cluster Storage Level')
    axs[1].set_xlim(0, 365)
    axs[1].set_xlabel('Days')
    axs[1].set_ylabel('Storage Level')
    axs[1].grid(True)

    # Gráfico para Base (conectando os pontos especificados)
    axs[2].plot(indices, values, label='Base', color='red', marker='o', linestyle='-')
    axs[2].set_title('Base Storage Level')
    axs[2].set_xlim(0, 365)
    axs[2].set_xlabel('Days')
    axs[2].set_ylabel('Storage Level')
    axs[2].grid(True)

    # Ajustar o layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.93, hspace=0.4) 
    plt.show()
    return fig