# Comparative Analysis Tutorial

## Overview

This tutorial demonstrates how to perform comparative analysis using different temporal clustering methods and storage configurations in the Storage-in-OSeMOSYS framework.

## Temporal Clustering Methods Comparison

### Available Methods

The framework supports four temporal representation methods:

1. **Kotzur Method** - Advanced k-means clustering with storage considerations
2. **Niet Method** - Hierarchical clustering approach
3. **Welsch Method** - Representative days selection
4. **8760 Hours** - Full hourly resolution (baseline)

### Comparison Setup

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from src.utilities import *
import time

# Define comparison parameters
methods = ['Kotzur', 'Niet', 'Welsch', '8760']
input_path = Path("inputs_csv")
output_base = Path("Results_Comparison")

# Storage for results
results = {}
performance_metrics = {}

# Run comparison
for method in methods:
    print(f"\n=== Running {method} Method ===")
    
    # Track computational time
    start_time = time.time()
    
    # Create method-specific output directory
    output_path = output_base / f"Results_{method}"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Run model
    try:
        result = run_storage_model(method, input_path, output_path)
        results[method] = result
        
        # Calculate performance metrics
        computation_time = time.time() - start_time
        performance_metrics[method] = {
            'computation_time': computation_time,
            'model_size': get_model_size(method),
            'memory_usage': get_memory_usage()
        }
        
        print(f"✓ {method} completed in {computation_time:.2f} seconds")
        
    except Exception as e:
        print(f"✗ {method} failed: {str(e)}")
        results[method] = None
```

### Performance Analysis

```python
# Create performance comparison dataframe
perf_df = pd.DataFrame(performance_metrics).T
print("Performance Comparison:")
print(perf_df)

# Plot computation time comparison
plt.figure(figsize=(12, 8))

# Subplot 1: Computation Time
plt.subplot(2, 2, 1)
methods_clean = [m for m in methods if m in perf_df.index]
times = [perf_df.loc[m, 'computation_time'] for m in methods_clean]
bars = plt.bar(methods_clean, times, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
plt.title('Computation Time Comparison')
plt.ylabel('Time (seconds)')
plt.xticks(rotation=45)

# Add value labels on bars
for bar, time_val in zip(bars, times):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
             f'{time_val:.1f}s', ha='center', va='bottom')

