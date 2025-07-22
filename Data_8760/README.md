# Data_8760 Directory

## Overview

The `Data_8760` directory contains time-series data files for full hourly resolution modeling (8760 hours = 365 days × 24 hours) used by OSeMOSYS model. This directory serves as the baseline temporal resolution for comparison with clustered temporal methods.

## File Structure

The directory contains **11 CSV files** with hourly time-series data:

### Capacity Factor Files

#### Technology-Specific Capacity Factors
- **`CapacityFactor_Wind.csv`** - Wind power capacity factors (hourly resolution)
- **`CapacityFactor_Solar.csv`** - Solar PV capacity factors (hourly resolution)
- **`CapacityFactor_Hydro.csv`** - Hydroelectric capacity factors (hourly resolution)

#### Aggregated Capacity Factors
- **`CapacityFactor.csv`** - Combined capacity factors for all technologies (hourly resolution)
- **`CapacityFactor1.csv`** to **`CapacityFactor5.csv`** - Multiple capacity factor scenarios (hourly resolution)

### Demand Profile Files
- **`SpecifiedDemandProfile.csv`** - Hourly electricity demand profile (hourly resolution)
- **`SpecifiedDemandProfile2.csv`** - Alternative demand scenario (hourly resolution)

## Data Format

All files follow the standard OSeMOSYS CSV format:

```csv
REGION,TECHNOLOGY/FUEL,TIMESLICE,YEAR,VALUE
```

### Column Descriptions

- **REGION**: Geographic region identifier (e.g., "Simplicity2")
- **TECHNOLOGY**: Technology type (e.g., "WINDPOWER") for capacity factors
- **FUEL**: Energy carrier (e.g., "ELECTRICITY") for demand profiles  
- **TIMESLICE**: Hour index (1 to 8760)
- **YEAR**: Model year (e.g., 2010)
- **VALUE**: Normalized value (0-1 for capacity factors, demand fraction for profiles)


### Technology Profiles

#### Wind Power
- **High variability**: Values range from ~0.1 to ~0.95
- **Realistic wind patterns**: Captures diurnal and seasonal variations
- **Sample values**: 0.937, 0.855, 0.720 (showing wind intermittency)

#### Solar Power  
- **Diurnal pattern**: Zero values during nighttime hours (1-8)
- **Daylight generation**: Non-zero values during daylight hours
- **Sample progression**: 0.0 → 0.0 → 0.02 (sunrise pattern)

#### Hydroelectric
- **Stable output**: Relatively constant around 0.108
- **Low variability**: Consistent baseload characteristics
- **Seasonal patterns**: May reflect water availability variations

#### Electricity Demand
- **Normalized demand**: Values around 0.0001 (10⁻⁴)
- **Load variations**: Captures daily demand cycles
- **Peak/off-peak**: Shows typical electrical load patterns

## Usage in Storage-in-OSeMOSYS

### Baseline Reference
- **Full resolution modeling**: Used as ground truth for accuracy comparison
- **Clustering validation**: Reference for evaluating temporal clustering methods
- **Storage analysis**: Captures detailed storage operation requirements

### Computational Considerations
- **Large model size**: 8760 time slices create large optimization problems
- **Memory intensive**: Requires significant computational resources
- **Accurate representation**: Provides most detailed temporal dynamics

### Integration with Temporal Methods

1. **Kotzur Method**: Uses this data to identify representative periods
2. **Niet Method**: Statistical analysis of these profiles for clustering
3. **Welsch Method**: Selects representative days from this dataset
4. **8760 Method**: Uses this data directly without clustering

## File Relationships

### Primary vs. Alternative Scenarios
- **CapacityFactor.csv**: Main renewable energy scenario
- **CapacityFactor_[Technology].csv**: Technology-specific profiles
- **CapacityFactor[1-5].csv**: Alternative scenarios for sensitivity analysis

### Demand Variations
- **SpecifiedDemandProfile.csv**: Base case demand pattern
- **SpecifiedDemandProfile2.csv**: Alternative demand scenario

## Data Quality and Validation

### Completeness
- ✅ **Full annual coverage**: 8760 hourly values
- ✅ **No missing data**: Complete time series
- ✅ **Consistent format**: Standardized CSV structure

### Physical Constraints
- ✅ **Capacity factors**: Values between 0 and 1
- ✅ **Energy balance**: Demand profiles sum to annual demand
- ✅ **Temporal continuity**: Sequential hourly data

### Realistic Patterns
- ✅ **Diurnal cycles**: Daily patterns in solar and demand
- ✅ **Seasonal variations**: Annual weather patterns
- ✅ **Technology characteristics**: Appropriate profiles for each technology

## Best Practices

### When to Use 8760-Hour Data
- **Detailed storage studies**: When storage dynamics are critical
- **Accuracy validation**: Benchmarking temporal clustering methods  
- **Research applications**: Academic studies requiring high temporal resolution
- **Small systems**: When computational resources allow full resolution

### Performance Optimization
- **Memory management**: Monitor RAM usage for large models
- **Solver selection**: Use high-performance solvers while available (Gurobi), however we have used glpk as an open-source alternative.
- **Parallel processing**: Leverage multi-core systems

## Related Files

This directory works in conjunction with:
- **`inputs_csv/`**: Static technology and economic parameters
- **`Model_*/`**: OSeMOSYS model files for different temporal methods
- **`Results/`**: Output analysis and storage results
- **`src/`**: Python modules for data processing and analysis

## Technical Notes

- **Leap year handling**: Files may contain 8761 or 8762 rows depending on year
- **Time zone**: Data assumed to be in consistent time zone
- **Units**: Capacity factors are dimensionless (0-1), demand is normalized
- **Interpolation**: Hourly values assumed to represent hourly averages

This high-resolution dataset enables comprehensive analysis of energy storage systems with detailed temporal dynamics while serving as the foundation for validating computationally efficient temporal clustering approaches.
