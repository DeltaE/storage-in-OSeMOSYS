# Basic Usage Tutorial

## Getting Started with Storage-in-OSeMOSYS

This tutorial provides a step-by-step guide to using the Storage-in-OSeMOSYS framework for energy system modeling with storage technologies.

## Prerequisites

Before starting, ensure you have:

- **Environment Setup**: Conda environment with all dependencies installed
- **Data Preparation**: Input data files in the correct format
- **GLPK Solver**: Linear programming solver for optimization

## Quick Start Example

### 1. Environment Activation

```bash
# Activate the conda environment
conda activate storage_osemosys

# Verify installation
python -c "import otoole; print('OtoOle version:', otoole.__version__)"
```

### 2. Basic Model Run

```python
# Import required modules
from pathlib import Path
import pandas as pd
from src.utilities import *

# Set up paths
project_root = Path.cwd()
config_path = project_root / "config" / "config.yaml"
input_path = project_root / "inputs_csv"
output_path = project_root / "Results"

# Load configuration
config = load_config(config_path)

# Run basic model
method = "Kotzur"  # Choose clustering method
result = run_storage_model(method, input_path, output_path, config)
```

### 3. Examining Results

```python
# Load and examine storage results
storage_results = pd.read_csv(output_path / "StorageLevelStart.csv")
print("Storage level results:")
print(storage_results.head())

# Plot storage operation
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(storage_results['Value'])
plt.title('Storage Level Over Time')
plt.xlabel('Time Period')
plt.ylabel('Storage Level')
plt.grid(True)
plt.show()
```

## Step-by-Step Workflow

### Step 1: Data Preparation

Prepare your input data in CSV format:

```
inputs_csv/
├── TECHNOLOGY.csv          # Technology definitions
├── FUEL.csv                # Fuel types
├── STORAGE.csv             # Storage technologies
├── CapitalCost.csv         # Investment costs
├── VariableCost.csv        # Operational costs
└── ... (other parameter files)
```

### Step 2: Configuration

Edit the configuration file:

```yaml
# config/config.yaml
model:
  method: "Kotzur"           # Clustering method
  years: [2020, 2030, 2040] # Model years
  regions: ["REGION1"]       # Regions to model

storage:
  technologies: ["BATT", "PHES"]  # Storage technologies
  initial_level: 0.5              # Initial storage level (50%)
  
solver:
  name: "glpk"              # Solver to use
  options: "--tmlim 3600"   # Solver options
```

### Step 3: Model Execution

Run the complete workflow:

```python
from pathlib import Path
import subprocess

# Set method and paths
method = "Kotzur"
input_excel = "path/to/input.xlsx"
output_dir = "Results"

# Convert Excel to CSV
convert_excel_to_csv(input_excel, "inputs_csv")

# Run clustering (if needed)
if method != "8760":
    run_temporal_clustering(method, "inputs_csv")

# Generate data file
generate_datafile("inputs_csv", f"model_{method}.dat")

# Solve model
solve_model(f"model_{method}.dat", f"solution_{method}.sol")

# Extract results
extract_results(f"solution_{method}.sol", output_dir)
```

### Step 4: Results Analysis

Analyze the results:

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load results
capacity = pd.read_csv("Results/TotalCapacityAnnual.csv")
storage_level = pd.read_csv("Results/StorageLevelStart.csv")
production = pd.read_csv("Results/ProductionByTechnology.csv")

# Plot capacity expansion
storage_capacity = capacity[capacity['TECHNOLOGY'].str.contains('STORAGE')]
plt.figure(figsize=(10, 6))
for tech in storage_capacity['TECHNOLOGY'].unique():
    tech_data = storage_capacity[storage_capacity['TECHNOLOGY'] == tech]
    plt.plot(tech_data['YEAR'], tech_data['VALUE'], label=tech, marker='o')

plt.title('Storage Capacity Expansion')
plt.xlabel('Year')
plt.ylabel('Capacity (GW)')
plt.legend()
plt.grid(True)
plt.show()
```

## Common Use Cases

### Case 1: Renewable Integration Study

```python
# Configure for high renewable scenario
config = {
    'renewable_target': 0.8,  # 80% renewable target
    'storage_cost_reduction': 0.5,  # 50% cost reduction by 2030
    'method': 'Kotzur'  # Use Kotzur clustering
}

# Run scenario
results = run_scenario('high_renewable', config)
```

### Case 2: Storage Technology Comparison

```python
# Compare different storage technologies
storage_techs = ['BATT', 'PHES', 'CAES']  # Battery, Pumped Hydro, Compressed Air

results = {}
for tech in storage_techs:
    config['storage_technologies'] = [tech]
    results[tech] = run_storage_model('Kotzur', inputs, outputs, config)

# Compare results
compare_storage_technologies(results)
```

### Case 3: Temporal Resolution Study

```python
# Compare different temporal clustering methods
methods = ['Kotzur', 'Niet', 'Welsch', '8760']

results = {}
for method in methods:
    results[method] = run_storage_model(method, inputs, outputs, config)

# Analyze computational efficiency vs. accuracy
analyze_temporal_methods(results)
```

## Best Practices

### Data Quality

- **Validate Input Data**: Check for missing values, unrealistic parameters
- **Consistent Units**: Ensure all data uses consistent units (GW, GWh, etc.)
- **Time Series Alignment**: Verify time series data alignment

### Model Configuration

- **Appropriate Method Selection**: Choose clustering method based on study needs
- **Solver Settings**: Configure solver for optimal performance
- **Storage Parameters**: Set realistic storage characteristics

### Performance Optimization

- **Memory Management**: Monitor memory usage for large models
- **Parallel Processing**: Use multiple cores when available
- **Result Storage**: Efficiently store and organize results

## Troubleshooting

### Common Issues

1. **Empty Result Files**
   - Check model constraints
   - Verify data file generation
   - Review solver log

2. **Long Computation Times**
   - Consider temporal clustering
   - Optimize solver settings
   - Reduce model complexity

3. **Infeasible Solutions**
   - Review storage constraints
   - Check demand-supply balance
   - Validate technology parameters

### Getting Help

- **Documentation**: Refer to the complete documentation
- **Examples**: Check additional example notebooks
- **Community**: Join the OSeMOSYS community forums
- **Issues**: Report bugs on the GitHub repository

## Next Steps

After completing this basic tutorial:

1. **Explore Advanced Features**: Learn about advanced configuration options
2. **Comparative Analysis**: Compare different modeling approaches
3. **Custom Analysis**: Develop custom analysis scripts
4. **Contribute**: Contribute to the project development

Continue with the [Comparative Analysis](comparative_analysis.md) tutorial for more advanced usage.
