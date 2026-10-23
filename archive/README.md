# Archive

Superseded material kept for provenance. Nothing in the workflow, the notebook or the
validation reads from this folder.

| Path | What it is | Superseded by |
|---|---|---|
| `Storage_Article/` | Earlier full copy of the project (pre-R2 code, inputs and models) | the repository itself |
| `validation_soc_nested_copy/` | Older duplicate of the SoC verification (top-level imports) | `validation/soc/` |
| `src/Welsch_intraday.py` | First Welsch intraday reconstruction (`intraday_welsch`) | `src/Welsch_intraday2.py` |
| `src/graph_generator_3graphs.py` | Unused three-panel plotting variant | `src/graph_generator.py` |
| `notebooks/playground.ipynb` | Exploratory scratch notebook | `notebooks/reproduce_study.ipynb` |
| `docs/tutorials/` | Tutorial pages *Basic usage*, *Comparative analysis*, *Advanced configuration*, which described functions and options the code does not have | `notebooks/reproduce_study.ipynb` and the workflow pages of the documentation |
| `docs/results_analysis.md`, `docs/QUICK_REFERENCE.md` | Generic results-analysis page (features not in the code) and an empty page | `docs/source/notes/outputs.md` |
| `data_8760_unused/` | Alternative capacity-factor and demand profiles not used in the study | `data/timeseries/` |
| `reverted_2026-10-18/` | Files from commit `4b14ecc` that had reverted the R2 fixes (old `main.py`, `automation.py`, `src` modules, inputs with demand 2.0 / VRE capital cost 999 999 / variable cost 4.167, `README.md`, `pyproject.toml`, `.gitignore`), plus the uncommitted `config.yaml` and `cluster.py` edits at the time of the restore | the restored R2 versions |
