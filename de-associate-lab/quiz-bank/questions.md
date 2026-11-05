# Question bank (for the tutor)

Exam-style questions grounded in the course material. The tutor uses these as **inspiration** and
writes variations — do not show the answer key to the learner before they answer.
Format: `[tag] (lesson) Question` · options · **Answer** · why · source.

---
## Ingestion `[ingestion]`
1. (1.3) A daily job runs `COPY INTO sales_bronze FROM '/Volumes/raw/sales' FILEFORMAT = CSV`. Yesterday's run loaded 10 files; today 2 new files arrived and the job runs twice by mistake. How many files are loaded today in total?
   A. 24 B. 12 C. 2 D. 4
   **C** — COPY INTO is idempotent: already-loaded files are skipped, so the second run loads 0. *(Course 1, slide 35)*
2. (1.3) Which COPY INTO clause lets the target table's schema evolve when files have new columns?
   A. `FORMAT_OPTIONS ('header'='true')` B. `COPY_OPTIONS ('mergeSchema'='true')` C. `FILEFORMAT = DELTA` D. `OPTIONS (inferSchema true)`
   **B** — COPY_OPTIONS controls the operation (mergeSchema, force); FORMAT_OPTIONS controls parsing. *(slide 35)*
3. (1.4) A team must ingest millions of JSON files per hour, with new columns appearing over time, at low latency. Best choice?
   A. CTAS with read_files B. COPY INTO C. Auto Loader D. INSERT OVERWRITE
   **C** — Auto Loader scales to millions of files/hour and evolves schema automatically. *(slide 39)*
4. (1.4) In Databricks SQL, which keyword makes `read_files` read incrementally inside a streaming table?
   A. `INCREMENTAL` B. `LIVE` C. `STREAM` D. `CONTINUOUS`
   **C** — `FROM STREAM read_files(...)`. *(slide 38; notebook 02B)*
5. (1.4) In Python, which `format()` value means Auto Loader?
   A. `"autoloader"` B. `"cloudFiles"` C. `"delta"` D. `"stream"`
   **B** *(slide 38)*
6. (1.2) What does `DROP TABLE` do to an **external** table?
   A. Deletes data and metadata B. Deletes only metadata; files stay C. Moves files to trash D. Fails
   **B** *(notebook 02A, managed vs external)*
7. (1.5) Which expression adds the source file name in a bronze table?
   A. `input_file()` B. `_metadata.file_name` C. `_file_name()` D. `current_file`
   **B** — `_metadata.file_name`; also `_metadata.file_modification_time`. *(slide 43)*
8. (1.6) A CSV column `cost` is read as BIGINT, but one row contains `$100`. With read_files defaults, what happens?
   A. The query fails B. The row is dropped C. `cost` is NULL and `$100` is stored in `_rescued_data` D. `cost` becomes STRING
   **C** *(slides 46–47)*
9. (1.7) `json_col` is a JSON-formatted STRING. Which returns the city?
   A. `json_col.address.city` B. `json_col:address:city` C. `json_col['address.city']` D. `get(json_col, city)`
   **B** — colon syntax for JSON strings; dot syntax is for STRUCT. *(slide 55)*
10. (1.7) Which function returns the STRUCT schema of a JSON string?
    A. `from_json` B. `to_json` C. `schema_of_json` D. `parse_json`
    **C** — then use it in `from_json(col, schema)`. *(slides 63–64)*
11. (1.7) An `items` array is empty for some events. You need one row per item **and** keep events without items. Use:
    A. `explode` B. `explode_outer` C. `flatten` D. `posexplode`
    **B** *(notebook 06)*
12. (1.9) In `MERGE INTO`, rows in the source that have no match in the target can be handled with:
    A. `WHEN MATCHED THEN INSERT` B. `WHEN NOT MATCHED THEN INSERT` C. `WHEN NOT MATCHED THEN UPDATE` D. `ON CONFLICT DO INSERT`
    **B** *(slide 86)*
13. (1.9) A MERGE fails because the source has a new column. Which fixes it on DBR 15.2+?
    A. `MERGE WITH SCHEMA EVOLUTION INTO …` B. `MERGE INTO … OPTIONS (overwriteSchema)` C. `ALTER TABLE … SET TBLPROPERTIES ('delta.mergeSchema')` D. `MERGE FORCE INTO`
    **A** — or set `spark.databricks.delta.schema.autoMerge.enabled = true`. *(notebook 09)*
