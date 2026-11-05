# Course 1 — Data Ingestion with Lakeflow Connect (study notes)

Source: `source/text/slides/c1-ingestion.txt` + notebooks in `source/text/notebooks/c1-ingestion/`.

---
## §1 Lakeflow, Delta Lake, medallion  (slides 8–26, notebook 01)
**Lakeflow** = Databricks' unified data-engineering product. It has three parts:
| Part | Old name | Job |
|---|---|---|
| Lakeflow **Connect** | — | ingestion connectors |
| Lakeflow **Spark Declarative Pipelines** (SDP) | DLT / Delta Live Tables | ETL pipelines |
| Lakeflow **Jobs** | Workflows | orchestration |
They all run on Apache Spark + Structured Streaming, with **Unity Catalog** (governance) and
**Delta Lake** (storage).

**Lakeflow Connect connector types** (slide 17):
- *Upload files* — local file → volume or table.
- *Standard connectors* — cloud object storage, Kafka, … using batch, incremental batch or streaming.
- *Managed connectors* — SaaS apps (Salesforce, Workday, ServiceNow…) and databases (SQL Server, …).

**Three ingestion methods** (slides 18–20):
| Method | What it does | Tools |
|---|---|---|
| Batch | reprocesses **all** records every run | `CREATE TABLE AS` (CTAS), `spark.read.load()` |
| Incremental batch | only **new** data, old files skipped | `COPY INTO`, Auto Loader with timed trigger, `CREATE OR REFRESH STREAMING TABLE` |
| Streaming | continuous, near real-time micro-batches | Auto Loader with continuous trigger, SDP continuous mode |

**Delta Lake**: open-source protocol. A Delta table = a folder of **Parquet data files** + a
**`_delta_log/`** folder of JSON transaction-log files. Features: ACID transactions, DML
(UPDATE/DELETE/MERGE), time travel, schema enforcement & evolution.

**Medallion architecture**: Bronze (raw) → Silver (cleaned) → Gold (business-level aggregates).

**Unity Catalog 3-level namespace**: `catalog.schema.table`. Files live in **volumes**:
path is always `/Volumes/<catalog>/<schema>/<volume>/…`.
Useful commands: `SHOW SCHEMAS IN cat`, `DESCRIBE TABLE EXTENDED t`, `DESCRIBE VOLUME v`, `LIST '/Volumes/...'`.

⚠ **Exam trap:** `USE CATALOG x` / `USE SCHEMA y` set defaults so you can write only the table name.

---
## §2 Batch ingestion: CTAS + `read_files()`  (slides 29–32, 39; notebook 02A)
```sql
CREATE TABLE historical_users_bronze AS
SELECT * FROM read_files('/Volumes/dbacademy_ecommerce/v01/raw/users-historical',
                         format => 'parquet');
```
- `read_files()` reads JSON, CSV, XML, TEXT, BINARYFILE, PARQUET, AVRO, ORC; infers a unified schema;
  adds `_rescued_data` by default; can be used with `STREAM` for Auto Loader.
- Quick look without options: ``SELECT * FROM parquet.`/Volumes/.../path` `` (also `csv.`, `json.`, `text.`).
- CTAS creates a **Delta** table by default. It is **not** incremental: run again = reads everything again.
- Python: `spark.read.format("parquet").load(path).write.mode("overwrite").saveAsTable("t")`.

**Managed vs external tables**
| | Managed | External |
|---|---|---|
| Who manages data files | Databricks (UC managed storage) | you (your LOCATION) |
| `DROP TABLE` | deletes metadata **and data** | deletes metadata only, **data stays** |
| Recommended | yes, for new tables | sharing with other platforms / existing data |

---
## §3 Incremental batch: `COPY INTO` (legacy)  (slides 33–35)
```sql
CREATE TABLE IF NOT EXISTS users_bronze;          -- empty table, schema optional
COPY INTO users_bronze
  FROM '/Volumes/.../users-historical'
  FILEFORMAT = parquet
  FORMAT_OPTIONS ('header' = 'true')            -- how to PARSE the files
  COPY_OPTIONS ('mergeSchema' = 'true');        -- how COPY INTO BEHAVES
```
- **Idempotent & retriable**: files already loaded are **skipped** → run it twice, no duplicates.
- `COPY_OPTIONS ('force' = 'true')` reloads files even if already loaded.
- If the table has fewer columns than the files → schema mismatch error, fix with `mergeSchema`.
- Best for thousands of files; for millions use Auto Loader.

⚠ **Exam trap:** FORMAT_OPTIONS = parsing (header, sep…); COPY_OPTIONS = behaviour (mergeSchema, force).

---
## §4 Auto Loader & streaming tables  (slides 36–40; notebooks 02B, A2)
Auto Loader = incremental file ingestion built on **Structured Streaming**. Scales to millions of
files per hour; tracks processed files in a **checkpoint**; detects & evolves schema.

Python:
```python
(spark.readStream
   .format("cloudFiles")                        # ← "cloudFiles" means Auto Loader
   .option("cloudFiles.format", "csv")
   .option("cloudFiles.schemaLocation", checkpoint_path)
   .load("/Volumes/catalog/schema/files")
 .writeStream
   .option("checkpointLocation", checkpoint_path)
   .trigger(availableNow=True)                  # or processingTime="5 seconds"
   .toTable("catalog.schema.table"))
```
SQL (streaming table — needs a SQL warehouse or a pipeline):
```sql
CREATE OR REFRESH STREAMING TABLE sql_csv_autoloader
SCHEDULE EVERY 1 WEEK                       -- optional
AS SELECT * FROM STREAM read_files('/Volumes/.../src', format => 'CSV', sep => '|', header => true);

REFRESH STREAMING TABLE sql_csv_autoloader;  -- picks up only NEW files
```
**Comparison (slide 39)**
| | CTAS / spark.read | COPY INTO | Auto Loader |
|---|---|---|---|
| Type | batch | incremental batch | incremental batch or streaming |
| Scale | small datasets | thousands of files | millions+ files, billions for backfill |
| Idempotent | no | yes | yes |
| Schema evolution | manual / inferred | with options | automatic |
| Latency | high | moderate (scheduled) | low or high (config) |

