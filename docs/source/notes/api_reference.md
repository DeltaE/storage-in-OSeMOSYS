# Module Overview

The `src` package holds every step of the workflow. `workflow/main.py` calls them in order (see
{doc}`workflow_guide`); `src.reproduce` wraps whole runs for the notebook and the batch runner.
Signatures and docstrings for every function are in the generated reference
({doc}`../autoapi/src/index`).

Most functions take file paths and plain Python values, read or write OSeMOSYS-style CSV files
(`REGION, …, VALUE`) and return the path they wrote.

## Clustering

| Function | Module | What it does |
|---|---|---|
| `cluster_data(capacity_factor_path, demand_profile_path, n_clusters, random_state=0, n_init=1)` | `src.cluster` | k-means on daily 48-value vectors (24 scaled CF + 24 scaled demand values). Returns the sorted representative days and, for each of the 365 days, the representative day that stands in for it. |

```python
from src.cluster import cluster_data

days, sequence = cluster_data("data/timeseries/CapacityFactor_Wind.csv",
                              "data/timeseries/SpecifiedDemandProfile.csv", n_clusters=4)
```

## Building the model inputs

| Function | Module | Writes |
|---|---|---|
| `new_list(length, output_file)` | `src.update_list` | A set with members 1…`length` (`TIMESLICE`, `TIMESLICECRO`, `DAYTYPE`, `DAYSCRO`, `DAILYTIMEBRACKET`) |
| `CFandSDP(input_file, representative_days, hour_grouping, output_file, operation='mean')` | `src.update_CFandSDP` | Capacity factor (`'mean'`) or demand profile (`'sum'`) of the representative days, aggregated into blocks |
| `yearsplit(timeslices, representative_days, chronological_sequence, days_in_year, output_file)` | `src.update_yearsplit` | `YearSplit`: share of the year each time slice represents |
| `conversionlts(blocks_per_day, chronological_timeslices, timeslices, chronological_sequence, representative_days, output_file)` | `src.update_conversionlts` | Novo: chronological block → representative time slice (dense) |
| `conversionlts_sparse(blocks_per_day, chronological_sequence, representative_days, output_file)` | `src.update_conversionlts` | The same mapping, non-zero entries only (used for the Kotzur reconstruction) |
| `conversionld(timeslices, representative_days, output_file, label='DAYTYPE')` | `src.update_conversionld` | Time slice → day type (or → season with `label='SEASON'`) |
| `conversionldc(chronological_sequence, representative_days, days_in_year, output_file)` | `src.update_conversionldc` | Kotzur: day type → chronological day |
| `conversionlh(timeslices, blocksperday, output_file)` | `src.update_conversionlh` | Welsch: time slice → daily time bracket |
| `daysindaytype(representative_days, chronological_sequence, output_file)` | `src.update_daysindaytype` | Welsch: number of days of each day type |
| `new_yaml_param(yaml_file, param_name, new_value)` | `src.update_params_yaml_otoole` | Sets the default of a parameter in an otoole config file |

Note that `conversionld` takes the **number** of representative days as its second argument.

## Solving and collecting results

| Function | Module | What it does |
|---|---|---|
| `run_simulation(case_info)` | `src.simulation` | Runs `glpsol` for one formulation (entry of `cases` in the config), retries with other GLPK options if needed, writes `simulation_results.txt` and returns `'optimal'` or `'FAILED'` |
| `table(sim_results_path, sol_path, scenario_name, model, new_capacity_path, new_storage_capacity_path, filter_val1, filter_val2, excel_path)` | `src.table_generator` | Appends one row (LP size, cost, time, memory, capacities, status) to `Simulation_Results.xlsx` |
| `copy_and_rename(results_case, results_destination_folder, new_results_filename)` | `src.copy_rename_csv` | Copies a result CSV into the results folder under a new name |
| `read_csvfile(path)` | `src.read_csv` | Reads the single `VALUE` of a one-row result file (e.g. the year-start storage level) |

## Post-processing

| Function | Module | What it does |
|---|---|---|
| `intraday_kotzur(conversion_path, storage_path, storage_level_start, output_path)` | `src.Kotzur_intraday` | Kotzur SoC at every chronological block, accumulated from the representative blocks |
| `intraday_welsch2(storage_path, blocksperday, timeslices, representative_days, chronological_sequence, storage_level_start, output_path)` | `src.Welsch_intraday2` | Welsch SoC in grouped day-type order |
| `graph(file_base, file_kotzur, file_kotzur_intraday, file_cluster, file_niet, file_welsch, file_welsch_intraday, representative_days, blocks_per_day, file_yearsplit)` | `src.graph_generator` | Returns three matplotlib figures comparing the four SoC trajectories (daily, hourly, two weeks) |

## Configuration and console output

| Function | Module | What it does |
|---|---|---|
| `load_config(config_file_path='config/config.yaml')` | `src.utilities` | Reads a YAML file; raises `FileNotFoundError` if it is missing |
| `print_update(level, message)`, `print_info(info)`, `print_banner(message)`, `print_module_title(text)` | `src.utilities` | Coloured progress messages |

## Reproducing the study (`src.reproduce`)

| Function | What it does |
|---|---|
| `check_environment()` | Installed versions compared with the paper |
| `run_case(resource, k, h, *, cap=1000.0, random_state=0, results_dir='results', models=None, limited=None, suffix='', timeout=None, verbose=False)` | Runs one scenario through `workflow/main.py` and returns its rows |
| `run_grid(resources, ks, hs, skip_existing=True, **kw)` | Runs a grid of scenarios, skipping completed ones |
| `load_results(xlsx)`, `add_errors(df)`, `table4(df)`, `compare_to_archive(new, archive)` | Tidy results, errors against the k365h1 Novo benchmark, Table 4 of the paper, bit-for-bit comparison |
| `clustering(resource, k, random_state=0)`, `seed_robustness(...)` | Clustering of one case; stability across k-means seeds |
| `run_soc_validation()` | Runs `validation/soc/run.py` and returns its summary |
| `read_storage(...)`, `hourly_trajectory(...)`, `soc_violations(...)`, `fidelity_metrics(...)`, `rainflow_cycles(...)` | SoC trajectories and the metrics of Sections 4.3–4.4 |

```python
from src.reproduce import run_case

df = run_case("WND", k=8, h=1)
print(df[["Model", "Total cost", "Storage Capacity"]])
```
