"""Helpers for the local Databricks-style practice labs.

    from labutils import get_spark, RAW, reset_lab
    spark = get_spark()
"""
import os
import shutil
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent
RAW = LAB_ROOT / "data" / "raw"              # our stand-in for /Volumes/<catalog>/<schema>/raw
WAREHOUSE = LAB_ROOT / ".lab_warehouse"       # where local Delta tables are stored
CHECKPOINTS = LAB_ROOT / ".lab_checkpoints"   # streaming checkpoints

_JAVA_HOME = "/opt/homebrew/opt/openjdk@17"
_spark = None


def get_spark():
    """Return a local SparkSession with Delta Lake enabled (created once, then reused)."""
    global _spark
    if _spark is not None:
        return _spark
    if not os.environ.get("JAVA_HOME") and Path(_JAVA_HOME).exists():
        os.environ["JAVA_HOME"] = _JAVA_HOME
    from delta import configure_spark_with_delta_pip
    from pyspark.sql import SparkSession

    builder = (
        SparkSession.builder.master("local[2]")
        .appName("de-associate-lab")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.warehouse.dir", str(WAREHOUSE))
        .config("spark.sql.sources.default", "delta")              # CREATE TABLE = Delta, like Databricks
        .config("spark.sql.legacy.createHiveTableByDefault", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.databricks.delta.retentionDurationCheck.enabled", "false")
    )
    _spark = configure_spark_with_delta_pip(builder).getOrCreate()
    _spark.sparkContext.setLogLevel("ERROR")
    from labutils.datagen import ensure_data

    ensure_data()
    return _spark


def reset_lab(schema: str):
    """Drop and recreate a lab schema (database) and its streaming checkpoints."""
    spark = get_spark()
    spark.sql(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
    shutil.rmtree(WAREHOUSE / f"{schema}.db", ignore_errors=True)  # leftovers from old sessions
    spark.sql(f"CREATE SCHEMA {schema}")
    spark.sql(f"USE {schema}")
    shutil.rmtree(CHECKPOINTS / schema, ignore_errors=True)
    print(f"Schema '{schema}' is empty and selected (like USE SCHEMA in Databricks).")


def checkpoint(schema: str, name: str) -> str:
    """Path for a streaming checkpoint, e.g. checkpoint('lab1', 'users_stream')."""
    p = CHECKPOINTS / schema / name
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p)


def path(*parts) -> str:
    """Path to raw data, e.g. path('sales-csv'). Stands in for '/Volumes/.../raw/sales-csv'."""
    return str(RAW.joinpath(*parts))


def table_path(schema: str, table: str) -> str:
    """Folder of a managed table in the local warehouse (lets checks read it by path)."""
    return str(WAREHOUSE / f"{schema}.db" / table)


def show(df, n=20):
    """Pretty-print a DataFrame (like display() in Databricks)."""
    try:
        from IPython.display import display

        display(df.limit(n).toPandas())
    except Exception:
        df.show(n, truncate=False)
