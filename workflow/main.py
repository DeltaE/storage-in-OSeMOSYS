"""Run one scenario (all selected storage formulations) as defined in config/config.yaml.

Usage, from anywhere:  python workflow/main.py
"""
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
os.chdir(REPO)  # all paths in config/config.yaml are relative to the repository root
sys.path.insert(0, str(REPO))

import matplotlib
matplotlib.use('Agg')  # headless backend: no Qt needed, figures are written to disk
import json
import src.utilities as utils
import src # loading the src module to access its functions/methods
import otoole
import shutil


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
system_inputs_dir:Path = Path(config.get('system_inputs', 'data/system'))  # parameter CSVs shared by all formulations

random_state:int = config.get('random_state', 0)          # manuscript: fixed random state 0
vre_technology:str = config.get('vre_technology', 'WINDPOWER')  # all data/timeseries CF files use this label
representative_days, chronological_sequence = src.cluster_data(input_CF_csv_file,input_SDP_csv_file,n_clusters, random_state=random_state)
# Traceability: store the exact clustering used by all four formulations
with open(results_destination_folder / f"{scenario_name}_clustering.json", 'w') as fh:
    json.dump({'scenario': scenario_name, 'random_state': random_state, 'n_clusters': n_clusters,
               'hour_grouping': hour_grouping, 'CF': str(input_CF_csv_file), 'SDP': str(input_SDP_csv_file),
               'StorageMaxCapacity': StorageMaxCapacity,
               'representative_days': [int(d) for d in representative_days],
               'chronological_sequence': [int(d) for d in chronological_sequence]}, fh)
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
# Optional subset of formulations, e.g. models: [Model_Niet, Model_Kotzur] (default: all four)
_selected = config.get('models') or list(cases.keys())
cases = {k: v for k, v in cases.items() if k in _selected}

utils.print_info(f"Cases from config: {list(cases.keys())}")
for case_name, case_info in cases.items():
    # --- prepare a clean case directory BEFORE any formulation-specific step ---
    case_root = Path(case_info['root_directory'])
    case_input_dir = case_root / case_info['input_otoole_csv']['directory']
    case_input_dir.mkdir(parents=True, exist_ok=True)
    case_results_dir = case_root / case_info['results']['directory']
    case_results_dir.mkdir(parents=True, exist_ok=True)  # glpsol cannot create it
    # Remove this formulation's OWN generated outputs from the previous run (git-ignored), so a failed
    # solve can never be reported with stale results from an earlier scenario.
    for stale in list(case_results_dir.glob('*.csv')) + [case_root / case_info['data_sol']]:
        stale.unlink(missing_ok=True)
    # Run parameters (DaySplit, YearSplit, storage limits) are written into a git-ignored copy of the
    # otoole template, so the tracked model files under models/ never change when a scenario runs.
    template_otoole_config = case_root / case_info['otoole_config']
    run_otoole_config = case_root / f"{template_otoole_config.stem}.run.yaml"
    shutil.copy(template_otoole_config, run_otoole_config)
    expected_names = set(utils.load_config(template_otoole_config).keys())
    for csv_file in system_inputs_dir.glob('*.csv'):
        if csv_file.stem in expected_names:
            shutil.copy(csv_file, case_input_dir / csv_file.name)
    # ---------------------------------------------------------------------------------------------

    if case_name == 'Model_Cluster':
        utils.print_update(level=1,message=f"Updating case: {case_name}")

        # Updating timeslicecro
        output_timeslicecro_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['timeslicecro']
        
        src.new_list(chronological_timeslices, output_timeslicecro_csv_file)

        # Updating conversionlts
        output_conversionlts_csv_file = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory'] / case_info['input_otoole_csv']['conversionlts']
        src.conversionlts(blocks_per_day, chronological_timeslices, timeslices, chronological_sequence, representative_days, output_conversionlts_csv_file)

        # Updating day split in yaml file
        otoole_yaml_file = run_otoole_config
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
        otoole_yaml_file = run_otoole_config
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
        otoole_yaml_file = run_otoole_config
        src.new_yaml_param(otoole_yaml_file, 'DaySplit', day_split)

    if case_name == 'Model_Niet' or case_name == 'Model_Cluster' or case_name == 'Model_Kotzur' or case_name == 'Model_Welsch':
        utils.print_update(level=1,message=f"Updating case: {case_name}")
        
        # Define the source directory
        source_template = system_inputs_dir
        # List all CSV files in the directory
        csv_files = list(source_template.glob('*.csv'))
                
        # Creating txt from csv using otoole
        input_csv_dir = Path(case_info['root_directory']) / case_info['input_otoole_csv']['directory']
        output_txt_file = Path(case_info['root_directory']) / case_info['output_otoole_txt']
        template_config = run_otoole_config
        
        # NOTE: the template CSVs from data/system/ are now copied at the
        # START of each case (see top of loop). Copying them here overwrote the formulation-specific
        # files generated above (Conversionld, Conversionlh, Conversionls, DaysInDayType,
        # DAILYTIMEBRACKET) with empty templates, which silently broke Kotzur and Welsch.
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
        otoole_yaml_file = run_otoole_config
        src.new_yaml_param(otoole_yaml_file, 'YearSplit', year_split)

        # Updating storage info in yaml file
        #src.new_yaml_param(otoole_yaml_file, 'StorageLevelStart', StorageLevelStart)
        src.new_yaml_param(otoole_yaml_file, 'StorageMaxCapacity', StorageMaxCapacity)
        src.new_yaml_param(otoole_yaml_file, 'ResidualStorageCapacity', ResidualStorageCapacity)
        
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
    src.table(simulation_results, data_sol_results, scenario_name, case_name, capacity_path, storage_capacity_path, vre_technology, 'BATTERY', results_file)

