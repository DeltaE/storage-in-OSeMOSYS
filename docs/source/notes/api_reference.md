# API Reference

This section provides detailed documentation for all modules, classes, and functions in the Storage-in-OSeMOSYS framework.

## Module Overview

The Storage-in-OSeMOSYS framework is organized into several key modules:

- **`src.utilities`**: Core utility functions for configuration and formatting
- **`src.cluster`**: Time-series clustering functionality
- **`src.simulation`**: OSeMOSYS model execution and management
- **`src.update_list`**: Data structure update functions
- **`src.update_CFandSDP`**: Capacity factor and demand profile processing
- **`src.graph_generator`**: Visualization and plotting functions
- **`src.table_generator`**: Results analysis and table generation

## Core Utilities (`src.utilities`)

### Configuration Management

#### `load_config(config_path: Path) -> dict`
Loads and parses YAML configuration files.

**Parameters:**
- `config_path` (Path): Path to the YAML configuration file

**Returns:**
- `dict`: Parsed configuration dictionary

**Example:**
```python
from pathlib import Path
import src.utilities as utils

config = utils.load_config(Path('config/config.yaml'))
scenario_name = config['scenario_name']
```

**Raises:**
- `FileNotFoundError`: If configuration file doesn't exist
- `yaml.YAMLError`: If YAML syntax is invalid

### Terminal Output Functions

#### `print_update(level: int, message: str) -> None`
Prints formatted status messages with hierarchical indentation.

**Parameters:**
- `level` (int): Indentation level (1-4)
- `message` (str): Message to display

**Example:**
```python
utils.print_update(level=1, message="Starting analysis")
utils.print_update(level=2, message="Loading data")
utils.print_update(level=3, message="Processing file: data.csv")
```

**Output:**
```
▶ Starting analysis
  ▶ Loading data
    ▶ Processing file: data.csv
```

#### `print_info(message: str) -> None`
Prints informational messages in blue color.

#### `print_warning(message: str) -> None`
Prints warning messages in yellow color.

#### `print_error(message: str) -> None`
Prints error messages in red color.

## Time-Series Clustering (`src.cluster`)

### Main Clustering Function

#### `cluster_data(cf_file: Path, sdp_file: Path, n_clusters: int) -> Tuple[List[int], List[int]]`
Performs K-means clustering on combined capacity factor and demand profile data.

**Parameters:**
- `cf_file` (Path): Path to capacity factor CSV file (8760 hours)
- `sdp_file` (Path): Path to specified demand profile CSV file (8760 hours)  
- `n_clusters` (int): Number of clusters for representative days

**Returns:**
- `Tuple[List[int], List[int]]`: Representative day indices and chronological sequence mapping

**Algorithm:**
1. Load hourly time-series data (8760 hours)
2. Reshape into daily profiles (365 days × 24 hours)
3. Normalize data for clustering
4. Apply K-means clustering
5. Select representative days closest to cluster centroids
6. Create mapping from chronological days to representative days

**Example:**
```python
import src

representative_days, chronological_sequence = src.cluster_data(
    cf_file=Path("Data_8760/CapacityFactor.csv"),
    sdp_file=Path("Data_8760/SpecifiedDemandProfile.csv"),
    n_clusters=4
)

print(f"Representative days: {representative_days}")
# Output: Representative days: [15, 89, 156, 278]

print(f"First 10 days mapping: {chronological_sequence[:10]}")
# Output: First 10 days mapping: [0, 0, 1, 1, 0, 2, 2, 1, 0, 3]
```

**Data Format Requirements:**
- CSV files with hourly data (8760 rows)
- First column: timestamps or indices
- Subsequent columns: technology/region data
- No missing values (will cause clustering failure)

## Simulation Management (`src.simulation`)

### Model Execution

#### `run_simulation(case_info: dict) -> bool`
Executes OSeMOSYS model simulation using GLPK solver.

**Parameters:**
- `case_info` (dict): Model configuration from config YAML

**Returns:**
- `bool`: True if simulation completed successfully

**Process:**
1. Validates input files exist
2. Executes GLPK solver on OSeMOSYS datafile
3. Monitors simulation progress
4. Validates output files generated

**Example:**
```python
case_info = {
    'root_directory': 'Model_Cluster',
    'output_otoole_txt': 'osemosys_fast_Cluster.txt',
    'solver_command': 'glpsol --math osemosys_fast_Cluster.txt'
}

success = src.run_simulation(case_info)
if success:
    print("Simulation completed successfully")
else:
    print("Simulation failed")
```

## Data Processing Functions

### List Generation (`src.update_list`)

#### `new_list(count: int, output_file: Path, start: int = 1) -> None`
Generates sequential numbered lists for OSeMOSYS set definitions.

