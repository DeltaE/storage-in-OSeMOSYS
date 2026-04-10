# Environment Setup Guide

This guide provides detailed instructions for setting up the Storage-in-OSeMOSYS development and execution environment.

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Memory**: Minimum 8GB RAM (16GB recommended for large datasets)
- **Storage**: 5GB free space for dependencies and results
- **Python**: 3.11+ (3.13 recommended)

### Required Software
- **Conda/Miniconda**: For environment management
- **Git**: For version control and repository cloning
- **GLPK**: Linear programming solver (installed via conda)

## Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/DeltaE/storage-in-OSeMOSYS.git
cd storage-in-OSeMOSYS
```

### 2. Automated Environment Setup
```bash
# Create environment and install all dependencies
make setup

# Activate environment
conda activate storage_osemosys

# Verify installation
make test-env
```

### 3. Test Installation
```bash
# Run basic functionality test
python -c "import src.utilities as utils; print('✓ Imports working')"

# Test GLPK solver
glpsol --version

# Check key packages
python -c "import otoole, pandas, numpy, matplotlib; print('✓ Core packages loaded')"
```

## Manual Environment Setup

If you prefer manual setup or encounter issues with the automated approach:

### 1. Create Conda Environment
```bash
# Create environment with Python 3.13
conda create -n storage_osemosys python=3.13 -y

# Activate environment
conda activate storage_osemosys
```

### 2. Install Core Dependencies
```bash
# Scientific computing stack
conda install -c conda-forge numpy=2.3.1 pandas=2.2.3 matplotlib=3.10.0 -y

# Machine learning for clustering
conda install -c conda-forge scikit-learn=1.7.1 -y

# File I/O and configuration
conda install -c conda-forge pyyaml=6.0.2 openpyxl=3.1.5 -y

# OSeMOSYS integration
conda install -c conda-forge glpk=5.0 -y
pip install otoole==1.1.5

# Utilities
conda install -c conda-forge colorama -y
```

### 3. Install Additional Dependencies
```bash
# Development tools
conda install -c conda-forge black flake8 pytest -y

# Documentation tools
conda install -c conda-forge sphinx sphinx-book-theme myst-parser -y

# Jupyter for notebooks
conda install -c conda-forge jupyter notebook ipykernel -y
```

## Environment File Management

### Using environment.yml
The project includes a comprehensive `env/environment.yml` file:

```bash
# Create environment from file
conda env create -f env/environment.yml

# Update existing environment
conda env update -f env/environment.yml --prune
```

### Environment Export
```bash
# Export current environment
conda env export > env/environment_backup.yml

# Export only explicitly installed packages
conda env export --from-history > env/environment_minimal.yml
```

## Makefile Commands

The project includes a comprehensive Makefile for environment management:

### Environment Management
```bash
make setup          # Complete environment setup (create + deps + test)
make env-create     # Create environment from environment.yml
make env-update     # Update existing environment from environment.yml
make env-export     # Export current environment to environment.yml
make env-remove     # Remove the conda environment
make env-list       # List all conda environments
make env-info       # Show environment information
make test-env       # Test environment and dependencies
make clean          # Remove .pyc files and __pycache__ directories
make recreate       # Remove and recreate the environment from scratch
make backup         # Export environment to timestamped backup file
```

### Running the Model
```bash
make run-main       # Run main.py inside the conda environment
make activate       # Print the conda activate command
```

### Development Workflow
```bash
make dev-setup      # Setup with development tools (black, flake8, pytest)
```

### Documentation
```bash
make docs-build    # Build documentation with Sphinx
make docs-serve    # Serve documentation locally at http://localhost:8000
make docs-clean    # Clean documentation build files
make docs-setup    # Install documentation dependencies
make docs-autodoc  # Auto-generate API docs from source code
make docs-full     # Complete workflow: autodoc + build
make docs-live     # Live development server with auto-reload
make docs-deploy   # Deploy documentation to GitHub Pages
make docs-check    # Check documentation for errors
```

## Package Details

### Core Scientific Stack
```yaml
# Data processing and analysis
numpy: 2.3.1         # Numerical computing
pandas: 2.2.3        # Data manipulation
matplotlib: 3.10.0   # Plotting and visualization
scikit-learn: 1.7.1  # Machine learning (clustering)

# File I/O and configuration  
pyyaml: 6.0.2        # YAML configuration files
openpyxl: 3.1.5      # Excel file handling
```

### Energy System Modeling
```yaml
# OSeMOSYS integration
otoole: 1.1.5        # OSeMOSYS data processing
glpk: 5.0           # Linear programming solver

# Additional solvers (optional)
# cbc: 2.10.5        # Alternative LP solver
# cplex: 22.1.1      # Commercial solver (license required)
```

### Development and Documentation
```yaml
# Code quality
black: 24.3.0        # Code formatting
flake8: 7.0.0       # Style checking
pytest: 8.1.1       # Testing framework

# Documentation
sphinx: 7.2.6       # Documentation generator
sphinx-book-theme: 1.1.2  # Modern documentation theme
myst-parser: 2.0.0  # Markdown support in Sphinx

