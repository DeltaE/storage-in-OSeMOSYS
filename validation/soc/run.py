import os
import sys
import shutil
import subprocess
import yaml
import pandas as pd

case_directory = os.path.dirname(os.path.abspath(__file__))
root_directory = os.path.dirname(os.path.dirname(case_directory))  # repository root (validation/soc -> ..)
sys.path.insert(0, root_directory)

from src.update_list import new_list
from src.update_yearsplit import yearsplit
from src.update_conversionld import conversionld
from src.update_conversionlh import conversionlh
from src.update_conversionldc import conversionldc
from src.update_conversionlts import conversionlts
from src.update_daysindaytype import daysindaytype
from src.update_params_yaml_otoole import new_yaml_param
from src.Kotzur_intraday import intraday_kotzur
from src.Welsch_intraday2 import intraday_welsch2

output_directory = os.path.join(case_directory, 'results')
input_directory = os.path.join(output_directory, 'inputs_csv')
shutil.copytree(os.path.join(case_directory, 'inputs_csv'), input_directory, dirs_exist_ok=True)
hour_grouping = 6
days_in_year = 4
period_hours = 24 * days_in_year
representative_days = [1, 2]
chronological_sequence = [1, 2, 1, 2]
blocks_per_day = 24 // hour_grouping
timeslices = len(representative_days) * blocks_per_day
chronological_timeslices = days_in_year * blocks_per_day

# Input CSVs use MW and MWh; model time weights are normalized over 96 hours.
for name in ['SpecifiedAnnualDemand', 'StorageLevelStart',
             'ResidualStorageCapacity', 'StorageMaxCapacity']:
    path = os.path.join(input_directory, name + '.csv')
    data = pd.read_csv(path)
    data['VALUE'] = data['VALUE'] / period_hours
    data.to_csv(path, index=False)

# Prepare temporal inputs with the same functions used in main.py.
for name, length in [('TIMESLICE', timeslices), ('DAYTYPE', len(representative_days)),
                     ('DAILYTIMEBRACKET', blocks_per_day), ('DAYSCRO', days_in_year),
                     ('TIMESLICECRO', chronological_timeslices)]:
    new_list(length, os.path.join(input_directory, name + '.csv'))
yearsplit(timeslices, representative_days, chronological_sequence, days_in_year,
          os.path.join(input_directory, 'YearSplit.csv'))
conversionld(timeslices, len(representative_days), os.path.join(input_directory, 'Conversionld.csv'))
conversionlh(timeslices, blocks_per_day, os.path.join(input_directory, 'Conversionlh.csv'))
conversionld(timeslices, 1, os.path.join(input_directory, 'Conversionls.csv'), label='SEASON')
conversionldc(chronological_sequence, representative_days, days_in_year,
              os.path.join(input_directory, 'Conversionldc.csv'))
conversion_path = os.path.join(input_directory, 'Conversionlts.csv')
conversionlts(blocks_per_day, chronological_timeslices, timeslices,
              chronological_sequence, representative_days, conversion_path)
daysindaytype(representative_days, chronological_sequence,
              os.path.join(input_directory, 'DaysInDayType.csv'))

initial_state = pd.read_csv(os.path.join(input_directory, 'StorageLevelStart.csv'),
                            float_precision='round_trip')['VALUE'].iloc[0]
manual = pd.read_csv(os.path.join(case_directory, 'independent_reference.csv'))
comparison = []
summary = []

