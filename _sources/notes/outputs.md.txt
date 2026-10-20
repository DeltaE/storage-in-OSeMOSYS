# Outputs

All outputs of a run are written to the folder set in `results.directory` (default `Results/`).

## `Simulation_Results.xlsx`

One row per scenario and formulation; repeated runs append rows (the reproduction tools keep the last
row of each scenario and formulation).

| Column | Meaning |
|---|---|
| `Scenario`, `Model` | Scenario label and formulation directory (`Model_Cluster` = Novo) |
| `Number of constraints`, `Number of variables`, `Non-zero elements in the matrix` | LP size from the GLPK solution file |
| `Total cost` | Objective value, model cost units |
| `Matrix and Running Time` | Wall time of model generation and solve, s (older files: `Matriz and Running Time`) |
| `Running time` | Solver time reported by GLPK, s |
| `Memory used` | Peak memory reported by GLPK, MB |
| `Power Capacity` | New VRE capacity |
| `Storage Capacity` | **New** storage energy capacity, kW·yr (total = new + 0.05 residual) |
| `Solver status` | `optimal` or `FAILED`; capacities are empty for failed solves |

## State-of-charge files

| File | Content |
|---|---|
| `<scenario>_Storage_Level_Model_Niet.csv` | SoC at the start of each representative timeslice |
| `<scenario>_Storage_Level_Model_Cluster.csv` | Novo: SoC at the start of each chronological timeslice (365 × 24/*h* values) |
| `<scenario>_Storage_Level_Model_Kotzur.csv` | SoC at the start of each chronological day |
| `<scenario>_Storage_Level_Model_Kotzur_intraday.csv` | Kotzur trajectory reconstructed within each day (`VALUEACCUMULATED`) |
| `<scenario>_Storage_Level_Model_Welsch.csv` | SoC at the start of each day type |
| `<scenario>_Storage_Level_Model_Welsch_intraday.csv` | Welsch trajectory reconstructed in grouped day-type order |

## Other files

| File | Content |
|---|---|
| `<scenario>_clustering.json` | k, h, seed, storage cap, representative days and the day-to-representative mapping |
| `<scenario>_Conversionlts_sparse.csv` | Chronological → representative timeslice mapping used for the Kotzur reconstruction |
| `<scenario>_Figure*.png` | Daily, hourly and two-week SoC comparison (only when all four formulations ran) |
| `logs/<scenario>.log` | Full console output of the run (batch and notebook runs) |
| `Model_<name>/results/*.csv` | All OSeMOSYS result tables of the last run of that formulation |

## Loading results in Python

```python
import src.reproduce as rp
res = rp.load_results("Results/Simulation_Results.xlsx")   # tidy table: resource, k, h, formulation, ...
rp.table4(res)                                              # Table 4 of the paper (needs the k365h1 runs)
rp.add_errors(res)                                          # cost and capacity error vs k365h1 Novo
```
