import os
import yaml
import subprocess
import matplotlib.pyplot as plt
from src import (
    cluster_data, run_simulation, new_list, CFandSDP, conversionlts, conversionld, conversionlh, conversionldc, 
    yearsplit, daysindaytype, new_yaml_param, copy_and_rename, intraday_kotzur, intraday_welsch, intraday_welsch2, read_csvfile, graph, table
)

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

scenario_name = config['scenario_name']
days_in_year = config['days_in_year']
seasons = config['seasons']
hour_grouping = config['hour_grouping']
n_clusters = config['n_clusters']
StorageLevelStart = config['StorageLevelStart']
StorageMaxCapacity = config['StorageMaxCapacity']
ResidualStorageCapacity = config['ResidualStorageCapacity']
results_destination_folder = config['results']['directory']
results_GUI_destination_folder = config['results']['directory_GUI']
results_copied_filename = config['results']['results_copied_filename']
results_excel_file = config['results']['results_excel_file']
input_CF_csv_file = os.path.join(config['data_8760']['directory'],config['data_8760']['CF'])
input_SDP_csv_file = os.path.join(config['data_8760']['directory'],config['data_8760']['SDP'])

representative_days, chronological_sequence = cluster_data(input_CF_csv_file,input_SDP_csv_file,n_clusters)

print(representative_days)

# Number of blocks per day based on the hour grouping
blocks_per_day = 24 // hour_grouping
# Total timeslices considering the representative days
timeslices = len(representative_days) * blocks_per_day
# Chronological timeslices is number of days in year * blocks per day. If hourly analysis, chronological timeslice is 8760
chronological_timeslices = days_in_year * blocks_per_day
year_split = 1 / timeslices
day_split = hour_grouping / (24 * 365)

cases = config['cases']

