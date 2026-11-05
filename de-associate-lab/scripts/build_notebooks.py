"""Build the lab notebooks: notebooks/labN_*.ipynb (with TODOs) and notebooks/solutions/*.ipynb.

Cells: ("md", text) | ("code", code) | ("ex", todo_code, solution_code)
Run:  .venv/bin/python scripts/build_notebooks.py
"""
from pathlib import Path

import nbformat as nbf

LAB = Path(__file__).resolve().parent.parent
OUT = LAB / "notebooks"

SETUP = '''import sys, os
sys.path.insert(0, os.path.abspath(".."))          # lets the notebook import labutils
from labutils import get_spark, path, reset_lab, show, checkpoint, table_path, landing
from labutils.check import check
from pyspark.sql import functions as F
spark = get_spark()'''

LEGEND = """**How this lab works**
- Run cells top to bottom (`Shift+Enter`). After a kernel restart, run again from the top.
- Cells marked `# TODO` contain `<FILL-IN>`: replace it with your code, then run the `check(...)` cell.
- Stuck? Ask Claude in the terminal: *"hint for 1c"*. Solutions are in `notebooks/solutions/` (try first!).
- 🖥 **Local** means open-source Spark + Delta on your Mac. ☁ **Databricks** shows the real syntax for the exam.
"""

