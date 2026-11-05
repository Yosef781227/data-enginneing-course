# Course 3 — Lakeflow Spark Declarative Pipelines (study notes)

Source: `source/text/slides/c3-pipelines.txt` + notebooks in `source/text/notebooks/c3-pipelines/`.
**SDP = Spark Declarative Pipelines**, previously **DLT (Delta Live Tables)** / Lakeflow Declarative Pipelines.

---
## §1 What SDP is; dataset types  (slides 12–41)
Without SDP you hand-code checkpoints, retries, dependency order, quality checks, backfills.
With SDP you **declare** the tables; SDP handles orchestration, checkpoints, retries, scaling.

| Dataset | SQL | Processes | Typical layer |
|---|---|---|---|
| **Streaming table (ST)** | `CREATE OR REFRESH STREAMING TABLE` | only **new** data, appended; each file read **exactly once** | bronze, silver |
| **Materialized view (MV)** | `CREATE OR REFRESH MATERIALIZED VIEW` | result **recomputed** to be correct for current data (incremental refresh on serverless when possible) | gold, aggregations, joins |
| **View** | `CREATE VIEW` | no data stored; registered in UC; can't be a streaming source | — |
| **Temporary view** | `CREATE TEMPORARY VIEW` | only during pipeline, **not** in UC | intermediate steps |

```sql
CREATE OR REFRESH STREAMING TABLE 1_bronze_db.orders_bronze AS
SELECT *, current_timestamp() AS processing_time, _metadata.file_name AS source_file
FROM STREAM read_files('${source}/orders', format => 'JSON');

CREATE OR REFRESH STREAMING TABLE 2_silver_db.orders_silver AS
SELECT order_id, timestamp(order_timestamp) AS order_timestamp, customer_id, notifications
FROM STREAM 1_bronze_db.orders_bronze;              -- STREAM = read only new rows

CREATE OR REFRESH MATERIALIZED VIEW 3_gold_db.gold_orders_by_date AS
SELECT date(order_timestamp) AS order_date, count(*) AS total_daily_orders
FROM 2_silver_db.orders_silver                       -- no STREAM for MV
GROUP BY date(order_timestamp);
```
- **Dependencies are parsed automatically** → file/code order does not matter; SDP builds the DAG
  (pipeline graph).
- Old syntax (still works): `CREATE OR REFRESH STREAMING LIVE TABLE`, `CREATE OR REFRESH LIVE TABLE`
  (= MV), `CREATE LIVE VIEW`, `LIVE.table_name`.
- Python: `from pyspark import pipelines as dp` with `@dp.table`, `@dp.materialized_view`,
  `@dp.expect…` (old: `import dlt`, `@dlt.table`).

⚠ **Exam trap:** aggregation over everything → MV. Append-only incremental ingestion → ST.

---
## §2 Pipeline editor & settings  (slides 42–52; notebook 2)
- **Lakeflow Pipelines Editor** (multi-file editor): folders of `.sql`/`.py` files, pipeline graph,
  dry run, data preview.
- Settings: **compute** (serverless recommended; classic fixed-size or **enhanced autoscaling**),
  **code assets** (root folder + source files), **default catalog & schema**, **configuration**
  (key-value parameters), environment, tags, budget, advanced (event log table…).
- Use configuration in SQL with `${key}` → `FROM STREAM read_files('${source}/orders', …)`.
  In Python: `spark.conf.get("source")`.
- **Dry run** validates code without writing data. **Full refresh** deletes data + checkpoints and
  reprocesses everything; block it with table property `pipelines.reset.allowed = false`.

---
## §3 Data quality expectations  (slides 53–58; notebooks 3, 4)
`CONSTRAINT <name> EXPECT (<condition>) [ON VIOLATION <action>]`
| Action | Bad rows | Pipeline |
|---|---|---|
| *(none)* = **WARN** (default) | **kept** in target | continues; metrics logged |
| `DROP ROW` | **removed** | continues; drop count logged |
| `FAIL UPDATE` | — | the **update fails** (flow stops; needs fix & rerun) |
```sql
CREATE OR REFRESH STREAMING TABLE 2_silver_db.orders_silver (
  CONSTRAINT valid_notifications EXPECT (notifications IN ('Y','N')),
  CONSTRAINT valid_date EXPECT (order_timestamp > '2021-01-01') ON VIOLATION FAIL UPDATE,
  CONSTRAINT valid_id   EXPECT (customer_id IS NOT NULL)        ON VIOLATION DROP ROW
) AS SELECT … FROM STREAM 1_bronze_db.orders_bronze;
```
Python: `@dp.expect`, `@dp.expect_or_drop`, `@dp.expect_or_fail`, `@dp.expect_all…({...})`.
Metrics appear in the pipeline UI and **event log**. MVs with expectations are fully refreshed.

---
## §4 Joins, production, event log  (slides 62–78; notebook 5)
- **Stream–snapshot (static) join**: new rows of a ST join to **all** rows of a lookup table.
- **ST + ST → MV join**: an MV joins all rows of two streaming tables, recomputed each run.
- Stream–stream joins are out of course scope (need watermarks).
- **Pipeline modes**: **Triggered** — process available data then stop (manual or scheduled).
  **Continuous** — keep running, low latency, always-on compute.
- Production: schedule, email notifications (start/success/failure), monitor.
- **Event log** = audit logs, data quality results, progress, lineage. Default: hidden Delta table
  in the pipeline's default catalog/schema; can publish as a named table (advanced settings).
  Query with `SELECT * FROM event_log(TABLE(my_st))` or the published table.

---
## §5 Change Data Capture: AUTO CDC INTO  (slides 79–88)
- **CDC** = capture inserts/updates/deletes from a source and apply them to a target.
- **SCD Type 1**: overwrite with latest values, delete = remove, **no history**.
- **SCD Type 2**: keep history: old row closed with `__END_AT`, new row with `__START_AT`.
```sql
CREATE OR REFRESH STREAMING TABLE customers_silver;      -- target must be a streaming table

CREATE FLOW scd_type_1_flow AS
AUTO CDC INTO customers_silver            -- formerly APPLY CHANGES INTO
FROM STREAM customers_bronze_clean
KEYS (customer_id)                        -- unique key
APPLY AS DELETE WHEN operation = 'DELETE'
SEQUENCE BY process_date                  -- ordering column: handles out-of-order events
COLUMNS * EXCEPT (operation, _rescued_data)
STORED AS SCD TYPE 1;                     -- or SCD TYPE 2
```
Python: `dp.create_auto_cdc_flow(...)` (old `dlt.apply_changes`).
⚠ **Exam trap:** `SEQUENCE BY` is what handles out-of-order records; `KEYS` identifies the row.
