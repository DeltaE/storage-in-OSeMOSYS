"""Reproducibility proof: save one reference instance of the workflow, then show that a fresh run of
workflow/main.py reproduces it.

The instance is one scenario (default: the scenario in config/config.yaml, k4h1WND) solved with all
four formulations. It is stored in validation/reference_instance/<scenario>/:

    manifest.json   scenario settings, environment, git commit, SHA-256 of every generated input
    inputs/         per formulation: the otoole datafile passed to glpsol (the complete LP data)
                    and the run copy of the otoole config
    results/        clustering, summary table (LP size, cost, capacities, status) and the
                    storage-level trajectories written by main.py

Usage, from anywhere:
    python workflow/reproducibility_proof.py --save      # run main.py and store the reference instance
    python workflow/reproducibility_proof.py             # run main.py again and compare with it

The check writes results/proof/<scenario>/reproducibility_report.md and exits with status 1 if any
check fails. It also compares the run with the published archive (data/published_results/main).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import numpy as np
import pandas as pd
import yaml

import src.reproduce as rp

REFERENCE_ROOT = REPO / "validation" / "reference_instance"
PROOF_ROOT = REPO / "results" / "proof"
ARCHIVE_XLSX = REPO / "data" / "published_results" / "main" / "Simulation_Results.xlsx"

SUMMARY_COLS = ["Scenario", "Model", "Number of constraints", "Number of variables",
                "Non-zero elements in the matrix", "Total cost", "Power Capacity",
                "Storage Capacity", "Solver status"]
LP_SIZE_COLS = ["Number of constraints", "Number of variables", "Non-zero elements in the matrix"]
VALUE_COLS = ["Total cost", "Power Capacity", "Storage Capacity"]
TRAJECTORIES = ["Niet", "Welsch", "Welsch_intraday", "Kotzur", "Kotzur_intraday", "Cluster"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True)
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=REPO, capture_output=True, text=True)
        return out.stdout.strip() + ("-dirty" if dirty.stdout.strip() else "")
    except OSError:
        return None


def scenario_from_config() -> dict:
    cfg = yaml.safe_load((REPO / "config" / "config.yaml").read_text(encoding="utf-8"))
    return {"scenario": cfg["scenario_name"], "resource": cfg["resource"], "k": int(cfg["n_clusters"]),
            "h": int(cfg["hour_grouping"]), "cap": float(cfg["StorageMaxCapacity"]),
            "random_state": int(cfg.get("random_state", 0))}


def run_instance(spec: dict) -> Path:
    """Solve the instance through workflow/main.py into an empty results/proof/<scenario> folder."""
    out = PROOF_ROOT / spec["scenario"]
    shutil.rmtree(out, ignore_errors=True)   # Simulation_Results.xlsx is appended to, so start clean
    out.mkdir(parents=True)
    print(f"Running workflow/main.py for {spec['scenario']} (all four formulations) ...")
    rp.run_case(spec["resource"], spec["k"], spec["h"], cap=spec["cap"],
                random_state=spec["random_state"], results_dir=out.relative_to(REPO), verbose=True)
    return out


def generated_inputs() -> dict:
    """SHA-256 of every file main.py generated for each formulation (CSV inputs and otoole datafile)."""
    cfg = yaml.safe_load((REPO / "config" / "config.yaml").read_text(encoding="utf-8"))
    hashes = {}
    for model, case in cfg["cases"].items():
        root = REPO / case["root_directory"]
        files = sorted((root / case["input_otoole_csv"]["directory"]).glob("*.csv"))
        files.append(root / case["output_otoole_txt"])
        hashes[model] = {str(f.relative_to(root)).replace("\\", "/"): sha256(f) for f in files}
    return hashes


def summary(results_dir: Path) -> pd.DataFrame:
    res = rp.load_results(results_dir / "Simulation_Results.xlsx")
    return res[SUMMARY_COLS].sort_values("Model").reset_index(drop=True)


# ---------------------------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------------------------
def save(spec: dict) -> None:
    run_dir = run_instance(spec)
    name = spec["scenario"]
    ref = REFERENCE_ROOT / name
    shutil.rmtree(ref, ignore_errors=True)
    (ref / "inputs").mkdir(parents=True)
    (ref / "results").mkdir()

    cfg = yaml.safe_load((REPO / "config" / "config.yaml").read_text(encoding="utf-8"))
    for model, case in cfg["cases"].items():
        root = REPO / case["root_directory"]
        dest = ref / "inputs" / model
        dest.mkdir()
        shutil.copy(root / case["output_otoole_txt"], dest)
        shutil.copy(root / f"{Path(case['otoole_config']).stem}.run.yaml", dest)

    shutil.copy(run_dir / f"{name}_clustering.json", ref / "results")
    for t in TRAJECTORIES:
        shutil.copy(run_dir / f"{name}_Storage_Level_Model_{t}.csv", ref / "results")
    summary(run_dir).to_csv(ref / "results" / "summary.csv", index=False)

    env = rp.check_environment()
    manifest = {"instance": spec,
                "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "git_commit": git_commit(),
                "platform": platform.platform(),
                "environment": dict(zip(env["component"], env["installed"])),
                "generated_inputs_sha256": generated_inputs(),
                "reference_files_sha256": {str(p.relative_to(ref)).replace("\\", "/"): sha256(p)
                                           for p in sorted(ref.rglob("*")) if p.is_file()}}
    (ref / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Reference instance saved to {ref.relative_to(REPO)}")


# ---------------------------------------------------------------------------------------------
# Check
# ---------------------------------------------------------------------------------------------
def rel_diff(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-12)))


def check(spec: dict, rtol: float, atol: float) -> bool:
    name = spec["scenario"]
    ref = REFERENCE_ROOT / name
    manifest = json.loads((ref / "manifest.json").read_text(encoding="utf-8"))
    rows = []   # (check, detail, passed)

    for p, digest in manifest["reference_files_sha256"].items():
        if sha256(ref / p) != digest:
            rows.append((f"reference file intact: {p}", "SHA-256 changed since --save", False))

    env = rp.check_environment()
    installed = dict(zip(env["component"], env["installed"]))
    for comp, v in manifest["environment"].items():
        rows.append((f"environment: {comp}", f"reference {v}, now {installed.get(comp)}",
                     installed.get(comp) == v))

    run_dir = run_instance(spec)

    # 1. clustering: identical representative days and day mapping
    new_cl = json.loads((run_dir / f"{name}_clustering.json").read_text(encoding="utf-8"))
    ref_cl = json.loads((ref / "results" / f"{name}_clustering.json").read_text(encoding="utf-8"))
    for key in ["representative_days", "chronological_sequence"]:
        rows.append((f"clustering: {key}", "identical" if new_cl[key] == ref_cl[key] else "differs",
                     new_cl[key] == ref_cl[key]))

    # 2. generated model inputs: byte-identical
    new_hash = generated_inputs()
    for model, files in manifest["generated_inputs_sha256"].items():
        bad = [f for f, d in files.items() if new_hash.get(model, {}).get(f) != d]
        rows.append((f"inputs {model}: {len(files)} files byte-identical",
                     "all identical" if not bad else "differ: " + ", ".join(bad), not bad))

    # 3. solver results: status, LP size exact, objective and capacities within rtol
    new_s = summary(run_dir).set_index("Model")
    ref_s = pd.read_csv(ref / "results" / "summary.csv").set_index("Model")
    for model in ref_s.index:
        if model not in new_s.index:
            rows.append((f"results {model}", "missing from fresh run", False))
            continue
        n, r = new_s.loc[model], ref_s.loc[model]
        rows.append((f"results {model}: solver status", f"{n['Solver status']}",
                     n["Solver status"] == r["Solver status"] == "optimal"))
        lp_ok = all(int(n[c]) == int(r[c]) for c in LP_SIZE_COLS)
        rows.append((f"results {model}: LP size", f"{int(n[LP_SIZE_COLS[0]])} rows, "
                     f"{int(n[LP_SIZE_COLS[1]])} cols, {int(n[LP_SIZE_COLS[2]])} nonzeros", lp_ok))
        for c in VALUE_COLS:
            d = rel_diff(n[c], r[c])
            rows.append((f"results {model}: {c}", f"{n[c]:.10g} (rel. diff {d:.1e})", d <= rtol))

    # 4. storage trajectories
    for t in TRAJECTORIES:
        a = rp.read_storage(run_dir, name, t).to_numpy(float)
        b = rp.read_storage(ref / "results", name, t).to_numpy(float)
        if a.shape != b.shape:
            rows.append((f"SoC {t}", f"length {a.size} vs {b.size}", False))
            continue
        d = float(np.max(np.abs(a - b))) if a.size else 0.0
        rows.append((f"SoC {t}: {a.size} values", f"max abs diff {d:.1e}", d <= atol))

    # 5. published archive (the numbers in the paper), if the scenario is archived there
    arch = rp.load_results(ARCHIVE_XLSX)
    arch = arch[arch["Scenario"] == name].set_index("Model")
    for model in arch.index.intersection(new_s.index):
        for c in VALUE_COLS:
            d = rel_diff(new_s.loc[model, c], arch.loc[model, c])
            rows.append((f"published archive {model}: {c}", f"rel. diff {d:.1e}", d <= rtol))

    # environment differences are reported but do not fail the proof on their own
    passed = all(ok for chk, _, ok in rows if not chk.startswith("environment"))
    write_report(run_dir, spec, manifest, rows, passed, rtol, atol)
    return passed


def write_report(run_dir: Path, spec: dict, manifest: dict, rows: list, passed: bool,
                 rtol: float, atol: float) -> None:
    env = rp.check_environment()
    lines = [f"# Reproducibility proof: {spec['scenario']}", "",
             f"**Result: {'PASS' if passed else 'FAIL'}**", "",
             f"- Reference: `validation/reference_instance/{spec['scenario']}` saved "
             f"{manifest['created_utc']} at commit `{manifest['git_commit']}` on {manifest['platform']}",
             f"- This run: {datetime.now(timezone.utc).isoformat(timespec='seconds')} at commit "
             f"`{git_commit()}` on {platform.platform()}",
             f"- Environment now: " + ", ".join(f"{c} {v}" for c, v in zip(env['component'], env['installed'])),
             f"- Tolerances: relative {rtol:g} for cost and capacities, absolute {atol:g} kW·yr for SoC", "",
             "| Check | Detail | Pass |", "|---|---|---|"]
    lines += [f"| {c} | {d} | {'yes' if ok else '**no**'} |" for c, d, ok in rows]
    report = run_dir / "reproducibility_report.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    pd.DataFrame(rows, columns=["check", "detail", "pass"]).to_csv(run_dir / "reproducibility_report.csv", index=False)
    failed = [c for c, _, ok in rows if not ok]
    print(f"\n{'PASS' if passed else 'FAIL'}: {len(rows) - len(failed)}/{len(rows)} checks passed")
    for c in failed:
        print(f"  not passed: {c}")
    print(f"Report: {report.relative_to(REPO)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--save", action="store_true", help="run main.py and store the reference instance")
    ap.add_argument("--scenario", help="reference instance to check (default: scenario in config/config.yaml)")
    ap.add_argument("--rtol", type=float, default=1e-9, help="relative tolerance, cost and capacities")
    ap.add_argument("--atol", type=float, default=1e-9, help="absolute tolerance, SoC trajectories (kW·yr)")
    args = ap.parse_args()

    if args.save:
        save(scenario_from_config())
        return
    name = args.scenario or scenario_from_config()["scenario"]
    manifest_path = REFERENCE_ROOT / name / "manifest.json"
    if not manifest_path.exists():
        sys.exit(f"No reference instance {manifest_path.relative_to(REPO)}; create it with --save")
    spec = json.loads(manifest_path.read_text(encoding="utf-8"))["instance"]
    sys.exit(0 if check(spec, args.rtol, args.atol) else 1)


if __name__ == "__main__":
    main()