# =====================================================================================
LAB1 = [
    ("md", """# Lab 1 — Data Ingestion (Course 1: Lakeflow Connect)
Lessons 1.1–1.9 · exercises `1a`–`1h` · schema `lab1`

""" + LEGEND),
    ("code", SETUP + '\nreset_lab("lab1")'),

    ("md", """## 1a · Delta Lake basics (lesson 1.1)
A Delta table = **Parquet data files** + a **`_delta_log/`** folder (the transaction log).
Every write creates a new **version** → ACID, time travel, `DESCRIBE HISTORY`.

**Task:** create table `lab1.demo_delta (id INT, name STRING)` and insert 3 rows."""),
    ("ex", '''# TODO 1a
spark.sql("""<FILL-IN: CREATE TABLE ...>""")
spark.sql("""<FILL-IN: INSERT INTO ... VALUES ...>""")''',
     '''spark.sql("CREATE TABLE lab1.demo_delta (id INT, name STRING)")
spark.sql("INSERT INTO lab1.demo_delta VALUES (1, 'peter'), (2, 'zebi'), (3, 'samarth')")'''),
    ("code", '''t = table_path("lab1", "demo_delta")
print("data files :", sorted(f for f in os.listdir(t) if f.endswith(".parquet")))
print("_delta_log :", sorted(os.listdir(t + "/_delta_log")))
show(spark.sql("DESCRIBE HISTORY lab1.demo_delta").select("version", "operation", "operationParameters"))'''),
    ("code", 'check("1a")'),

    ("md", """## 1b · Batch ingestion with CTAS (lesson 1.2)
☁ Databricks:
```sql
CREATE TABLE historical_users_bronze AS
SELECT * FROM read_files('/Volumes/dbacademy_ecommerce/v01/raw/users-historical', format => 'parquet');
```
🖥 Local: `read_files()` is Databricks-only. Use the *query files by path* form instead:
``SELECT * FROM parquet.`<path>` `` (works on Databricks too).

Notice the files starting with `_` (like `_SUCCESS`) — Spark ignores them."""),
    ("code", '''users_path = path("users-historical")
print(sorted(os.listdir(users_path)))
show(spark.sql(f"SELECT * FROM parquet.`{users_path}` LIMIT 5"))'''),
    ("ex", '''# TODO 1b: create lab1.users_bronze_ctas from the Parquet files with CTAS
spark.sql(f"""
CREATE TABLE lab1.users_bronze_ctas AS
<FILL-IN>
""")''',
     '''spark.sql(f"""
CREATE TABLE lab1.users_bronze_ctas AS
SELECT * FROM parquet.`{users_path}`
""")'''),
    ("code", 'check("1b")'),
    ("md", """### Managed vs external tables — watch what DROP does
Run the cell and read the output. Then answer: *after `DROP TABLE`, which table's files still exist?*"""),
    ("code", '''import shutil
ext_location = os.path.abspath("../.lab_external/users_ext")
shutil.rmtree(ext_location, ignore_errors=True)
spark.sql(f"CREATE TABLE lab1.users_external LOCATION '{ext_location}' AS SELECT * FROM lab1.users_bronze_ctas")
spark.sql("CREATE TABLE lab1.users_managed AS SELECT * FROM lab1.users_bronze_ctas")
managed_location = table_path("lab1", "users_managed")
spark.sql("DROP TABLE lab1.users_external")
spark.sql("DROP TABLE lab1.users_managed")
print("external files still there? ", os.path.exists(ext_location + "/_delta_log"))
print("managed  files still there? ", os.path.exists(managed_location + "/_delta_log"))'''),

    ("md", """## 1c · Incremental batch with COPY INTO (lesson 1.3)
☁ Databricks:
```sql
CREATE TABLE users_bronze_ci;                         -- empty, no schema needed
COPY INTO users_bronze_ci
  FROM '/Volumes/.../users'  FILEFORMAT = parquet
  COPY_OPTIONS ('mergeSchema' = 'true');
```
🖥 Local: `COPY INTO` is Databricks-only, so the lab has a look-alike: `copy_into(spark, table, folder, format, merge_schema=..., force=...)`.
It keeps the same rules: **idempotent** (already-loaded files are skipped), `force` reloads, new columns need `mergeSchema`.

`landing.land("users", n)` simulates new files arriving in a volume."""),
    ("code", '''from labutils.ingest import copy_into, reset_state
reset_state("lab1.users_bronze_ci")
vol = landing.reset("users")
landing.land("users", 2)
spark.sql("CREATE TABLE lab1.users_bronze_ci")    # empty table without a schema'''),
    ("ex", '''# TODO 1c
# 1) load the landed files into lab1.users_bronze_ci (format "parquet")
<FILL-IN>
# 2) run the SAME load again. How many rows does it insert? Why?
<FILL-IN>
# 3) land the next batch (it has a NEW column `country`) and load it.
landing.land("users", 1)
#    It fails with a schema mismatch -> fix it with the right option.
<FILL-IN>
print(spark.table("lab1.users_bronze_ci").count(), "rows")''',
     '''copy_into(spark, "lab1.users_bronze_ci", vol, "parquet")
copy_into(spark, "lab1.users_bronze_ci", vol, "parquet")          # 0 rows: COPY INTO is idempotent
landing.land("users", 1)
try:
    copy_into(spark, "lab1.users_bronze_ci", vol, "parquet")
except Exception as e:
    print("ERROR:", e)
copy_into(spark, "lab1.users_bronze_ci", vol, "parquet", merge_schema=True)
print(spark.table("lab1.users_bronze_ci").count(), "rows")'''),
    ("code", 'check("1c")'),

    ("md", """## 1d · Auto Loader idea: incremental streaming with a checkpoint (lesson 1.4)
☁ Databricks Auto Loader (Python):
```python
(spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "parquet")
      .option("cloudFiles.schemaLocation", checkpoint_path)
      .load("/Volumes/.../users")
 .writeStream.option("checkpointLocation", checkpoint_path)
      .trigger(availableNow=True)
      .toTable("users_bronze_stream"))
```
☁ Databricks SQL: `CREATE OR REFRESH STREAMING TABLE t AS SELECT * FROM STREAM read_files(...)`, then `REFRESH STREAMING TABLE t`.

🖥 Local: `cloudFiles` is Databricks-only, but Auto Loader is **built on Structured Streaming**. The plain
file source + a **checkpoint** gives the same core behaviour: each file is processed **once**.
`trigger(availableNow=True)` = process everything new, then stop (incremental batch)."""),
    ("code", '''vol_stream = landing.reset("users_stream")
users_schema = "user_id STRING, user_first_touch_timestamp BIGINT, email STRING"'''),
    ("ex", '''# TODO 1d: complete the streaming read/write
def refresh_users_stream():
    (spark.readStream
        .format(<FILL-IN>)                      # local file format of the landed files
        .schema(users_schema)                   # streaming file sources need a schema
        .load(vol_stream)
     .writeStream
        .option("checkpointLocation", <FILL-IN>)    # use checkpoint("lab1", "users_stream")
        .trigger(availableNow=True)
        .toTable("lab1.users_bronze_stream")
     .awaitTermination())''',
     '''def refresh_users_stream():
    (spark.readStream
        .format("parquet")
        .schema(users_schema)
        .load(vol_stream)
     .writeStream
        .option("checkpointLocation", checkpoint("lab1", "users_stream"))
        .trigger(availableNow=True)
        .toTable("lab1.users_bronze_stream")
     .awaitTermination())'''),
    ("code", '''landing.land("users_stream", 1); refresh_users_stream()
print("after run 1:", spark.table("lab1.users_bronze_stream").count())
landing.land("users_stream", 1); refresh_users_stream()
print("after run 2:", spark.table("lab1.users_bronze_stream").count())
refresh_users_stream()   # nothing new arrived -> nothing to do
print("after run 3:", spark.table("lab1.users_bronze_stream").count(), " <- same: files are never read twice")'''),
    ("code", 'check("1d")'),

    ("md", """## 1e · Metadata columns on ingest (lesson 1.5)
☁ Databricks SQL:
```sql
CREATE TABLE sales_bronze AS
SELECT *, _metadata.file_modification_time AS file_modification_time,
          _metadata.file_name AS source_file, current_timestamp() AS ingestion_time
FROM read_files('/Volumes/.../sales-csv', format => 'csv', sep => '|', header => true);
```
🖥 Local: same idea with the PySpark API (the course shows it as the Python equivalent).
The CSV files are separated by `|` and have a header row."""),
    ("ex", '''# TODO 1e
sales_df = (spark.read
    .option("header", True)
    .option("sep", <FILL-IN>)
    .csv(path("sales-csv"))
    .select("*",
            <FILL-IN>,     # source_file            <- _metadata.file_name
            <FILL-IN>,     # file_modification_time <- _metadata.file_modification_time
            <FILL-IN>))    # ingestion_time         <- current timestamp
sales_df.write.mode("overwrite").saveAsTable("lab1.sales_bronze")''',
     '''sales_df = (spark.read
    .option("header", True)
    .option("sep", "|")
    .csv(path("sales-csv"))
    .select("*",
            F.col("_metadata.file_name").alias("source_file"),
            F.col("_metadata.file_modification_time").alias("file_modification_time"),
            F.current_timestamp().alias("ingestion_time")))
sales_df.write.mode("overwrite").saveAsTable("lab1.sales_bronze")'''),
    ("code", '''show(spark.sql("SELECT source_file, count(*) AS total FROM lab1.sales_bronze GROUP BY source_file ORDER BY 1"))
check("1e")'''),

    ("md", """## 1f · Rescuing malformed data (lesson 1.6)
Look at the raw file: two prices are written as `$945.00` — not a valid DOUBLE.

☁ Databricks: `read_files(..., schema => 'item_id STRING, name STRING, price DOUBLE', rescueddatacolumn => '_rescued_data')`
→ `price` is NULL and `_rescued_data` = `{"price":"$945.00","_file_path":"..."}`. Fix with
`coalesce(price, cast(replace(_rescued_data:price, '$', '') AS DOUBLE))`.

🖥 Local: open-source Spark has a cousin: **`columnNameOfCorruptRecord`** (keeps the *whole raw line*)."""),
    ("code", '''show(spark.read.text(path("malformed")))
items_raw = (spark.read
    .schema("item_id STRING, name STRING, price DOUBLE, _corrupt_record STRING")
    .option("header", True)
    .option("mode", "PERMISSIVE")
    .option("columnNameOfCorruptRecord", "_corrupt_record")
    .csv(path("malformed"))
    .cache())
items_raw.createOrReplaceTempView("items_raw")
show(items_raw)'''),
    ("ex", '''# TODO 1f: fill price_fixed — use price, or the 3rd value of the raw line without "$"
spark.sql("""
CREATE OR REPLACE TABLE lab1.items_bronze AS
SELECT item_id, name, price,
       <FILL-IN> AS price_fixed,
       _corrupt_record
FROM items_raw
""")''',
     '''spark.sql("""
CREATE OR REPLACE TABLE lab1.items_bronze AS
SELECT item_id, name, price,
       coalesce(price, cast(regexp_replace(split(_corrupt_record, ',')[2], '[$]', '') AS DOUBLE)) AS price_fixed,
       _corrupt_record
FROM items_raw
""")'''),
    ("code", 'show(spark.table("lab1.items_bronze")); check("1f")'),

    ("md", """## 1g · Semi-structured JSON (lesson 1.7)
The Kafka-style events have **base64-encoded** `key` and `value` columns.
1. Decode: `cast(unbase64(value) AS STRING)` → a JSON-formatted STRING.
2. ☁ Databricks reads fields with colon syntax: `decoded_value:user_id`, `decoded_value:geo:city`.
   🖥 Local equivalent: `get_json_object(decoded_value, '$.user_id')`.
3. Convert to a STRUCT with `from_json(col, schema)`; find the schema with `schema_of_json`.
4. One row per array element with `explode`; **`explode_outer` keeps rows whose array is empty**."""),
    ("code", 'show(spark.read.json(path("events-kafka")), 3)'),
    ("ex", '''# TODO 1g-1: decode the base64 value column
spark.sql(f"""
CREATE OR REPLACE TABLE lab1.events_decoded AS
SELECT key, offset, partition, timestamp, topic,
       <FILL-IN> AS decoded_value
FROM json.`{path('events-kafka')}`
""")''',
     '''spark.sql(f"""
CREATE OR REPLACE TABLE lab1.events_decoded AS
SELECT key, offset, partition, timestamp, topic,
       cast(unbase64(value) AS STRING) AS decoded_value
FROM json.`{path('events-kafka')}`
""")'''),
    ("code", '''sample = spark.table("lab1.events_decoded").first().decoded_value
print(sample)
print(spark.sql(f"SELECT schema_of_json('{sample}') AS s").first().s)
show(spark.sql("SELECT get_json_object(decoded_value, '$.user_id') AS user_id, "
               "get_json_object(decoded_value, '$.geo.city') AS city FROM lab1.events_decoded"), 3)'''),
    ("ex", '''# TODO 1g-2: parse to a STRUCT and flatten: one row per item, but KEEP events without items
event_schema = "<FILL-IN: the STRUCT<...> schema (copy from schema_of_json above)>"
spark.sql(f"""
CREATE OR REPLACE TABLE lab1.events_flat AS
WITH parsed AS (SELECT from_json(decoded_value, '{event_schema}') AS e FROM lab1.events_decoded),
     exploded AS (SELECT e, <FILL-IN>(e.items) AS item FROM parsed)
SELECT e.user_id, e.event_name, e.geo.city AS city, item.item_id, item.price_usd, item.quantity
FROM exploded
""")''',
     '''event_schema = ("STRUCT<device: STRING, event_name: STRING, event_timestamp: BIGINT, "
                "geo: STRUCT<city: STRING, state: STRING>, "
                "items: ARRAY<STRUCT<item_id: STRING, price_usd: DOUBLE, quantity: BIGINT>>, user_id: STRING>")
spark.sql(f"""
CREATE OR REPLACE TABLE lab1.events_flat AS
WITH parsed AS (SELECT from_json(decoded_value, '{event_schema}') AS e FROM lab1.events_decoded),
     exploded AS (SELECT e, explode_outer(e.items) AS item FROM parsed)
SELECT e.user_id, e.event_name, e.geo.city AS city, item.item_id, item.price_usd, item.quantity
FROM exploded
""")'''),
    ("code", 'show(spark.table("lab1.events_flat"), 8); check("1g")'),

    ("md", """## 1h · MERGE INTO, schema evolution, time travel (lesson 1.9)
`MERGE INTO target USING source ON <key> WHEN MATCHED ... WHEN NOT MATCHED ...`
Source rows have a `status`: `update` → update the email, `delete` → delete the row, `new` → insert."""),
    ("code", '''spark.sql("""CREATE OR REPLACE TABLE lab1.main_users_target AS SELECT * FROM VALUES
  (1, 'Peter',   'peter@old.com',   DATE'2024-01-01', 'current'),
  (2, 'Zebi',    'zebi@x.com',      DATE'2024-01-02', 'current'),
  (3, 'Samarth', 'samarth@x.com',   DATE'2024-01-03', 'current')
  AS t(id, first_name, email, sign_up_date, status)""")
spark.sql("""CREATE OR REPLACE TABLE lab1.update_users_source AS SELECT * FROM VALUES
  (1, 'Peter',  'peter@new.com',  DATE'2024-01-01', 'update'),
  (2, 'Zebi',   'zebi@x.com',     DATE'2024-01-02', 'delete'),
  (4, 'Kostas', 'kostas@x.com',   DATE'2024-05-20', 'new')
  AS t(id, first_name, email, sign_up_date, status)""")'''),
    ("ex", '''# TODO 1h-1: write the MERGE
spark.sql("""
MERGE INTO lab1.main_users_target t
USING lab1.update_users_source s
ON <FILL-IN>
WHEN MATCHED AND s.status = 'update' THEN <FILL-IN>
WHEN MATCHED AND s.status = 'delete' THEN <FILL-IN>
WHEN NOT MATCHED THEN <FILL-IN>
""")
show(spark.sql("SELECT * FROM lab1.main_users_target ORDER BY id"))''',
     '''spark.sql("""
MERGE INTO lab1.main_users_target t
USING lab1.update_users_source s
ON t.id = s.id
WHEN MATCHED AND s.status = 'update' THEN UPDATE SET t.email = s.email, t.status = s.status
WHEN MATCHED AND s.status = 'delete' THEN DELETE
WHEN NOT MATCHED THEN INSERT (id, first_name, email, sign_up_date, status)
                      VALUES (s.id, s.first_name, s.email, s.sign_up_date, s.status)
""")
show(spark.sql("SELECT * FROM lab1.main_users_target ORDER BY id"))'''),
    ("md", """**Schema evolution.** The next source has a new column `country`. Without evolution, MERGE fails
(schema enforcement). ☁ Databricks: `MERGE WITH SCHEMA EVOLUTION INTO ...` (DBR 15.2+), or set
`spark.databricks.delta.schema.autoMerge.enabled = true`. 🖥 Locally only the config works."""),
    ("code", '''spark.sql("""CREATE OR REPLACE TABLE lab1.new_users_source AS SELECT * FROM VALUES
  (5, 'Ana', 'ana@x.com', DATE'2024-06-01', 'new', 'CA')
  AS t(id, first_name, email, sign_up_date, status, country)""")'''),
    ("ex", '''# TODO 1h-2: enable schema evolution, then MERGE new users in (insert all columns)
<FILL-IN: spark.conf.set(...)>
spark.sql("""
MERGE INTO lab1.main_users_target t
USING lab1.new_users_source s
ON t.id = s.id
WHEN NOT MATCHED THEN <FILL-IN>
""")
show(spark.sql("SELECT * FROM lab1.main_users_target ORDER BY id"))''',
     '''spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
spark.sql("""
MERGE INTO lab1.main_users_target t
USING lab1.new_users_source s
ON t.id = s.id
WHEN NOT MATCHED THEN INSERT *
""")
show(spark.sql("SELECT * FROM lab1.main_users_target ORDER BY id"))'''),
    ("code", '''show(spark.sql("DESCRIBE HISTORY lab1.main_users_target").select("version", "operation"))
print("version 0 (before any MERGE):")
show(spark.sql("SELECT * FROM lab1.main_users_target VERSION AS OF 0 ORDER BY id"))
check("1h")'''),
    ("md", """## Done 🎉
Ask Claude: `/quiz ingestion 5` to test yourself, or run the original course notebooks in Databricks Free Edition
(see `databricks/FREE_EDITION_GUIDE.md`) to try `read_files`, Auto Loader and streaming tables for real."""),
]

