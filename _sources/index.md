# Storage-in-OSeMOSYS Documentat

```{toctree}
:caption: 'Documentation:'
:maxdepth: 3

notes/README_ENVIRONMENT
notes/workflow_guide
notes/about_storage_algorithms
notes/configuration_guide
notes/QUICK_REFERENCE
```

A comprehensive framework for analyzing energy storage systems using OSeMOSYS with time-series clustering and temporal disaggregation methods.

<!-- <img src="_static/storage_models_overview.png" alt="Storage Models Overview" width="800"/> -->

```{warning}
This library is under active development. For latest updates, check the [GitHub repository](https://github.com/DeltaE/storage-in-OSeMOSYS).
```

## Project Overview

Storage-in-OSeMOSYS implements four different temporal representation methods for energy system optimization, each addressing the challenge of modeling energy storage systems with varying levels of computational complexity and accuracy:

- **🔄 Model_Cluster**: Time-series clustering approach for representative day selection
- **📊 Model_Kotzur**: Kotzur temporal disaggregation method with daily mapping
- **⏰ Model_Welsch**: Welsch temporal representation with fixed patterns
- **🔗 Model_Niet**: Niet temporal method with direct chronological linking

## Key Features

- 🔄 **Time-series clustering** for representative day selection using K-means
- 📊 **Multiple temporal methods** comparing different storage modeling approaches  
- ⚡ **OSeMOSYS integration** with OtoOle for seamless data processing
- 📈 **Automated visualization** and comparative results analysis
- 🛠️ **Modular design** with utilities for configuration management
- 🔧 **GLPK solver integration** for linear programming optimization
- 🐍 **Python 3.13** support with modern pathlib usage
- 📋 **Conda environment** management with comprehensive Makefile

## Documentation Structure

```{toctree}
:caption: 'User Guide:'
:maxdepth: 3

notes/README_ENVIRONMENT
notes/workflow_guide
notes/about_storage_algorithms
notes/configuration_guide
```

```{toctree}
:caption: 'Technical Reference:'
:maxdepth: 2

notes/api_reference
api/index
notes/model_specifications
notes/results_analysis
```

```{toctree}
:caption: 'Examples & Tutorials:'
:maxdepth: 2

notebooks/basic_usage
notebooks/comparative_analysis
notebooks/advanced_configuration
```

## Quick Start

### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/DeltaE/storage-in-OSeMOSYS.git
cd storage-in-OSeMOSYS

# Setup conda environment
make setup
conda activate storage_osemosys

# Verify installation
make test-env
```

### 2. Basic Usage
```bash
# Run analysis with default configuration
python main.py

# Check results
ls Results/
```

### 3. Configuration
Edit `config/config.yaml` to customize:
```yaml
scenario_name: "k4h1WND"
days_in_year: 365
n_clusters: 4
hour_grouping: 1
```

## Research Context

This framework addresses the critical challenge of modeling energy storage systems in large-scale energy planning. Storage systems fundamentally differ from conventional generation and demand technologies because they **move energy across time**, creating complex temporal dependencies that are computationally expensive to model accurately.

### The Storage Modeling Challenge

Energy storage modeling is complex because:

1. **🔁 Time-shifting behavior**: Storage moves energy across time periods rather than just producing or consuming
2. **⏳ State continuity**: The state of charge depends on all previous time periods  
3. **🔗 Temporal coupling**: Decisions in one hour affect options in future hours
4. **⚡ Multi-scale dynamics**: From minute-level frequency regulation to seasonal energy shifting

### Our Solution

Storage-in-OSeMOSYS provides a systematic comparison of four established temporal representation methods, allowing researchers to:

- **Evaluate trade-offs** between computational efficiency and model accuracy
- **Compare results** across different temporal abstraction approaches  
- **Select appropriate methods** based on specific research questions and constraints
- **Understand limitations** of each approach for storage system analysis

## Project Team

**Research Lead**: Md Eliasinul Islam  
**Institution**: Delta E+ Research Lab, Simon Fraser University  
**License**: MIT License

## Citation

If you use Storage-in-OSeMOSYS in your research, please cite:

```bibtex
@software{storage_osemosys_2025,
  title={Storage-in-OSeMOSYS: A Framework for Temporal Representation Methods in Energy Storage Modeling},
  author={Islam, Md Eliasinul},
  organization={Delta E+ Research Lab, Simon Fraser University},
  year={2025},
  url={https://github.com/DeltaE/storage-in-OSeMOSYS}
}
```

---

```{note}
For technical support, please open an issue on [GitHub](https://github.com/DeltaE/storage-in-OSeMOSYS/issues).
For research collaboration inquiries, contact the Delta E+ Research Lab.
```
