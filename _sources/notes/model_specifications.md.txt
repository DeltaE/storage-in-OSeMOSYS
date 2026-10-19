# Model Specifications

## Overview

This section provides detailed specifications for the Storage-in-OSeMOSYS models.

## OSeMOSYS Integration

Storage-in-OSeMOSYS builds upon the Open Source Energy Modelling System (OSeMOSYS) framework to provide advanced storage modeling capabilities.

### Model Variants

The framework supports four different temporal clustering approaches:

1. **Kotzur Method** - Advanced temporal clustering using machine learning techniques
2. **Niet Method** - Statistical clustering approach for representative periods
3. **Welsch Method** - Time series aggregation with optimization
4. **8760 Hours** - Full year hourly resolution (no clustering)

## Storage Technologies

### Storage Parameters

- **StorageLevelStart** - Initial storage level at the beginning of each time slice
- **StorageMaxChargeRate** - Maximum charging rate for storage technologies
- **StorageMaxDischargeRate** - Maximum discharging rate for storage technologies
- **StorageLevelSeasonEnd** - Storage level at the end of each season

### Storage Constraints

The model implements various constraints to ensure realistic storage operation:

- Energy balance constraints
- Charging/discharging rate limits
- Storage capacity constraints
- Seasonal storage carryover

## Technical Implementation

### Model Files

- `osemosys_fast_Kotzur.txt` - Kotzur method implementation
- `osemosys_fast_Niet.txt` - Niet method implementation  
- `osemosys_fast_Welsch.txt` - Welsch method implementation
- OSeMOSYS base model files for 8760-hour resolution

### Data Processing

The framework uses OtoOle for data conversion between different formats:
- Excel to CSV conversion
- CSV to datafile generation
- Result processing and analysis

## Future Development

This section will be expanded with:
- Detailed mathematical formulations
- Parameter sensitivity analysis
- Validation case studies
- Performance benchmarking results