# Subplot 2: Model Size
plt.subplot(2, 2, 2)
sizes = [perf_df.loc[m, 'model_size'] for m in methods_clean]
bars = plt.bar(methods_clean, sizes, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
plt.title('Model Size Comparison')
plt.ylabel('Variables + Constraints')
plt.xticks(rotation=45)

# Add value labels
for bar, size in zip(bars, sizes):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
             f'{size:,}', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.show()
```

## Storage Technology Comparison

### Multi-Technology Analysis

```python
# Define storage technologies to compare
storage_technologies = {
    'Battery': {
        'capital_cost': 400,  # $/kWh
        'efficiency': 0.85,
        'max_hours': 4
    },
    'Pumped_Hydro': {
        'capital_cost': 150,  # $/kWh
        'efficiency': 0.75,
        'max_hours': 8
    },
    'Compressed_Air': {
        'capital_cost': 100,  # $/kWh
        'efficiency': 0.65,
        'max_hours': 12
    }
}

# Run comparison for each technology
storage_results = {}

for tech_name, tech_params in storage_technologies.items():
    print(f"\n=== Analyzing {tech_name} ===")
    
    # Update configuration for this technology
    config = update_storage_config(tech_params)
    
    # Run model with Kotzur method (fastest)
    output_path = output_base / f"Storage_{tech_name}"
    result = run_storage_model('Kotzur', input_path, output_path, config)
    storage_results[tech_name] = result

# Compare storage technology results
compare_storage_technologies(storage_results)
```

### Storage Impact Analysis

```python
# Compare scenarios with and without storage
scenarios = {
    'No_Storage': {'storage_enabled': False},
    'With_Storage': {'storage_enabled': True}
}

scenario_results = {}

for scenario_name, config in scenarios.items():
    print(f"\n=== Running {scenario_name} Scenario ===")
    output_path = output_base / f"Scenario_{scenario_name}"
    result = run_storage_model('Kotzur', input_path, output_path, config)
    scenario_results[scenario_name] = result

# Analyze storage impact
analyze_storage_impact(scenario_results)
```

## Accuracy vs. Efficiency Trade-offs

### Clustering Accuracy Assessment

```python
# Load 8760-hour baseline results
baseline_8760 = load_results(output_base / "Results_8760")

# Compare clustered methods against 8760 baseline
accuracy_metrics = {}

for method in ['Kotzur', 'Niet', 'Welsch']:
    if method in results and results[method] is not None:
        method_results = load_results(output_base / f"Results_{method}")
        
        # Calculate accuracy metrics
        accuracy_metrics[method] = calculate_accuracy_metrics(
            method_results, baseline_8760
        )

# Create accuracy comparison
accuracy_df = pd.DataFrame(accuracy_metrics).T
print("Accuracy Comparison (vs. 8760 baseline):")
print(accuracy_df)

# Plot accuracy vs. efficiency
plt.figure(figsize=(10, 6))

for method in accuracy_metrics.keys():
    if method in perf_df.index:
        x = perf_df.loc[method, 'computation_time']
        y = accuracy_metrics[method]['overall_accuracy']
        plt.scatter(x, y, s=100, label=method)
        plt.annotate(method, (x, y), xytext=(5, 5), 
                    textcoords='offset points')

plt.xlabel('Computation Time (seconds)')
plt.ylabel('Accuracy Score (0-1)')
plt.title('Accuracy vs. Computational Efficiency')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

## Sensitivity Analysis

### Parameter Sensitivity

```python
# Define parameter ranges for sensitivity analysis
sensitivity_params = {
    'storage_cost': np.linspace(100, 500, 5),  # $/kWh
    'renewable_capacity': np.linspace(0.3, 0.9, 4),  # fraction
    'demand_growth': np.linspace(0.01, 0.05, 3)  # annual growth rate
}

# Run sensitivity analysis
sensitivity_results = {}

for param_name, param_values in sensitivity_params.items():
    print(f"\n=== Sensitivity Analysis: {param_name} ===")
    sensitivity_results[param_name] = {}
    
    for value in param_values:
        # Update configuration
        config = create_sensitivity_config(param_name, value)
        
        # Run model
        output_path = output_base / f"Sensitivity_{param_name}_{value:.3f}"
        result = run_storage_model('Kotzur', input_path, output_path, config)
        sensitivity_results[param_name][value] = result

# Plot sensitivity results
plot_sensitivity_analysis(sensitivity_results)
```

## Regional Comparison

### Multi-Regional Analysis

```python
# Define regions for comparison
regions = {
    'North': {'renewable_resource': 'high', 'demand_pattern': 'industrial'},
    'South': {'renewable_resource': 'medium', 'demand_pattern': 'residential'},
    'Coast': {'renewable_resource': 'low', 'demand_pattern': 'mixed'}
}

regional_results = {}

for region_name, region_config in regions.items():
    print(f"\n=== Analyzing {region_name} Region ===")
    
    # Update input data for region
    regional_input_path = prepare_regional_data(input_path, region_config)
    
    # Run model
    output_path = output_base / f"Regional_{region_name}"
    result = run_storage_model('Kotzur', regional_input_path, output_path)
    regional_results[region_name] = result

# Compare regional results
compare_regional_results(regional_results)
```

## Economic Analysis

### Cost-Benefit Analysis

```python
# Calculate economic metrics for each scenario
economic_metrics = {}

for method, result in results.items():
    if result is not None:
        metrics = calculate_economic_metrics(result)
        economic_metrics[method] = metrics

# Create economic comparison
econ_df = pd.DataFrame(economic_metrics).T
print("Economic Comparison:")
print(econ_df)

# Plot economic metrics
plt.figure(figsize=(15, 10))

# Total system cost
plt.subplot(2, 3, 1)
costs = econ_df['total_system_cost']
plt.bar(costs.index, costs.values)
plt.title('Total System Cost')
plt.ylabel('Cost (M$)')
plt.xticks(rotation=45)

# Storage investment
plt.subplot(2, 3, 2)
storage_inv = econ_df['storage_investment']
plt.bar(storage_inv.index, storage_inv.values, color='orange')
plt.title('Storage Investment')
plt.ylabel('Investment (M$)')
plt.xticks(rotation=45)

# LCOE comparison
plt.subplot(2, 3, 3)
lcoe = econ_df['LCOE']
plt.bar(lcoe.index, lcoe.values, color='green')
plt.title('Levelized Cost of Energy')
plt.ylabel('LCOE ($/MWh)')
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
```

## Results Visualization

### Comprehensive Dashboard

```python
def create_comparison_dashboard(results, performance_metrics):
    """Create a comprehensive comparison dashboard"""
    
    fig, axes = plt.subplots(3, 3, figsize=(18, 15))
    fig.suptitle('Storage-in-OSeMOSYS Comparative Analysis Dashboard', fontsize=16)
    
    # 1. Computation Time
    ax = axes[0, 0]
    methods = list(performance_metrics.keys())
    times = [performance_metrics[m]['computation_time'] for m in methods]
    ax.bar(methods, times)
    ax.set_title('Computation Time')
    ax.set_ylabel('Seconds')
    
    # 2. Storage Capacity
    ax = axes[0, 1]
    for method in methods:
        if method in results and results[method]:
            capacity_data = get_storage_capacity_data(results[method])
            ax.plot(capacity_data.index, capacity_data.values, label=method, marker='o')
    ax.set_title('Storage Capacity Evolution')
    ax.set_ylabel('Capacity (GW)')
    ax.legend()
    
    # 3. System Cost
    ax = axes[0, 2]
    costs = [get_total_system_cost(results[m]) for m in methods if results[m]]
    ax.bar(methods[:len(costs)], costs)
    ax.set_title('Total System Cost')
    ax.set_ylabel('Cost (M$)')
    
    # 4. Storage Operation
    ax = axes[1, 0]
    for method in methods:
        if method in results and results[method]:
            operation_data = get_storage_operation_data(results[method])
            ax.plot(operation_data.index, operation_data.values, label=method)
    ax.set_title('Storage Operation Pattern')
    ax.set_ylabel('Storage Level (%)')
    ax.legend()
    
    # 5. Renewable Integration
    ax = axes[1, 1]
    renewable_shares = [get_renewable_share(results[m]) for m in methods if results[m]]
    ax.bar(methods[:len(renewable_shares)], renewable_shares)
    ax.set_title('Renewable Energy Share')
    ax.set_ylabel('Share (%)')
    
    # 6. Emissions
    ax = axes[1, 2]
    emissions = [get_total_emissions(results[m]) for m in methods if results[m]]
    ax.bar(methods[:len(emissions)], emissions, color='red', alpha=0.7)
    ax.set_title('Total CO2 Emissions')
    ax.set_ylabel('Mt CO2')
    
    # 7. Model Size
    ax = axes[2, 0]
    sizes = [performance_metrics[m]['model_size'] for m in methods]
    ax.bar(methods, sizes, color='purple', alpha=0.7)
    ax.set_title('Model Size')
    ax.set_ylabel('Variables + Constraints')
    
    # 8. Accuracy Score
    ax = axes[2, 1]
    if 'accuracy_metrics' in globals():
        accuracy_scores = [accuracy_metrics[m]['overall_accuracy'] 
                          for m in methods if m in accuracy_metrics]
        ax.bar(methods[:len(accuracy_scores)], accuracy_scores, color='green', alpha=0.7)
    ax.set_title('Accuracy Score')
    ax.set_ylabel('Score (0-1)')
    
    # 9. Summary metrics
    ax = axes[2, 2]
    ax.axis('off')
    summary_text = create_summary_text(results, performance_metrics)
    ax.text(0.1, 0.9, summary_text, transform=ax.transAxes, 
            fontsize=10, verticalalignment='top')
    ax.set_title('Summary')
    
    plt.tight_layout()
    plt.show()

# Create the dashboard
create_comparison_dashboard(results, performance_metrics)
```

## Key Insights and Recommendations

### Method Selection Guidelines

Based on the comparative analysis:

1. **For Quick Analysis**: Use Kotzur method for fast, accurate results
2. **For Detailed Studies**: Use 8760-hour resolution when computational resources allow
3. **For Storage-Heavy Systems**: Kotzur method provides best storage representation
4. **For Academic Research**: Compare multiple methods to validate findings

### Best Practices

1. **Always validate** clustered results against 8760-hour baseline
2. **Consider computational budget** when selecting temporal resolution
3. **Analyze sensitivity** to key parameters before making conclusions
4. **Document methodology** and assumptions for reproducibility

### Future Work

The comparative analysis reveals opportunities for:
- Hybrid clustering approaches
- Adaptive temporal resolution
- Machine learning-enhanced clustering
- Real-time optimization capabilities

Continue with [Advanced Configuration](advanced_configuration.md) for expert-level usage.
