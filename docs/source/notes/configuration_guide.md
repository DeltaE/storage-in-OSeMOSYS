# Configuration Guide

This guide explains how to configure Storage-in-OSeMOSYS for different analysis scenarios.

## Configuration File Structure

The main configuration is stored in `config/config.yaml`:

```yaml
# Analysis Parameters
scenario_name: "k4h1WND"
days_in_year: 365
seasons: 4
hour_grouping: 1
n_clusters: 4

# Storage Parameters
StorageLevelStart: 0.5
StorageMaxCapacity: 100
ResidualStorageCapacity: 0

# Data Sources
data_8760:
  directory: "Data_8760"
  CF: "CapacityFactor.csv"
  SDP: "SpecifiedDemandProfile.csv"

# Model Cases
cases:
  Model_Cluster:
    root_directory: "Model_Cluster"
    otoole_config: "config_fast_Cluster.yaml"
    # ... additional case-specific settings
```

## Key Configuration Parameters

### Analysis Parameters

#### `scenario_name`
- **Type**: String
- **Description**: Identifier for the analysis run
- **Example**: `"k4h1WND"` (4 clusters, 1-hour grouping, wind scenario)
- **Usage**: Used in output file naming and result identification

#### `days_in_year`
- **Type**: Integer
- **Default**: 365
- **Description**: Total number of days to model
- **Options**: 
  - `365`: Full year analysis
  - `30-90`: Seasonal analysis
  - `7-14`: Weekly analysis for testing

#### `n_clusters`
- **Type**: Integer
- **Range**: 2-20 (recommended: 3-8)
- **Description**: Number of representative days for clustering
- **Trade-offs**:
  - More clusters = Higher accuracy, longer computation
  - Fewer clusters = Faster computation, less detail

#### `hour_grouping`
- **Type**: Integer
- **Options**: 1, 2, 3, 4, 6, 8, 12, 24
- **Description**: Hours aggregated into single time block
- **Examples**:
  - `1`: Hourly resolution (8760 time steps)
  - `2`: 2-hour blocks (4380 time steps)
  - `24`: Daily resolution (365 time steps)

#### `seasons`
- **Type**: Integer
- **Default**: 4
- **Description**: Number of seasons for Welsch method
- **Common values**: 1 (no seasons), 2 (summer/winter), 4 (quarterly)

### Storage Parameters

#### `StorageLevelStart`
- **Type**: Float (0.0-1.0)
- **Description**: Initial state of charge as fraction of capacity
- **Examples**:
  - `0.0`: Empty battery at start
  - `0.5`: Half-charged battery
  - `1.0`: Fully charged battery

#### `StorageMaxCapacity`
- **Type**: Float
- **Units**: Energy units (e.g., MWh)
- **Description**: Maximum storage capacity
- **Considerations**: Should match your system scale

#### `ResidualStorageCapacity`
- **Type**: Float
- **Description**: Pre-existing storage capacity
- **Default**: 0 (no existing storage)

## Model-Specific Configuration

Each temporal method has specific configuration requirements:

### Model_Cluster Configuration
```yaml
Model_Cluster:
  root_directory: "Model_Cluster"
  otoole_config: "config_fast_Cluster.yaml"
  output_otoole_txt: "osemosys_fast_Cluster.txt"
  input_otoole_csv:
    directory: "data"
    timeslice: "TIMESLICE.csv"
    timeslicecro: "TIMESLICECRO.csv"
    conversionlts: "Conversionlts.csv"
    # ... other CSV files
```

### Model_Kotzur Configuration
```yaml
Model_Kotzur:
  root_directory: "Model_Kotzur"
  otoole_config: "config_fast_Kotzur.yaml"
  input_otoole_csv:
    dayscro: "DAYSCRO.csv"
    conversionld: "Conversionld.csv"
    conversionldc: "Conversionldc.csv"
    # ... other CSV files
```

### Model_Welsch Configuration
```yaml
Model_Welsch:
  root_directory: "Model_Welsch"
  otoole_config: "config_fast_Welsch.yaml"
  input_otoole_csv:
    dailytimebracket: "DAILYTIMEBRACKET.csv"
    conversionlh: "Conversionlh.csv"
    conversionls: "Conversionls.csv"
    daysindaytype: "DaysInDayType.csv"
    # ... other CSV files
```

## Data Configuration

### Input Data Paths
```yaml
data_8760:
  directory: "Data_8760"
  CF: "CapacityFactor.csv"     # Renewable generation profiles
  SDP: "SpecifiedDemandProfile.csv"  # Electricity demand profiles
```

### Results Configuration
```yaml
results:
  directory: "Results"                    # Main results folder
  directory_GUI: "Results_GUI"           # GUI-specific results
  results_copied_filename: "Storage_Level"  # Base filename for results
  results_excel_file: "results.xlsx"     # Summary Excel file
```

## Common Configuration Scenarios

