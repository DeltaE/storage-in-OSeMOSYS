# Storage-in-OSeMOSYS

A comprehensive framework for analyzing energy storage systems using OSeMOSYS with time-series clustering and temporal disaggregation methods.

## Project Overview

This project implements multiple temporal representation methods for energy system optimization using OSeMOSYS:

- **Model_Cluster**: Time-series clustering approach
- **Model_Kotzur**: Kotzur temporal disaggregation method
- **Model_Welsch**: Welsch temporal representation
- **Model_Niet**: Niet temporal method

Each method provides different approaches to handle the temporal complexity in energy system modeling while maintaining computational efficiency.

## Features

- 🔄 **Time-series clustering** for representative day selection
- 📊 **Multiple temporal representation methods** (Cluster, Kotzur, Welsch, Niet)
- ⚡ **OSeMOSYS integration** with OtoOle for data processing
- 📈 **Automated visualization** and results comparison
- 🛠️ **Modular design** with utilities for configuration management
- 🔧 **GLPK solver integration** for optimization

## Quick Start

### 1. Environment Setup

```bash
# Create and activate environment
make setup
conda activate storage_osemosys

# Verify installation
make test-env
```

### 2. Configuration

Edit `config/config.yaml` to set your parameters:

```yaml
scenario_name: "k4h1WND"
days_in_year: 365
seasons: 4
hour_grouping: 1
n_clusters: 4
```

### 3. Run Analysis

```bash
# Run the main analysis
make run-main

# Or run directly
python main.py
```

## Project Structure

```
storage-in-OSeMOSYS/
├── main.py                 # Main execution script
├── config/
│   └── config.yaml         # Main configuration file
├── src/                    # Source modules
│   ├── __init__.py         # Module imports
│   ├── utilities.py        # Utility functions
│   ├── cluster.py          # Time-series clustering
│   ├── simulation.py       # OSeMOSYS simulation runner
│   ├── graph_generator.py  # Visualization tools
│   └── ...                 # Other modules
├── env/
│   └── environment.yml     # Conda environment specification
├── inputs_csv/             # Base CSV input data
├── Data_8760/              # Hourly time-series data
├── Results/                # Analysis outputs
├── Model_*/                # Model-specific directories
├── Makefile               # Environment management
└── README_ENVIRONMENT.md   # Environment setup guide
```

## Dependencies

### Core Requirements
- **Python 3.13.5**
- **NumPy** - Numerical computing
- **Pandas** - Data manipulation
- **Matplotlib** - Plotting
- **Scikit-learn** - Clustering algorithms
- **PyYAML** - Configuration handling
- **OpenPyXL** - Excel file operations

### OSeMOSYS Tools
- **OtoOle** - OSeMOSYS data processing
- **GLPK** - Linear programming solver
- **Colorama** - Terminal output formatting

### Additional Tools
- **SciPy** - Scientific computing
- **Pathlib** - Path handling

## Usage

### Basic Workflow

1. **Load Configuration**: The system reads parameters from `config/config.yaml`
2. **Data Clustering**: Applies k-means clustering to identify representative days
3. **Model Updates**: Updates OSeMOSYS input files for each temporal method
4. **Simulation**: Runs GLPK optimization for each model variant
5. **Results Processing**: Generates comparative analysis and visualizations

### Key Functions

```python
import src.utilities as utils
import src

# Load configuration
config = utils.load_config('config/config.yaml')

# Perform clustering
representative_days, sequence = src.cluster_data(cf_file, sdp_file, n_clusters)

# Run simulation
src.run_simulation(case_info)

# Generate visualizations
fig1, fig2, fig3 = src.graph(files...)
```

### Configuration Options

| Parameter | Description | Example |
|-----------|-------------|---------|
| `scenario_name` | Analysis scenario identifier | `"k4h1WND"` |
| `n_clusters` | Number of representative days | `4` |
| `hour_grouping` | Hours per time block | `1` |
| `days_in_year` | Days to analyze | `365` |
| `seasons` | Number of seasons | `4` |

## Temporal Methods

### 1. Model_Cluster
- Uses time-series clustering to select representative days
- Maintains chronological relationships through conversion matrices
- Ideal for capturing seasonal and daily patterns

### 2. Model_Kotzur
- Implements Kotzur's temporal disaggregation approach
- Focuses on storage inter-temporal constraints
- Excellent for long-term storage analysis

### 3. Model_Welsch
- Uses Welsch temporal representation method
- Balances computational efficiency with accuracy
- Good for systems with complex temporal dependencies

### 4. Model_Niet
- Implements Niet's temporal clustering approach
- Alternative clustering strategy
- Useful for comparison studies

## Output Files

### Results Structure
```
Results/
├── {scenario}_Storage_Level_Model_*.csv    # Storage level results
├── {scenario}_Figure.png                   # Comparative plots
├── {scenario}_Figure_Hourly.png           # Hourly analysis
├── {scenario}_Figure_Hourly_2Weeks.png    # Detailed view
└── {scenario}_Results.xlsx                # Comprehensive results
```

### Visualization Types
1. **Daily storage profiles** for each method
2. **Hourly comparisons** across full year
3. **Two-week detailed analysis** for pattern validation

## Advanced Usage

### Custom Clustering
```python
# Modify clustering parameters
from src.cluster import cluster_data

representative_days, sequence = cluster_data(
    capacity_factor_path="Data_8760/CapacityFactor.csv",
    demand_profile_path="Data_8760/SpecifiedDemandProfile.csv",
    n_clusters=8  # Adjust cluster count
)
```

### Results Analysis
```python
# Load and analyze results
TO BE UPDATED
```

## Environment Management

### Makefile Commands
```bash
make help          # Show all commands
make setup         # Complete environment setup
make env-create    # Create environment from YAML
make env-update    # Update existing environment
make test-env      # Verify installation
make clean         # Clean temporary files
make backup        # Backup environment
```

### Manual Environment Setup
```bash
# Create environment
conda env create -f env/environment.yml -n storage_osemosys

# Activate
conda activate storage_osemosys

# Install additional packages
pip install otoole colorama
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Reinstall dependencies
   make env-update
   make install-deps
   ```

2. **GLPK Not Found**
   ```bash
   conda activate storage_osemosys
   conda install -c conda-forge glpk
   ```

3. **Configuration Issues**
   ```bash
   # Verify config structure
   python -c "import src.utilities as utils; utils.load_config('config/config.yaml')"
   ```

### Performance Tips

- **Reduce clusters**: Lower `n_clusters` for faster execution
- **Increase hour_grouping**: Use 2-4 hour blocks for reduced complexity
- **Parallel execution**: Consider parallelizing model runs

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this work, please cite:

```bibtex
@software{storage_osemosys,
  title={Storage-in-OSeMOSYS: Temporal Representation Methods for Energy Storage Analysis},
  author={Bruno Borba, Md Eliasinul Islam, Taco Niet},
  year={2025},
  url={https://github.com/DeltaE/storage-in-OSeMOSYS}
}
```

## Support

- **Documentation**: See `README_ENVIRONMENT.md` for detailed setup
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join project discussions for help and collaboration

---

**Co-Developed by**: Bruno Borba, Md Eliasinul Islam
**Affiliation**: Delta E+ Research Lab, Simon Fraser University, BC, CA

for more - [storage-in-OSeMOSYS documentation](https://deltae.github.io/storage-in-OSeMOSYS/)
