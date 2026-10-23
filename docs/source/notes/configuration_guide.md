# Configuration Guide

One run of `workflow/main.py` solves one scenario with the four storage formulations. Everything
it needs is read from `config/config.yaml`; all paths in that file are relative to the repository
root.

The reproduction tools (`notebooks/reproduce_study.ipynb`, `workflow/automation.py`) rewrite the
scenario settings for each run and restore the file afterwards, so it only needs editing by hand
for single runs.

## Scenario

```yaml
scenario_name: k4h1WND        # label used in every output file name
resource: WND                 # WND | SOL | HYD (labels and the k365h1 baseline file)
n_clusters: 4                 # representative days k (365 = full-year benchmark)
hour_grouping: 1              # block length h in hours
days_in_year: 365
seasons: 1
random_state: 0               # k-means seed
vre_technology: WINDPOWER     # technology label in the capacity-factor files
```

| Key | Meaning | Values used in the study |
|---|---|---|
| `scenario_name` | Prefix of all result files. Convention: `k<k>h<h><resource>`, suffix `_limited` for the stress test, `_s<seed>` for other seeds | `k4h1WND`, `k20h1SOL`, `k365h1HYD_limited`, … |
| `resource` | Which system the run represents; also selects the matching `k365h1` baseline for the figures | `WND`, `SOL`, `HYD` |
| `n_clusters` | Number of representative days k | 2–10, 20–100 in steps of 10, and 365 |
| `hour_grouping` | Hours per intra-day block h; must divide 24 | 1, 2, 4, 6, 8, 12 |
| `days_in_year` | Length of the chronological year in days | 365 (do not change: the time series have 8760 hours) |
| `seasons` | Number of seasons in the Welsch formulation | 1 |
| `random_state` | k-means seed (`n_init = 1`, k-means++) | 0; 1 and 2 for the seed-sensitivity runs |
| `vre_technology` | Technology whose new capacity is reported as `Power Capacity` | `WINDPOWER` (all three profiles use this label) |

Derived quantities: blocks per day `b = 24 / h`, representative time slices `k · b`, chronological
time blocks `365 · b`.

## Storage

```yaml
StorageMaxCapacity: 1000.0     # cap on total storage energy capacity, kW·yr
ResidualStorageCapacity: 0.05  # existing storage, kW·yr
StorageLevelStart: 0.05        # not applied (the initial SoC is a decision variable)
```

`StorageMaxCapacity` caps **total** capacity (new + residual). 1000 kW·yr is non-binding and is used
for all main runs; 0.2 kW·yr gives the binding-capacity stress test (reported new capacity 0.15).

## Inputs

```yaml
system_inputs: data/system      # OSeMOSYS parameter CSVs shared by all formulations
data_8760:
  directory: data/timeseries
  CF: CapacityFactor_Wind.csv   # or CapacityFactor_Solar.csv / CapacityFactor_Hydro.csv
  SDP: SpecifiedDemandProfile.csv
```

`CF` and `SDP` are the 8760-hour profiles that are clustered and aggregated. To study another
system, add the new profiles to `data/timeseries/` (same CSV layout) and point `CF`/`SDP` at them.

## Outputs

```yaml
results:
  directory: results                    # all result files of the run
  directory_GUI: results/GUI            # copy of the hourly comparison figure
  results_copied_filename: Storage_Level
  results_excel_file: Simulation_Results.xlsx
```

Repeated runs append rows to `Simulation_Results.xlsx`. The files are described in {doc}`outputs`.

## Formulations

The `cases` block defines one entry per formulation (`Model_Cluster` is Novo): its folder under
`models/`, model file, otoole template and the names of the generated CSVs. These entries match the
model files and normally need no change.

To run only some formulations, add a list:

```yaml
models: [Model_Niet, Model_Kotzur]
```

Without it all four run. The comparison figures are produced only when all four run.