for model_name in ['Niet', 'Welsch', 'Kotzur', 'Cluster']:
    print('Running Model_' + model_name, flush=True)
    formulation = 'Novo' if model_name == 'Cluster' else model_name
    reference = manual[formulation + '_MWh'].dropna().reset_index(drop=True)
    original_directory = os.path.join(root_directory, 'models', 'Model_' + model_name)
    model_directory = os.path.join(output_directory, 'Model_' + model_name)
    model_input_directory = os.path.join(model_directory, 'inputs_csv')
    results_directory = os.path.join(model_directory, 'results')
    os.makedirs(model_input_directory, exist_ok=True)
    os.makedirs(results_directory, exist_ok=True)

    # Copy the configuration and input CSVs required by each formulation.
    config_name = 'otoole_config_' + model_name + '.yaml'
    config_path = os.path.join(model_directory, config_name)
    shutil.copyfile(os.path.join(original_directory, config_name), config_path)
    new_yaml_param(config_path, 'DaySplit', hour_grouping / period_hours)
    with open(config_path) as file:
        config = yaml.safe_load(file)
    for name, definition in config.items():
        if definition['type'] in ['param', 'set']:
            shutil.copyfile(os.path.join(input_directory, name + '.csv'),
                            os.path.join(model_input_directory, name + '.csv'))

    data_path = os.path.join(model_directory, model_name + '.txt')
    subprocess.run(['otoole', 'convert', 'csv', 'datafile', model_input_directory,
                    data_path, config_path])

    # Fix the initial SoC variable to the value used in the manual calculation.
    # The model determines charging and discharging from generation and demand inputs.
    with open(os.path.join(original_directory, 'osemosys_fast_' + model_name + '.txt'), encoding='utf-8') as file:
        model = file.read()
    initial_condition = ("\ns.t. InitialSoC: StorageLevelStart['Simplicity2','BATTERY'] = "
                         + str(initial_state) + ';\nsolve;')
    model_path = os.path.join(model_directory, 'osemosys_fast_' + model_name + '.txt')
    with open(model_path, 'w', encoding='utf-8') as file:
        file.write(model.replace('\nsolve;', initial_condition))
    result = subprocess.run(['glpsol', '-m', model_path, '-d', data_path],
                            cwd=output_directory, capture_output=True, text=True)
    with open(os.path.join(model_directory, 'solver.log'), 'w', encoding='utf-8') as file:
        file.write(result.stdout + result.stderr)

    # Compare native storage states with their manual references.
    if model_name in ['Niet', 'Cluster']:
        native_file, state_column = 'StorageLevelTSStart.csv', 'StorageLevelTSStart'
        index_column = 'TIMESLICE' if model_name == 'Niet' else 'TIMESLICECRO'
        expected_native = reference
    elif model_name == 'Kotzur':
        native_file, state_column = 'StorageLevelChronoDayStart.csv', 'StorageLevelChronoDayStart'
        index_column = 'DAYSCRO'
        expected_native = reference.iloc[::blocks_per_day].reset_index(drop=True)
    else:
        native_file, state_column = 'StorageLevelDayTypeStart.csv', 'StorageLevelDayTypeStart'
        index_column = 'DAYTYPE'
        # Start of group A and start of group B, after both occurrences of A.
        expected_native = reference.iloc[[0, 2 * blocks_per_day]].reset_index(drop=True)
    native = pd.read_csv(os.path.join(results_directory, native_file), float_precision='round_trip')
    native_soc = native.sort_values(index_column)[state_column].reset_index(drop=True) * period_hours
    native_error = (native_soc - expected_native).abs().max()
    reconstructed_error = None
    comparison.append(pd.DataFrame({'Formulation': formulation, 'Output': 'Native',
                                   'Point': range(1, len(native_soc) + 1),
                                   'Manual_MWh': expected_native, 'Model_MWh': native_soc}))

    # Compare trajectories reconstructed by the existing Kotzur and Welsch functions.
    if model_name in ['Kotzur', 'Welsch']:
        storage_path = os.path.join(results_directory, 'StorageLevelTSResults.csv')
        start = pd.read_csv(os.path.join(results_directory, 'StorageLevelStartResults.csv'),
                            float_precision='round_trip')['VALUE'].iloc[0]
        reconstructed_path = os.path.join(results_directory, 'reconstructed_soc.csv')
        if model_name == 'Kotzur':
            intraday_kotzur(conversion_path, storage_path, start, reconstructed_path)
        else:
            intraday_welsch2(storage_path, blocks_per_day, timeslices, representative_days,
                            chronological_sequence, start, reconstructed_path)
        reconstructed = pd.read_csv(reconstructed_path, float_precision='round_trip')
        calculated_soc = reconstructed['VALUEACCUMULATED'] * period_hours
        reconstructed_error = (calculated_soc - reference).abs().max()
        comparison.append(pd.DataFrame({'Formulation': formulation, 'Output': 'Reconstructed',
                                       'Point': range(1, len(calculated_soc) + 1),
                                       'Manual_MWh': reference, 'Model_MWh': calculated_soc}))

    summary.append({'Formulation': formulation, 'Native_points': len(native_soc),
                    'Max_native_error_MWh': native_error,
                    'Max_reconstructed_error_MWh': reconstructed_error})

comparison = pd.concat(comparison, ignore_index=True)
comparison['Difference_MWh'] = comparison['Model_MWh'] - comparison['Manual_MWh']
comparison.to_csv(os.path.join(output_directory, 'soc_comparison.csv'), index=False)
summary = pd.DataFrame(summary)
summary.to_csv(os.path.join(output_directory, 'summary.csv'), index=False)
print(summary.to_string(index=False))