for case_name, case_info in cases.items():

    if case_name == 'Model_Cluster':
        print(f"Updating case: {case_name}")
        
        # Updating timeslicecro
        output_timeslicecro_csv_file = os.path.join(case_info['root_directory'], 
                                                case_info['input_otoole_csv']['directory'], 
                                                case_info['input_otoole_csv']['timeslicecro'])
        new_list(chronological_timeslices, output_timeslicecro_csv_file)

        # Updating conversionlts
        output_conversionlts_csv_file = os.path.join(case_info['root_directory'], 
                                                case_info['input_otoole_csv']['directory'], 
                                                case_info['input_otoole_csv']['conversionlts'])
        conversionlts(blocks_per_day, chronological_timeslices, timeslices, chronological_sequence, representative_days, output_conversionlts_csv_file)

        # Updating day split in yaml file
        otoole_yaml_file = os.path.join(case_info['root_directory'], case_info['otoole_config'])
        new_yaml_param(otoole_yaml_file, 'DaySplit', day_split)

    if case_name == 'Model_Kotzur':
        print(f"Updating case: {case_name}")
        
        # Updating dayscro
        output_dayscro_csv_file = os.path.join(case_info['root_directory'], 
                                                case_info['input_otoole_csv']['directory'], 
                                                case_info['input_otoole_csv']['dayscro'])
        new_list(days_in_year, output_dayscro_csv_file)
        
        # Updating conversionld
        output_conversionld_csv_file = os.path.join(case_info['root_directory'], 
                                                case_info['input_otoole_csv']['directory'], 
                                                case_info['input_otoole_csv']['conversionld'])
        conversionld(timeslices, len(representative_days), output_conversionld_csv_file)

        # Updating conversionldc
        output_conversionldc_csv_file = os.path.join(case_info['root_directory'], 
                                                case_info['input_otoole_csv']['directory'], 
                                                case_info['input_otoole_csv']['conversionldc'])
        conversionldc(chronological_sequence, representative_days, days_in_year, output_conversionldc_csv_file)

        # Updating day split in yaml file
        otoole_yaml_file = os.path.join(case_info['root_directory'], case_info['otoole_config'])
        new_yaml_param(otoole_yaml_file, 'DaySplit', day_split)

    if case_name == 'Model_Welsch':
        print(f"Updating case: {case_name}")
        
        # Updating dailytimebracket
        output_dailytimebracket_csv_file = os.path.join(case_info['root_directory'], 
                                                case_info['input_otoole_csv']['directory'], 
                                                case_info['input_otoole_csv']['dailytimebracket'])
        new_list(blocks_per_day, output_dailytimebracket_csv_file)
        
        # Updating conversionld
        output_conversionld_csv_file = os.path.join(case_info['root_directory'], 
                                                case_info['input_otoole_csv']['directory'], 
                                                case_info['input_otoole_csv']['conversionld'])
        conversionld(timeslices, len(representative_days), output_conversionld_csv_file)

        # Updating conversionlh
        output_conversionlh_csv_file = os.path.join(case_info['root_directory'], 
                                                case_info['input_otoole_csv']['directory'], 
                                                case_info['input_otoole_csv']['conversionlh'])
        conversionlh(timeslices, blocks_per_day, output_conversionlh_csv_file)

        # Updating conversionls
        output_conversionls_csv_file = os.path.join(case_info['root_directory'], 
                                                case_info['input_otoole_csv']['directory'], 
                                                case_info['input_otoole_csv']['conversionls'])
        conversionld(timeslices, seasons, output_conversionls_csv_file, label='SEASON')

        # Updating daysindaytype
        output_daysindaytype_csv_file = os.path.join(case_info['root_directory'], 
                                                case_info['input_otoole_csv']['directory'], 
                                                case_info['input_otoole_csv']['daysindaytype'])
        daysindaytype(representative_days, chronological_sequence, output_daysindaytype_csv_file)

        # Updating day split in yaml file
        otoole_yaml_file = os.path.join(case_info['root_directory'], case_info['otoole_config'])
        new_yaml_param(otoole_yaml_file, 'DaySplit', day_split)

    if case_name == 'Model_Niet' or case_name == 'Model_Cluster' or case_name == 'Model_Kotzur' or case_name == 'Model_Welsch':
        print(f"Updating case: {case_name}")
        
        # Updating timeslice
        output_timeslice_csv_file = os.path.join(case_info['root_directory'], 
                                                case_info['input_otoole_csv']['directory'], 
                                                case_info['input_otoole_csv']['timeslice'])
        new_list(timeslices, output_timeslice_csv_file)

        # Updating daytype
        output_daytype_csv_file = os.path.join(case_info['root_directory'], 
                                                case_info['input_otoole_csv']['directory'], 
                                                case_info['input_otoole_csv']['daytype'])
        daytypes = len(representative_days)
        new_list(daytypes, output_daytype_csv_file)

        # Updating yearsplit
        output_yearsplit_csv_file = os.path.join(case_info['root_directory'], 
                                            case_info['input_otoole_csv']['directory'], 
                                            case_info['input_otoole_csv']['yearsplit'])
        yearsplit(timeslices, representative_days,  chronological_sequence, days_in_year, output_yearsplit_csv_file)

        # Updating capacity factor (averaging the values)
        output_CF_csv_file = os.path.join(case_info['root_directory'], 
                                        case_info['input_otoole_csv']['directory'],
                                        case_info['input_otoole_csv']['capacity_factor'])
        CFandSDP(input_CF_csv_file, representative_days, hour_grouping, output_CF_csv_file, operation='mean')

        # Updating specified demand profile (summing the values)
        output_SDP_csv_file = os.path.join(case_info['root_directory'], 
                                        case_info['input_otoole_csv']['directory'],
                                        case_info['input_otoole_csv']['specified_demand_profile'])
        CFandSDP(input_SDP_csv_file, representative_days, hour_grouping, output_SDP_csv_file, operation='sum')

        # Updating year split in yaml file
        # This is no longer necessary because the yearsplit was updated in the CSV.
        # But I kept it in case the yearsplit is the same in some study.
        otoole_yaml_file = os.path.join(case_info['root_directory'], case_info['otoole_config'])
        new_yaml_param(otoole_yaml_file, 'YearSplit', year_split)

        # Updating storage info in yaml file
        #new_yaml_param(otoole_yaml_file, 'StorageLevelStart', StorageLevelStart)
        new_yaml_param(otoole_yaml_file, 'StorageMaxCapacity', StorageMaxCapacity)
        new_yaml_param(otoole_yaml_file, 'ResidualStorageCapacity', ResidualStorageCapacity)

        # Creating txt from csv using otoole
        input_csv_dir = os.path.join(case_info['root_directory'], case_info['input_otoole_csv']['directory'])
        output_txt_file = os.path.join(case_info['root_directory'], case_info['output_otoole_txt'])
        template_config = os.path.join(case_info['root_directory'], case_info['otoole_config'])
        command = f"otoole convert csv datafile {input_csv_dir} {output_txt_file} {template_config}"
        subprocess.run(command, shell=True, text=True)

    print(f"Running case: {case_name}")
    run_simulation(case_info)

    print(f"Saving results case: {case_name}")
    results_case = os.path.join(case_info['root_directory'], 
                            case_info['results']['directory'],
                            case_info['results']['storage_level'])
    new_results_filename = '_'.join([scenario_name,results_copied_filename,case_name]) + '.csv'
    copy_and_rename(results_case, results_destination_folder, new_results_filename)

    data_sol_results = os.path.join(case_info['root_directory'], case_info['data_sol'])
    simulation_results = os.path.join(case_info['root_directory'], case_info['simulation_results'])
    results_file = os.path.join(results_destination_folder, results_excel_file)

    capacity_path = os.path.join(case_info['root_directory'], 
                            case_info['results']['directory'],
                            case_info['results']['power_capacity'])
    storage_capacity_path = os.path.join(case_info['root_directory'], 
                            case_info['results']['directory'],
                            case_info['results']['storage_capacity'])
    table(simulation_results, data_sol_results, scenario_name, case_name, capacity_path, storage_capacity_path, 'WINDPOWER', 'BATTERY', results_file)

