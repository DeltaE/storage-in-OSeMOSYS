import shutil
import os

def copy_and_rename(results_case, results_destination_folder, new_results_filename):
    
    results_destination_path = os.path.join(results_destination_folder, new_results_filename)

    shutil.copy(results_case, results_destination_path)