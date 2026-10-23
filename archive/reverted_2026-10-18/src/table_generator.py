import pandas as pd
from os.path import exists
from typing import Optional

def read_simulation_results(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    memory_used = lines[2].split(": ")[1].strip()
    running_time = lines[1].split(": ")[1].strip()
    matrix_running_time = lines[0].split(": ")[1].strip()
    return matrix_running_time, running_time, memory_used

def read_sol_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    num_constraints = int(lines[1].split(":")[1].strip())
    num_variables = int(lines[2].split(":")[1].strip())
    non_zeros = int(lines[3].split(":")[1].strip())
    total_cost = float(lines[5].split("=")[1].strip().split(" ")[0])
    return num_constraints, num_variables, non_zeros, total_cost

def read_excel_value(file_path, filter_col, filter_val):
    df = pd.read_csv(file_path)
    filtered_value = df[df[filter_col] == filter_val]['VALUE'].iloc[0] if not df[df[filter_col] == filter_val].empty else None
    return filtered_value

def append_to_excel(df, excel_path):
    if exists(excel_path):
        with pd.ExcelWriter(excel_path, mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
    else:
        df.to_excel(excel_path, index=False)

def table(
    sim_results_path: str,
    sol_path: str,
    scenario_name: str,
    model: str,
    new_capacity_path: str,
    new_storage_capacity_path: str,
    filter_val1: str,
    filter_val2: str,
    excel_path: str
) -> None:
    matrix_running_time, running_time, memory_used = read_simulation_results(sim_results_path)
    num_constraints, num_variables, non_zeros, total_cost = read_sol_file(sol_path)
    new_capacity_value = read_excel_value(new_capacity_path, 'TECHNOLOGY', filter_val1)
    new_storage_capacity_value = read_excel_value(new_storage_capacity_path, 'STORAGE', filter_val2)
    data = {
        "Scenario": [scenario_name],
        "Model": [model],
        "Number of constraints": [num_constraints],
        "Number of variables": [num_variables],
        "Non-zero elements in the matrix": [non_zeros],
        "Total cost": [total_cost],
        "Matriz and Running Time": [matrix_running_time],
        "Running time": [running_time],
        "Memory used": [memory_used],
        "Power Capacity": [new_capacity_value],
        "Storage Capacity": [new_storage_capacity_value]
    }
    results_df = pd.DataFrame(data)
    append_to_excel(results_df, excel_path)

