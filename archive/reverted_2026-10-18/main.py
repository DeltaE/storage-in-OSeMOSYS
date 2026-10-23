
from matplotlib import typing
import src.utilities as utils
from pathlib import Path
import src # loading the src module to access its functions/methods
import otoole
import shutil
from typing import Dict

# from src import (
#     cluster_data, run_simulation, new_list, CFandSDP, conversionlts, conversionld, conversionlh, conversionldc, 
#     yearsplit, daysindaytype, new_yaml_param, copy_and_rename, intraday_kotzur, intraday_welsch, intraday_welsch2, read_csvfile, graph, table
# )


# Load configuration
config_path:Path=Path('config/config.yaml')
config:dict = utils.load_config(config_path)


utils.print_update(level=2,message="Extracting parameters from the configuration")
scenario_name:str = config['scenario_name']
days_in_year:int = config['days_in_year']
seasons:int = config['seasons']
hour_grouping:int= config['hour_grouping']
n_clusters:int= config['n_clusters']
StorageLevelStart:float = config['StorageLevelStart']
StorageMaxCapacity:float = config['StorageMaxCapacity']
ResidualStorageCapacity:float = config['ResidualStorageCapacity']

results_destination_folder:Path = Path(config['results']['directory'])
results_destination_folder.mkdir(parents=True, exist_ok=True)

results_GUI_destination_folder:Path = Path(config['results']['directory_GUI'])
results_GUI_destination_folder.mkdir(parents=True, exist_ok=True)

results_copied_filename:str = config['results']['results_copied_filename']
results_excel_file:str = config['results']['results_excel_file']
input_CF_csv_file:Path = Path(config['data_8760']['directory']) / config['data_8760']['CF']
input_SDP_csv_file:Path = Path(config['data_8760']['directory']) / config['data_8760']['SDP']

representative_days, chronological_sequence = src.cluster_data(input_CF_csv_file,input_SDP_csv_file,n_clusters)
utils.print_update(level=2,message=f"Representative days: {representative_days}")


# Number of blocks per day based on the hour grouping
blocks_per_day:int = 24 // hour_grouping
utils.print_update(level=2,message=f"Hour Grouping from config: {hour_grouping}")


# Total timeslices considering the representative days
timeslices:int = len(representative_days) * blocks_per_day
utils.print_update(level=2,message=f"Timeslices: {timeslices}")


# Chronological timeslices is number of days in year * blocks per day. If hourly analysis, chronological timeslice is 8760
chronological_timeslices:int = days_in_year * blocks_per_day
year_split:int = 1 / timeslices
day_split:int = hour_grouping / (24 * 365)


cases:dict = config['cases']

