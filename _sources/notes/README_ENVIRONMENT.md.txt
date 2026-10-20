# Environment Setup Guide

The project runs in one conda environment, `storage_osemosys`, with the package versions used in the
paper. It works on Windows, macOS and Linux.

## Prerequisites

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda
- Git
- About 2 GB of disk space. The full-year benchmark runs (k = 365) need about 12 GB of RAM; all
  other runs need less than 3 GB.

## Set up with make

```bash
git clone https://github.com/DeltaE/storage-in-OSeMOSYS.git
cd storage-in-OSeMOSYS

make setup                       # create the environment and check it
conda activate storage_osemosys
```

`make setup` runs three steps, which you can also run on their own:

| Command | What it does |
|---|---|
| `make env-create` | `conda env create -f env/environment-crossplatform.yml` |
| `make install-deps` | `pip install otoole colorama` (already in the environment file; kept as a safety net) |
| `make test-env` | Imports every package and `src`, and checks that `glpsol` is on the path |

## Set up without make

```bash
conda env create -f env/environment-crossplatform.yml
conda activate storage_osemosys
glpsol --version                 # GLPK 5.0
python -c "import src, otoole; print('ok')"
```

Without conda, install GLPK 5.0 so that `glpsol` is on the path, then
`pip install -r requirements.txt`.

## What is installed

`env/environment-crossplatform.yml` pins the versions reported in the paper:

| Package | Version | Used for |
|---|---|---|
| Python | 3.13.5 | |
| GLPK (`glpsol`) | 5.0 | LP solver |
| otoole | 1.1.5 | CSV → GLPK data file conversion |
| scikit-learn | 1.7.1 | k-means clustering of days |
| pandas, NumPy, SciPy | 2.2.3, 2.3.1, 1.16.0 | data handling |
| matplotlib | 3.10.0 | figures |
| openpyxl, PyYAML, colorama | 3.1.5, 6.0.2, 0.4.6 | Excel output, configuration, console output |
| JupyterLab, ipykernel | latest | the reproduction notebook |

`env/environment.yml` is the exact Linux export of the environment used for the study (with build
strings). It is kept for provenance; `make env-export` refreshes it.

The first step of the reproduction notebook compares the installed versions with these.

## Documentation tools

```bash
make docs-setup                  # installs docs/requirements.txt into the environment
make docs-build                  # builds docs/build/html
make docs-serve                  # serves it at http://localhost:8000
```

## Other make commands

| Command | Purpose |
|---|---|
| `make env-update` | Update the environment from `env/environment-crossplatform.yml` |
| `make env-remove`, `make recreate` | Remove, or remove and rebuild, the environment |
| `make env-info`, `make env-list`, `make env-size` | Inspect environments |
| `make backup` | Export the environment to `backups/` with a timestamp |
| `make clean` | Delete `__pycache__` folders and `.pyc` files |
| `make help` | List all commands |

## Troubleshooting

| Problem | Fix |
|---|---|
| `glpsol: command not found` | Activate the environment; if it is still missing: `conda install -c conda-forge glpk=5.0` |
| `ModuleNotFoundError: src` | Run scripts as `python workflow/main.py` (from any folder), or start Jupyter in the repository root or in `notebooks/` |
| `make: command not found` | Install make (`conda install -c conda-forge make`) or use the commands in *Set up without make* |
| Environment solve is slow or fails | Update conda (`conda update -n base conda`) and retry; the file only uses conda-forge |
| Different numbers from the paper | Check the versions in step 1 of the reproduction notebook; scikit-learn < 1.4 changed the k-means default |