print(f"Generating graph")
file_conversionlts = os.path.join(config['cases']['Model_Cluster']['root_directory'], 
                                config['cases']['Model_Cluster']['input_otoole_csv']['directory'], 
                                config['cases']['Model_Cluster']['input_otoole_csv']['conversionlts'])
file_kotzur_storage = os.path.join(config['cases']['Model_Kotzur']['root_directory'], 
                                config['cases']['Model_Kotzur']['results']['directory'], 
                                config['cases']['Model_Kotzur']['results']['storage_levelTS'])
file_kotzur_intraday = os.path.join(results_destination_folder,'_'.join([scenario_name,results_copied_filename,'Model_Kotzur_intraday']) + '.csv')
file_kotzur_storage_start= os.path.join(config['cases']['Model_Kotzur']['root_directory'], 
                                config['cases']['Model_Kotzur']['results']['directory'], 
                                config['cases']['Model_Kotzur']['results']['storage_level_Start'])
StorageLevelStartKotzur = read_csvfile(file_kotzur_storage_start)

intraday_kotzur(file_conversionlts, file_kotzur_storage, StorageLevelStartKotzur, file_kotzur_intraday)

file_welsch_storage = os.path.join(config['cases']['Model_Welsch']['root_directory'], 
                                config['cases']['Model_Welsch']['results']['directory'], 
                                config['cases']['Model_Welsch']['results']['storage_levelTS'])
file_welsch_intraday = os.path.join(results_destination_folder,'_'.join([scenario_name,results_copied_filename,'Model_Welsch_intraday']) + '.csv')
file_welsch_storage_start= os.path.join(config['cases']['Model_Welsch']['root_directory'], 
                                config['cases']['Model_Welsch']['results']['directory'], 
                                config['cases']['Model_Welsch']['results']['storage_level_Start'])

StorageLevelStartWelsch = read_csvfile(file_welsch_storage_start)
intraday_welsch2(file_welsch_storage, blocks_per_day, timeslices, representative_days, chronological_sequence, StorageLevelStartWelsch, file_welsch_intraday)

file_base = os.path.join(results_destination_folder,'_'.join(['k365h1WND_Storage_Level_Model_Niet']) + '.csv')
file_kotzur = os.path.join(results_destination_folder,'_'.join([scenario_name,results_copied_filename,'Model_Kotzur']) + '.csv')
file_cluster = os.path.join(results_destination_folder,'_'.join([scenario_name,results_copied_filename,'MOdel_Cluster']) + '.csv')
file_niet = os.path.join(results_destination_folder,'_'.join([scenario_name,results_copied_filename,'Model_Niet']) + '.csv')
file_welsch = os.path.join(results_destination_folder,'_'.join([scenario_name,results_copied_filename,'Model_Welsch']) + '.csv')

fig, fig2, fig3 = graph(file_base, file_kotzur, file_kotzur_intraday, file_cluster, file_niet, file_welsch, file_welsch_intraday, representative_days, blocks_per_day, output_yearsplit_csv_file)

figure_filename = '_'.join([scenario_name, 'Figure']) + '.png'
figure_path = os.path.join(results_destination_folder, figure_filename)
figure_GUI_pah = os.path.join(results_GUI_destination_folder, figure_filename)
fig.savefig(figure_path)
#fig.savefig(figure_GUI_pah)

figure2_filename = '_'.join([scenario_name, 'Figure_Hourly']) + '.png'
figure2_path = os.path.join(results_destination_folder, figure2_filename)

fig2.savefig(figure2_path)
fig2.savefig(figure_GUI_pah)

figure3_filename = '_'.join([scenario_name, 'Figure_Hourly_2Weeks']) + '.png'
figure3_path = os.path.join(results_destination_folder, figure3_filename)

fig3.savefig(figure3_path)
