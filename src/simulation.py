import os
import subprocess
import re
import time

# GLPK's primal simplex occasionally fails to recover an optimal basis on these LPs
# ("glp_simplex: unable to recover undefined or non-optimal solution"); whether it happens depends
# on platform and build. The same LP then solves with the options below, all giving the same
# optimum. Earlier versions did not detect the failure and read stale result CSVs from the
# previous scenario (8 Welsch rows of the archived sweep have Total cost = 0 for this reason).
FALLBACK_OPTIONS = ["", "--nopresol", "--dual", "--exact"]


def _solved(output):
    return ("OPTIMAL LP SOLUTION FOUND" in output) or ("OPTIMAL SOLUTION FOUND" in output)


def run_simulation(case_info):
    root_directory = case_info['root_directory']
    # The model files write their result CSVs to ResultsPath = '<Model_X>/results', relative to the
    # folder that holds the model folders, so glpsol runs from there (models/).
    models_directory = os.path.dirname(os.path.abspath(root_directory))
    case_folder = os.path.basename(os.path.normpath(root_directory))
    data_infile_path = os.path.join(case_folder, case_info['output_otoole_txt'])
    model_file_path = os.path.join(case_folder, case_info['model_file'])
    data_glp_path = os.path.join(case_folder, case_info['data_glp'])
    data_sol_path = os.path.join(case_folder, case_info['data_sol'])

    start_time = time.time()
    for option in FALLBACK_OPTIONS:
        command = f"glpsol -m {model_file_path} -d {data_infile_path} --wglp {data_glp_path} --write {data_sol_path} {option}".strip()
        result = subprocess.run(command, capture_output=True, text=True, shell=True, cwd=models_directory)
        output = result.stdout + result.stderr
        if _solved(output):
            break
        print(f"!!! {root_directory}: GLPK did not report an optimal solution with options '{option}'; retrying")
    end_time = time.time()
    execution_time = end_time - start_time
    status = "optimal" if _solved(output) else "FAILED"

    print(f"Simulation output:\n{output}")

    time_used_search = re.search(r"Time used:\s+([\d.]+)\s+secs", output)
    memory_used_search = re.search(r"Memory used:\s+([\d.]+)\s+Mb", output)
    time_used = time_used_search.group(1) if time_used_search else "nan"
    memory_used = memory_used_search.group(1) if memory_used_search else "nan"
    print(f"Total Time: {execution_time:.2f} seconds")
    print(f"Running Time: {time_used} seconds")
    print(f"Memory Used: {memory_used} MB")
    print(f"Solver status: {status} (options: '{option}')")

    results_file_path = os.path.join(root_directory, "simulation_results.txt")
    with open(results_file_path, 'w') as results_file:
        results_file.write(f"Matrix + Running Time: {execution_time:.2f} seconds\n")
        results_file.write(f"Running Time: {time_used} seconds\n")
        results_file.write(f"Memory Used: {memory_used} MB\n")
        results_file.write(f"Solver status: {status}\n")
        results_file.write(f"GLPK options: {option or 'default'}\n")
    return status