# cases:dict = {k: cases[k] for k in list(cases.keys())[1:2]} # 20250719:EL: testing each scenario
utils.print_info(f"Cases from config: {list(cases.keys())}")
# """ 
for case_name, case_info in cases.items():
    if case_name == 'Model_Cluster':
        utils.print_update(level=1,message=f"Updating case: {case_name}")

        # Updating timeslicecro
        output_timeslicecro_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['timeslicecro']
        
        src.new_list(chronological_timeslices, output_timeslicecro_csv_file)

        # Updating conversionlts
        output_conversionlts_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['conversionlts']
        src.conversionlts(blocks_per_day, chronological_timeslices, timeslices, chronological_sequence, representative_days, output_conversionlts_csv_file)

        # Updating day split in yaml file
        otoole_yaml_file = Path(case_info['root_directory']) / case_info['otoole_config']
        src.new_yaml_param(otoole_yaml_file, 'DaySplit', day_split)
    if case_name == 'Model_Kotzur':
        utils.print_update(level=1,message=f"Updating case: {case_name}")
        
        # Updating dayscro
        output_dayscro_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['dayscro']
        src.new_list(days_in_year, output_dayscro_csv_file)

        # Updating conversionld
        output_conversionld_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['conversionld']
        src.conversionld(timeslices, len(representative_days), output_conversionld_csv_file)

        # Updating conversionldc
        output_conversionldc_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['conversionldc']
        src.conversionldc(chronological_sequence, representative_days, days_in_year, output_conversionldc_csv_file)

        # Updating day split in yaml file
        otoole_yaml_file = Path(case_info['root_directory']) / case_info['otoole_config']
        src.new_yaml_param(otoole_yaml_file, 'DaySplit', day_split)

    if case_name == 'Model_Welsch':
        utils.print_update(level=1,message=f"Updating case: {case_name}")
        
        # Updating dailytimebracket
        output_dailytimebracket_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['dailytimebracket']
        src.new_list(blocks_per_day, output_dailytimebracket_csv_file)

        # Updating conversionld
        output_conversionld_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['conversionld']
        src.conversionld(timeslices, len(representative_days), output_conversionld_csv_file)

        # Updating conversionlh
        output_conversionlh_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['conversionlh']
        src.conversionlh(timeslices, blocks_per_day, output_conversionlh_csv_file)

        # Updating conversionls
        output_conversionls_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['conversionls']
        src.conversionld(timeslices, seasons, output_conversionls_csv_file, label='SEASON')

        # Updating daysindaytype
        output_daysindaytype_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['daysindaytype']
        src.daysindaytype(representative_days, chronological_sequence, output_daysindaytype_csv_file)

        # Updating day split in yaml file
        otoole_yaml_file = Path(case_info['root_directory']) / case_info['otoole_config']
        src.new_yaml_param(otoole_yaml_file, 'DaySplit', day_split)

    if case_name == 'Model_Niet' or case_name == 'Model_Cluster' or case_name == 'Model_Kotzur' or case_name == 'Model_Welsch':
        utils.print_update(level=1,message=f"Updating case: {case_name}")
        
        # Define the source directory
        source_template = Path("inputs_csv")
        # List all CSV files in the directory
        csv_files = list(source_template.glob('*.csv'))
                
        # Creating txt from csv using otoole
        input_csv_dir = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory']
        output_txt_file = Path(case_info['root_directory']) / case_info['output_otoole_txt']
        template_config = Path(case_info['root_directory']) / case_info['otoole_config']
        
        #-----------------------------------------------------
        # 20250719 --- Missing workflow step added by Elias
        otoole_cfg=utils.load_config(template_config)
        excepted_file_names = set(otoole_cfg.keys())
        
        # Copy matching files to input_csv_dir directory
        input_csv_dir.mkdir(exist_ok=True)
        
        for csv_file in csv_files:
            # Remove .csv extension and compare
            name_no_ext = csv_file.stem
            if name_no_ext in excepted_file_names:
                shutil.copy(csv_file, input_csv_dir / csv_file.name)
                utils.print_update(level=3,message=f"Copied: {csv_file.name}")
            
        utils.print_update(level=2,message="Using Otoole python API to convert CSV files to TXT")
        utils.print_update(level=3,message=f"Converting CSV files to TXT for case: {case_name}")
                
        #-----------------------------------------------------
        # Updating timeslice
        output_timeslice_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['timeslice']
        src.new_list(timeslices, output_timeslice_csv_file)

        # Updating daytype
        output_daytype_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['daytype']
        daytypes = len(representative_days)
        src.new_list(daytypes, output_daytype_csv_file)

        # Updating yearsplit
        output_yearsplit_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['yearsplit']
        src.yearsplit(timeslices, representative_days,  chronological_sequence, days_in_year, output_yearsplit_csv_file)

        # Updating capacity factor (averaging the values)
        output_CF_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['capacity_factor']
        src.CFandSDP(input_CF_csv_file, representative_days, hour_grouping, output_CF_csv_file, operation='mean')

        # Updating specified demand profile (summing the values)
        output_SDP_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['specified_demand_profile']
        src.CFandSDP(input_SDP_csv_file, representative_days, hour_grouping, output_SDP_csv_file, operation='sum')

        # Updating year split in yaml file
        # This is no longer necessary because the yearsplit was updated in the CSV.
        # But I kept it in case the yearsplit is the same in some study.
        otoole_yaml_file = Path(case_info['root_directory']) / case_info['otoole_config']
        print(otoole_yaml_file)
        src.new_yaml_param(otoole_yaml_file, 'YearSplit', year_split)

        # Updating storage info in yaml file
        #src.new_yaml_param(otoole_yaml_file, 'StorageLevelStart', StorageLevelStart)
        src.new_yaml_param(otoole_yaml_file, 'StorageMaxCapacity', StorageMaxCapacity)
        src.new_yaml_param(otoole_yaml_file, 'ResidualStorageCapacity', ResidualStorageCapacity)
        
        # command = f"otoole convert csv datafile {input_csv_dir} {output_txt_file} {template_config}"
        # result = subprocess.run(command, shell=True, text=True, capture_output=True)
        print
        result=otoole.convert(template_config, 'csv', 'datafile', input_csv_dir, output_txt_file) # using API instead of CLI
        
        if result:
            utils.print_update(level=2,message="✔️ Otoole conversion executed successfully.")
        else:
            utils.print_update(level=2,message="❌ Otoole conversion failed.")


    utils.print_update(level=2,message=f"Running simulation for case: {case_name}")
    src.run_simulation(case_info)

    utils.print_update(level=2,message=f"Saving results case: {case_name}")
    results_case = Path(case_info['root_directory']) / case_info['results']['directory'] / case_info['results']['storage_level']
    new_results_filename = '_'.join([scenario_name,results_copied_filename,case_name]) + '.csv'
    src.copy_and_rename(results_case, results_destination_folder, new_results_filename)

    data_sol_results = Path(case_info['root_directory']) / case_info['data_sol']
    simulation_results = Path(case_info['root_directory']) / case_info['simulation_results']
    results_file = Path(results_destination_folder) / results_excel_file

    capacity_path = Path(case_info['root_directory']) / case_info['results']['directory'] / case_info['results']['power_capacity']
    storage_capacity_path = Path(case_info['root_directory']) / case_info['results']['directory'] / case_info['results']['storage_capacity']
    src.table(simulation_results, data_sol_results, scenario_name, case_name, capacity_path, storage_capacity_path, 'WINDPOWER', 'BATTERY', results_file)

