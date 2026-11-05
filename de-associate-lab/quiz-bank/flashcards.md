# Flashcards — FRONT :: BACK

## platform
- Three parts of Lakeflow? :: Connect (ingestion), Spark Declarative Pipelines (ETL, ex-DLT), Jobs (orchestration, ex-Workflows)
- Unity Catalog 3-level name? :: catalog.schema.table
- Path format for files in a volume? :: /Volumes/<catalog>/<schema>/<volume>/<path>
- Medallion layers? :: Bronze = raw, Silver = cleaned, Gold = business aggregates
- What is Photon? :: Databricks' vectorized C++ query engine — faster SQL/DataFrame work

## ingestion
- CTAS + read_files: batch or incremental? :: Batch — rereads all files every run
- COPY INTO is idempotent — meaning? :: Already-loaded files are skipped; running twice adds no duplicates
- FORMAT_OPTIONS vs COPY_OPTIONS? :: FORMAT = how to parse files (header, sep); COPY = behaviour (mergeSchema, force)
- Auto Loader format name in Python? :: format("cloudFiles") + option("cloudFiles.format", "json")
- Auto Loader is built on? :: Spark Structured Streaming (uses a checkpoint)
- SQL streaming table from files? :: CREATE OR REFRESH STREAMING TABLE t AS SELECT * FROM STREAM read_files(...)
- Two _metadata fields used in the course? :: _metadata.file_name and _metadata.file_modification_time
- What is _rescued_data? :: Column holding values that don't match the schema, as a JSON string
- Read field from JSON string column? :: colon syntax: col:field:subfield
- STRING vs STRUCT vs VARIANT for JSON? :: STRING flexible/slow; STRUCT schema-enforced/fast; VARIANT flexible + fast
- explode vs explode_outer? :: explode_outer keeps rows whose array is NULL or empty
- Lakehouse Federation? :: Query external databases in place, without moving data
- Delta Sharing? :: Open protocol to share data across platforms, clouds and regions

## delta
- What is in _delta_log? :: JSON commit files (+ checkpoints) = the transaction log; each commit = a version
- Time travel syntax? :: SELECT * FROM t VERSION AS OF 3  /  TIMESTAMP AS OF '2025-01-01'
- MERGE matched / not matched actions? :: Matched → UPDATE or DELETE; Not matched → INSERT; Not matched by source → UPDATE or DELETE
- MERGE schema evolution? :: MERGE WITH SCHEMA EVOLUTION INTO … or spark.databricks.delta.schema.autoMerge.enabled=true
- Managed vs external DROP? :: Managed deletes data + metadata; external deletes metadata only
- OPTIMIZE vs VACUUM? :: OPTIMIZE compacts small files; VACUUM deletes unreferenced old files (default 7 days)

## jobs
- Job vs task? :: Job = scheduled/orchestrated unit; task = one piece of work inside it
- Job param vs task param, same key? :: Job parameter wins
- Pass a value between tasks? :: dbutils.jobs.taskValues.set / get, or {{tasks.<task>.values.<key>}}
- Five trigger types? :: Scheduled (cron), file arrival, table update, continuous, manual
- Run-if options? :: All succeeded, At least one succeeded, None failed, All done, At least one failed, All failed
- For each task input variable? :: {{input}}
- Repair run? :: Re-run only failed tasks (+ downstream); can change parameters
- Job run history tables? :: system.lakeflow.jobs, job_tasks, job_run_timeline, job_task_run_timeline
- Why not all-purpose clusters in prod? :: Costly; use job clusters (terminate after run) or serverless
- Modular orchestration task? :: Run Job task (parent job calls child jobs)

## sdp
- Streaming table vs materialized view? :: ST: incremental, append, each record once. MV: result recomputed for current data
- Temporary view in a pipeline? :: Exists only during the pipeline; not registered in Unity Catalog
- Read a streaming table incrementally in SQL? :: FROM STREAM table_name
- Expectation default action? :: WARN — keep the row, log the metric
- DROP ROW vs FAIL UPDATE? :: DROP ROW removes bad rows; FAIL UPDATE stops the update
- Pipeline config in SQL? :: ${key}
- Triggered vs continuous pipeline? :: Triggered: run on available data then stop. Continuous: always on, low latency
- Event log contains? :: Audit logs, data-quality results, progress, lineage
- AUTO CDC INTO old name? :: APPLY CHANGES INTO
- SEQUENCE BY does what? :: Orders changes so out-of-order events apply correctly
- SCD Type 1 vs 2? :: Type 1 overwrites (no history); Type 2 keeps history with start/end columns
- Block full refresh? :: Table property pipelines.reset.allowed = false

## devops
- CI? :: Merge code often + run automated tests to catch errors early
- Continuous delivery vs deployment? :: Delivery: prod deploy is manual. Deployment: fully automatic to prod
- Test pyramid? :: Unit (fast, many) → Integration → System (slow, few)
- PySpark test helpers? :: assertDataFrameEqual, assertSchemaEqual (pyspark.testing.utils)
- pytest discovers? :: Files test_*.py and functions test_*
- Git folders authenticate with? :: Personal Access Token (PAT) or GitHub app
- DABs? :: Declarative Automation Bundles — YAML (databricks.yml) for resources + targets dev/stage/prod
- Bundle CLI commands? :: databricks bundle validate / deploy -t <target> / run -t <target> <job>
- REST API vs CLI vs SDK? :: API: raw HTTP · CLI: shell scripts/one-off · SDK: apps & automation in code
