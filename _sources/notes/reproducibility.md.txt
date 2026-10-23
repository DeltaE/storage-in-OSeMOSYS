# Reproducibility guide

This page explains how to regenerate the results of

> Borba, B., Islam, M. E., & Niet, T. *Storage in Long-Term Energy Planning Models with Temporal
> Aggregation: Best Practices and Algorithms.* Environmental Research Communications (2026).

from this repository, which result comes from which step, how long each step takes, and what was
verified. The executable version of this guide is the notebook {doc}`../notebooks/reproduce_study`
(`notebooks/reproduce_study.ipynb` in the repository).

## 1. Requirements

| Item | Version used in the paper | Notes |
|---|---|---|
| Python | 3.13.5 | |
| GLPK (`glpsol`) | 5.0 | conda-forge, all platforms |
| otoole | 1.1.5 | CSV → MathProg data conversion |
| scikit-learn | 1.7.1 | k-means; versions < 1.4 used a different `n_init` default |
| pandas / NumPy | 2.2.3 / 2.3.1 | |
| Hardware | Intel Core i7, 16 GB RAM | 16 GB is needed only for Novo at k = 365 |

All of these are installed by `env/environment-crossplatform.yml` ({doc}`README_ENVIRONMENT`).

## 2. What is in the repository

| Path | Content |
|---|---|
| `config/config.yaml` | Scenario settings and paths |
| `data/timeseries/` | Hourly capacity factors (`CapacityFactor_Wind.csv`, `_Solar.csv`, `_Hydro.csv`) and demand profile (`SpecifiedDemandProfile.csv`) |
| `data/system/` | System parameters (Table 3 of the paper) |
| `models/Model_*/` | OSeMOSYS model file and otoole configuration of each formulation |
| `workflow/main.py`, `src/` | Pipeline: clustering, input generation, solve, post-processing |
| `workflow/automation.py` | Command-line batch runner |
| `src/reproduce.py` | Helpers used by the notebook (runs, tables, metrics) |
| `validation/soc/` | Independent hand-calculated SoC verification |
| `data/published_results/` | Result tables of the paper and the trajectories behind Table 4 and Section 4.4 |
| `notebooks/reproduce_study.ipynb` | Step-by-step reproduction |
| `archive/` | Superseded scripts and data, not used by the workflow |

