"""Batch runner for the scenario grid of the paper (cross-platform).

Examples
--------
python workflow/automation.py --resources WND --k 4 8 20 --h 1                 # a few cases
python workflow/automation.py --resources WND SOL HYD --k all --h all          # full 108 x 3 grid
python workflow/automation.py --resources WND SOL HYD --k 365 --h 1            # full-year benchmarks
python workflow/automation.py --resources WND SOL --k 365 --h 1 --cap 0.2      # stress test (Section 4.4)

Each scenario is solved with all four formulations by workflow/main.py; results are appended to
<results>/Simulation_Results.xlsx. Already completed scenarios are skipped. config/config.yaml is
restored after every run.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repository root, for `src`

from src import reproduce as rp


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--resources", nargs="+", default=["WND", "SOL", "HYD"], choices=list(rp.RESOURCES))
    ap.add_argument("--k", nargs="+", default=["all"], help="representative days, or 'all'")
    ap.add_argument("--h", nargs="+", default=["all"], help="block length in hours, or 'all'")
    ap.add_argument("--cap", type=float, default=rp.UNCONSTRAINED_CAP,
                    help="total storage energy cap in kW.yr (default non-binding; 0.2 = stress test)")
    ap.add_argument("--seed", type=int, default=0, help="k-means random_state (paper: 0)")
    ap.add_argument("--results", default="results", help="output folder, relative to the repository root")
    a = ap.parse_args()
    ks = rp.K_VALUES if a.k == ["all"] else [int(x) for x in a.k]
    hs = rp.H_VALUES if a.h == ["all"] else [int(x) for x in a.h]
    suffix = "" if a.seed == 0 else f"_s{a.seed}"
    rp.run_grid(a.resources, ks, hs, cap=a.cap, random_state=a.seed, results_dir=a.results, suffix=suffix)


if __name__ == "__main__":
    main()
