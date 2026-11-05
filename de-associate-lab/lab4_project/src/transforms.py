"""Lab 4 — modular PySpark functions (course 4, notebooks 2.1 / 2.2L).

TODO: implement the three functions. Each one takes a DataFrame and RETURNS a new DataFrame.
Check your work with:  .venv/bin/python -m labutils.check 4a
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def convert_miles_to_km(df: DataFrame, new_column_name: str, miles_column: str) -> DataFrame:
    """Add `new_column_name` = miles_column * 1.60934, rounded to 2 decimals."""
    # TODO
    raise NotImplementedError


def uppercase_column_names(df: DataFrame) -> DataFrame:
    """Return the same data with every column name in UPPER CASE."""
    # TODO
    raise NotImplementedError


def add_high_cholest_flag(df: DataFrame) -> DataFrame:
    """Add column HighCholest_Group from HighCholest:
    0 -> 'Normal', 1 -> 'Above Average', 2 -> 'High', anything else (incl. NULL) -> 'Unknown'."""
    # TODO
    raise NotImplementedError