# =====================================================================================
LAB2 = [
    ("md", """# Lab 2 — Lakeflow Jobs concepts (Course 2)
Lessons 2.1–2.6 · exercises `2a`–`2d` · schema `lab2`

Real jobs are built in the **Jobs UI** (or API / SDK / bundles). Here `labutils.jobsim.Job` runs Python
functions as tasks with the **same rules**: DAG dependencies, run-if, If/else, For each, parameters,
task values, `{{dynamic references}}`, retries and repair. Do the real UI version in Databricks Free Edition later.

| Databricks | This lab |
|---|---|
| Notebook task | `@job.task("key")` function — gets `ctx` |
| `dbutils.widgets.get("x")` | `ctx.widget("x")` |
| `dbutils.jobs.taskValues.set(key=, value=)` | `ctx.task_values.set(key, value)` |
| `dbutils.jobs.taskValues.get(taskKey=, key=)` | `ctx.task_values.get(taskKey, key)` |
| If/else condition task | `job.if_else(...)` |
| For each task | `job.for_each(...)` — item is `ctx.input` / `{{input}}` |
| Repair run | `job.repair(run)` |

""" + LEGEND),
    ("code", SETUP + '\nfrom labutils.jobsim import Job\nreset_lab("lab2")'),

    ("md", """## 2a · A multi-task job is a DAG (lessons 2.1–2.2)
Two ingestion tasks have no dependency → they can run **in parallel**. The join task must wait for **both**
(a *funnel* pattern). **Task:** set `depends_on` for the join task."""),
    ("ex", '''# TODO 2a
job = Job("retail_job")

@job.task("ingest_orders")
def ingest_orders(ctx):
    landing.reset("orders"); landing.land("orders", 2)
    spark.read.json(landing.volume("orders")).write.mode("overwrite").saveAsTable("lab2.orders_bronze")

@job.task("ingest_customers")
def ingest_customers(ctx):
    (spark.range(1, 41).selectExpr("id AS customer_id", "concat('customer_', id) AS name")
          .write.mode("overwrite").saveAsTable("lab2.customers"))

@job.task("join_customers_orders", depends_on=<FILL-IN>)
def join_customers_orders(ctx):
    spark.sql("""CREATE OR REPLACE TABLE lab2.customers_orders AS
                 SELECT o.*, c.name FROM lab2.orders_bronze o JOIN lab2.customers c USING (customer_id)""")

run = job.run()
run.save("2a")''',
     '''job = Job("retail_job")

@job.task("ingest_orders")
def ingest_orders(ctx):
    landing.reset("orders"); landing.land("orders", 2)
    spark.read.json(landing.volume("orders")).write.mode("overwrite").saveAsTable("lab2.orders_bronze")

@job.task("ingest_customers")
def ingest_customers(ctx):
    (spark.range(1, 41).selectExpr("id AS customer_id", "concat('customer_', id) AS name")
          .write.mode("overwrite").saveAsTable("lab2.customers"))

@job.task("join_customers_orders", depends_on=["ingest_orders", "ingest_customers"])
def join_customers_orders(ctx):
    spark.sql("""CREATE OR REPLACE TABLE lab2.customers_orders AS
                 SELECT o.*, c.name FROM lab2.orders_bronze o JOIN lab2.customers c USING (customer_id)""")

run = job.run()
run.save("2a")'''),
    ("code", '''check("2a")
# Why "Directed ACYCLIC Graph"? Try a cycle:
from labutils.jobsim import Task
bad = Job("cycle")
bad.add_task(Task("a", lambda c: None, ["b"]))
bad.add_task(Task("b", lambda c: None, ["a"]))
try:
    bad.run()
except ValueError as e:
    print("ERROR:", e)'''),

    ("md", """## 2b · Parameters and task values (lesson 2.3)
- **Task parameters** belong to one task. **Job parameters** apply to every task and **override** a task
  parameter with the same key. Both can be overridden at run time (*Run now with different parameters*).
- **Task values** pass results from one task to a later task.
- **Dynamic value references**: `{{tasks.<task_key>.values.<key>}}`, `{{job.parameters.<name>}}`, `{{job.run_id}}` …

**Task:** (1) save the row count as task value `row_count`; (2) pass it to `report` with a dynamic reference;
(3) run the job with job parameter `catalog = "lab2_prod"`. Predict first: which `catalog` does `count_orders` print?"""),
    ("ex", '''# TODO 2b
job = Job("params_job", parameters={"catalog": "lab2_dev"})

@job.task("count_orders", parameters={"catalog": "task_default", "min_id": "75000"})
def count_orders(ctx):
    print("count_orders sees catalog =", ctx.widget("catalog"))
    n = spark.table("lab2.orders_bronze").filter(f"order_id > {ctx.widget('min_id')}").count()
    <FILL-IN>                                   # share n as task value "row_count"

@job.task("report", depends_on=["count_orders"], parameters={"rows": "<FILL-IN>"})
def report(ctx):
    print(f"report: catalog={ctx.widget('catalog')} rows={ctx.widget('rows')}")
    print("same value read directly:", ctx.task_values.get(taskKey="count_orders", key="row_count"))

run = job.run(parameters=<FILL-IN>)
run.save("2b")''',
     '''job = Job("params_job", parameters={"catalog": "lab2_dev"})

@job.task("count_orders", parameters={"catalog": "task_default", "min_id": "75000"})
def count_orders(ctx):
    print("count_orders sees catalog =", ctx.widget("catalog"))
    n = spark.table("lab2.orders_bronze").filter(f"order_id > {ctx.widget('min_id')}").count()
    ctx.task_values.set("row_count", n)

@job.task("report", depends_on=["count_orders"], parameters={"rows": "{{tasks.count_orders.values.row_count}}"})
def report(ctx):
    print(f"report: catalog={ctx.widget('catalog')} rows={ctx.widget('rows')}")
    print("same value read directly:", ctx.task_values.get(taskKey="count_orders", key="row_count"))

run = job.run(parameters={"catalog": "lab2_prod"})
run.save("2b")'''),
    ("code", 'check("2b")'),

    ("md", """## 2c · Run-if, If/else and For each (lesson 2.5)
- **If/else task** compares two values (`==, !=, >, >=, <, <=`) → downstream tasks hang on the **True** or **False** branch.
  The branch not taken is **Excluded**.
- **For each task** runs one nested task per item of an array; the item is `{{input}}` (here `ctx.input`).
- **Run if**: `ALL_SUCCEEDED` (default), `AT_LEAST_ONE_SUCCEEDED`, `NONE_FAILED`, `ALL_DONE`, `AT_LEAST_ONE_FAILED`, `ALL_FAILED`.

**Task:** the For each task depends on **both** branches. One branch is always excluded, so which `run_if`
lets it run? (Try `ALL_SUCCEEDED` first and see what happens.)"""),
    ("ex", '''# TODO 2c
job = Job("advanced_job")

@job.task("check_duplicates")
def check_duplicates(ctx):
    df = spark.table("lab2.orders_bronze")
    has = df.count() != df.dropDuplicates(["order_id"]).count()
    ctx.task_values.set("has_duplicates", str(has).lower())

job.if_else("duplicates_exist", left="<FILL-IN: reference the task value>", op="==", right="true",
            depends_on=["check_duplicates"])

@job.task("drop_duplicates", depends_on=[("duplicates_exist", True)])
def drop_duplicates(ctx):
    spark.table("lab2.orders_bronze").dropDuplicates(["order_id"]).write.mode("overwrite").saveAsTable("lab2.orders_clean")

@job.task("no_duplicates", depends_on=[("duplicates_exist", False)])
def no_duplicates(ctx):
    spark.table("lab2.orders_bronze").write.mode("overwrite").saveAsTable("lab2.orders_clean")

STATES = ["CA", "NY", "VA"]
def state_report(ctx):                  # the nested task: runs once per state
    i = STATES.index(ctx.input)
    (spark.table("lab2.orders_clean").filter(f"customer_id % 3 = {i}")
          .write.mode("overwrite").saveAsTable(f"lab2.orders_{ctx.input.lower()}"))

job.for_each("state_reports", inputs=STATES, fn=state_report, concurrency=3,
             depends_on=["drop_duplicates", "no_duplicates"], run_if="<FILL-IN>")

run = job.run()
run.save("2c")''',
     '''job = Job("advanced_job")

@job.task("check_duplicates")
def check_duplicates(ctx):
    df = spark.table("lab2.orders_bronze")
    has = df.count() != df.dropDuplicates(["order_id"]).count()
    ctx.task_values.set("has_duplicates", str(has).lower())

job.if_else("duplicates_exist", left="{{tasks.check_duplicates.values.has_duplicates}}", op="==", right="true",
            depends_on=["check_duplicates"])

@job.task("drop_duplicates", depends_on=[("duplicates_exist", True)])
def drop_duplicates(ctx):
    spark.table("lab2.orders_bronze").dropDuplicates(["order_id"]).write.mode("overwrite").saveAsTable("lab2.orders_clean")

@job.task("no_duplicates", depends_on=[("duplicates_exist", False)])
def no_duplicates(ctx):
    spark.table("lab2.orders_bronze").write.mode("overwrite").saveAsTable("lab2.orders_clean")

STATES = ["CA", "NY", "VA"]
def state_report(ctx):
    i = STATES.index(ctx.input)
    (spark.table("lab2.orders_clean").filter(f"customer_id % 3 = {i}")
          .write.mode("overwrite").saveAsTable(f"lab2.orders_{ctx.input.lower()}"))

job.for_each("state_reports", inputs=STATES, fn=state_report, concurrency=3,
             depends_on=["drop_duplicates", "no_duplicates"], run_if="NONE_FAILED")

run = job.run()
run.save("2c")'''),
    ("code", 'check("2c")'),

    ("md", """## 2d · Retries and repair runs (lesson 2.6)
- **Retry policy**: a task can retry automatically (e.g. `max_retries=2` → up to 3 attempts).
- **Repair run**: after a failure, re-run **only the failed tasks and the tasks after them**. Successful tasks are
  **not** re-run (saves time and money). You may change parameters for the repair.

The job below has a bug: a wrong table name in a **parameter**. **Task:** repair the run with the right parameter."""),
    ("code", '''attempts = {"n": 0}
job = Job("flaky_job")

@job.task("ingest", max_retries=2)
def ingest(ctx):
    attempts["n"] += 1
    if attempts["n"] == 1:
        raise ConnectionError("temporary network problem")   # 1st attempt fails, retry succeeds
    print("ingest ok on attempt", attempts["n"])

@job.task("transform", depends_on=["ingest"], parameters={"source_table": "lab2.orders_bronz"})
def transform(ctx):
    n = spark.table(ctx.widget("source_table")).count()
    ctx.task_values.set("rows", n)

@job.task("publish", depends_on=["transform"])
def publish(ctx):
    print("published", ctx.task_values.get("transform", "rows"), "rows")

run = job.run()'''),
    ("ex", '''# TODO 2d: repair the failed run, overriding the parameter source_table with the correct table
run = job.repair(run, parameters=<FILL-IN>)
run.save("2d")''',
     '''run = job.repair(run, parameters={"source_table": "lab2.orders_bronze"})
run.save("2d")'''),
    ("code", '''check("2d")
print("ingest ran", attempts["n"], "times in total — the repair did NOT re-run it.")'''),
    ("md", """## Next
- Build the same jobs in the real **Jobs UI**: course notebooks `1 Demo`…`6 Demo` in Databricks Free Edition.
- Triggers (schedule/cron, file arrival, table update, continuous) and notifications are UI-only — study `notes/c2-jobs.md` §4.
- Ask Claude: `/quiz jobs 5`."""),
]

