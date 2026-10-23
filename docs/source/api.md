# API

<p class="page-intro">
All the modelling code lives in the <code>src</code> package. Running the study does not
require it, because <code>python workflow/main.py</code> calls everything. This section is for
reusing one step of the method in other work, or for seeing exactly how a step in the paper is
written in code. The cards lead to the reference; the guide below explains how it can be put to
use.
</p>

<div class="section-cards">
  <a class="section-card section-card--map" href="notes/api_reference.html">
    <span class="section-card__head">
      <span class="section-card__icon" aria-hidden="true"></span>
      <span class="section-card__step">Overview</span>
    </span>
    <span class="section-card__title">Module overview</span>
    <span class="section-card__text">What each module does, with examples and the full workflow in one script.</span>
  </a>
  <a class="section-card section-card--battery" href="autoapi/src/cluster/index.html">
    <span class="section-card__head">
      <span class="section-card__icon" aria-hidden="true"></span>
      <span class="section-card__step">Method</span>
    </span>
    <span class="section-card__title">Representative days</span>
    <span class="section-card__text"><code>src.cluster</code>: k-means clustering that picks the typical days.</span>
  </a>
  <a class="section-card section-card--repeat" href="autoapi/src/reproduce/index.html">
    <span class="section-card__head">
      <span class="section-card__icon" aria-hidden="true"></span>
      <span class="section-card__step">Study</span>
    </span>
    <span class="section-card__title">Reproduce helpers</span>
    <span class="section-card__text"><code>src.reproduce</code>: run scenarios, load results and rebuild the paper's tables.</span>
  </a>
  <a class="section-card section-card--api" href="autoapi/src/index.html">
    <span class="section-card__head">
      <span class="section-card__icon" aria-hidden="true"></span>
      <span class="section-card__step">Reference</span>
    </span>
    <span class="section-card__title">Full reference</span>
    <span class="section-card__text">Every module and function in <code>src</code>, generated from the source code.</span>
  </a>
</div>

## How to use this section

**1. Locate the step of interest.** Each module does one step of the method, so the reference
reads like the method section of the paper:

| Step in the study | Module | What it provides |
| --- | --- | --- |
| Pick representative days | `src.cluster` | `cluster_data()` groups the 365 days with k-means and returns the chosen days plus a day-by-day map of which representative day stands in for each real day |
| Shrink the hourly data | `src.update_CFandSDP` | `CFandSDP()` keeps only the representative days and averages (or sums) hours into blocks |
| Build the time structure | `src.update_yearsplit`, `src.update_conversion*`, `src.update_daysindaytype` | The OSeMOSYS time-slice sets and weights each storage formulation needs |
| Rebuild the intra-day SoC | `src.Kotzur_intraday`, `src.Welsch_intraday2` | Turns the solved Kotzur and Welsch storage levels into a SoC series for every time block of the year |
| Solve and collect | `src.simulation`, `src.table_generator` | Runs GLPK and writes cost, capacity and runtime to `Simulation_Results.xlsx` |
| Reproduce the paper | `src.reproduce` | `run_case()`, `load_results()`, `add_errors()`, `table4()` for scripted scenario sweeps |

**2. Call it from a script.** The functions take file paths and plain Python values, so any one
of them can be used without the rest. For example, the clustering can be applied to other wind and
demand profiles to see which representative days it picks:

```python
from src.cluster import cluster_data

days, sequence = cluster_data("my_wind_cf.csv", "my_demand.csv", n_clusters=8, random_state=0)
print(days)          # the 8 representative days
print(sequence[:7])  # which representative day stands in for each day of the first week
```

Similarly, one scenario of the study can be rerun with all four formulations, returning a table:

```python
from src.reproduce import run_case

df = run_case("WND", k=8, h=1)
print(df[["Model", "Total cost", "Storage Capacity"]])
```

**3. Use it as a reference for other models.** For work in another framework, the modules
are a compact recipe: how many representative days to use, how to weight them, and how each
formulation links storage across days. Reading `src.update_yearsplit` and the `update_conversion*`
modules next to {doc}`notes/about_storage_algorithms` shows exactly what each formulation adds to a
model, which can then be ported to another tool.

```{toctree}
:hidden:
:maxdepth: 2

notes/api_reference
autoapi/src/index
```
