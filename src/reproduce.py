"""Helpers for reproducing Bruno, Islam & Niet, "Storage in long-term energy planning models with
temporal aggregation" (Environ. Res. Commun., ERC-105849) with this repository.

Used by ``notebooks/reproduce_study.ipynb`` and ``workflow/automation.py``. Every model run goes
through ``workflow/main.py`` unchanged, so the notebook exercises exactly the code path that
produced the published numbers.

Naming: the formulation called *Novo* in the paper is implemented in ``Model_Cluster``.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from importlib import metadata
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

REPO = Path(__file__).resolve().parents[1]
TIMESERIES = REPO / "data" / "timeseries"      # hourly capacity factors and demand profile
MAIN = REPO / "workflow" / "main.py"
SOC_VALIDATION = REPO / "validation" / "soc"

# ---------------------------------------------------------------------------------------------
# Experimental design (manuscript Sections 3.2-3.4)
# ---------------------------------------------------------------------------------------------
RESOURCES = {"WND": "CapacityFactor_Wind.csv",
             "SOL": "CapacityFactor_Solar.csv",
             "HYD": "CapacityFactor_Hydro.csv"}
DEMAND_PROFILE = "SpecifiedDemandProfile.csv"
K_VALUES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]   # 18 values
H_VALUES = [1, 2, 4, 6, 8, 12]                                                  # 6 values
MODELS = ["Model_Niet", "Model_Welsch", "Model_Kotzur", "Model_Cluster"]
FORMULATION = {"Model_Niet": "Niet", "Model_Welsch": "Welsch",
               "Model_Kotzur": "Kotzur", "Model_Cluster": "Novo"}
UNCONSTRAINED_CAP = 1000.0   # kW.yr, non-binding upper limit on total storage energy capacity
STRESS_CAP = 0.2             # kW.yr, Section 4.4 (total = new + residual 0.05)
RESIDUAL_STORAGE = 0.05

MANUSCRIPT_ENV = {"python": "3.13.5", "glpsol": "5.0", "otoole": "1.1.5",
                  "scikit-learn": "1.7.1", "pandas": "2.2.3", "numpy": "2.3.1"}


# ---------------------------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------------------------
def _glpsol_version() -> str | None:
    exe = shutil.which("glpsol")
    if exe is None:
        return None
    out = subprocess.run([exe, "--version"], capture_output=True, text=True).stdout
    m = re.search(r"Solver\s+([\d.]+)", out)
    return m.group(1) if m else out.splitlines()[0]


def check_environment() -> pd.DataFrame:
    """Installed versions against the environment stated in Section 3.4."""
    found = {"python": sys.version.split()[0], "glpsol": _glpsol_version()}
    for pkg in ["otoole", "scikit-learn", "pandas", "numpy"]:
        try:
            found[pkg] = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            found[pkg] = None
    rows = []
    for k, ref in MANUSCRIPT_ENV.items():
        v = found.get(k)
        status = "missing" if v is None else ("match" if v == ref else "differs")
        rows.append({"component": k, "manuscript": ref, "installed": v, "status": status})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------------------
# Running scenarios through main.py
# ---------------------------------------------------------------------------------------------
def _child_env() -> dict:
    """UTF-8 output for child Python processes; on Windows a redirected stdout otherwise uses cp1252,
    which cannot encode the progress symbols printed by main.py (UnicodeEncodeError)."""
    import os
    return {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}


def scenario_name(resource: str, k: int, h: int, limited: bool = False, suffix: str = "") -> str:
    return f"k{k}h{h}{resource}{'_limited' if limited else ''}{suffix}"


def run_case(resource: str, k: int, h: int, *, cap: float = UNCONSTRAINED_CAP,
             random_state: int = 0, results_dir: str | Path = "results", models: list | None = None,
             limited: bool | None = None, suffix: str = "", timeout: float | None = None,
             verbose: bool = False) -> pd.DataFrame:
    """Run one scenario (all four formulations unless ``models`` is given) via ``main.py``.

    The config file is restored afterwards. Returns the rows appended to Simulation_Results.xlsx.
    """
    if limited is None:
        limited = cap < UNCONSTRAINED_CAP
    name = scenario_name(resource, k, h, limited, suffix)
    results_dir = Path(results_dir)
    results_abs = results_dir if results_dir.is_absolute() else REPO / results_dir
    (results_abs / "logs").mkdir(parents=True, exist_ok=True)

    cfg_path = REPO / "config" / "config.yaml"
    original = cfg_path.read_text(encoding="utf-8")
    cfg = yaml.safe_load(original)
    cfg.update(scenario_name=name, resource=resource, n_clusters=int(k), hour_grouping=int(h),
               StorageMaxCapacity=float(cap), random_state=int(random_state))
    cfg["data_8760"]["CF"] = RESOURCES[resource]
    cfg["data_8760"]["SDP"] = DEMAND_PROFILE
    cfg["results"]["directory"] = str(results_dir).replace("\\", "/")
    cfg["results"]["directory_GUI"] = (str(results_dir) + "/GUI").replace("\\", "/")
    cfg["models"] = list(models) if models else MODELS
    log = results_abs / "logs" / f"{name}.log"
    t0 = time.time()
    try:
        cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
        with open(log, "w", encoding="utf-8") as fh:
            proc = subprocess.run([sys.executable, str(MAIN)], cwd=REPO, stdout=fh,
                                  stderr=subprocess.STDOUT, timeout=timeout, env=_child_env())
    finally:
        cfg_path.write_text(original, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(f"{name}: main.py failed (exit {proc.returncode}); see {log}")
    if verbose:
        print(f"{name}: done in {time.time() - t0:.1f} s")
    res = load_results(results_abs / "Simulation_Results.xlsx")
    return res[res["Scenario"] == name]


def run_grid(resources, ks, hs, *, skip_existing: bool = True, **kw) -> pd.DataFrame:
    """Run a grid of scenarios; already-completed scenarios are skipped."""
    results_dir = Path(kw.get("results_dir", "results"))
    xlsx = (results_dir if results_dir.is_absolute() else REPO / results_dir) / "Simulation_Results.xlsx"
    for r in resources:
        for k in ks:
            for h in hs:
                done = load_results(xlsx) if xlsx.exists() else pd.DataFrame(columns=["Scenario", "Model"])
                name = scenario_name(r, k, h, kw.get("cap", UNCONSTRAINED_CAP) < UNCONSTRAINED_CAP,
                                     kw.get("suffix", ""))
                n_models = len(kw.get("models") or MODELS)
                if skip_existing and (done["Scenario"] == name).sum() >= n_models:
                    continue
                run_case(r, k, h, verbose=True, **kw)
    return load_results(xlsx)


# ---------------------------------------------------------------------------------------------
# Results tables
# ---------------------------------------------------------------------------------------------
_SCEN = re.compile(r"^k(?P<k>\d+)h(?P<h>\d+)(?P<resource>WND|SOL|HYD)(?P<limited>_limited)?(?P<suffix>.*)$")


def _seconds(x):
    if isinstance(x, str):
        m = re.search(r"([\d.]+)", x)
        return float(m.group(1)) if m else np.nan
    return float(x)


def load_results(xlsx: str | Path) -> pd.DataFrame:
    """Tidy Simulation_Results.xlsx (one row per scenario x formulation, last run kept)."""
    df = pd.read_excel(xlsx)
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
    if "Matriz and Running Time" in df.columns:          # header spelling of earlier versions
        old = df.pop("Matriz and Running Time")
        df["Matrix and Running Time"] = df["Matrix and Running Time"].fillna(old) \
            if "Matrix and Running Time" in df.columns else old
    parts = df["Scenario"].str.extract(_SCEN)
    df["resource"] = parts["resource"]
    df["k"] = pd.to_numeric(parts["k"])
    df["h"] = pd.to_numeric(parts["h"])
    df["limited"] = parts["limited"].notna()
    df["formulation"] = df["Model"].map(FORMULATION)
    df["total_time_s"] = df["Matrix and Running Time"].map(_seconds)
    df["solve_time_s"] = df["Running time"].map(_seconds)
    df["memory_MB"] = df["Memory used"].map(_seconds)
    return df.drop_duplicates(["Scenario", "Model"], keep="last").reset_index(drop=True)


def add_errors(df: pd.DataFrame) -> pd.DataFrame:
    """Cost and storage-capacity error (%) against the k365h1 Novo benchmark of the same resource.

    Errors use unrounded values. (Table 4 in the paper divides by the benchmark rounded to two
    decimals, which shifts some capacity errors by up to ~3 percentage points.)
    """
    out = []
    for (res, lim), g in df.groupby(["resource", "limited"]):
        b = g[(g.k == 365) & (g.h == 1) & (g.Model == "Model_Cluster")]
        if b.empty:
            b = g[(g.k == 365) & (g.h == 1)]
        if b.empty:
            out.append(g.assign(cost_err_pct=np.nan, cap_err_pct=np.nan))
            continue
        bc, bs = b["Total cost"].iloc[0], b["Storage Capacity"].iloc[0]
        out.append(g.assign(cost_err_pct=100 * (g["Total cost"] / bc - 1),
                            cap_err_pct=100 * (g["Storage Capacity"] / bs - 1)))
    return pd.concat(out, ignore_index=True)


TABLE4_CASES = {"WND": [365, 8, 20], "SOL": [365, 9, 20], "HYD": [365, 7, 20]}


def table4(df: pd.DataFrame) -> pd.DataFrame:
    """Rebuild manuscript Table 4 (h = 1, unconstrained)."""
    d = add_errors(df[~df.limited])
    rows = []
    for res, ks in TABLE4_CASES.items():
        for k in ks:
            sub = d[(d.resource == res) & (d.k == k) & (d.h == 1)]
            for f in ["Niet", "Welsch", "Kotzur", "Novo"]:
                r = sub[sub.formulation == f]
                if r.empty:
                    continue
                r = r.iloc[0]
                rows.append({"Scenario": res, "Case": f"k{k}h1", "Formulation": f,
                             "Total cost": r["Total cost"], "Cost error (%)": r["cost_err_pct"],
                             "Storage capacity (kW·yr)": r["Storage Capacity"],
                             "Capacity error (%)": r["cap_err_pct"],
                             "Runtime (s)": r["total_time_s"], "Memory (MB)": r["memory_MB"]})
    return pd.DataFrame(rows)


def compare_to_archive(new: pd.DataFrame, archive: pd.DataFrame,
                       cols=("Total cost", "Power Capacity", "Storage Capacity")) -> pd.DataFrame:
    """Relative difference between fresh runs and the archived results (same Scenario x Model)."""
    m = new.merge(archive, on=["Scenario", "Model"], suffixes=("_new", "_archive"))
    out = m[["Scenario", "Model"]].copy()
    for c in cols:
        out[f"{c} (new)"] = m[f"{c}_new"]
        out[f"{c} (archive)"] = m[f"{c}_archive"]
        out[f"{c} rel. diff"] = (m[f"{c}_new"] - m[f"{c}_archive"]).abs() / m[f"{c}_archive"].abs()
    return out


# ---------------------------------------------------------------------------------------------
# Clustering and seed robustness
# ---------------------------------------------------------------------------------------------
def clustering(resource: str, k: int, random_state: int = 0):
    """Representative days and chronological day->representative mapping, as used by main.py."""
    from src.cluster import cluster_data
    return cluster_data(TIMESERIES / RESOURCES[resource], TIMESERIES / DEMAND_PROFILE,
                        k, random_state=random_state)


def seed_robustness(resources=("WND", "SOL", "HYD"), ks=K_VALUES, seeds=range(10)) -> pd.DataFrame:
    """Compare clusterings for alternative seeds against seed 0.

    day_agreement: share of the 365 days mapped to the same representative day as with seed 0.
    ARI: adjusted Rand index of the day partition (label-permutation invariant).
    same_rep_days: whether the set of representative days is identical.
    """
    from sklearn.metrics import adjusted_rand_score
    rows = []
    for r in resources:
        for k in ks:
            rep0, seq0 = clustering(r, k, 0)
            for s in seeds:
                if s == 0:
                    continue
                rep, seq = clustering(r, k, s)
                rows.append({"resource": r, "k": k, "seed": s,
                             "day_agreement": float(np.mean(np.array(seq) == np.array(seq0))),
                             "ARI": adjusted_rand_score(seq0, seq),
                             "same_rep_days": rep == rep0})
    return pd.DataFrame(rows)


def phantom_swing(resource: str, k: int, random_state: int = 0) -> dict:
    """Storage swing that Niet's chaining of representative days adds over the actual day order.

    Solver-free diagnostic. In Niet (constraint S2) the representative days are chained in date
    order of the medoid days, and each representative hour's net flow is multiplied by YearSplit,
    so one hour lasts N_c hours, N_c being the number of days in its cluster. Kotzur and Novo follow
    the actual sequence of the 365 days. ``phantom_swing_day_blocks`` repeats each representative
    day N_c times instead, which is how Welsch (one season) orders day types; for wind both
    readings give almost the same swing, for solar they do not (stretching hours breaks the
    day/night cycle). The VRE profile is scaled so that the represented year is energy-neutral;
    curtailment and optimised capacities are ignored.
    """
    demand = pd.read_csv(TIMESERIES / DEMAND_PROFILE).VALUE.to_numpy()[:8760].reshape(365, 24)
    cf = pd.read_csv(TIMESERIES / RESOURCES[resource]).VALUE.to_numpy()[:8760].reshape(365, 24)
    rep, seq = clustering(resource, k, random_state)
    seq = np.asarray(seq)
    n = {r: int((seq == r).sum()) for r in rep}
    a = sum(n[r] * demand[r - 1].sum() for r in rep) / sum(n[r] * cf[r - 1].sum() for r in rep)
    net = {r: a * cf[r - 1] - demand[r - 1] for r in rep}
    swing = lambda x: np.ptp(np.cumsum(x))
    stretched = swing(np.concatenate([n[r] * net[r] for r in rep]))      # Niet S2: hour x N_c
    blocks = swing(np.concatenate([np.tile(net[r], n[r]) for r in rep]))  # Welsch: N_c days in a row
    chrono = swing(np.concatenate([net[r] for r in seq]))                # Kotzur/Novo: actual order
    return {"resource": resource, "k": k, "seed": random_state, "swing_niet": stretched,
            "swing_day_blocks": blocks, "swing_chronological": chrono,
            "phantom_swing": stretched - chrono, "phantom_swing_day_blocks": blocks - chrono}


# ---------------------------------------------------------------------------------------------
# Independent SoC verification
# ---------------------------------------------------------------------------------------------
def run_soc_validation() -> pd.DataFrame:
    proc = subprocess.run([sys.executable, str(SOC_VALIDATION / "run.py")], cwd=REPO,
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          env=_child_env())
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout[-2000:] + proc.stderr[-2000:])
    return pd.read_csv(SOC_VALIDATION / "results" / "summary.csv")


# ---------------------------------------------------------------------------------------------
# Storage trajectories, stress-test statistics and fidelity metrics
# ---------------------------------------------------------------------------------------------
def read_storage(results_dir: str | Path, scenario: str, model: str) -> pd.Series:
    """Native or reconstructed storage level written by main.py.

    model: 'Niet', 'Cluster' (Novo), 'Kotzur' (day starts), 'Kotzur_intraday', 'Welsch' (day-type
    starts) or 'Welsch_intraday'.
    """
    f = Path(results_dir) / f"{scenario}_Storage_Level_Model_{model}.csv"
    d = pd.read_csv(f)
    col = "VALUEACCUMULATED" if "VALUEACCUMULATED" in d.columns else d.columns[-1]
    return d[col].reset_index(drop=True)


def soc_violations(soc, upper: float, lower: float = 0.0, tol: float = 1e-9) -> dict:
    """Count bound violations of a storage trajectory.

    strict: SoC > upper + tol or SoC < lower - tol (physically infeasible states).
    at_or_beyond: SoC >= upper - tol or SoC <= lower + tol (includes states exactly on a bound,
    which are feasible). The paper's '183 h above' for wind equals the at_or_beyond count.
    """
    v = np.asarray(soc, dtype=float)
    above, below = int((v > upper + tol).sum()), int((v < lower - tol).sum())
    at_up = int((v >= upper - tol).sum())
    return {"n": len(v), "max": v.max(), "min": v.min(),
            "above_strict": above, "below_strict": below, "total_strict": above + below,
            "share_strict_pct": 100 * (above + below) / len(v),
            "at_or_above_upper": at_up,
            "total_if_counting_at_bound": at_up + below,
            "share_if_counting_at_bound_pct": 100 * (at_up + below) / len(v)}


def _expand(values, block_hours: int, n: int = 8760) -> np.ndarray:
    return np.repeat(np.asarray(values, dtype=float), block_hours)[:n]


def hourly_trajectory(results_dir, scenario: str, formulation: str, h: int) -> np.ndarray:
    """8760-h storage trajectory used for the fidelity metrics.

    Novo and Kotzur: chronological block series (Kotzur reconstructed), held over each block.
    Welsch: reconstructed series in its native grouped day-type order, as plotted by
    graph_generator.py. Niet: representative blocks held for their year-split duration.
    """
    if formulation == "Novo":
        return _expand(read_storage(results_dir, scenario, "Cluster"), h)
    if formulation == "Kotzur":
        return _expand(read_storage(results_dir, scenario, "Kotzur_intraday"), h)
    if formulation == "Welsch":
        return _expand(read_storage(results_dir, scenario, "Welsch_intraday"), h)
    if formulation == "Niet":
        lvl = read_storage(results_dir, scenario, "Niet").to_numpy()
        js = Path(results_dir) / f"{scenario}_clustering.json"
        if js.exists():
            c = json.loads(js.read_text())
            rep, seq = c["representative_days"], c["chronological_sequence"]
        else:
            m = _SCEN.match(scenario)
            rep, seq = clustering(m["resource"], int(m["k"]))
        b = 24 // h
        hours = np.repeat([seq.count(d) * 24 / b for d in rep], b)
        counts = np.round(np.cumsum(hours)).astype(int)
        counts = np.diff(np.r_[0, counts])
        return np.repeat(lvl, counts)[:8760]
    raise ValueError(formulation)


def rainflow_cycles(series) -> float:
    """Equivalent full cycles by rainflow counting (ASTM E1049-85 three-point method).

    Half cycles count 0.5. Returns the total number of (equivalent full) cycles.
    """
    x = np.asarray(series, dtype=float)
    if len(x) < 3:
        return 0.0
    x = x[np.r_[True, np.diff(x) != 0]]          # drop flat steps
    if len(x) < 3:
        return 0.0
    rev = [x[0]] + [x[i] for i in range(1, len(x) - 1) if (x[i] - x[i - 1]) * (x[i + 1] - x[i]) < 0] + [x[-1]]
    stack, count = [], 0.0
    for p in rev:
        stack.append(p)
        while len(stack) >= 3:
            X, Y = abs(stack[-1] - stack[-2]), abs(stack[-2] - stack[-3])
            if X < Y:
                break
            if len(stack) == 3:
                count += 0.5
                stack.pop(0)
            else:
                count += 1.0
                last = stack.pop()
                stack.pop()
                stack.pop()
                stack.append(last)
    count += 0.5 * (len(stack) - 1)
    return count


def fidelity_metrics(benchmark, test) -> dict:
    b, t = np.asarray(benchmark, float), np.asarray(test, float)
    n = min(len(b), len(t))
    b, t = b[:n], t[:n]
    return {"MAE": float(np.mean(np.abs(t - b))),
            "RMSE": float(np.sqrt(np.mean((t - b) ** 2))),
            "Pearson": float(np.corrcoef(b, t)[0, 1]) if t.std() > 0 and b.std() > 0 else np.nan,
            "rainflow_cycles": rainflow_cycles(t),
            "rainflow_cycles_benchmark": rainflow_cycles(b)}