# =====================================================================================
LAB3 = [
    ("md", """# Lab 3 — Spark Declarative Pipelines concepts (Course 3)
Lessons 3.1–3.5 · exercises `3a`–`3d` · schema `lab3`

☁ In Databricks you **declare** tables in SQL and SDP runs them:
```sql
CREATE OR REFRESH STREAMING TABLE orders_bronze AS
  SELECT *, current_timestamp() AS processing_time, _metadata.file_name AS source_file
  FROM STREAM read_files('${source}/orders', format => 'JSON');
CREATE OR REFRESH STREAMING TABLE orders_silver AS
  SELECT order_id, timestamp(order_timestamp) AS order_timestamp, customer_id, notifications
  FROM STREAM orders_bronze;
CREATE OR REFRESH MATERIALIZED VIEW gold_orders_by_date AS
  SELECT date(order_timestamp) AS order_date, count(*) AS total_daily_orders
  FROM orders_silver GROUP BY date(order_timestamp);
```
🖥 Locally we build the **same three datasets by hand** with Structured Streaming. You will see exactly what SDP
automates for you: checkpoints, dependency order, incremental processing, recomputing the MV.

""" + LEGEND),
    ("code", SETUP + '''\nreset_lab("lab3")
for v in ("orders", "status", "customers"):
    landing.reset(v)
orders_schema = "order_id BIGINT, order_timestamp STRING, customer_id BIGINT, notifications STRING"
status_schema = "order_id BIGINT, order_status STRING, status_timestamp STRING"'''),

    ("md", """## 3a · Streaming tables + materialized view (lesson 3.1)
- **Streaming table** = append-only, each input processed **once** (checkpoint). Reading from a ST uses `STREAM`.
- **Materialized view** = result is **recomputed** to match the current data (SDP refreshes incrementally when it can).
- **Task:** complete silver (read bronze as a stream) and gold (daily counts)."""),
    ("ex", '''# TODO 3a
def refresh_orders_bronze():
    (spark.readStream.format("json").schema(orders_schema).load(landing.volume("orders"))
          .select("*", F.current_timestamp().alias("processing_time"),
                  F.col("_metadata.file_name").alias("source_file"))
     .writeStream.option("checkpointLocation", checkpoint("lab3", "orders_bronze"))
          .trigger(availableNow=True).toTable("lab3.orders_bronze").awaitTermination())

def refresh_orders_silver():
    (spark.readStream.table(<FILL-IN>)                # = FROM STREAM orders_bronze
          .select("order_id", F.to_timestamp("order_timestamp").alias("order_timestamp"),
                  "customer_id", "notifications")
     .writeStream.option("checkpointLocation", checkpoint("lab3", "orders_silver"))
          .trigger(availableNow=True).toTable("lab3.orders_silver").awaitTermination())

def refresh_gold():                                   # materialized view = recompute the result
    spark.sql("""CREATE OR REPLACE TABLE lab3.gold_orders_by_date AS
                 SELECT <FILL-IN>
                 FROM lab3.orders_silver
                 GROUP BY date(order_timestamp)""")

def run_pipeline():        # SDP figures out this order from the code; here we write it ourselves
    refresh_orders_bronze(); refresh_orders_silver(); refresh_gold()''',
     '''def refresh_orders_bronze():
    (spark.readStream.format("json").schema(orders_schema).load(landing.volume("orders"))
          .select("*", F.current_timestamp().alias("processing_time"),
                  F.col("_metadata.file_name").alias("source_file"))
     .writeStream.option("checkpointLocation", checkpoint("lab3", "orders_bronze"))
          .trigger(availableNow=True).toTable("lab3.orders_bronze").awaitTermination())

def refresh_orders_silver():
    (spark.readStream.table("lab3.orders_bronze")
          .select("order_id", F.to_timestamp("order_timestamp").alias("order_timestamp"),
                  "customer_id", "notifications")
     .writeStream.option("checkpointLocation", checkpoint("lab3", "orders_silver"))
          .trigger(availableNow=True).toTable("lab3.orders_silver").awaitTermination())

def refresh_gold():
    spark.sql("""CREATE OR REPLACE TABLE lab3.gold_orders_by_date AS
                 SELECT date(order_timestamp) AS order_date, count(*) AS total_daily_orders
                 FROM lab3.orders_silver
                 GROUP BY date(order_timestamp)""")

def run_pipeline():
    refresh_orders_bronze(); refresh_orders_silver(); refresh_gold()'''),
    ("code", '''def counts(label):
    print(label, {t: spark.table(f"lab3.{t}").count() for t in ("orders_bronze", "orders_silver", "gold_orders_by_date")})

landing.land("orders", 2); run_pipeline(); counts("pipeline update 1:")
landing.land("orders", 2); run_pipeline(); counts("pipeline update 2:")
show(spark.table("lab3.gold_orders_by_date").orderBy("order_date"))
check("3a")'''),

    ("md", """## 3b · Data quality expectations (lesson 3.3)
`CONSTRAINT name EXPECT (condition) [ON VIOLATION DROP ROW | FAIL UPDATE]`
| action | bad rows | pipeline |
|---|---|---|
| (none) = WARN | kept | continues, metrics logged |
| `DROP ROW` | removed | continues, metrics logged |
| `FAIL UPDATE` | — | update stops |

🖥 Local helper: `expect(df, [(name, condition, "warn" | "drop" | "fail")])` prints event-log-style metrics.
**Task:** `valid_notifications` (`notifications IN ('Y','N')`) should only **warn**; `valid_id` (`customer_id IS NOT NULL`) should **drop**."""),
    ("ex", '''# TODO 3b
from labutils.sdp import expect, ExpectationFailed
silver_dq, metrics = expect(spark.table("lab3.orders_silver"), [
    ("valid_notifications", "notifications IN ('Y','N')", "<FILL-IN>"),
    ("valid_id",            "customer_id IS NOT NULL",    "<FILL-IN>"),
], dataset="orders_silver_dq")
silver_dq.write.mode("overwrite").saveAsTable("lab3.orders_silver_dq")''',
     '''from labutils.sdp import expect, ExpectationFailed
silver_dq, metrics = expect(spark.table("lab3.orders_silver"), [
    ("valid_notifications", "notifications IN ('Y','N')", "warn"),
    ("valid_id",            "customer_id IS NOT NULL",    "drop"),
], dataset="orders_silver_dq")
silver_dq.write.mode("overwrite").saveAsTable("lab3.orders_silver_dq")'''),
    ("code", '''check("3b")
# What does FAIL UPDATE do?
try:
    expect(spark.table("lab3.orders_silver"), [("valid_id", "customer_id IS NOT NULL", "fail")], dataset="strict")
except ExpectationFailed as e:
    print("PIPELINE UPDATE FAILED:", e)'''),

    ("md", """## 3c · Joining two streaming tables in a materialized view (lesson 3.4)
To join **all rows** of two streaming tables every update, SDP uses a **materialized view**
(stream–stream joins need watermarks and are out of course scope).
**Task:** build the status pipeline, then join orders and statuses in `full_order_info_gold`."""),
    ("code", '''def refresh_status():
    (spark.readStream.format("json").schema(status_schema).load(landing.volume("status"))
     .writeStream.option("checkpointLocation", checkpoint("lab3", "status_bronze"))
          .trigger(availableNow=True).toTable("lab3.status_bronze").awaitTermination())
    (spark.readStream.table("lab3.status_bronze")
          .select("order_id", "order_status", F.to_timestamp("status_timestamp").alias("status_timestamp"))
     .writeStream.option("checkpointLocation", checkpoint("lab3", "status_silver"))
          .trigger(availableNow=True).toTable("lab3.status_silver").awaitTermination())

landing.land("status", 4); refresh_status()'''),
    ("ex", '''# TODO 3c
spark.sql("""
CREATE OR REPLACE TABLE lab3.full_order_info_gold AS
SELECT o.order_id, o.order_timestamp, o.customer_id, s.order_status, s.status_timestamp
FROM lab3.orders_silver o
<FILL-IN> lab3.status_silver s ON <FILL-IN>
""")''',
     '''spark.sql("""
CREATE OR REPLACE TABLE lab3.full_order_info_gold AS
SELECT o.order_id, o.order_timestamp, o.customer_id, s.order_status, s.status_timestamp
FROM lab3.orders_silver o
INNER JOIN lab3.status_silver s ON o.order_id = s.order_id
""")'''),
    ("code", '''show(spark.sql("SELECT order_status, count(*) n FROM lab3.full_order_info_gold GROUP BY 1"))
check("3c")'''),

    ("md", """## 3d · Change Data Capture with SCD Type 1 (lesson 3.5)
☁ Databricks:
```sql
CREATE OR REFRESH STREAMING TABLE customers_silver;
CREATE FLOW scd_type_1_flow AS AUTO CDC INTO customers_silver
FROM STREAM customers_bronze
KEYS (customer_id)
APPLY AS DELETE WHEN operation = 'DELETE'
SEQUENCE BY process_date
COLUMNS * EXCEPT (operation)
STORED AS SCD TYPE 1;
```
🖥 Locally we rebuild AUTO CDC by hand: `foreachBatch` + `MERGE`.
The 2nd batch has **two updates for Peter that arrive out of order** (05-20 first, then 05-15). `SEQUENCE BY` makes the
**latest process_date win**. **Task:** keep only the latest change per key, and apply deletes."""),
    ("code", '''from pyspark.sql.window import Window
cdc_schema = "customer_id BIGINT, name STRING, address STRING, operation STRING, process_date STRING"
spark.sql("CREATE OR REPLACE TABLE lab3.customers_silver (customer_id BIGINT, name STRING, address STRING, process_date STRING)")'''),
    ("ex", '''# TODO 3d
def apply_changes(batch_df, batch_id):
    w = Window.partitionBy("customer_id").orderBy(<FILL-IN>)      # newest change first (SEQUENCE BY)
    latest = batch_df.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")
    latest.createOrReplaceTempView("changes")
    latest.sparkSession.sql("""
      MERGE INTO lab3.customers_silver t USING changes s ON t.customer_id = s.customer_id
      WHEN MATCHED AND <FILL-IN> THEN DELETE
      WHEN MATCHED AND s.process_date >= t.process_date THEN
           UPDATE SET t.name = s.name, t.address = s.address, t.process_date = s.process_date
      WHEN NOT MATCHED AND s.operation != 'DELETE' THEN
           INSERT (customer_id, name, address, process_date) VALUES (s.customer_id, s.name, s.address, s.process_date)
    """)

def refresh_customers():
    (spark.readStream.format("json").schema(cdc_schema).load(landing.volume("customers"))
     .writeStream.foreachBatch(apply_changes)
          .option("checkpointLocation", checkpoint("lab3", "customers_cdc"))
          .trigger(availableNow=True).start().awaitTermination())''',
     '''def apply_changes(batch_df, batch_id):
    w = Window.partitionBy("customer_id").orderBy(F.col("process_date").desc())
    latest = batch_df.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")
    latest.createOrReplaceTempView("changes")
    latest.sparkSession.sql("""
      MERGE INTO lab3.customers_silver t USING changes s ON t.customer_id = s.customer_id
      WHEN MATCHED AND s.operation = 'DELETE' THEN DELETE
      WHEN MATCHED AND s.process_date >= t.process_date THEN
           UPDATE SET t.name = s.name, t.address = s.address, t.process_date = s.process_date
      WHEN NOT MATCHED AND s.operation != 'DELETE' THEN
           INSERT (customer_id, name, address, process_date) VALUES (s.customer_id, s.name, s.address, s.process_date)
    """)

def refresh_customers():
    (spark.readStream.format("json").schema(cdc_schema).load(landing.volume("customers"))
     .writeStream.foreachBatch(apply_changes)
          .option("checkpointLocation", checkpoint("lab3", "customers_cdc"))
          .trigger(availableNow=True).start().awaitTermination())'''),
    ("code", '''landing.land("customers", 1); refresh_customers()
print("after batch 1:"); show(spark.table("lab3.customers_silver").orderBy("customer_id"))
landing.land("customers", 1); refresh_customers()
print("after batch 2 (update, out-of-order update, delete, insert):"); show(spark.table("lab3.customers_silver").orderBy("customer_id"))
check("3d")'''),
    ("md", """## Next
- In Databricks Free Edition, open course 3's `2 Demo` and build the real pipeline in the **Lakeflow Pipelines Editor**:
  see the pipeline graph, dry run, full refresh, and the event log.
- Ask Claude: `/quiz sdp 5` or `/explain streaming table vs materialized view`."""),
]

