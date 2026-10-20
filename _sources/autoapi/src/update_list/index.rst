src.update_list
===============

.. py:module:: src.update_list


Functions
---------

.. autoapisummary::

   src.update_list.new_list


Module Contents
---------------

.. py:function:: new_list(length: int, output_file: str | pathlib.Path)

   Generates a list of integers from 1 to the specified length, saves it as a CSV file, and returns the output file path. Used to update timeslice and daytype.

   :param length: The number of integers to include in the list.
   :type length: int
   :param output_file: The file path where the CSV will be saved.
   :type output_file: str

   :returns: The path to the output CSV file.
   :rtype: str

   The generated CSV will contain a single column named 'VALUE' with integers from 1 to 'length' (inclusive).