The complete set of result files (all trajectories and figures, about 290 MB) is archived on Zenodo
([10.5281/zenodo.23598757](https://doi.org/10.5281/zenodo.23598757)). Unpack it as `data/full_archive/`
(containing `Results_Demand_Variation/` and `Results_Limited/`); the notebook detects it automatically and otherwise uses `data/published_results/`.

## 3. Step by step

### 3.1 Install

```bash
git clone https://github.com/DeltaE/storage-in-OSeMOSYS.git
cd storage-in-OSeMOSYS
conda env create -f env/environment-crossplatform.yml
conda activate storage_osemosys
```

### 3.2 Quick verification (about 2 minutes)

```bash
jupyter lab notebooks/reproduce_study.ipynb   # run all cells with the default switches
```

With the default switches the notebook:

1. checks the installed versions against the paper;
2. lists the model inputs and plots the time series;
3. reruns the clustering, checks that it is deterministic, and repeats it with seeds 1–9;
4. runs the hand-calculated SoC verification;
5. solves k4h1 for the three systems with all four formulations (12 LPs) and compares cost, VRE
   capacity and storage capacity with the archived results (the cell fails if they differ);
6. rebuilds Table 4, the cost-error curves, the stress-test statistics and the SoC metrics from the
   archived results.

### 3.3 Full regeneration

Set the switches at the top of the notebook, or use the command line:

| Step | Command | Solves | Time* | Peak RAM |
|---|---|---|---|---|
| Full-year benchmarks (Section 4.1) | `python workflow/automation.py --resources WND SOL HYD --k 365 --h 1` | 12 | ~50 min | ~12 GB |
| Aggregated configurations (Sections 4.2–4.3) | `python workflow/automation.py --resources WND SOL HYD --k all --h all` | 1296 | 2–4 h | ~3 GB |
| Stress test (Section 4.4) | `python workflow/automation.py --resources WND SOL --k 365 --h 1 --cap 0.2` | 8 | ~30 min | ~12 GB |
| Seed sensitivity | `python workflow/automation.py --resources WND SOL HYD --k 4 8 20 --h 1 --seed 1` (and `--seed 2`) | 72 | ~10 min | < 1 GB |
| SoC verification (Section 4.1) | `python validation/soc/run.py` | 4 | < 1 min | < 0.1 GB |

\*GLPK 5.0, Intel Core i7, 16 GB RAM. The sweep needs about 0.8 h of solver time; the rest is input
generation and file conversion.

Results go to `results/`. Rerun the notebook afterwards: every table and figure uses fresh results where
they exist and archived results otherwise.

## 4. Where each result comes from

| Paper element | Content | Source | Notebook step |
|---|---|---|---|
| Figure 1, Table 2 | Classification of storage formulations | Conceptual | — |
| Figure 2, Table 1 | Formulations on a synthetic one-week series | Illustrative example, not produced by this pipeline | — |
| Table 3, Figures 3–5 | System parameters, VRE and demand profiles | `data/system/`, `data/timeseries/` | 2 |
| Section 3.2 | Clustering settings | `src/cluster.py` | 3 |
| Section 4.1, verification | Hand-calculated SoC check | `validation/soc/` | 4 |
| Figure 6, Table S1 | Full-year hourly benchmarks | k365h1 runs | 6 |
| Table 4, Figure 7, Tables S2–S4 | Cost and capacity errors, runtimes | Aggregated runs + benchmarks | 7–8 |
| Figure 8 | MAE, RMSE, Pearson r, rainflow cycles | SoC trajectories | 10 |
| Section 4.4, Figures 9–10 | Binding-capacity stress test | k365h1 runs with cap 0.2 kW·yr | 9 |
| Clustering robustness (Table S5) | Partition stability and cost spread across seeds | Seeds 0–9 (clustering), 0–2 (optimisation) | 3.1, 11 |

Conventions used throughout:

* **Errors** are relative to the k365h1 Novo run of the same system, computed from unrounded values.
* **Storage capacity** in the tables is *new* capacity; total capacity adds the 0.05 kW·yr residual.
* **Stress-test violations** count hours with SoC strictly above the cap or below zero. Hours exactly
  at the cap are feasible and are reported separately.
* **Figure 8 metrics**: each aggregated trajectory is expanded to 8760 hours. Novo and Kotzur use
  chronological blocks (Kotzur reconstructed within days); Welsch uses its reconstructed trajectory in
  grouped day-type order; Niet holds each representative block for its year-split duration. Rainflow
  counting follows ASTM E1049-85, with half cycles counted as 0.5.

## 5. What was verified

| Check | Result |
|---|---|
| k4h1, WND/SOL/HYD, 4 formulations (12 solves) | Identical to the archived results: cost difference 0; capacities agree to ≤ 1e-13 relative |
| Table 4 aggregated cases: k8, k20 WND; k9, k20 SOL; k7, k20 HYD (24 solves) | Identical to the archived results |
| SoC verification, 4 formulations and 2 reconstructions | Zero deviation from the hand calculation |
| Kotzur reconstruction with the sparse mapping | Identical to the dense-mapping trajectory (≤ 1e-14) |
| Clustering with a fixed seed | Deterministic |

## 6. Numerical and platform notes

* **Determinism.** With the same GLPK version and inputs, solutions are identical across runs.
  Different GLPK builds or platforms can follow different simplex paths. The optimal objective is
  unchanged, but degenerate LPs can return different, equally optimal, capacities or SoC trajectories.
* **Solver failures.** GLPK's primal simplex occasionally stops on a Welsch LP with *"unable to recover
  undefined or non-optimal solution"*, depending on the platform. The pipeline detects this and
  re-solves with `--nopresol`, `--dual` and `--exact`; in the cases tested all three give the same
  optimum. Eight Welsch rows of the original sweep (k4h12, k6h2, k6h8 HYD; k5h1, k7h1, k8h1 SOL;
  k5h4, k7h8 WND) were affected. The re-solved values are in
  `data/published_results/corrections/welsch_reruns.xlsx`, and the notebook uses them.
* **Clustering.** `n_init = 1` and `random_state = 0` are set explicitly. Partitions differ between
  seeds, so error levels at a given k depend on the clustering. The notebook quantifies this (step 11).
* **Runtimes and memory** depend on hardware and solver. Ratios between formulations are more
  transferable than absolute values, and memory ratios more than time ratios.

## 7. Changes made for the published version

The code was corrected after the original runs so that a fresh clone reproduces the archived results.
None of the corrections changes the model equations.

| Change | Reason |
|---|---|
| Template CSVs are copied before the formulation-specific files are generated | The previous order overwrote the Kotzur and Welsch mapping files with empty templates |
| `data/system/` (formerly `inputs_csv/`) holds the values used in the paper (demand 20, VRE capital cost 1200, VRE variable cost 20) | The repository previously contained placeholder values |
| Model result folders are created at run time; stale results are cleared | Fresh clones failed; failed solves could report results of the previous run |
| Solver status check and automatic retry | See section 6 |
| Explicit `n_init`, `random_state` and clustering record per run | Clustering is reproducible across scikit-learn versions and traceable |
| Sparse chronological mapping for the Kotzur reconstruction | Kotzur post-processing no longer requires the 12 GB Novo run |
| Cross-platform environment, headless plotting, UTF-8 child processes | Runs on Windows, macOS and Linux |

### Documentation changes

The tutorial pages *Basic usage*, *Comparative analysis* and *Advanced configuration*, and the
*Results analysis* page, described functions and features that the code does not provide. They are no
longer published (copies are in `archive/docs/`). The module overview, configuration, workflow,
environment and model-specification pages were rewritten to match the code, and the full API
reference is generated from the source ({doc}`../autoapi/src/index`).