# =====================================================================================
LAB4 = [
    ("md", """# Lab 4 — DevOps: modular code and unit tests (Course 4)
Lessons 4.1, 4.4 · exercises `4a`–`4c` · project folder `lab4_project/`

```
lab4_project/
├── pytest.ini              # pytest settings (pythonpath = .)
├── src/transforms.py       # ← 4a: write your functions here
└── tests/
    ├── conftest.py         # shared `spark` fixture
    └── test_transforms.py  # ← 4b/4c: write your tests here
```
Open the files in VS Code, edit them, then come back and run the cells. This is the same layout as the course's
`src/helpers/project_functions.py` + `tests/unit_tests/`.

""" + LEGEND),
    ("code", SETUP + '''\nimport subprocess, importlib
PROJECT = os.path.abspath("../lab4_project")
def pytest(*args):
    r = subprocess.run([sys.executable, "-m", "pytest", "-v", "-p", "no:cacheprovider", *args],
                       cwd=PROJECT, capture_output=True, text=True, env={**os.environ, "PYTHONPATH": os.path.abspath("..")})
    print(r.stdout[-4000:], r.stderr[-2000:])'''),

    ("md", """## 4a · Modularize PySpark code (lesson 4.1)
Course "before" code (everything in one block):
```python
df = spark.read.table("samples.nyctaxi.trips").withColumn("trip_distance_km", F.round(F.col("trip_distance") * 1.60934, 2))
df = df.select([F.col(c).alias(c.upper()) for c in df.columns])
```
**Task:** implement the 3 functions in `lab4_project/src/transforms.py` (docstrings explain each one).
Small functions = easy to **reuse** and easy to **unit test**."""),
    ("code", '''sys.path.insert(0, PROJECT)
import src.transforms as transforms
importlib.reload(transforms)
trips = spark.createDataFrame([(1.0, 0), (2.5, 1), (10.0, 2), (3.3, None)], ["trip_distance", "HighCholest"])
try:
    show(transforms.add_high_cholest_flag(transforms.uppercase_column_names(
         transforms.convert_miles_to_km(trips, "trip_distance_km", "trip_distance")).withColumnRenamed("HIGHCHOLEST", "HighCholest")))
except NotImplementedError:
    print("Not implemented yet — edit lab4_project/src/transforms.py")
check("4a")'''),

    ("md", """## 4b · Unit tests with pytest (lesson 4.4)
- pytest finds files `test_*.py` and functions `test_*` automatically.
- `pyspark.testing.utils.assertDataFrameEqual(actual, expected)` compares DataFrames (rows + schema);
  `assertSchemaEqual` compares only schemas.
- The `spark` fixture in `conftest.py` is created once and shared by all tests.

**Task:** add tests to `lab4_project/tests/test_transforms.py` (at least 3 tests in total)."""),
    ("code", 'pytest()\ncheck("4b")'),

    ("md", """## 4c · Do your tests really catch bugs?
The checker runs your tests against **6 buggy versions** of `transforms.py` (in `labutils/_mutants/`).
Good tests **fail** on every buggy version. Add tests for edge cases until no bug "survives"."""),
    ("code", 'check("4c")'),

    ("md", """## Concepts to know (no local lab)
**Integration tests (4.5)** — two ways: SDP expectations on test tables (`ON VIOLATION FAIL UPDATE`), or a Lakeflow
Job with tasks `Unit_Tests → ETL pipeline → integration test notebook`.

**Git folders (4.6)** — clone a GitHub repo into the workspace, branch, commit, push; merge with a pull request in GitHub;
then *pull* in Databricks. Authenticate with a Personal Access Token.

**Declarative Automation Bundles (4.7)** — read `lab4_project/databricks.yml`: one YAML file describes the job,
and **targets** `dev` / `prod` change only the settings. Commands: `databricks bundle validate`,
`databricks bundle deploy -t dev`, `databricks bundle run -t dev health_etl_job`."""),
    ("code", 'print(open(os.path.join(PROJECT, "databricks.yml")).read())'),
]

