"""Lab 4 — unit tests (course 4, notebooks 2.4 / 2.5L).

Run:  cd lab4_project && ../.venv/bin/python -m pytest -v
One example test is done for you. TODO: add tests until `check 4b` and `check 4c` pass.
Tip: test edge cases (NULL, 0, values outside 0-2, rounding, names with spaces).
"""
from pyspark.testing.utils import assertDataFrameEqual

from src.transforms import add_high_cholest_flag, convert_miles_to_km, uppercase_column_names  # noqa: F401


def test_convert_miles_to_km_basic(spark):
    df = spark.createDataFrame([(1.0,)], ["miles"])
    actual = convert_miles_to_km(df, "km", "miles")
    expected = spark.createDataFrame([(1.0, 1.61)], ["miles", "km"])
    assertDataFrameEqual(actual, expected)


# TODO: test uppercase_column_names


# TODO: test add_high_cholest_flag (all 5 cases: 0, 1, 2, another number, NULL)