# Jupyter ecosystem
jupyter: 1.0.0      # Jupyter notebook
ipykernel: 6.29.3   # Jupyter kernel
nbsphinx: 0.9.3     # Notebook integration in docs
```

### Utilities
```yaml
# Terminal and system
colorama: 0.4.6     # Colored terminal output
pathlib: built-in   # Modern path handling (Python 3.4+)
shutil: built-in    # File operations
typing: built-in    # Type hints (Python 3.5+)
```

## Environment Verification

### Comprehensive Test Script
```bash
# Run the complete verification
make test-env
```

Or manually verify components:

```python
# test_environment.py
import sys
import importlib
from pathlib import Path

def test_python_version():
    """Test Python version compatibility."""
    version = sys.version_info
    assert version.major == 3, f"Python 3 required, got {version.major}"
    assert version.minor >= 11, f"Python 3.11+ required, got {version.major}.{version.minor}"
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")

def test_core_packages():
    """Test core package imports."""
    packages = [
        'numpy', 'pandas', 'matplotlib', 'sklearn', 
        'yaml', 'openpyxl', 'otoole', 'colorama'
    ]
    
    for package in packages:
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"✓ {package} {version}")
        except ImportError as e:
            print(f"✗ {package}: {e}")
            raise

def test_solver():
    """Test GLPK solver availability."""
    import subprocess
    try:
        result = subprocess.run(['glpsol', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"✓ GLPK: {version}")
        else:
            raise Exception("GLPK not responding")
    except FileNotFoundError:
        raise Exception("GLPK not found in PATH")

def test_project_imports():
    """Test project-specific imports."""
    try:
        import src.utilities as utils
        import src
        print("✓ Project modules importable")
        
        # Test utility functions
        config_path = 'config/config.yaml'
        if Path(config_path).exists():
            config = utils.load_config(Path(config_path))
            print("✓ Configuration loading works")
        else:
            print("⚠ Configuration file not found (optional for testing)")
            
    except ImportError as e:
        print(f"✗ Project imports failed: {e}")
        raise

if __name__ == "__main__":
    test_python_version()
    test_core_packages()
    test_solver()
    test_project_imports()
    print("\n🎉 Environment verification successful!")
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Conda Environment Creation Fails
```bash
# Update conda
conda update conda

# Clear package cache
conda clean --all

# Create environment with explicit channel
conda create -n storage_osemosys -c conda-forge python=3.13
```

#### 2. GLPK Installation Issues
```bash
# For Ubuntu/Debian
sudo apt-get install glpk-utils

# For macOS with Homebrew
brew install glpk

# Verify installation
which glpsol
glpsol --version
```

#### 3. OtoOle Installation Problems
```bash
# Install from PyPI with specific version
pip install otoole==1.1.5

# If compilation issues, try conda-forge
conda install -c conda-forge otoole

# Alternative: install from source
pip install git+https://github.com/OSeMOSYS/otoole.git
```

#### 4. Import Errors
```bash
# Check if environment is activated
conda info --envs
conda activate storage_osemosys

# Verify Python path
python -c "import sys; print(sys.path)"

# Check installed packages
conda list
pip list
```

#### 5. Memory Issues During Installation
```bash
# Install packages one by one
conda install numpy -y
conda install pandas -y
# ... continue individually

# Or use pip with no-cache
pip install --no-cache-dir otoole
```

#### 6. Path Issues on Windows
```bash
# Use forward slashes or raw strings
config_path = Path('config/config.yaml')  # Good
config_path = r'config\config.yaml'       # Also works

# Avoid mixing path separators
config_path = 'config\\config.yaml'       # Avoid if possible
```

## Performance Optimization

### Environment Tuning
```bash
# Set environment variables for better performance
export OPENBLAS_NUM_THREADS=4
export MKL_NUM_THREADS=4
export NUMEXPR_MAX_THREADS=4

# For development
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Memory Management
```python
# In config.yaml, adjust for available memory
n_clusters: 4          # Reduce for less memory usage
hour_grouping: 2       # Increase to reduce time resolution
days_in_year: 365      # Reduce for testing (e.g., 30 days)
```

## Development Environment

### Additional Tools for Development
```bash
# Install development extras
conda install -c conda-forge \
    jupyter jupyterlab \
    ipython \
    pre-commit \
    git-lfs

# Setup pre-commit hooks
pre-commit install

# Configure Jupyter for project
python -m ipykernel install --user --name storage_osemosys --display-name "Storage OSeMOSYS"
```

### IDE Configuration

#### VS Code
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "~/miniconda3/envs/storage_osemosys/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "files.associations": {
        "*.yml": "yaml",
        "*.yaml": "yaml"
    }
}
```

#### PyCharm
1. File → Settings → Project → Python Interpreter
2. Add → Conda Environment → Existing Environment
3. Select: `~/miniconda3/envs/storage_osemosys/bin/python`

## Environment Maintenance

### Regular Updates
```bash
# Monthly environment update
make update-env

# Security updates
conda update --all

# Check for outdated packages
conda list --outdated
```

### Environment Backup
```bash
# Backup current working environment
conda env export > env/environment_$(date +%Y%m%d).yml

# Create minimal reproducible environment
conda env export --from-history > env/environment_minimal.yml
```

This comprehensive environment setup ensures a robust, reproducible development and execution environment for Storage-in-OSeMOSYS analysis.