# =====================================================================================
LAB5 = [
    ("md", """# Lab 5 — Exam extras: Delta maintenance, SQL patterns, streaming (beyond course material)
Lessons 5.2, 5.4, 5.5 · exercises `5a`–`5d` · schema `lab5`

""" + LEGEND),
    ("code", SETUP + '\nreset_lab("lab5")'),

    ("md", """## 5a · OPTIMIZE, RESTORE, VACUUM (lesson 5.2)
Many small writes → many small files → slow reads. `OPTIMIZE` compacts them (`ZORDER BY` co-locates by column).
`RESTORE` rolls back to an old version. `VACUUM` deletes files not used by the current version (default keep 7 days) —
after it, time travel to old versions **fails** (you will see red Spark error logs — that is expected)."""),
    ("code", '''spark.sql("CREATE TABLE lab5.events_small (id INT, kind STRING)")
for i in range(12):
    spark.sql(f"INSERT INTO lab5.events_small VALUES ({i}, '{'click' if i % 2 else 'view'}')")
def files():
    return spark.sql("DESCRIBE DETAIL lab5.events_small").first().numFiles
print("files before OPTIMIZE:", files())'''),
    ("ex", '''# TODO 5a
spark.sql("<FILL-IN: OPTIMIZE with ZORDER BY id>")
print("files after OPTIMIZE:", files())
spark.sql("<FILL-IN: RESTORE the table to version 3>")
print("rows after RESTORE:", spark.table("lab5.events_small").count())
spark.sql("<FILL-IN: VACUUM keeping 0 hours (only OK in a lab!)>")''',
     '''spark.sql("OPTIMIZE lab5.events_small ZORDER BY (id)")
print("files after OPTIMIZE:", files())
spark.sql("RESTORE TABLE lab5.events_small TO VERSION AS OF 3")
print("rows after RESTORE:", spark.table("lab5.events_small").count())
spark.sql("VACUUM lab5.events_small RETAIN 0 HOURS")'''),
    ("code", '''show(spark.sql("DESCRIBE HISTORY lab5.events_small").select("version", "operation"))
try:
    # note: count(*) alone can be answered from the Delta log stats, so read real data:
    spark.sql("SELECT * FROM lab5.events_small VERSION AS OF 5").collect()
except Exception as e:
    print("Time travel after VACUUM fails:", type(e).__name__)
check("5a")'''),

    ("md", """## 5b · Latest row per key with a window function (lesson 5.4)
Very common exam pattern: `row_number() OVER (PARTITION BY key ORDER BY ts DESC)` then keep `rn = 1`."""),
    ("code", '''spark.sql("""CREATE OR REPLACE TEMP VIEW user_updates AS SELECT * FROM VALUES
  ('u1', 'u1@first.com',  TIMESTAMP'2024-01-01 10:00'),
  ('u1', 'u1@third.com',  TIMESTAMP'2024-03-01 10:00'),
  ('u1', 'u1@second.com', TIMESTAMP'2024-02-01 10:00'),
  ('u2', 'u2@x.com',      TIMESTAMP'2024-01-05 10:00'),
  ('u3', 'u3@x.com',      TIMESTAMP'2024-01-07 10:00'),
  ('u3', 'u3@x.com',      TIMESTAMP'2024-01-07 10:00')
  AS t(user_id, email, updated_at)""")'''),
    ("ex", '''# TODO 5b
spark.sql("""
CREATE OR REPLACE TABLE lab5.users_latest AS
WITH ranked AS (
  SELECT *, <FILL-IN> AS rn FROM user_updates)
SELECT user_id, email, updated_at FROM ranked WHERE rn = 1
""")''',
     '''spark.sql("""
CREATE OR REPLACE TABLE lab5.users_latest AS
WITH ranked AS (
  SELECT *, row_number() OVER (PARTITION BY user_id ORDER BY updated_at DESC) AS rn FROM user_updates)
SELECT user_id, email, updated_at FROM ranked WHERE rn = 1
""")'''),
    ("code", 'show(spark.table("lab5.users_latest")); check("5b")'),

    ("md", """## 5c · Higher-order functions on arrays (lesson 5.4)
Work on arrays **without exploding**: `size`, `transform(arr, x -> ...)`, `filter(arr, x -> ...)`,
`exists(arr, x -> ...)`, `aggregate(arr, start, (acc, x) -> ...)`."""),
    ("code", '''schema = "STRUCT<user_id: STRING, items: ARRAY<STRUCT<item_id: STRING, price_usd: DOUBLE, quantity: BIGINT>>>"
spark.sql(f"""CREATE OR REPLACE TEMP VIEW events AS
SELECT from_json(cast(unbase64(value) AS STRING), '{schema}') AS e FROM json.`{path('events-kafka')}`""")'''),
    ("ex", '''# TODO 5c
spark.sql("""
CREATE OR REPLACE TABLE lab5.event_item_totals AS
SELECT e.user_id,
       <FILL-IN> AS item_count,          -- number of items
       <FILL-IN> AS order_value,         -- sum of price_usd * quantity (aggregate)
       <FILL-IN> AS expensive_items      -- items with price_usd > 1000 (filter)
FROM events
""")''',
     '''spark.sql("""
CREATE OR REPLACE TABLE lab5.event_item_totals AS
SELECT e.user_id,
       size(e.items) AS item_count,
       aggregate(e.items, 0D, (acc, x) -> acc + x.price_usd * x.quantity) AS order_value,
       filter(e.items, x -> x.price_usd > 1000) AS expensive_items
FROM events
""")'''),
    ("code", 'show(spark.table("lab5.event_item_totals"), 8); check("5c")'),

    ("md", """## 5d · Streaming aggregation and output modes (lesson 5.5)
Output modes: **append** (only new rows — not allowed for aggregations without a watermark), **complete** (rewrite the
whole result), **update** (only changed rows). **Task:** pick the output mode that writes the full count table."""),
    ("code", '''landing.reset("orders_agg"); landing.land("orders_agg", 3)
orders_schema = "order_id BIGINT, order_timestamp STRING, customer_id BIGINT, notifications STRING"'''),
    ("ex", '''# TODO 5d
(spark.readStream.format("json").schema(orders_schema).load(landing.volume("orders_agg"))
      .groupBy("customer_id").agg(F.count("*").alias("n_orders"))
 .writeStream.outputMode("<FILL-IN>")
      .option("checkpointLocation", checkpoint("lab5", "orders_per_customer"))
      .trigger(availableNow=True).toTable("lab5.orders_per_customer").awaitTermination())''',
     '''(spark.readStream.format("json").schema(orders_schema).load(landing.volume("orders_agg"))
      .groupBy("customer_id").agg(F.count("*").alias("n_orders"))
 .writeStream.outputMode("complete")
      .option("checkpointLocation", checkpoint("lab5", "orders_per_customer"))
      .trigger(availableNow=True).toTable("lab5.orders_per_customer").awaitTermination())'''),
    ("code", 'show(spark.table("lab5.orders_per_customer").orderBy(F.desc("n_orders")), 5); check("5d")'),
]

