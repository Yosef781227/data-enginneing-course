# Extra exam topics — beyond the 4 course folders

These topics appear in the Data Engineer Associate exam guide but are only touched lightly
(or not at all) in your training folder. Facts here come from general Databricks knowledge,
**not** from your course files. Check details against docs.databricks.com.

---
## §1 Unity Catalog governance
- Hierarchy: **metastore** (one per region) → **catalog** → **schema** (database) →
  tables, views, **volumes**, functions, models. Name: `catalog.schema.object`.
- Securables need privileges. Common privileges: `USE CATALOG`, `USE SCHEMA`, `SELECT`, `MODIFY`,
  `CREATE TABLE`, `CREATE SCHEMA`, `READ VOLUME`, `WRITE VOLUME`, `ALL PRIVILEGES`.
  To read a table a user needs **USE CATALOG + USE SCHEMA + SELECT**.
```sql
GRANT USE CATALOG ON CATALOG sales TO `analysts`;
GRANT USE SCHEMA  ON SCHEMA sales.gold TO `analysts`;
GRANT SELECT      ON TABLE  sales.gold.revenue TO `analysts`;
REVOKE SELECT ON TABLE sales.gold.revenue FROM `analysts`;
SHOW GRANTS ON TABLE sales.gold.revenue;
```
- **Owner** of an object can grant privileges on it. Prefer granting to **groups**, not users.
  Use **service principals** for automated jobs.
- Managed tables/volumes: UC manages storage; DROP deletes data. External: use **storage
  credentials** + **external locations**; DROP keeps files.
- UC gives **automatic lineage** (table & column level), audit logs, and data discovery.
- Row filters and column masks for fine-grained access; dynamic views with `is_account_group_member()`.
- **Delta Sharing**: share tables to other orgs/platforms; provider creates a **share** and a
  **recipient**. Databricks-to-Databricks sharing or open sharing (token).
- **Lakehouse Federation**: create a **connection** + **foreign catalog** to query MySQL,
  PostgreSQL, Snowflake… in place.

## §2 Delta Lake maintenance & optimization
| Command | What it does |
|---|---|
| `OPTIMIZE t` | compacts many small files into larger ones |
| `OPTIMIZE t ZORDER BY (col)` | co-locates data by column for data skipping (older method) |
| `CLUSTER BY (col)` on CREATE / ALTER | **liquid clustering** (recommended over partitioning + Z-order) |
| `VACUUM t [RETAIN n HOURS]` | deletes data files no longer referenced; default retention **7 days**; after vacuum you cannot time-travel past retention |
| `RESTORE TABLE t TO VERSION AS OF n` | roll back |
| `DESCRIBE HISTORY t` / `DESCRIBE DETAIL t` | version log / size, files, location |
| `CREATE TABLE … SHALLOW CLONE / DEEP CLONE src` | copy metadata only / copy data too |
- **Predictive optimization** (UC managed tables) runs OPTIMIZE/VACUUM automatically.
- Partition only very large tables on low-cardinality columns; prefer liquid clustering.
- Generated columns, `CHECK` constraints and `NOT NULL` constraints enforce quality on Delta tables.

## §3 Compute & platform
- **Control plane** (Databricks account: UI, jobs, notebooks) vs **compute plane** (where data is
  processed; serverless in Databricks account, classic in your cloud account).
- **All-purpose cluster**: interactive, shared, dev. **Job cluster**: per job run, auto-terminates.
- **SQL warehouse**: for SQL/BI (serverless, pro, classic). **Serverless** compute: no cluster setup.
- **Photon**: vectorized C++ engine → faster SQL/DataFrame workloads.
- Cluster access modes: *Standard* (shared, UC-safe) vs *Dedicated* (single user).
- Auto-termination saves cost; autoscaling adjusts workers; cluster policies limit config.
- **Databricks Runtime (DBR)**: Spark + libraries version; LTS versions for stability.

## §4 Spark SQL & PySpark transformations (common exam code)
```sql
-- CTE + window function: latest row per key (de-duplicate)
WITH ranked AS (
  SELECT *, row_number() OVER (PARTITION BY user_id ORDER BY updated_at DESC) AS rn FROM users)
SELECT * FROM ranked WHERE rn = 1;

SELECT DISTINCT * FROM t;                 -- remove exact duplicates
SELECT count(*), count(col), count_if(col IS NULL) FROM t;   -- count(col) skips NULLs!

-- Higher-order functions on arrays
SELECT transform(items, x -> x.price * 2), filter(items, x -> x.qty > 0),
       exists(items, x -> x.qty = 0), aggregate(prices, 0D, (acc, x) -> acc + x) FROM t;

-- PIVOT
SELECT * FROM (SELECT region, quarter, amount FROM sales)
PIVOT (sum(amount) FOR quarter IN ('Q1','Q2','Q3','Q4'));

-- SQL UDF
CREATE FUNCTION to_km(miles DOUBLE) RETURNS DOUBLE RETURN round(miles * 1.60934, 2);
```
- Joins: INNER, LEFT, RIGHT, FULL, LEFT SEMI (keep rows with a match), LEFT ANTI (keep rows
  without a match), CROSS. `UNION` removes duplicates, `UNION ALL` keeps them.
- Dates: `date_format`, `to_date`, `from_unixtime`, `date_add`, `datediff`, `current_timestamp`.
- PySpark: `df.select / withColumn / filter / groupBy().agg / join / dropDuplicates / na.fill`,
  `F.col, F.when().otherwise(), F.explode, F.from_json`. `df.createOrReplaceTempView("v")`
  makes a DataFrame queryable in SQL.
- Views: **view** (saved in catalog), **temporary view** (session only),
  **global temp view** (`global_temp.` schema, across notebooks on the same cluster).

## §5 Structured Streaming basics
- `spark.readStream … .writeStream` with a **checkpointLocation** (stores progress → exactly-once).
- Triggers: default (micro-batch ASAP), `processingTime="1 minute"`, `availableNow=True`
  (process everything available in batches, then stop — incremental batch), `once=True` (old).
- Output modes: **append** (new rows only), **complete** (whole result, for aggregations),
  **update** (changed rows).
- **Watermark** `withWatermark("event_time", "10 minutes")` limits state for late data in
  aggregations and stream–stream joins.
- A streaming source must be **append-only**; to stream from a table that has updates/deletes use
  `skipChangeCommits` or Change Data Feed.