### High-Resolution Analysis
```yaml
# For detailed analysis with high temporal resolution
scenario_name: "detailed_k8h1"
n_clusters: 8
hour_grouping: 1
days_in_year: 365
```

### Fast Prototyping
```yaml
# For quick testing and development
scenario_name: "test_k3h4"
n_clusters: 3
hour_grouping: 4      # 6-hour blocks
days_in_year: 30      # One month only
```

### Seasonal Analysis
```yaml
# For seasonal storage studies
scenario_name: "seasonal_k6h1"
n_clusters: 6
hour_grouping: 1
seasons: 4
days_in_year: 365
```

### Computational Efficiency
```yaml
# For large-scale studies with computational constraints
scenario_name: "efficient_k4h8"
n_clusters: 4
hour_grouping: 8      # 8-hour blocks
days_in_year: 365
```

## Configuration Validation

### Parameter Relationships
- `timeslices = n_clusters * (24 / hour_grouping)`
- `chronological_timeslices = days_in_year * (24 / hour_grouping)`
- `year_split = 1 / timeslices`
- `day_split = hour_grouping / (24 * 365)`

### Validation Checks
```python
# Built-in validation in utilities
def validate_config(config):
    """Validate configuration parameters."""
    
    # Check temporal parameters
    assert config['n_clusters'] >= 2, "Need at least 2 clusters"
    assert config['hour_grouping'] in [1,2,3,4,6,8,12,24], "Invalid hour grouping"
    assert 24 % config['hour_grouping'] == 0, "Hour grouping must divide 24"
    
    # Check storage parameters
    assert 0 <= config['StorageLevelStart'] <= 1, "Storage start level must be 0-1"
    assert config['StorageMaxCapacity'] > 0, "Storage capacity must be positive"
    
    # Check file paths
    data_dir = Path(config['data_8760']['directory'])
    assert data_dir.exists(), f"Data directory not found: {data_dir}"
```

## Advanced Configuration

### Custom Data Sources
```yaml
# Using custom input data
data_8760:
  directory: "Custom_Data"
  CF: "wind_solar_profiles.csv"
  SDP: "demand_profiles_2024.csv"
```

### Multiple Scenarios
```yaml
# Define scenario variants
scenarios:
  base_case:
    StorageMaxCapacity: 100
    n_clusters: 4
  
  high_storage:
    StorageMaxCapacity: 500
    n_clusters: 6
  
  low_resolution:
    hour_grouping: 4
    n_clusters: 3
```

### Solver Configuration
```yaml
# Solver-specific settings (in otoole config files)
solver:
  name: "glpk"
  options:
    tmlim: 3600      # Time limit in seconds
    mipgap: 0.01     # MIP gap tolerance
    presolve: true   # Enable presolving
```

## Configuration Best Practices

### 1. Naming Conventions
- Use descriptive scenario names: `k{clusters}h{hours}_{technology}`
- Include resolution info: `high_res`, `daily`, `seasonal`
- Add version numbers for iterations: `v1`, `v2`, etc.

### 2. Parameter Selection Guidelines

#### Time Resolution
- **Hourly (`hour_grouping=1`)**: For intraday storage, frequency regulation
- **2-4 hour blocks**: For daily cycle analysis
- **Daily (`hour_grouping=24`)**: For seasonal studies

#### Clustering
- **3-4 clusters**: Basic representative days (weekday, weekend, peak, off-peak)
- **5-8 clusters**: Seasonal variations
- **8+ clusters**: High diversity in renewable/demand patterns

#### Duration
- **Full year**: For annual planning studies
- **Seasonal**: For specific season analysis
- **Monthly**: For testing and development

### 3. Storage Parameter Guidelines
- Start with moderate storage sizes (10-20% of daily demand)
- Initial state of charge: 0.5 for neutral start
- Consider real-world storage characteristics

### 4. Computational Considerations
```yaml
# Memory usage estimation
estimated_variables = n_clusters * (24/hour_grouping) * n_technologies * n_years
memory_gb = estimated_variables / 1000000  # Rough estimate

# Time estimation
computation_time_minutes = (n_clusters * (24/hour_grouping)) / 100  # Rough estimate
```

## Configuration File Management

### Version Control
```bash
# Keep configuration files in version control
git add config/
git commit -m "Update configuration for scenario X"

# Tag important configurations
git tag -a config_v1.0 -m "Baseline configuration"
```

### Configuration Templates
```bash
# Create configuration templates
cp config/config.yaml config/templates/baseline.yaml
cp config/config.yaml config/templates/high_resolution.yaml
cp config/config.yaml config/templates/fast_testing.yaml
```

### Environment-Specific Configs
```yaml
# config/config_dev.yaml - Development settings
scenario_name: "dev_test"
days_in_year: 7
n_clusters: 2

# config/config_prod.yaml - Production settings  
scenario_name: "production_run"
days_in_year: 365
n_clusters: 6
```

This configuration guide enables users to customize Storage-in-OSeMOSYS for their specific research needs while understanding the implications of different parameter choices.
