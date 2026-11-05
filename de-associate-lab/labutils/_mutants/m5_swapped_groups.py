"""MUTANT (buggy on purpose): 1 and 2 groups are swapped."""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def convert_miles_to_km(df: DataFrame, new_column_name: str, miles_column: str) -> DataFrame:
    return df.withColumn(new_column_name, F.round(F.col(miles_column) * 1.60934, 2))


def uppercase_column_names(df: DataFrame) -> DataFrame:
    return df.select([F.col(f"`{c}`").alias(c.upper()) for c in df.columns])


def add_high_cholest_flag(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "HighCholest_Group",
        F.when(F.col("HighCholest") == 0, "Normal")
        .when(F.col("HighCholest") == 1, "High")
        .when(F.col("HighCholest") == 2, "High")
        .otherwise("Unknown"),
    )
