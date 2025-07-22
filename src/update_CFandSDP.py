import pandas as pd

#Funtion to reduce CapacityFactor and SpecifiedDemandProfile
def CFandSDP(input_file, representative_days, hour_grouping, output_file, operation='mean'):
    # Load the data from the CSV file
    df = pd.read_csv(input_file)
    # Calculate the time slices for the representative days
    intervals = [((day - 1) * 24 + 1, day * 24) for day in representative_days]
    # Filter the data for only the time slices of the representative days
    filtered_df = pd.concat([df[(df['TIMESLICE'] >= start) & (df['TIMESLICE'] <= end)] for start, end in intervals])
    # Add a 'Day' column to correctly separate the data by day
    filtered_df['Day'] = ((filtered_df['TIMESLICE'] - 1) // 24) + 1
    # Create an 'Hour_Group' identifier for each record
    filtered_df['Hour_Group'] = ((filtered_df['TIMESLICE'] - 1) % 24 // hour_grouping) + 1
    
    # Apply the specified operation: mean or sum
    if operation == 'sum':
        group_columns = ['REGION', 'FUEL', 'YEAR', 'Day', 'Hour_Group']
        value_column = 'VALUE'
        final_columns = ['REGION', 'FUEL', 'TIMESLICE', 'YEAR', 'VALUE']
    else:
        group_columns = ['REGION', 'TECHNOLOGY', 'YEAR', 'Day', 'Hour_Group']
        value_column = 'VALUE'
        final_columns = ['REGION', 'TECHNOLOGY', 'TIMESLICE', 'YEAR', 'VALUE']
    
    # Perform the operation on the grouped data
    grouped_df = filtered_df.groupby(group_columns, as_index=False)[value_column].agg(operation)
    
    # Normalizar os valores somente se a operação for 'sum'
    if operation == 'sum':
        total_sum = grouped_df[value_column].sum()
        grouped_df[value_column] = grouped_df[value_column] / total_sum
    
    # Remove the 'Day' and 'Hour_Group' columns and assign a new sequential time slice number
    grouped_df['TIMESLICE'] = range(1, grouped_df.shape[0] + 1)
    # Select and reorder the final columns
    final_df = grouped_df[final_columns]
    # Save the processed data to a CSV file
    final_df.to_csv(output_file, index=False)
    # Return the path to the saved CSV file
    return output_file