⚠ **Exam trap:** `STREAM` keyword is required in SQL to get Auto Loader behaviour.
⚠ **Exam trap:** "millions of files / near real-time / schema drift" → answer is Auto Loader.

---
## §5 Metadata columns on ingest  (slides 41–44; notebook 03)
```sql
SELECT *,
  cast(from_unixtime(user_first_touch_timestamp / 1000000) AS DATE) AS first_touch_date,
  _metadata.file_modification_time AS file_modification_time,
  _metadata.file_name              AS source_file,
  current_timestamp()              AS ingestion_time
FROM read_files('/Volumes/.../users-historical', format => 'parquet');
```
`_metadata` is a hidden column available on file sources (also `file_path`, `file_size`).
Python: `.select("*", "_metadata.file_name")` or `F.col("_metadata.file_name")`.

---
## §6 Rescued data column  (slides 45–49; notebooks 04, 05L)
When a value does not match the schema, it is not lost: it goes into **`_rescued_data`** as a JSON
string, e.g. `{"cost":"$100","_file_path":"..."}`, and the typed column becomes NULL.
```sql
SELECT * FROM read_files('/Volumes/.../malformed.csv',
  format => 'csv', sep => '|', header => true,
  schema => 'order_id INT, email STRING, transactions_timestamp BIGINT',
  rescueddatacolumn => '_rescued_data');
```
- Data is rescued when: wrong type, column missing from schema, or case mismatch.
- Explicit schema = faster (no inference) and safer.
- Python: `.option("rescuedDataColumn", "_rescued_data")`.
- Fixing: `coalesce(price, cast(regexp_replace(_rescued_data:price, '[$]', '') AS DOUBLE))`.

---
## §7 Semi-structured JSON  (slides 50–67; notebooks 06, 07L)
Kafka-style data often has base64 `key`/`value` → decode: `cast(unbase64(value) AS STRING)`.

Three ways to hold JSON:
| Type | How to query | Pros / cons |
|---|---|---|
| STRING | `json_col:address:city` (colon syntax) | flexible, slow, no schema |
| STRUCT | `from_json(json_col, '<schema>')` then `col.address.city` | schema enforced, fast |
| VARIANT | `parse_json(json_col)` then `v:user_id::STRING` | flexible + fast (newer) |
```sql
SELECT schema_of_json('{"a":1,"b":[1,2]}');                -- returns the STRUCT schema string
SELECT from_json(decoded_value, 'STRUCT<user_id: STRING, items: ARRAY<STRUCT<item_id: STRING, price_usd: DOUBLE>>>') AS s
FROM kafka_events_bronze_decoded;
SELECT s.user_id, explode(s.items) AS item FROM t;          -- one row per array element
```
- `explode()` drops rows whose array is NULL/empty; `explode_outer()` keeps them (with NULL).
- JSON types → SQL: string→STRING, number→INT/DOUBLE, boolean→BOOLEAN, object→STRUCT, array→ARRAY.
- XML (appendix A1): `read_files(..., format => 'xml', rowTag => 'book')`.

---
## §8 Enterprise ingestion & alternatives  (slides 68–84; notebook 08)
- **Managed connectors** (Lakeflow Connect): UI or API; fully managed; credentials stored in UC;
  run as **serverless pipelines** writing to **streaming tables**.
  - SaaS: pipeline calls the app API directly.
  - Databases: an **ingestion gateway** (classic compute) reads changes → staging in a UC
    **volume** → serverless pipeline loads streaming tables.
- **Partner Connect**: third-party tools (Fivetran, Qlik, Informatica, Rivery…).
- **Lakehouse Federation**: *query* external databases **without moving data** (ad-hoc, POC).
- **Delta Sharing**: open protocol to share data securely across platforms, clouds, regions.
- **Databricks Marketplace**: datasets, notebooks, models, dashboards — powered by Delta Sharing.

---
## §9 MERGE INTO, history, time travel  (slides 85–94; notebook 09)
```sql
MERGE INTO main_users_target t
USING update_users_source s
ON t.id = s.id
WHEN MATCHED AND s.status = 'update' THEN UPDATE SET t.email = s.email, t.status = s.status
WHEN MATCHED AND s.status = 'delete' THEN DELETE
WHEN NOT MATCHED THEN INSERT (id, first_name, email, sign_up_date, status)
                      VALUES (s.id, s.first_name, s.email, s.sign_up_date, s.status);
```
- Matched → UPDATE or DELETE. Not matched (by target) → INSERT. `WHEN NOT MATCHED BY SOURCE` → UPDATE/DELETE.
- Use for upserts, SCD, CDC, and **de-duplicating** inserts (insert only if not matched).
- Source has a new column → error (schema enforcement). Fix: `MERGE WITH SCHEMA EVOLUTION INTO …`
  (DBR 15.2+) or `SET spark.databricks.delta.schema.autoMerge.enabled = true`.
- `DESCRIBE HISTORY t` → versions; `SELECT * FROM t VERSION AS OF 1` / `TIMESTAMP AS OF '…'`;
  `RESTORE TABLE t TO VERSION AS OF 1`.
