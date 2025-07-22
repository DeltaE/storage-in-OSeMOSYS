import yaml

def new_yaml_param(yaml_file, param_name, new_value):
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)
    
    if param_name in data:
        data[param_name]['default'] = new_value
        with open(yaml_file, 'w') as file:
            yaml.safe_dump(data, file)
