import yaml
import subprocess

n_clusters = [4]
#n_clusters = [4, 8, 12]
#n_clusters = [2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40]
#n_clusters = [2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
#n_clusters = [50, 60, 70, 80, 90, 100]

hour_grouping = [1]
#hour_grouping = [12]
#hour_grouping = [1, 2, 4, 6, 8, 12]

############# OTHER UPDATES #######################

# Fix the final name of scenario_name in this file

# Fix in the config the:
    # directory_GUI = 'Results\GUI2'
    # CF = 'CapacityFactor1.csv'

# Remove the 'base' plot from the 3 graphs in graph_generator if running the 365

# Update the base file in main

####################################################

def update_yaml_and_run_script(n_cluster, hour_group, yaml_path, python_script_path):
    
    with open(yaml_path, 'r') as file:
        config_data = yaml.safe_load(file)

    config_data['n_clusters'] = n_cluster
    config_data['hour_grouping'] = hour_group
    #config_data['scenario_name'] = f"k{n_cluster}h{hour_group}sazonal2"
    #config_data['scenario_name'] = f"k{n_cluster}h{hour_group}eol_limitado"
    #config_data['scenario_name'] = f"k{n_cluster}h{hour_group}WND"
    config_data['scenario_name'] = f"k{n_cluster}h{hour_group}WND_limited"
    #config_data['scenario_name'] = f"k{n_cluster}h{hour_group}"
    
    with open(yaml_path, 'w') as file:
        yaml.safe_dump(config_data, file)

    subprocess.run(['.venv\Scripts\python', python_script_path])

def automate_configurations(n_clusters_list, hour_grouping_list, yaml_path, python_script_path):
    for n_cluster in n_clusters_list:
        for hour_group in hour_grouping_list:
            update_yaml_and_run_script(n_cluster, hour_group, yaml_path, python_script_path)

automate_configurations(n_clusters, hour_grouping, 'config.yaml', 'main.py')