14. (1.8) Query a PostgreSQL database from Databricks **without copying the data**:
    A. Delta Sharing B. Lakehouse Federation C. Auto Loader D. Partner Connect
    **B** *(slide 82)*
15. (1.8) Managed connectors for databases use which component to read source changes?
    A. SQL warehouse B. Ingestion gateway (classic compute) C. Delta Sharing server D. Auto Loader
    **B** — then a serverless pipeline loads streaming tables. *(slide 75)*

## Delta `[delta]`
16. (1.1) What does the `_delta_log` folder contain?
    A. Parquet data B. JSON transaction log files recording each version C. Checkpoints for Auto Loader D. Table permissions
    **B** *(slide 23)*
17. (1.9) Query a table as it was 2 versions ago:
    A. `SELECT * FROM t@v2` B. `SELECT * FROM t VERSION AS OF 2` C. `SELECT * FROM HISTORY(t, 2)` D. `RESTORE t 2`
    **B** — VERSION AS OF *n* is a version number; check `DESCRIBE HISTORY` to find it.
18. (5.2) After `VACUUM t RETAIN 168 HOURS`, what is no longer possible?
    A. Querying the current version B. Time travel to versions whose files were removed C. Running OPTIMIZE D. INSERT *(beyond course)*
    **B**
19. (5.2) Many small files slow down queries. Which command compacts them?
    A. VACUUM B. OPTIMIZE C. ANALYZE D. REFRESH *(beyond course)*
    **B**

## Lakeflow Jobs `[jobs]`
20. (2.1) Cheapest reliable compute for a nightly production notebook job?
    A. Shared all-purpose cluster B. Job cluster or serverless jobs compute C. SQL warehouse D. Single-node interactive cluster
    **B** — all-purpose clusters are for interactive work and cost more. *(slides 28, 87)*
21. (2.3) A job parameter `env=prod` and a task parameter `env=dev` both exist. What does the task see?
    A. dev B. prod C. both D. error
    **B** — job parameters override task parameters with the same key. *(slide 44)*
22. (2.3) Task A computes a row count that task B needs. Best way to pass it?
    A. Write it to a widget B. `dbutils.jobs.taskValues.set` in A and `taskValues.get` (or `{{tasks.A.values.key}}`) in B C. A global Python variable D. A job parameter
    **B** *(slide 48)*
23. (2.4) Start a job when new files land in a Unity Catalog volume:
    A. Scheduled trigger B. File arrival trigger C. Continuous trigger D. Table update trigger
    **B** *(slide 56)*
24. (2.4) A job must start a new run as soon as the previous run finishes, for a streaming workload:
    A. Continuous B. Cron every minute C. Manual D. File arrival
    **A** *(slide 57)*
25. (2.5) Task D depends on B and C and should run if **at least one** of them succeeded:
    A. All succeeded B. At least one succeeded C. All done D. None failed
    **B** *(slide 67)*
26. (2.5) Run the same notebook for each of `["CA","NY","VA"]` in parallel:
    A. If/else task B. For each task with concurrency C. Three jobs D. Run Job task
    **B** — the item is passed as `{{input}}`. *(slide 73)*
27. (2.6) A 10-task job failed at task 8. How do you re-run only what is needed?
    A. Run now B. Repair run C. Clone the job D. Reset the job
    **B** — repair re-runs failed tasks and their dependents only. *(slide 78)*
28. (2.6) Which catalog holds job run history as system tables?
    A. `system.billing` B. `system.lakeflow` C. `system.access` D. `hive_metastore`
    **B** — `jobs`, `job_tasks`, `job_run_timeline`, `job_task_run_timeline`. *(slide 82)*
29. (2.7) Split a huge job into a parent job that calls smaller jobs:
    A. For each task B. Run Job task C. If/else task D. Pipeline task
    **B** *(slide 92)*

## Spark Declarative Pipelines `[sdp]`
30. (3.1) Which dataset reads only new rows from its source on each update?
    A. Materialized view B. Streaming table C. Temporary view D. View
    **B** *(slide 31)*
