src
===

.. py:module:: src


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/src/Kotzur_intraday/index
   /autoapi/src/Welsch_intraday/index
   /autoapi/src/Welsch_intraday2/index
   /autoapi/src/cluster/index
   /autoapi/src/copy_rename_csv/index
   /autoapi/src/graph_generator/index
   /autoapi/src/graph_generator_3graphs/index
   /autoapi/src/read_csv/index
   /autoapi/src/simulation/index
   /autoapi/src/table_generator/index
   /autoapi/src/update_CFandSDP/index
   /autoapi/src/update_conversionld/index
   /autoapi/src/update_conversionldc/index
   /autoapi/src/update_conversionlh/index
   /autoapi/src/update_conversionlts/index
   /autoapi/src/update_daysindaytype/index
   /autoapi/src/update_list/index
   /autoapi/src/update_params_yaml_otoole/index
   /autoapi/src/update_yearsplit/index
   /autoapi/src/utilities/index


Functions
---------

.. autoapisummary::

   src.cluster_data
   src.new_list
   src.CFandSDP
   src.conversionlts
   src.conversionld
   src.conversionlh
   src.conversionldc
   src.yearsplit
   src.daysindaytype
   src.new_yaml_param
   src.run_simulation
   src.copy_and_rename
   src.intraday_kotzur
   src.intraday_welsch
   src.intraday_welsch2
   src.read_csvfile
   src.graph
   src.table


Package Contents
----------------

.. py:function:: cluster_data(capacity_factor_path, demand_profile_path, n_clusters)

.. py:function:: new_list(length: int, output_file: str | pathlib.Path)

   Generates a list of integers from 1 to the specified length, saves it as a CSV file, and returns the output file path. Used to update timeslice and daytype.

   :param length: The number of integers to include in the list.
   :type length: int
   :param output_file: The file path where the CSV will be saved.
   :type output_file: str

   :returns: The path to the output CSV file.
   :rtype: str

   The generated CSV will contain a single column named 'VALUE' with integers from 1 to 'length' (inclusive).



.. py:function:: CFandSDP(input_file, representative_days, hour_grouping, output_file, operation='mean')

.. py:function:: conversionlts(blocks_per_day, chronological_timeslices, timeslices, chronological_sequence, representative_days, output_file)

.. py:function:: conversionld(timeslices, representative_days, output_file, label='DAYTYPE')

.. py:function:: conversionlh(timeslices, blocksperday, output_file)

.. py:function:: conversionldc(chronological_sequence, representative_days, days_in_year, output_file)

.. py:function:: yearsplit(timeslices, representative_days, chronological_sequence, days_in_year, output_file)

.. py:function:: daysindaytype(representative_days, chronological_sequence, output_file)

.. py:function:: new_yaml_param(yaml_file, param_name, new_value)

.. py:function:: run_simulation(case_info)

.. py:function:: copy_and_rename(results_case, results_destination_folder, new_results_filename)

.. py:function:: intraday_kotzur(conversion_path, storage_path, storage_level_start, output_path)

.. py:function:: intraday_welsch(storage_path, blocksperday, timeslices, representative_days, output_path)

.. py:function:: intraday_welsch2(storage_path, blocksperday, timeslices, representative_days, chronological_sequence, storage_level_start, output_path)

.. py:function:: read_csvfile(path)

.. py:function:: graph(file_base, file_kotzur, file_kotzur_intraday, file_cluster, file_niet, file_welsch, file_welsch_intraday, representative_days, blocks_per_day, file_yearsplit)

.. py:function:: table(sim_results_path: str, sol_path: str, scenario_name: str, model: str, new_capacity_path: str, new_storage_capacity_path: str, filter_val1: str, filter_val2: str, excel_path: str) -> None