**Parameters:**
- `count` (int): Number of items in the list
- `output_file` (Path): Output CSV file path
- `start` (int): Starting number (default: 1)

**Example:**
```python
# Generate timeslice list
src.new_list(count=96, output_file=Path("Model_Cluster/data/TIMESLICE.csv"))

# Generated content:
# TIMESLICE
# 1
# 2
# ...
# 96
```

### Profile Processing (`src.update_CFandSDP`)

#### `CFandSDP(input_file: Path, representative_days: List[int], hour_grouping: int, output_file: Path, operation: str) -> None`
Processes capacity factor and demand profiles for representative days.

**Parameters:**
- `input_file` (Path): Input 8760-hour profile file
- `representative_days` (List[int]): Representative day indices from clustering
- `hour_grouping` (int): Hours to aggregate (1=hourly, 24=daily)
- `output_file` (Path): Output processed profile file
- `operation` (str): Aggregation operation ('mean' for CF, 'sum' for demand)

**Processing Logic:**
1. Extract data for representative days only
2. Aggregate within time blocks based on `hour_grouping`
3. Apply aggregation operation (mean/sum)
4. Write to OSeMOSYS-compatible CSV format

**Example:**
```python
# Process capacity factors (averaging within time blocks)
src.CFandSDP(
    input_file=Path("Data_8760/CapacityFactor.csv"),
    representative_days=[15, 89, 156, 278],
    hour_grouping=2,  # 2-hour blocks
    output_file=Path("Model_Cluster/data/CapacityFactor.csv"),
    operation='mean'
)

# Process demand profiles (summing within time blocks)  
src.CFandSDP(
    input_file=Path("Data_8760/SpecifiedDemandProfile.csv"),
    representative_days=[15, 89, 156, 278],
    hour_grouping=2,
    output_file=Path("Model_Cluster/data/SpecifiedDemandProfile.csv"),
    operation='sum'
)
```

## Temporal Mapping Functions

### Time-Sequence Conversion

#### `conversionlts(blocks_per_day: int, chronological_timeslices: int, timeslices: int, chronological_sequence: List[int], representative_days: List[int], output_file: Path) -> None`
Creates mapping between representative timeslices and chronological sequence.

**Parameters:**
- `blocks_per_day` (int): Number of time blocks per day
- `chronological_timeslices` (int): Total chronological timeslices (365 * blocks_per_day)
- `timeslices` (int): Representative timeslices (n_clusters * blocks_per_day)
- `chronological_sequence` (List[int]): Day-to-cluster mapping
- `representative_days` (List[int]): Representative day indices
- `output_file` (Path): Output conversion mapping file

#### `conversionld(timeslices: int, representative_days_count: int, output_file: Path, label: str = 'DAYTYPE') -> None`
Creates mapping between timeslices and day types.

#### `conversionldc(chronological_sequence: List[int], representative_days: List[int], days_in_year: int, output_file: Path) -> None`
Creates mapping between chronological days and representative day clusters.

### Time Disaggregation

#### `yearsplit(timeslices: int, representative_days: List[int], chronological_sequence: List[int], days_in_year: int, output_file: Path) -> None`
Calculates the fraction of the year represented by each timeslice.

**Formula:**
```
yearsplit[timeslice] = (days_mapped_to_cluster / days_in_year) / blocks_per_day
```

**Example:**
If cluster 1 represents 90 days out of 365, and we have hourly resolution:
```
yearsplit_cluster1 = (90 / 365) / 24 = 0.0103
```

## Visualization (`src.graph_generator`)

### Main Plotting Function

#### `graph(file_base: Path, file_kotzur: Path, file_kotzur_intraday: Path, file_cluster: Path, file_niet: Path, file_welsch: Path, file_welsch_intraday: Path, representative_days: List[int], blocks_per_day: int, yearsplit_file: Path) -> Tuple[Figure, Figure, Figure]`
Generates comparative visualization plots for all temporal methods.

**Returns:**
- `Tuple[Figure, Figure, Figure]`: Overview, hourly detail, and 2-week detail plots

**Generated Plots:**
1. **Overview Plot**: Annual storage levels for all methods
2. **Hourly Detail**: High-resolution view of representative periods  
3. **Two-Week Detail**: Focused view on specific time periods

### Post-Processing Functions

#### `intraday_kotzur(conversion_file: Path, storage_file: Path, storage_start: float, output_file: Path) -> None`
Disaggregates Kotzur method results to full chronological sequence.

#### `intraday_welsch2(storage_file: Path, blocks_per_day: int, timeslices: int, representative_days: List[int], chronological_sequence: List[int], storage_start: float, output_file: Path) -> None`
Disaggregates Welsch method results with continuity preservation.

## Results Analysis (`src.table_generator`)