31. (3.1) A gold table with `GROUP BY` over all silver data should be a:
    A. Streaming table B. Materialized view C. Temporary view D. External table
    **B** — results are recomputed (incrementally where possible on serverless). *(slides 35–36)*
32. (3.1) Which is **not** registered in Unity Catalog?
    A. Streaming table B. Materialized view C. Temporary view D. View
    **C** *(slide 38)*
33. (3.1) Old DLT syntax `CREATE OR REFRESH LIVE TABLE` corresponds to today's:
    A. STREAMING TABLE B. MATERIALIZED VIEW C. VIEW D. TEMPORARY VIEW
    **B** *(slide 40)*
34. (3.3) `CONSTRAINT valid_id EXPECT (id IS NOT NULL)` with no ON VIOLATION clause. A row has NULL id. Result?
    A. Row dropped B. Update fails C. Row kept; violation counted in metrics D. Row moved to quarantine
    **C** — default action is WARN. *(slide 54)*
35. (3.3) Stop the pipeline update when any row violates a rule:
    A. `ON VIOLATION DROP ROW` B. `ON VIOLATION FAIL UPDATE` C. `ON VIOLATION STOP` D. `ON VIOLATION WARN`
    **B** *(slide 54)*
36. (3.2) How do you reference pipeline configuration key `source` in SQL code?
    A. `{{source}}` B. `${source}` C. `:source` D. `$source$`
    **B** *(slide 50)*
37. (3.4) Difference between triggered and continuous pipeline mode?
    A. Triggered processes available data then stops; continuous keeps running for low latency B. Triggered is streaming only C. Continuous cannot use streaming tables D. No difference
    **A** *(slide 73)*
38. (3.5) In `AUTO CDC INTO`, which clause handles records that arrive out of order?
    A. KEYS B. SEQUENCE BY C. APPLY AS DELETE WHEN D. STORED AS SCD TYPE 1
    **B** *(slide 84)*
39. (3.5) Keep full history of changes with start/end columns:
    A. SCD Type 1 B. SCD Type 2 C. Append only D. MERGE without WHEN MATCHED
    **B** *(slide 83)*
40. (3.2) What does a **full refresh** do?
    A. Processes only new data B. Clears data and checkpoints and reprocesses everything C. Refreshes only MVs D. Validates code without running
    **B** — block with `pipelines.reset.allowed = false`. *(notebook 2)*

## DevOps `[devops]`
41. (4.2) Code passes tests and is deployed to staging automatically, but production deployment needs manual approval. This is:
    A. Continuous integration only B. Continuous delivery C. Continuous deployment D. Manual release
    **B** *(Course 4 CD slides)*
42. (4.4) Which compares two DataFrames in a PySpark unit test?
    A. `df1 == df2` B. `pyspark.testing.utils.assertDataFrameEqual` C. `df.compare()` D. `assertSchemaEqual` only
    **B** *(slide 63)*
43. (4.4) Which test type is fastest and tests a single function in isolation?
    A. System B. Integration C. Unit D. Load
    **C**
44. (4.7) Databricks' recommended way to define and deploy jobs and pipelines to dev/stage/prod from YAML:
    A. REST API scripts B. Declarative Automation Bundles (DABs) C. Copying notebooks D. Repos API only
    **B** *(Course 4 CD slides)*
45. (4.3) Two ways to isolate dev, stage and prod in Databricks:
    A. Separate workspaces or separate Unity Catalog catalogs B. Separate notebooks C. Separate clusters only D. Separate DBR versions
    **A**

## Governance & platform `[governance]` `[platform]`
46. (5.1) A user needs to read `main.sales.orders`. Minimum privileges? *(beyond course)*
    A. SELECT on the table B. USE CATALOG on main, USE SCHEMA on main.sales, SELECT on the table C. ALL PRIVILEGES on main D. MODIFY on the table
    **B**
47. (1.1) Which Lakeflow component orchestrates notebooks, pipelines and SQL tasks?
    A. Connect B. Spark Declarative Pipelines C. Jobs D. Unity Catalog
    **C** *(slide 11)*
48. (1.8) Share live Delta tables securely with a partner company on another cloud:
    A. Lakehouse Federation B. Delta Sharing C. COPY INTO D. External tables
    **B** *(slide 82)*
