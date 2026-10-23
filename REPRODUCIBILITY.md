# Reproducibility guide

**Paper:** Bruno Borba, Md Eliasinul Islam, Taco Niet, *Storage in Long-Term Energy Planning Models with Temporal Aggregation: Best Practices and Algorithms*, Environmental Research Communications (ERC-105849).
**Code:** https://github.com/DeltaE/storage-in-OSeMOSYS · **Docs:** https://deltae.github.io/storage-in-OSeMOSYS/
**Archive of all result files:** [10.5281/zenodo.23598757](https://doi.org/10.5281/zenodo.23598757)

## 1. Quick start

```bash
conda env create -f env/environment-crossplatform.yml
conda activate storage_osemosys
jupyter lab notebooks/reproduce_study.ipynb
```

With the default switches the notebook runs in about 2 minutes. It checks the environment, documents all inputs, reruns the clustering and the multi-seed check, runs the independent SoC verification, re-solves k4h1 for the three systems (12 LPs) and compares them with the archive, and rebuilds Table 4, the cost-error curves, the stress-test statistics and the SoC fidelity metrics from the archived results. Turning the switches on regenerates everything from scratch.

| Workload | Solves | Time (GLPK 5.0, i7, 16 GB) | Peak RAM |
|---|---|---|---|
| Full-year benchmarks k365h1, 3 systems | 12 | ~50 min | ~12 GB (Novo) |
| Aggregated grid, 108 configurations × 3 systems | 1296 | 2–4 h (0.8 h solver time) | ~3 GB |
| Stress test k365h1, WND and SOL, cap 0.2 kW·yr | 8 | ~35 min | ~12 GB (Novo) |
| SoC verification (`validation/soc/`) | 4 | < 1 min | < 100 MB |
| Reproducibility proof (`workflow/reproducibility_proof.py`) | 4 | < 1 min | < 200 MB |

### Reproducibility proof with a saved instance

`validation/reference_instance/k4h1WND/` holds one complete instance of the workflow: the otoole
datafile of each formulation (the exact LP data passed to GLPK), the clustering, the summary table
and the storage trajectories, plus a manifest with the environment, git commit and SHA-256 of every
generated input. `python workflow/reproducibility_proof.py` (or `make proof`) reruns
`workflow/main.py` for that scenario and checks that the clustering is identical, every generated
input is byte-identical, LP sizes and solver status match, cost and capacities agree within 1e-9
(relative), the SoC trajectories agree within 1e-9 kW·yr, and the run matches the published archive.
The report is written to `results/proof/k4h1WND/reproducibility_report.md`; the script exits with
status 1 if a check fails. `--save` regenerates the reference instance from the current code.

## 2. What was verified

| Check | Result |
|---|---|
| k4h1 WND/SOL/HYD, all four formulations (12 solves) | identical to archive (cost: 0 difference; capacities ≤ 1e-13 relative) |
| Table 4 aggregated cases, k8/k20 WND, k9/k20 SOL, k7/k20 HYD (24 solves) | identical to archive |
| Table 4 costs and capacities | traceable to the archive without exception |
| Hand-calculated SoC verification | zero error for all four formulations and both reconstructions |
| Solar stress test at 0.2 kW·yr (Kotzur) | reproduces the paper exactly: max 0.2258, min −0.0175, 267 h above, 215 h below, 482 h (5.50 %) |
| Files delivered by B. Borba (`Results_Demand_Variation.zip`, `Storage_Article.rar`, `validation_soc.zip`, checksums in `data/ORIGINAL_DELIVERY_SHA256SUMS`) | all 6664 files present byte-for-byte in the repository; `data/full_archive/` equals the results zip |
| Fresh run vs the delivered table, 16 grid scenarios (k4–k30, h1–h12, all systems, 64 solves) | cost and capacities within 7e-9 relative (largest: Welsch k10h6HYD, GLPK fallback option) |
| LP size vs the delivered table | **not identical**: see Section 4, item 10 |

## 3. Corrections made to the repository for the published version

| # | Problem | Effect | Fix |
|---|---|---|---|
| 1 | `main.py` copied the template CSVs from `inputs_csv/` *after* generating the formulation-specific files. | `Conversionld`, `Conversionlh`, `Conversionls`, `DaysInDayType` and `DAILYTIMEBRACKET` were overwritten with empty templates; **Kotzur and Welsch solved a meaningless LP** (cost ≈ 39, no generation built). | Templates are copied at the start of each case. |
| 2 | `inputs_csv/` did not contain the values used for the paper: annual demand 2.0, VRE capital cost 999 999, VRE variable cost 4.167. | No published number could be reproduced. | Set to demand **20**, VRE capital cost **1200** (Table 3), VRE variable cost **20** (otoole default). These values reproduce the archive bit for bit. |
| 3 | `Model_*/results/` folders are not tracked by git; GLPK cannot create them. | Fresh clones failed at the first solve. | Created at run time. |
| 4 | GLPK's primal simplex occasionally fails on Welsch LPs ("unable to recover undefined or non-optimal solution"); the failure was not detected and result CSVs from the previous scenario were read. | **8 archived Welsch rows are invalid** (cost 0, stale capacities): k4h12HYD, k6h2HYD, k6h8HYD, k5h1SOL, k7h1SOL, k8h1SOL, k5h4WND, k7h8WND. | Status check plus automatic retry (`--nopresol`, `--dual`, `--exact`, identical optima where tested); stale outputs are cleared before each case; capacities are never reported from a failed solve. Re-solved values: `data/published_results/corrections/welsch_reruns.xlsx`. |
| 5 | `validation_soc/run.py` imported modules from `src/` as top-level modules, but `src/update_list.py` uses a package-relative import. | The verification script crashed. | Imports go through the `src` package. |
| 6 | Excel append did not pin the engine. | Crash if `xlsxwriter` is installed. | `engine='openpyxl'`. |
| 7 | `KMeans` relied on the default `n_init`. | Before scikit-learn 1.4 the default was 10, which gives different representative days. | `n_init=1`, `init='k-means++'`, `random_state` from `config.yaml`. |
| 8 | Hard-coded WND baseline file and VRE label; Qt backend required; Linux-only environment file; `automation.py` used a Windows-only interpreter path and a wrong config path. | Solar/hydro runs and non-Linux machines needed manual edits. | Resource-aware baseline, `Agg` backend, cross-platform environment, rewritten `automation.py`. |
| 9 | Kotzur reconstruction read Novo's dense `Conversionlts` (≈ 77 M rows at k365h1). | Kotzur results could not be post-processed without running Novo (~12 GB). | Sparse mapping (identical information) written per scenario. |
| 10 | Clustering, cap and seed were not recorded with the results. | Archived files could not be tied to their settings (e.g. the cap of a `_limited` run). | `<scenario>_clustering.json` stores k, h, seed, cap, representative days and day mapping. |

## 4. Notes on the archived results

1. **Section 4.4, wind, counting.** "224 h (183 above, 41 below)" counts hours with SoC **≥** 0.2 kW·yr; 69 of those hours lie exactly on the bound and are feasible. Strict counting of the archived trajectory gives 114 h above and 41 h below, **155 h (1.77 %)**. The solar figures use strict counting.
2. **Section 4.4, wind, provenance.** The archived wind stress run (source of 0.2213 / −0.0271) was produced with inputs different from the main study: its costs do not match a run with the paper's inputs. Regenerated with the paper's inputs (Niet, Welsch, Kotzur), Kotzur gives max 0.2274, min −0.0295, 67 h above and 40 h below (107 h, 1.22 %). Novo needs a 16 GB machine and is not part of the regenerated run.
3. **Section 4.4, cost.** Under the binding cap, Kotzur's total cost is 7.6 % below Niet/Novo in the archived wind run and 39.8 % below Niet in the regenerated wind run; for solar it is 3.1 % below Niet.
4. **Table 4.** Capacity errors are computed from the benchmark rounded to two decimals (WND k8h1 Niet: +676.0 % rounded vs +678.9 % unrounded). At full resolution the capacities of the four formulations differ by up to 0.055 kW·yr (SOL).
5. **Figure 6 (k365h1).** Kotzur still verifies SoC only at day boundaries at full resolution, so it does not reduce to the same recursion as the other three; the full-resolution capacities differ by up to 0.055 kW·yr. Section 4.4 relies on this difference.
6. **Inputs not listed in Table 3.** Annual demand (20) and VRE variable cost (20) both affect total cost.
7. **Seed robustness.** Across seeds 1–9 the day partition has a mean ARI of 0.62 (minimum 0.34), and the representative-day sets are identical only at k = 2. Re-optimising k = 4, 8, 20 (h = 1) with seeds 1–2 changes cost errors by up to 5.6 pp (HYD), 4.3 pp (SOL) and 8.1 pp (WND). For HYD the seed spread exceeds the between-formulation differences (≤ 0.2 pp); for WND at k ≤ 8, the separation between {Kotzur, Novo} and {Niet, Welsch} (7.9–11.5 pp across seeds) remains larger than the seed spread (≤ 3.6 pp). Table 4 errors therefore depend on the clustering.
8. **Figure 8 metrics.** No script for MAE/RMSE/Pearson/rainflow was in the delivery. The notebook re-implements them with stated alignment rules.
9. **Invalid Welsch rows.** The 8 failed Welsch solves (Section 3, item 4) are replaced by the re-solved values in `data/published_results/corrections/welsch_reruns.xlsx`.
10. **LP size.** Every archived LP is larger than the LP built from the repository inputs by n_TS + 8 rows, n_TS + 4 columns and a matching number of non-zeros (n_TS = number of timeslices; k4h1: +104 rows, +100 columns, +778 non-zeros), identically for all four formulations. This is the footprint of one additional technology with one mode of operation that is never active, so costs and capacities are unaffected. No input file in the delivery or in the git history contains a third technology, and the three input corrections (demand, VRE capital and variable cost) do not change the LP size. A fresh run gives the absolute LP size of the repository inputs; comparisons between formulations are unaffected because the offset is the same for all four.

## 5. Repository layout for reproduction

```
config/config.yaml           scenario settings and paths (rewritten per run by the notebook, then restored)
data/timeseries/             hourly capacity factors (wind, solar, hydro) and demand profile
data/system/                 OSeMOSYS parameter CSVs (Table 3 values)
models/Model_*/              OSeMOSYS model file and otoole template of each formulation
workflow/main.py             runs one scenario with all four formulations
workflow/automation.py       command-line batch runner
notebooks/reproduce_study.ipynb  step-by-step reproduction (this guide, executable)
src/reproduce.py             helpers: run_case, run_grid, table4, seed_robustness, soc_violations, fidelity_metrics
validation/soc/              independent hand-calculated SoC verification
results/                     fresh runs (created on first run, not tracked)
data/published_results/
  main/                      archived sweep table (Simulation_Results.xlsx) and k365h1 trajectories
  limited/                   archived stress-test table and wind trajectories
  corrections/               re-solved values for the 8 failed Welsch solves
  stress_R2/                 stress tests regenerated with the paper's inputs (Niet, Welsch, Kotzur)
  seeds/                     re-optimisation with k-means seeds 1 and 2
```

The full archive (all trajectories and figures, ~290 MB) is not tracked by git. Download `storage-in-OSeMOSYS-<version>-full_results.tar.gz` from Zenodo and unpack it as `data/full_archive/` (containing `Results_Demand_Variation/` and `Results_Limited/`); the notebook detects it automatically.

## 6. Zenodo deposit

`python workflow/build_zenodo_bundle.py --version vX.Y.Z` (from a clean, committed tree) writes
`dist/zenodo/vX.Y.Z/`: the code tarball (`git archive` of HEAD), the full results tarball
(`data/full_archive/`), a conda lock file of the environment, `PROVENANCE.md`, and `SHA256SUMS` /
`SHA256SUMS-contents`. The tarballs are deterministic, so rebuilding from the same commit gives
identical checksums. Deposit metadata is in `.zenodo.json`.
