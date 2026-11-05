"""Reference unit tests for lab 4 (show only if the learner asks twice)."""
from pyspark.testing.utils import assertDataFrameEqual

from src.transforms import add_high_cholest_flag, convert_miles_to_km, uppercase_column_names


def test_convert_miles_to_km_basic(spark):
    df = spark.createDataFrame([(1.0,)], ["miles"])
    expected = spark.createDataFrame([(1.0, 1.61)], ["miles", "km"])
    assertDataFrameEqual(convert_miles_to_km(df, "km", "miles"), expected)


def test_convert_miles_to_km_rounding(spark):
    df = spark.createDataFrame([(10.0,), (3.3,)], ["miles"])
    expected = spark.createDataFrame([(10.0, 16.09), (3.3, 5.31)], ["miles", "km"])
    assertDataFrameEqual(convert_miles_to_km(df, "km", "miles"), expected)


def test_uppercase_column_names(spark):
    df = spark.createDataFrame([(1, 2, 3)], ["id", "My_Column", "With Space"])
    assert uppercase_column_names(df).columns == ["ID", "MY_COLUMN", "WITH SPACE"]


def test_add_high_cholest_flag_all_cases(spark):
    df = spark.createDataFrame([(0,), (1,), (2,), (3,), (None,)], "HighCholest INT")
    expected = spark.createDataFrame(
        [(0, "Normal"), (1, "Above Average"), (2, "High"), (3, "Unknown"), (None, "Unknown")],
        "HighCholest INT, HighCholest_Group STRING")
    assertDataFrameEqual(add_high_cholest_flag(df), expected)
