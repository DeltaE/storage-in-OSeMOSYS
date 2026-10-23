import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def graph(file_base, file_kotzur, file_kotzur_intraday, file_cluster, file_niet, file_welsch, file_welsch_intraday, representative_days, blocks_per_day, file_yearsplit):
    # Ler os dados
    data_base = pd.read_csv(file_base)
    data_kotzur = pd.read_csv(file_kotzur)
    data_kotzur_intraday = pd.read_csv(file_kotzur_intraday)
    data_welsch_intraday = pd.read_csv(file_welsch_intraday)
    data_cluster = pd.read_csv(file_cluster)
    data_niet = pd.read_csv(file_niet)
    #data_welsch = pd.read_csv(file_welsch)
    yearsplit = pd.read_csv(file_yearsplit)

    # iNDICES
    ## Niet (Índices dos dias especificados (ajustados para índice baseado em zero))
    #daily_indice_niet = np.array(representative_days) - 1
    daily_indice_niet = (yearsplit['VALUE'] * 365).cumsum().shift(fill_value=0).values[::blocks_per_day]
    daily_indice_cluster = range(365)
    daily_indice_kotzur = range(365)
    daily_indice_base = range(365)
    daily_indice_welsch = range(365)
    #daily_indice_welsch = np.array(representative_days) - 1

    #hourly_indice_kotzur = np.arange(0, 365) * 24
    hourly_indice_kotzur = np.arange(0, 365*blocks_per_day) * (24/blocks_per_day)
    hourly_indice_base = range(8760)
    hourly_indice_cluster = np.arange(0, 365*blocks_per_day) * (24/blocks_per_day)
    hourly_indice_welsch = np.arange(0, 365*blocks_per_day) * (24/blocks_per_day)
    #hourly_indice_niet = list((yearsplit['VALUE'] * 8760).cumsum())
    hourly_indice_niet = (yearsplit['VALUE'] * 8760).cumsum().shift(fill_value=0).values
    #hourly_indice_niet = np.concatenate([np.arange((day - 1) * 24, day * 24, 24 / blocks_per_day) for day in representative_days])
    #hourly_indice_welsch = np.concatenate([np.arange((day - 1) * 24, day * 24, 24 / blocks_per_day) for day in representative_days])

    # Indice de 2 semananas (14 dias) a partir do primeiro dia representativo)
    first_representative_hour_base = (representative_days[0] - 1) * 24
    first_representative_hour_cluster = (representative_days[0] - 1) * blocks_per_day
    first_representative_hour_kotzur = (representative_days[0] - 1) * blocks_per_day
    last_representative_day_in_two_weeks = (representative_days[0] + 14)  # 14 dias depois do primeiro dia
    indice_two_weeks, = np.where(np.array(representative_days) < last_representative_day_in_two_weeks)
    representative_days_in_two_weeks = np.array(representative_days)[indice_two_weeks]
    
    two_weeks_hourly_indice_base = range(first_representative_hour_base, first_representative_hour_base + (14*24))
    two_weeks_hourly_indice_cluster = np.arange(first_representative_hour_cluster, first_representative_hour_cluster + (14*blocks_per_day)) * (24/blocks_per_day)
    two_weeks_hourly_indice_niet = np.concatenate([np.arange((day - 1) * 24, day * 24, 24 / blocks_per_day) for day in representative_days_in_two_weeks])
    two_weeks_hourly_indice_kotzur = np.arange(first_representative_hour_kotzur, first_representative_hour_kotzur + (14*blocks_per_day)) * (24/blocks_per_day)
    #two_weeks_hourly_indice_welsch = np.concatenate([np.arange((day - 1) * 24, day * 24, 24 / blocks_per_day) for day in representative_days_in_two_weeks])
    two_weeks_hourly_indice_welsch = np.arange(first_representative_hour_cluster, first_representative_hour_cluster + (14*blocks_per_day)) * (24/blocks_per_day)

    # DATA
    ## Cluster e Base (8760) (Pegando a primeira hora de cada dia. Base tem 24h)
    daily_kotzur_storage_level = data_kotzur['StorageLevelChronoDayStart']
    daily_cluster_storage_level = data_cluster['StorageLevelTSStart'][::blocks_per_day]
    daily_base_storage_level = data_base['StorageLevelTSStart'][::24]
    daily_niet_storage_level = [data_niet['StorageLevelTSStart'][i * blocks_per_day] for i in range(len(daily_indice_niet))]
    #daily_welsch_storage_level = [data_welsch['StorageLevelDayTypeStart'][i] for i in range(len(daily_indice_welsch))]
    daily_welsch_storage_level = data_welsch_intraday['VALUEACCUMULATED'][::blocks_per_day]

    hourly_base_storage_level = data_base['StorageLevelTSStart']
    hourly_cluster_storage_level = data_cluster['StorageLevelTSStart']
    #hourly_kotzur_storage_level = data_kotzur['StorageLevelChronoDayStart']
    hourly_kotzur_storage_level = data_kotzur_intraday['VALUEACCUMULATED']
    hourly_welsch_storage_level = data_welsch_intraday['VALUEACCUMULATED']
    hourly_niet_storage_level = data_niet['StorageLevelTSStart']

    # Plots (diário)
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(daily_indice_kotzur, daily_kotzur_storage_level, label='Kotzur', color='blue')
    #ax.plot(daily_indice_base, daily_base_storage_level, label='Base', color='black', linewidth=2)
    ax.plot(daily_indice_cluster, daily_cluster_storage_level, label='Cluster', color='green')
    ax.plot(daily_indice_niet, daily_niet_storage_level, label='Niet', color='red', marker='o', linestyle='-')
    ax.plot(daily_indice_welsch, daily_welsch_storage_level, label='Welsch', color='brown')
   
    ax.set_xlabel('Days')
    ax.set_ylabel('Storage Level')
    ax.grid(True)
    ax.legend()
    ax.set_title('Daily Storage Level Comparison')
    ax.set_xlim(0, 365)

    # Mostrar gráfico
    plt.tight_layout()
    #plt.show()

    # Plot2 (horário)
    fig2, ax2 = plt.subplots(figsize=(12, 6))

    #ax2.plot(hourly_indice_base, hourly_base_storage_level, label='Base', color='black', linewidth=2)
    ax2.plot(hourly_indice_cluster, hourly_cluster_storage_level, label='Cluster', color='green')
    ax2.plot(hourly_indice_kotzur, hourly_kotzur_storage_level, label='Kotzur', color='blue')
    ax2.plot(hourly_indice_welsch, hourly_welsch_storage_level, label='Welsch', color='brown')
    ax2.plot(hourly_indice_niet, hourly_niet_storage_level, label='Niet', color='red')
    #ax2.plot(hourly_indice_niet, hourly_niet_storage_level, label='Niet', color='red', marker='o', linestyle='-')

    variation_niet = 0.05

    for i, x_position in enumerate(hourly_indice_niet[::blocks_per_day]):
        corresponding_niet_value = hourly_niet_storage_level[i*blocks_per_day]
        # Defina ymin e ymax para cada barra de erro em torno do valor y
        y_niet_min = corresponding_niet_value - variation_niet
        y_niet_max = corresponding_niet_value + variation_niet

        # Desenhe as linhas verticais
        #ax2.vlines(x=x_position, ymin=y_niet_min, ymax=y_niet_max, color='black', linestyle='--', linewidth=1)


    ax2.set_xlabel('Hour of Year')
    ax2.set_ylabel('Storage Level')
    ax2.grid(True)
    ax2.legend()
    ax2.set_title('Hourly Storage Level Comparison')
    ax2.set_xlim(0, 8760)

    plt.tight_layout()
    #plt.show()

    # Plot3 (horário em 2 semanas)
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    #ax3.plot(two_weeks_hourly_indice_base, hourly_base_storage_level[first_representative_hour_base:first_representative_hour_base + 336], label='Base', color='black')
    ax3.plot(two_weeks_hourly_indice_cluster, hourly_cluster_storage_level[first_representative_hour_cluster:first_representative_hour_cluster + (14*blocks_per_day)], label='Cluster', color='green', marker='o')
    ax3.plot(two_weeks_hourly_indice_niet, hourly_niet_storage_level[:len(two_weeks_hourly_indice_niet)], label='Niet', color='red', marker='o', linestyle='-')
    #ax3.plot(two_weeks_hourly_indice_welsch, hourly_welsch_storage_level[:len(two_weeks_hourly_indice_niet)], label='Welsch', color='brown', marker='o', linestyle='-')
    ax3.plot(two_weeks_hourly_indice_kotzur, hourly_kotzur_storage_level[first_representative_hour_kotzur:first_representative_hour_kotzur + (14*blocks_per_day)], label='Kotzur', color='blue', marker='o')
    
    variation = 0.001

    for i, x_position in enumerate(two_weeks_hourly_indice_cluster[::blocks_per_day]):
        corresponding_cluster_value = hourly_cluster_storage_level[first_representative_hour_cluster + i*blocks_per_day]
        corresponding_kotzur_value = hourly_kotzur_storage_level[first_representative_hour_kotzur + i*blocks_per_day]
        # Defina ymin e ymax para cada barra de erro em torno do valor y
        y_cluster_min = corresponding_cluster_value - variation
        y_cluster_max = corresponding_cluster_value + variation
        y_kotzur_min = corresponding_kotzur_value - variation
        y_kotzur_max = corresponding_kotzur_value + variation

        # Desenhe as linhas verticais
        ax3.vlines(x=x_position, ymin=y_cluster_min, ymax=y_cluster_max, color='green', linestyle='--', linewidth=1)
        ax3.vlines(x=x_position, ymin=y_kotzur_min, ymax=y_kotzur_max, color='blue', linestyle='--', linewidth=1)

    ax3.set_xlabel('Hour of Year')
    ax3.set_ylabel('Storage Level')
    ax3.grid(True)
    ax3.legend()
    ax3.set_title('Two-Week Hourly Storage Level Comparison')
    ax3.set_xlim(first_representative_hour_base, first_representative_hour_base + 336)

    plt.tight_layout()
    #plt.show()

    return fig, fig2, fig3

    

