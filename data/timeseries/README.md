# Hourly time series (`data/timeseries`)

Hourly input profiles of the study (8760 hours, year 2010, region `Simplicity2`). This directory
was called `Data_8760` in earlier versions. Unused alternative profiles (`CapacityFactor.csv`,
`CapacityFactor1-5.csv`, `SpecifiedDemandProfile2.csv`) are in `archive/data_8760_unused/`.

| File | Used for | Range | Annual mean |
|---|---|---|---|
| `CapacityFactor_Wind.csv` | WND system | 0.010 – 0.939 | 0.524 |
| `CapacityFactor_Solar.csv` | SOL system (4433 hours at zero) | 0 – 0.941 | 0.184 |
| `CapacityFactor_Hydro.csv` | HYD system | 0.107 – 1.000 | 0.307 |
| `SpecifiedDemandProfile.csv` | all three systems | 1e-4 – 2e-4 | sums to 1 |

## Format

Standard otoole CSV, one row per hour:

```csv
REGION,TECHNOLOGY,TIMESLICE,YEAR,VALUE      # capacity factors
REGION,FUEL,TIMESLICE,YEAR,VALUE            # demand profile (FUEL = ELECTRICITY)
```

`TIMESLICE` runs from 1 to 8760. All three capacity-factor files use the technology label
`WINDPOWER`, so the same system inputs (`data/system/`) serve every resource; the label is set by
`vre_technology` in `config/config.yaml`.

## How the workflow uses them

`workflow/main.py` reads the profile named by `data_8760.CF` and `data_8760.SDP` in
`config/config.yaml` (the notebook and `workflow/automation.py` set `CF` from the resource:
WND, SOL or HYD). The daily profiles are clustered into k representative days (`src/cluster.py`);
within each block of h hours the capacity factor is averaged and the demand share is summed and
renormalised (`src/update_CFandSDP.py`). The results are written as `CapacityFactor`,
`SpecifiedDemandProfile` and the timeslice sets of each formulation. With k = 365 and h = 1 the full hourly year is used, which is
the benchmark for all aggregated runs.
