"""Local stand-in for Databricks `COPY INTO` (not available in open-source Spark).

Databricks:
    COPY INTO users_bronze_ci FROM '/Volumes/.../users' FILEFORMAT = parquet
      COPY_OPTIONS ('mergeSchema' = 'true');
Local:
    copy_into(spark, "lab1.users_bronze_ci", landing.volume("users"), "parquet", merge_schema=True)

Same behaviour that the exam asks about:
  * idempotent: files already loaded are skipped (state is kept per table)
  * force=True reloads every file
  * extra columns in new files -> error, unless merge_schema=True
  * target table may be created empty without a schema first
"""
import json
from pathlib import Path

from labutils import LAB_ROOT

STATE = LAB_ROOT / ".lab_state" / "copy_into"


class SchemaMismatch(Exception):
    pass


def _state_file(table):
    return STATE / f"{table}.json"


def reset_state(table):
    _state_file(table).unlink(missing_ok=True)


def copy_into(spark, table, source_dir, fileformat, format_options=None, merge_schema=False, force=False):
    sf = _state_file(table)
    loaded = set(json.loads(sf.read_text())) if sf.exists() else set()
    files = sorted(str(p) for p in Path(source_dir).iterdir()
                   if p.is_file() and not p.name.startswith((".", "_")))
    new = files if force else [f for f in files if f not in loaded]
    if not new:
        print(f"COPY INTO {table}: num_affected_rows=0 num_inserted_rows=0 (all files already loaded — skipped)")
        return 0
    reader = spark.read.format(fileformat)
    for k, v in (format_options or {}).items():
        reader = reader.option(k, v)
    df = reader.load(new)
    target_cols = [f.name for f in spark.table(table).schema.fields]
    extra = [c for c in df.columns if c not in target_cols]
    if target_cols and extra and not merge_schema:
        raise SchemaMismatch(
            f"A schema mismatch detected when writing to the Delta table. New columns {extra} are not in "
            f"{table}. To enable schema migration use COPY_OPTIONS ('mergeSchema' = 'true').")
    writer = df.write.format("delta").mode("append")
    if merge_schema or not target_cols:
        writer = writer.option("mergeSchema", "true")
    writer.saveAsTable(table)
    n = df.count()
    sf.parent.mkdir(parents=True, exist_ok=True)
    sf.write_text(json.dumps(sorted(loaded | set(new))))
    print(f"COPY INTO {table}: loaded {len(new)} file(s), num_inserted_rows={n}")
    return n