### Summary Table Generation

#### `table(simulation_results: Path, data_sol_results: Path, scenario_name: str, case_name: str, capacity_path: Path, storage_capacity_path: Path, technology: str, storage: str, results_file: Path) -> None`
Generates Excel summary tables with key performance indicators.

**Parameters:**
- `simulation_results` (Path): Raw simulation output directory
- `data_sol_results` (Path): Solver solution file
- `scenario_name` (str): Scenario identifier
- `case_name` (str): Model method name
- `capacity_path` (Path): Technology capacity results
- `storage_capacity_path` (Path): Storage capacity results  
- `technology` (str): Technology name for analysis (e.g., 'WINDPOWER')
- `storage` (str): Storage technology name (e.g., 'BATTERY')
- `results_file` (Path): Output Excel file path

**Generated Tables:**
- Technology capacity summary
- Storage capacity and energy
- Storage level statistics
- Operational characteristics
- Cost summary (if available)

## Configuration Updates (`src.yaml_operations`)

### YAML Parameter Updates

#### `new_yaml_param(yaml_file: Path, parameter: str, value: Union[float, int, str]) -> None`
Updates specific parameters in OSeMOSYS configuration YAML files.

**Example:**
```python
src.new_yaml_param(
    yaml_file=Path("Model_Cluster/config_fast_Cluster.yaml"),
    parameter='DaySplit',
    value=0.000114  # 1 hour / (24 hours * 365 days)
)

src.new_yaml_param(
    yaml_file=Path("Model_Cluster/config_fast_Cluster.yaml"),
    parameter='StorageMaxCapacity',
    value=100.0
)
```

## File Operations

### Results Management

#### `copy_and_rename(source_dir: Path, destination_dir: Path, new_filename: str) -> None`
Copies and renames result files to standardized location.

#### `read_csvfile(file_path: Path) -> float`
Reads single value from CSV file (typically for storage start values).

## Error Handling

### Common Exceptions

```python
# Configuration errors
class ConfigurationError(Exception):
    """Raised when configuration parameters are invalid."""
    pass

# Data processing errors  
class DataProcessingError(Exception):
    """Raised when data processing fails."""
    pass

# Simulation errors
class SimulationError(Exception):
    """Raised when OSeMOSYS simulation fails."""
    pass
```

### Validation Functions

```python
def validate_data_files(cf_file: Path, sdp_file: Path) -> None:
    """Validate input data files exist and have correct format."""
    
def validate_config_parameters(config: dict) -> None:
    """Validate configuration parameters are within acceptable ranges."""
    
def validate_simulation_results(results_dir: Path) -> bool:
    """Check if simulation completed successfully and results exist."""
```

## Usage Examples

### Complete Workflow Example

```python
from pathlib import Path
import src.utilities as utils
import src

# 1. Load configuration
config = utils.load_config(Path('config/config.yaml'))

# 2. Perform clustering
representative_days, chronological_sequence = src.cluster_data(
    cf_file=Path("Data_8760/CapacityFactor.csv"),
    sdp_file=Path("Data_8760/SpecifiedDemandProfile.csv"),
    n_clusters=config['n_clusters']
)

# 3. Process each model
for case_name, case_info in config['cases'].items():
    utils.print_update(level=1, message=f"Processing {case_name}")
    
    # Update data files
    if case_name == 'Model_Cluster':
        src.conversionlts(
            blocks_per_day=24//config['hour_grouping'],
            chronological_timeslices=365*24//config['hour_grouping'],
            timeslices=len(representative_days)*24//config['hour_grouping'],
            chronological_sequence=chronological_sequence,
            representative_days=representative_days,
            output_file=Path(case_info['root_directory']) / 'data' / 'Conversionlts.csv'
        )
    
    # Run simulation
    success = src.run_simulation(case_info)
    
    if success:
        utils.print_info(f"✓ {case_name} completed successfully")
    else:
        utils.print_error(f"✗ {case_name} failed")

# 4. Generate visualizations
fig1, fig2, fig3 = src.graph(
    file_base=Path("Results/base_Storage_Level_Model_Niet.csv"),
    file_kotzur=Path("Results/k4h1WND_Storage_Level_Model_Kotzur.csv"),
    # ... other file paths
    representative_days=representative_days,
    blocks_per_day=24//config['hour_grouping'],
    yearsplit_file=Path("Model_Cluster/data/YearSplit.csv")
)

# 5. Save results
fig1.savefig("Results/comparison_overview.png")
fig2.savefig("Results/comparison_detailed.png")
fig3.savefig("Results/comparison_2weeks.png")
```

This API reference provides comprehensive documentation for all functions and modules in the Storage-in-OSeMOSYS framework, enabling users to understand and extend the codebase effectively.
