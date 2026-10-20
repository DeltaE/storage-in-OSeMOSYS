src.table_generator
===================

.. py:module:: src.table_generator


Functions
---------

.. autoapisummary::

   src.table_generator.read_simulation_results
   src.table_generator.read_sol_file
   src.table_generator.read_excel_value
   src.table_generator.append_to_excel
   src.table_generator.table


Module Contents
---------------

.. py:function:: read_simulation_results(file_path)

.. py:function:: read_sol_file(file_path)

.. py:function:: read_excel_value(file_path, filter_col, filter_val)

.. py:function:: append_to_excel(df, excel_path)

.. py:function:: table(sim_results_path: str, sol_path: str, scenario_name: str, model: str, new_capacity_path: str, new_storage_capacity_path: str, filter_val1: str, filter_val2: str, excel_path: str) -> None

