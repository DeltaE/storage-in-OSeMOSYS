import os
import subprocess
import re
import time

def run_simulation(case_info):
    root_directory = case_info['root_directory']
    data_infile_path = os.path.join(root_directory, case_info['output_otoole_txt'])
    model_file_path = os.path.join(root_directory, case_info['model_file'])
    data_glp_path = os.path.join(root_directory, case_info['data_glp'])
    data_sol_path = os.path.join(root_directory, case_info['data_sol'])

    command = f"glpsol -m {model_file_path} -d {data_infile_path} --wglp {data_glp_path} --write {data_sol_path}"
    
    start_time = time.time()
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    end_time = time.time()
    execution_time = end_time - start_time

    output = result.stdout + result.stderr
    
    print(f"Simulation output:\n{output}")
    
    time_used_search = re.search(r"Time used:\s+([\d.]+)\s+secs", output)
    memory_used_search = re.search(r"Memory used:\s+([\d.]+)\s+Mb", output)

    if time_used_search and memory_used_search:
        time_used = time_used_search.group(1)
        memory_used = memory_used_search.group(1)
        print(f"XXXXXXXXXXXXX Total Time: {execution_time:.2f} seconds")
        print(f"XXXXXXXXXXXXX Running Time: {time_used} seconds")
        print(f"XXXXXXXXXXXXX Memory Used: {memory_used} MB")
    
        results_file_path = os.path.join(root_directory, "simulation_results.txt")
        with open(results_file_path, 'w') as results_file:
            results_file.write(f"Matrix + Running Time: {execution_time:.2f} seconds\n")
            results_file.write(f"Running Time: {time_used} seconds\n")
            results_file.write(f"Memory Used: {memory_used} MB\n")
    else:
        print("Could not find time or memory usage information in the output.")
