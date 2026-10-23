# SoC verification

This folder sits in `validation/soc/`; it uses the package in `src/` and the models in `models/Model_*`.
With the project environment active and `otoole` and `glpsol` on PATH, run:

```console
python validation/soc/run.py
```

The case has four days, A-B-A-B, with four six-hour blocks per day.
The two representative profiles A and B each occur twice; this assignment is specified in `run.py`.
Generation is 1 MW in the first block of A; demand is 1 MW in the first block of B.
Both are zero in the other blocks. The battery starts at 6 MWh, has an energy capacity
of 18 MWh and a power capacity of 1 MW, and has no charging or discharging losses.
Capacities are fixed. Each occurrence of A adds 6 MWh; each occurrence of B removes 6 MWh.

The hand-calculated sequences, omitting successive unchanged states, are:

| Formulation | Temporal representation | SoC (MWh) |
|---|---|---|
| Niet | Representative blocks weighted by two occurrences | 6 -> 18 -> 6 |
| Welsch | Grouped days A-A-B-B | 6 -> 12 -> 18 -> 12 -> 6 |
| Kotzur | Chronological days A-B-A-B | 6 -> 12 -> 6 -> 12 -> 6 |
| Novo (`Model_Cluster`) | Chronological blocks in A-B-A-B | 6 -> 12 -> 6 -> 12 -> 6 |

`inputs_csv` uses MW and MWh. The script divides energy inputs by 96 and multiplies
energy outputs by 96, consistent with temporal weights normalized over the four-day period.
It reuses the project's models and preparation/reconstruction functions, fixing the initial
SoC in generated model copies. The storage equations are unchanged.

`independent_reference.csv` lists the hand-calculated states at block starts:
eight weighted blocks for Niet and sixteen six-hour blocks for the other formulations.
`Point` is an index within each representation, not a shared chronological time.
The Welsch and Kotzur columns refer to their reconstructed trajectories; their native
group/day-start states are also compared with the corresponding entries.

`results/soc_comparison.csv` contains each manual/model pair;
`results/summary.csv` contains the maximum differences. Results are generated when the script runs.
