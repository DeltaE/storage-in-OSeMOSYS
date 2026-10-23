# Quickstart

## 1. Set up the environment

```bash
git clone https://github.com/DeltaE/storage-in-OSeMOSYS.git
cd storage-in-OSeMOSYS

make setup                       # creates the conda env and installs dependencies
conda activate storage_osemosys
make test-env                    # checks Python packages and the GLPK solver
```

Full details and manual setup: {doc}`notes/README_ENVIRONMENT`.

## 2. Choose a scenario

Edit `config/config.yaml`:

```yaml
scenario_name: k4h1WND        # label used for result files
resource: WND                 # WND | SOL | HYD
n_clusters: 4                 # number of representative days k
hour_grouping: 1              # hours per intra-day block h (1, 2, 4, 6, 8 or 12)
random_state: 0               # k-means seed used in the paper

data_8760:
  CF: CapacityFactor_Wind.csv # match the resource: _Wind, _Solar or _Hydro
```

All parameters are described in {doc}`notes/configuration_guide`.

## 3. Run

```bash
python workflow/main.py      # or: make run-main
```

The pipeline clusters the hourly data into representative days, writes the inputs for each
storage formulation, solves each model with GLPK and collects the results. The steps are
explained in {doc}`notes/workflow_guide`.

## 4. Look at the results

Results are written to `results/`. See {doc}`notes/outputs` for the file layout, or
{doc}`notes/reproducibility` to regenerate the published study.
