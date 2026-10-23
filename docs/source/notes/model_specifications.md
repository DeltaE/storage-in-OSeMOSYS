# Model Specifications

## Test system

All runs use the same single-node OSeMOSYS system, defined in `data/system/`:

| Element | Value |
|---|---|
| Region, year | `Simplicity2`, one model year (2010) |
| Fuel | `ELECTRICITY`, annual demand 20, shaped by the hourly profile in `data/timeseries/SpecifiedDemandProfile.csv` |
| VRE technology | `WINDPOWER` (the label is the same for all three systems; only the capacity-factor profile changes: wind, solar or hydro) |
| Storage | `BATTERY`, charged and discharged by the technology `BATTERY_STORAGE` (mode 1 charges, mode 2 discharges) |
| Storage cost and life | `CapitalCostStorage` 1000 per kW·yr, `OperationalLifeStorage` 1 year, `MinStorageCharge` 0 (otoole defaults) |
| Residual storage | 0.05 kW·yr (`ResidualStorageCapacity` in `config/config.yaml`) |
| Storage energy cap | 1000 kW·yr (non-binding) in the main runs; 0.2 kW·yr in the stress test |

The initial state of charge is a decision variable: `StorageLevelStart` in `config/config.yaml` is
not applied. All values are listed with their source in step 2 of the reproduction notebook.

## Formulations and model files

Each formulation has its own folder in `models/` with an OSeMOSYS model file and an otoole
configuration template. They share the rest of OSeMOSYS and differ only in the time sets and the
storage equations.

| Formulation | Folder | Extra time sets / mappings | SoC equation | Bounds |
|---|---|---|---|---|
| Niet | `models/Model_Niet` | none beyond `TIMESLICE` | `S2_StorageLevelTSStart` over representative time slices, weighted by `YearSplit` | `SC1`, `SC2` at each time slice |
| Welsch | `models/Model_Welsch` | `SEASON`, `DAYTYPE`, `DAILYTIMEBRACKET`, `DaysInDayType`, `Conversionls/ld/lh` | `S5`–`S15` (season, day-type start and finish) | `SC1`–`SC4` at the first and last day-type instances |
| Kotzur | `models/Model_Kotzur` | `DAYSCRO` (365 chronological days), `Conversionldc` | `S2_StorageLevelDayTypeFinish`, `S3_StorageLevelChronoDayStart` | `SC1`, `SC2` at each chronological day |
| Novo | `models/Model_Cluster` | `TIMESLICECRO` (365 × 24/h blocks), `Conversionlts` | `S2_StorageLevelTSStart` over chronological blocks | `SC1`, `SC2` at each chronological block |

All four require the storage to end the year where it started (a refilling constraint: `SC8` in
Niet and Novo, `SC4` in Kotzur, `S15` in Welsch) and cap the total storage capacity at
`StorageMaxCapacity` (`SC3`, or `SC7` in Welsch). See
{doc}`about_storage_algorithms` for what these differences mean in practice.

## How the inputs are generated

`workflow/main.py` writes the time sets and mappings each formulation needs into
`models/Model_<name>/inputs_csv/` (generated, not tracked), copies the shared parameters from
`data/system/`, and converts everything to a GLPK data file with otoole. Run-specific values
(`DaySplit`, `YearSplit`, `StorageMaxCapacity`, `ResidualStorageCapacity`) go into a temporary
`otoole_config_<name>.run.yaml`, so the templates in `models/` never change. The steps are
described in {doc}`workflow_guide`.

## Solver

GLPK 5.0 (`glpsol`). If GLPK reports a non-optimal result, the run is retried with `--nopresol`,
`--dual` and `--exact`; failed solves are recorded with status `FAILED` and no capacities.