# """
print("Generating graph")

file_conversionlts = Path(config['cases']['Model_Cluster']['root_directory']) / config['cases']['Model_Cluster']['input_otoole_csv']['directory'] / config['cases']['Model_Cluster']['input_otoole_csv']['conversionlts']
file_kotzur_storage = Path(config['cases']['Model_Kotzur']['root_directory']) / config['cases']['Model_Kotzur']['results']['directory'] / config['cases']['Model_Kotzur']['results']['storage_levelTS']
file_kotzur_intraday = Path(results_destination_folder) / ('_'.join([scenario_name,results_copied_filename,'Model_Kotzur_intraday']) + '.csv')
file_kotzur_storage_start = Path(config['cases']['Model_Kotzur']['root_directory']) / config['cases']['Model_Kotzur']['results']['directory'] / config['cases']['Model_Kotzur']['results']['storage_level_Start']

print(f"temp_DEBUG_prob_EL| file_kotzur_storage_start: {file_kotzur_storage_start}")
StorageLevelStartKotzur = src.read_csvfile(file_kotzur_storage_start)

src.intraday_kotzur(file_conversionlts, file_kotzur_storage, StorageLevelStartKotzur, file_kotzur_intraday)


file_welsch_storage = Path(config['cases']['Model_Welsch']['root_directory']) / config['cases']['Model_Welsch']['results']['directory'] / config['cases']['Model_Welsch']['results']['storage_levelTS']
file_welsch_intraday = Path(results_destination_folder) / ('_'.join([scenario_name,results_copied_filename,'Model_Welsch_intraday']) + '.csv')
file_welsch_storage_start = Path(config['cases']['Model_Welsch']['root_directory']) / config['cases']['Model_Welsch']['results']['directory'] / config['cases']['Model_Welsch']['results']['storage_level_Start']


StorageLevelStartWelsch = src.read_csvfile(file_welsch_storage_start)
src.intraday_welsch2(file_welsch_storage, blocks_per_day, timeslices, representative_days, chronological_sequence, StorageLevelStartWelsch, file_welsch_intraday)


file_base = Path(results_destination_folder) / ('_'.join(['k365h1WND_Storage_Level_Model_Niet']) + '.csv')
file_kotzur = Path(results_destination_folder) / ('_'.join([scenario_name,results_copied_filename,'Model_Kotzur']) + '.csv')
file_cluster = Path(results_destination_folder) / ('_'.join([scenario_name,results_copied_filename,'Model_Cluster']) + '.csv')
file_niet = Path(results_destination_folder) / ('_'.join([scenario_name,results_copied_filename,'Model_Niet']) + '.csv')
file_welsch = Path(results_destination_folder) / ('_'.join([scenario_name,results_copied_filename,'Model_Welsch']) + '.csv')

" Any output_yearsplit_csv_file"
output_yearsplit_csv_file=Path(config['cases']['Model_Cluster']['root_directory']) / config['cases']['Model_Cluster']['input_otoole_csv']['directory'] / config['cases']['Model_Cluster']['input_otoole_csv']['yearsplit']
fig, fig2, fig3 = src.graph(file_base, file_kotzur, file_kotzur_intraday, file_cluster, file_niet, file_welsch, file_welsch_intraday, representative_days, blocks_per_day, output_yearsplit_csv_file)


figure_filename = '_'.join([scenario_name, 'Figure']) + '.png'
figure_path = Path(results_destination_folder) / figure_filename
figure_GUI_pah = Path(results_GUI_destination_folder) / figure_filename
fig.savefig(figure_path)
#fig.savefig(figure_GUI_pah)


figure2_filename = '_'.join([scenario_name, 'Figure_Hourly']) + '.png'
figure2_path = Path(results_destination_folder) / figure2_filename


fig2.savefig(figure2_path)
fig2.savefig(figure_GUI_pah)


figure3_filename = '_'.join([scenario_name, 'Figure_Hourly_2Weeks']) + '.png'
figure3_path = Path(results_destination_folder) / figure3_filename


fig3.savefig(figure3_path)