print("Post-processing: intraday reconstruction and figures")
from src.update_conversionlts import conversionlts_sparse

if 'Model_Kotzur' in cases:
    # Sparse chronological mapping (identical information to Model_Cluster's Conversionlts, VALUE == 1 rows)
    file_conversionlts = Path(results_destination_folder) / f"{scenario_name}_Conversionlts_sparse.csv"
    conversionlts_sparse(blocks_per_day, chronological_sequence, representative_days, file_conversionlts)
    file_kotzur_storage = Path(config['cases']['Model_Kotzur']['root_directory']) / config['cases']['Model_Kotzur']['results']['directory'] / config['cases']['Model_Kotzur']['results']['storage_levelTS']
    file_kotzur_intraday = Path(results_destination_folder) / ('_'.join([scenario_name,results_copied_filename,'Model_Kotzur_intraday']) + '.csv')
    file_kotzur_storage_start = Path(config['cases']['Model_Kotzur']['root_directory']) / config['cases']['Model_Kotzur']['results']['directory'] / config['cases']['Model_Kotzur']['results']['storage_level_Start']
    StorageLevelStartKotzur = src.read_csvfile(file_kotzur_storage_start)
    src.intraday_kotzur(file_conversionlts, file_kotzur_storage, StorageLevelStartKotzur, file_kotzur_intraday)

if 'Model_Welsch' in cases:
    file_welsch_storage = Path(config['cases']['Model_Welsch']['root_directory']) / config['cases']['Model_Welsch']['results']['directory'] / config['cases']['Model_Welsch']['results']['storage_levelTS']
    file_welsch_intraday = Path(results_destination_folder) / ('_'.join([scenario_name,results_copied_filename,'Model_Welsch_intraday']) + '.csv')
    file_welsch_storage_start = Path(config['cases']['Model_Welsch']['root_directory']) / config['cases']['Model_Welsch']['results']['directory'] / config['cases']['Model_Welsch']['results']['storage_level_Start']
    StorageLevelStartWelsch = src.read_csvfile(file_welsch_storage_start)
    src.intraday_welsch2(file_welsch_storage, blocks_per_day, timeslices, representative_days, chronological_sequence, StorageLevelStartWelsch, file_welsch_intraday)

if set(cases) != {'Model_Cluster', 'Model_Kotzur', 'Model_Niet', 'Model_Welsch'}:
    utils.print_update(level=2, message="Subset of formulations run: comparison figures skipped.")
else:
    # Baseline file is only read by graph(); the base curve itself is not plotted. Use the matching
    # full-year run if present, otherwise fall back to this scenario's Niet result (previously hard-coded to WND).
    file_base = Path(results_destination_folder) / f"k365h1{config.get('resource', 'WND')}_{results_copied_filename}_Model_Niet.csv"
    if not file_base.exists():
        file_base = Path(results_destination_folder) / ('_'.join([scenario_name,results_copied_filename,'Model_Niet']) + '.csv')
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


    figure2_filename = '_'.join([scenario_name, 'Figure_Hourly']) + '.png'
    figure2_path = Path(results_destination_folder) / figure2_filename


    fig2.savefig(figure2_path)
    fig2.savefig(figure_GUI_pah)


    figure3_filename = '_'.join([scenario_name, 'Figure_Hourly_2Weeks']) + '.png'
    figure3_path = Path(results_destination_folder) / figure3_filename


    fig3.savefig(figure3_path)

import matplotlib.pyplot as plt
plt.close('all')
