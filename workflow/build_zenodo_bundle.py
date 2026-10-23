"""Build the Zenodo deposit that freezes the study: code, inputs, results and environment.

Output (dist/zenodo/<version>/):
    storage-in-OSeMOSYS-<version>-code.tar.gz       git archive of the release commit (code, models,
                                                    inputs, published results, validation, docs)
    storage-in-OSeMOSYS-<version>-full_results.tar.gz   data/full_archive (all 327 scenarios + stress
                                                    tests: trajectories, figures, Simulation_Results.xlsx)
    environment-lock-linux-64.txt                   `conda list --explicit` of the environment used
    PROVENANCE.md                                   origin of the archived results and checksums of the
                                                    files originally delivered for the manuscript
    SHA256SUMS                                      checksum of every file above
    SHA256SUMS-contents                             checksum of every file inside both tarballs

Tarballs are deterministic (sorted names, fixed mtime/owner, gzip without timestamp), so rebuilding
from the same commit gives byte-identical files.

Usage:
    python workflow/build_zenodo_bundle.py --version v1.1.0 [--env storage_osemosys]
The working tree must be clean (the code tarball is taken from HEAD).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FULL_ARCHIVE = REPO / "data" / "full_archive"
ORIGINALS = REPO / "data" / "ORIGINAL_DELIVERY_SHA256SUMS"   # files delivered for the manuscript
MTIME = 0


def sha256(data_or_path) -> str:
    h = hashlib.sha256()
    if isinstance(data_or_path, (bytes, bytearray)):
        h.update(data_or_path)
    else:
        with open(data_or_path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True).stdout


def deterministic_tar(src: Path, arcroot: str, dest: Path) -> dict[str, str]:
    """tar.gz of src under arcroot/; returns {member path: sha256}."""
    sums = {}
    with open(dest, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=MTIME) as gz, \
            tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for p in sorted(src.rglob("*")):
            if not p.is_file() or p.name.endswith("Zone.Identifier"):
                continue
            name = f"{arcroot}/{p.relative_to(src).as_posix()}"
            data = p.read_bytes()
            info = tarfile.TarInfo(name)
            info.size, info.mtime, info.mode = len(data), MTIME, 0o644
            tar.addfile(info, io.BytesIO(data))
            sums[name] = sha256(data)
    return sums


def code_tar(version: str, dest: Path) -> dict[str, str]:
    """git archive of HEAD, repacked deterministically; returns {member path: sha256}."""
    prefix = f"storage-in-OSeMOSYS-{version}"
    raw = subprocess.run(["git", "archive", "--format=tar", f"--prefix={prefix}/", "HEAD"],
                         cwd=REPO, capture_output=True, check=True).stdout
    sums = {}
    with tarfile.open(fileobj=io.BytesIO(raw)) as src, open(dest, "wb") as out, \
            gzip.GzipFile(fileobj=out, mode="wb", mtime=MTIME) as gz, \
            tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for m in sorted(src.getmembers(), key=lambda m: m.name):
            if not m.isfile():
                continue
            data = src.extractfile(m).read()
            info = tarfile.TarInfo(m.name)
            info.size, info.mtime, info.mode = len(data), MTIME, m.mode
            tar.addfile(info, io.BytesIO(data))
            sums[m.name] = sha256(data)
    return sums


def provenance(version: str, commit: str) -> str:
    lines = [f"# Provenance of the deposit ({version})", "",
             f"Built {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC} from commit `{commit}`.", "",
             "`full_results.tar.gz` contains `data/full_archive/`, the results reported in the manuscript.",
             "Its 3164 files are byte-identical to the contents of `Results_Demand_Variation.zip` delivered",
             "by B. Borba. The contents of `Storage_Article.rar` (earlier project copy) and",
             "`validation_soc.zip` (SoC verification) are in the code tarball under `archive/Storage_Article/`,",
             "`data/` and `validation/soc/`.", "",
             "The current code reproduces the archived costs and capacities; see REPRODUCIBILITY.md",
             "(Section 2) and `workflow/reproducibility_proof.py`. Known deviations of the archive (8 failed",
             "Welsch solves, LP-size offset) are listed in REPRODUCIBILITY.md.", "",
             "## Checksums of the originally delivered files", "", "| File | SHA-256 |", "|---|---|"]
    for line in ORIGINALS.read_text().splitlines():
        if line and not line.startswith("#"):
            digest, name = line.split(maxsplit=1)
            lines.append(f"| `{name}` | `{digest}` |")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--version", required=True, help="release tag, e.g. v1.1.0")
    ap.add_argument("--env", default="storage_osemosys", help="conda environment to lock")
    ap.add_argument("--allow-dirty", action="store_true", help="build although the working tree has changes")
    args = ap.parse_args()

    if git("status", "--porcelain", "--untracked-files=no").strip() and not args.allow_dirty:
        sys.exit("Working tree has uncommitted changes; commit first (the code tarball is taken from HEAD).")
    if not FULL_ARCHIVE.exists():
        sys.exit(f"{FULL_ARCHIVE} not found.")
    commit = git("rev-parse", "HEAD").strip()

    out = REPO / "dist" / "zenodo" / args.version
    out.mkdir(parents=True, exist_ok=True)
    base = f"storage-in-OSeMOSYS-{args.version}"
    members = {}

    print("code tarball ...")
    members.update(code_tar(args.version, out / f"{base}-code.tar.gz"))
    print("full results tarball ...")
    members.update(deterministic_tar(FULL_ARCHIVE, f"{base}-full_results", out / f"{base}-full_results.tar.gz"))

    print("environment lock ...")
    lock = subprocess.run(["conda", "list", "-n", args.env, "--explicit", "--md5"],
                          capture_output=True, text=True, check=True).stdout
    pip = subprocess.run(["conda", "run", "-n", args.env, "python", "-m", "pip", "freeze"],
                         capture_output=True, text=True, check=True).stdout
    (out / "environment-lock-linux-64.txt").write_text(lock + "\n# pip freeze\n" + "".join(f"# {l}\n" for l in pip.splitlines()))
    (out / "PROVENANCE.md").write_text(provenance(args.version, commit))

    # both files work with `sha256sum -c` (the second after unpacking the tarballs)
    with open(out / "SHA256SUMS-contents", "w") as fh:
        for name, h in sorted(members.items()):
            fh.write(f"{h}  {name}\n")
    top = {p.name: sha256(p) for p in sorted(out.iterdir()) if p.name != "SHA256SUMS"}
    with open(out / "SHA256SUMS", "w") as fh:
        for name, h in top.items():
            fh.write(f"{h}  {name}\n")
    for p in sorted(out.iterdir()):
        print(f"  {p.stat().st_size / 1e6:9.1f} MB  {p.relative_to(REPO)}")


if __name__ == "__main__":
    main()