NOTEBOOKS = {
    "lab1_ingestion": LAB1,
    "lab2_jobs": LAB2,
    "lab3_pipelines": LAB3,
    "lab4_devops": LAB4,
    "lab5_delta_sql_streaming": LAB5,
}
import sys as _sys  # noqa: E402
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from labs_exam import make as _make_exam_labs  # noqa: E402
NOTEBOOKS.update(_make_exam_labs(SETUP, LEGEND))


def _number_gaps(code):
    import re
    n = iter(range(1, 1000))
    return re.sub(r"<FILL-IN(?:[^<>\n]|<[^<>\n]*>)*>", lambda m: f"<FILL-IN {next(n)}>", code)


def build(cells, solution):
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {"name": "de-lab", "display_name": "DE Lab (.venv)", "language": "python"}
    for c in cells:
        if c[0] == "md":
            nb.cells.append(nbf.v4.new_markdown_cell(c[1]))
        elif c[0] == "code":
            nb.cells.append(nbf.v4.new_code_cell(c[1]))
        else:
            nb.cells.append(nbf.v4.new_code_cell(c[2] if solution else _number_gaps(c[1])))
    return nb


def main():
    (OUT / "solutions").mkdir(parents=True, exist_ok=True)
    for name, cells in NOTEBOOKS.items():
        nbf.write(build(cells, False), OUT / f"{name}.ipynb")
        nbf.write(build(cells, True), OUT / "solutions" / f"{name}_solution.ipynb")
        print("built", name)


if __name__ == "__main__":
    main()
