<img src="docs/source/_static/storage_in_osemosys_banner_202508.jpg" alt="banner" width="800">

Code, data and reproduction notebook for comparing four ways of representing energy storage in OSeMOSYS when the year is reduced to representative days.

## Project Overview

This project implements four storage state-of-charge (SoC) formulations for temporally aggregated OSeMOSYS models.

### Method names used in the paper and in the code

| Paper (Borba, Islam & Niet, *Environ. Res. Commun.*) | Linkage / verification | Code directory |
|---|---|---|
| **Niet** | direct link between representative time slices | `models/Model_Niet` |
| **Welsch** | fixed intra-day pattern per day type | `models/Model_Welsch` |
| **Kotzur** | chronological days, SoC verified at day boundaries | `models/Model_Kotzur` |
| **Novo** | chronological hours, SoC verified every time step | `models/Model_Cluster` |

## Reproducing the paper

Everything needed to regenerate the published results is in this repository:

```bash
conda env create -f env/environment-crossplatform.yml   # Python 3.13.5, GLPK 5.0, otoole 1.1.5, scikit-learn 1.7.1
conda activate storage_osemosys
jupyter lab notebooks/reproduce_study.ipynb             # step-by-step reproduction (fast steps on by default)
```

The notebook checks the environment, documents the inputs, reruns the clustering (including a multi-seed
robustness check), runs the independent hand-calculated SoC verification (`validation/soc/`), reproduces
selected cases bit-for-bit against the archived results, and rebuilds Table 4, the cost-error curves,
the stress-test statistics and the SoC fidelity metrics. Switches at the top enable the full-year benchmarks,
the 108-configuration sweep and the stress tests. See [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for details,
runtimes and the list of corrections made for the published version.

Command-line alternative:

```bash
python workflow/automation.py --resources WND SOL HYD --k all --h all     # 108 aggregated configurations x 3 systems
python workflow/automation.py --resources WND SOL HYD --k 365 --h 1       # full-year hourly benchmarks
python workflow/automation.py --resources WND SOL --k 365 --h 1 --cap 0.2 # binding-capacity stress test
python validation/soc/run.py                                              # independent SoC verification
python workflow/reproducibility_proof.py                                  # rerun main.py, compare with the saved reference instance
```

## Quick Start

### 1. Environment Setup

```bash
# Create and activate the environment (any OS); or: make setup
conda env create -f env/environment-crossplatform.yml
conda activate storage_osemosys
```

### 2. Configuration

Edit `config/config.yaml` to set your parameters:

```yaml
scenario_name: k4h1WND
resource: WND               # WND | SOL | HYD
n_clusters: 4               # representative days k
hour_grouping: 1            # hours per intra-day block h
random_state: 0             # k-means seed used in the paper
StorageMaxCapacity: 1000.0  # total storage energy cap, kW.yr (0.2 in the stress test)
```

### 3. Run Analysis

```bash
# Run the main analysis
make run-main

# Or run directly
python workflow/main.py
```

## Project Structure

```
storage-in-OSeMOSYS/
├── config/
│   └── config.yaml             # Scenario and path configuration (one scenario per run)
├── data/
│   ├── timeseries/             # Hourly time series (wind, solar, hydro CF; demand profile)
│   ├── system/                 # OSeMOSYS parameter CSVs shared by all formulations (Table 3)
│   ├── published_results/      # Archived result tables and key trajectories of the paper
│   └── full_archive/           # Optional: full results archive, Zenodo 10.5281/zenodo.23598757 (not tracked)
├── models/
│   └── Model_*/                # OSeMOSYS model file and otoole config of each formulation
├── src/                        # Python package: clustering, input generation, solve, post-processing
│   ├── cluster.py              # Representative-day clustering
│   ├── simulation.py           # GLPK runner
│   ├── reproduce.py            # Helpers used by the notebook and the batch runner
│   └── ...
├── workflow/
│   ├── main.py                 # Run one scenario (all four formulations)
│   └── automation.py           # Command-line batch runner for scenario grids
├── notebooks/
│   └── reproduce_study.ipynb   # Step-by-step reproduction of the study
├── validation/
│   └── soc/                    # Independent hand-calculated SoC verification (Section 4.1)
├── env/                        # Conda environments
├── docs/                       # Documentation site (Sphinx)
├── archive/                    # Superseded scripts, notebooks and data (not used by the workflow)
├── results/                    # Fresh outputs (created on first run, not tracked)
└── REPRODUCIBILITY.md          # Reproduction guide, runtimes, corrections log
```

## What a run produces

`python workflow/main.py` solves one scenario with all four formulations and writes to `results/`:

| File | Content |
|---|---|
| `Simulation_Results.xlsx` | One row per scenario and formulation: LP size, total cost, run time, memory, new VRE and storage capacity, solver status |
| `<scenario>_Storage_Level_Model_<name>.csv` | State of charge of each formulation (native, plus reconstructed `_intraday` series for Kotzur and Welsch) |
| `<scenario>_clustering.json` | Representative days and the day-to-representative mapping used by all four formulations |
| `<scenario>_Figure*.png` | Daily, hourly and two-week SoC comparison |

To load and compare results:

```python
import src.reproduce as rp
res = rp.load_results("results/Simulation_Results.xlsx")   # one row per scenario x formulation
rp.add_errors(res)                                          # cost and capacity error vs the k365h1 Novo benchmark
rp.table4(res)                                              # Table 4 of the paper (needs the k365h1 runs)
```

## Documentation

https://deltae.github.io/storage-in-OSeMOSYS/ explains the four formulations, the workflow, every
configuration setting and the output files. The API reference is generated from `src/`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `glpsol: command not found` | `conda install -c conda-forge glpk=5.0` in the `storage_osemosys` environment |
| `ModuleNotFoundError: src` | Run `python workflow/main.py` (works from any folder); start Jupyter in the repository root or `notebooks/` |
| A long run needs too much memory | Novo at k = 365 needs about 12 GB; all aggregated cases need less than 3 GB |

## License

MIT, see [LICENSE](LICENSE).

## Citation

Please cite the article (see also [`CITATION.cff`](CITATION.cff)):

> Borba, B., Islam, M. E., & Niet, T. *Storage in Long-Term Energy Planning Models with Temporal
> Aggregation: Best Practices and Algorithms.* Environmental Research Communications (2026).

Code, inputs and all results of the study are archived on Zenodo: [10.5281/zenodo.23598757](https://doi.org/10.5281/zenodo.23598757) (v1.2.0).

---

Developed by Bruno Borba, Md Eliasinul Islam and Taco Niet, Delta E+ Research Lab, Simon Fraser
University, BC, Canada.
