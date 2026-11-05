"""Per-exercise teaching content shown in the portal after the task passes:
`why` = how it works / what to remember for the exam, plus one exam-style question."""

C = {
 "1a": dict(
  why="Every write to a Delta table adds a JSON file to `_delta_log/`. Each file = one **version**. "
      "That log gives ACID transactions, `DESCRIBE HISTORY` and time travel. The data itself is Parquet.",
  q="What does the `_delta_log` folder contain?",
  opts=["The Parquet data files", "JSON commit files — one per table version", "Auto Loader checkpoints", "Table permissions"],
  a=1, ex="The transaction log records every change as a numbered JSON commit (Course 1, slide 23)."),
 "1b": dict(
  why="CTAS = `CREATE TABLE … AS SELECT`. It creates a **Delta** table and reads **all** files every time — it is "
      "**batch**, not incremental. On Databricks you write `FROM read_files('/Volumes/…', format => 'parquet')`. "
      "Managed table: DROP deletes data too. External table (with LOCATION): DROP keeps the files.",
  q="You run the same CTAS + read_files job every day. What happens to files loaded yesterday?",
  opts=["They are skipped", "They are read again", "They are deleted", "The job fails"],
  a=1, ex="CTAS is batch: it re-reads everything each run. For only-new-files use COPY INTO or Auto Loader."),
 "1c": dict(
  why="COPY INTO remembers which files it already loaded and **skips** them → **idempotent** (run twice = no duplicates). "
      "`COPY_OPTIONS ('mergeSchema'='true')` lets new columns in; `'force'='true'` reloads everything. "
      "`FORMAT_OPTIONS` is only for parsing (header, sep).",
  q="New files have an extra column. Where do you put `mergeSchema = 'true'` in COPY INTO?",
  opts=["FORMAT_OPTIONS", "COPY_OPTIONS", "FILEFORMAT", "TBLPROPERTIES"],
  a=1, ex="COPY_OPTIONS controls how COPY INTO behaves (mergeSchema, force). Course 1, slide 35."),
 "1d": dict(
  why="Auto Loader (`format(\"cloudFiles\")`) is built on **Structured Streaming**. The **checkpoint** remembers "
      "processed files, so each file is read once. `trigger(availableNow=True)` = process what is new, then stop. "
      "In SQL: `CREATE OR REFRESH STREAMING TABLE … FROM STREAM read_files(…)`.",
  q="Millions of new JSON files per hour, new columns appear sometimes. Best ingestion method?",
  opts=["CTAS with read_files", "COPY INTO", "Auto Loader", "INSERT OVERWRITE"],
  a=2, ex="Auto Loader scales to millions of files and evolves schema automatically (slide 39)."),
 "1e": dict(
  why="Every file source has a hidden `_metadata` column. In bronze tables we add "
      "`_metadata.file_name`, `_metadata.file_modification_time` and `current_timestamp()` so we always know "
      "where and when each row came from.",
  q="Which expression adds the source file name to each row?",
  opts=["input_file()", "_metadata.file_name", "current_file()", "_file_path"],
  a=1, ex="_metadata.file_name (and file_modification_time) — Course 1, slide 43."),
 "1f": dict(
  why="When a value does not fit the schema (like `$945.00` into DOUBLE) it is not lost. On Databricks it goes to "
      "`_rescued_data` as JSON and the column is NULL. You fix it later, e.g. "
      "`coalesce(price, cast(replace(_rescued_data:price,'$','') AS DOUBLE))`.",
  q="Column `cost` is BIGINT, one row has `$100`. With read_files defaults, what happens?",
  opts=["The query fails", "The row is dropped", "cost is NULL and $100 goes to _rescued_data", "cost becomes STRING"],
  a=2, ex="The rescued data column keeps malformed values (slides 46–47)."),
 "1g": dict(
  why="Kafka values are base64 → `cast(unbase64(value) AS STRING)`. A JSON string can be read with colon syntax "
      "(`col:field`), or parsed to a STRUCT with `from_json(col, schema)`; `schema_of_json` gives the schema. "
      "`explode` makes one row per array item; **`explode_outer` keeps rows with empty arrays**.",
  q="You need one row per item AND keep events that have no items. Use:",
  opts=["explode", "explode_outer", "flatten", "from_json"],
  a=1, ex="explode drops rows whose array is empty or NULL; explode_outer keeps them."),
 "1h": dict(
  why="MERGE = upsert. Matched → UPDATE or DELETE; not matched → INSERT. A new source column fails "
      "(schema enforcement) unless you use `MERGE WITH SCHEMA EVOLUTION` or the autoMerge setting. "
      "Each MERGE is a new version → `VERSION AS OF` shows old data.",
  q="Source rows with no match in the target are handled with:",
  opts=["WHEN MATCHED THEN INSERT", "WHEN NOT MATCHED THEN INSERT", "WHEN NOT MATCHED THEN UPDATE", "ON CONFLICT INSERT"],
  a=1, ex="Not matched (by target) → INSERT. Course 1, slide 86."),
 "2a": dict(
  why="A job is a **DAG**: tasks + `depends on` arrows, no cycles. Tasks without a dependency between them run "
      "**in parallel**. One task waiting for several = *funnel*; one feeding many = *fan-out*.",
  q="Task C depends on A and B. A and B have no dependencies. How do A and B run?",
  opts=["A then B", "B then A", "In parallel", "Only one of them runs"],
  a=2, ex="Independent tasks run in parallel; C waits for both (slide 33)."),
 "2b": dict(
  why="Job parameters apply to all tasks and **override task parameters with the same key**. "
      "Task values pass results between tasks: `dbutils.jobs.taskValues.set/get`, or the reference "
      "`{{tasks.<task>.values.<key>}}`.",
  q="Job parameter env=prod, task parameter env=dev. What does the task see?",
  opts=["dev", "prod", "both", "an error"],
  a=1, ex="Job parameters win (slide 44)."),
 "2c": dict(
  why="If/else compares two values → tasks hang on the True or False branch; the other branch is **Excluded**. "
      "For each runs a nested task per item (`{{input}}`), optionally in parallel. A task after both branches needs "
      "run-if **None failed** — with *All succeeded* it would be skipped because one branch was excluded.",
  q="Run the same notebook for CA, NY and VA in parallel. Which task type?",
  opts=["If/else condition", "For each", "Run Job", "Pipeline"],
  a=1, ex="For each loops over an input array, with a concurrency setting (slide 73)."),
 "2d": dict(
  why="Retries re-run a task automatically. **Repair run** re-runs only the failed tasks and the tasks after them — "
      "successful tasks are not repeated (saves time and cost). You can change parameters for the repair.",
  q="A 10-task job failed at task 8. Fastest way to finish it?",
  opts=["Run now again", "Repair run", "Delete and recreate the job", "Add more retries"],
  a=1, ex="Repair run re-runs only what failed (slide 78)."),
 "3a": dict(
  why="**Streaming table** = append-only, processes only new data (checkpoint). **Materialized view** = result "
      "recomputed to match current data — good for aggregations. In SDP you just declare them; SDP handles "
      "checkpoints, order and refresh. Reading a streaming table incrementally uses `FROM STREAM`.",
  q="A gold table with GROUP BY over all silver data should be a:",
  opts=["Streaming table", "Materialized view", "Temporary view", "External table"],
  a=1, ex="MVs recompute results for the current data (slides 35–36)."),
 "3b": dict(
  why="`CONSTRAINT name EXPECT (cond)` → default **WARN** (keep row, log metric). `ON VIOLATION DROP ROW` removes "
      "bad rows. `ON VIOLATION FAIL UPDATE` stops the update. Results go to the pipeline event log.",
  q="EXPECT (id IS NOT NULL) with no ON VIOLATION clause. A row has NULL id. Result?",
  opts=["Row dropped", "Update fails", "Row kept, violation logged", "Row quarantined"],
  a=2, ex="Default action is WARN (slide 54)."),
 "3c": dict(
  why="To join **all** rows of two streaming tables on every update, SDP uses a **materialized view**. "
      "Stream–static joins join only new rows to a full lookup table. Stream–stream joins need watermarks "
      "(out of course scope).",
  q="Join all rows of two streaming tables each pipeline run. Use a:",
  opts=["Streaming table", "Materialized view", "Temporary view", "COPY INTO"],
  a=1, ex="Course 3, slides 66–68."),
 "3d": dict(
  why="`AUTO CDC INTO` (old: APPLY CHANGES INTO) applies inserts/updates/deletes. `KEYS` = row id, "
      "`SEQUENCE BY` = order of changes (fixes out-of-order data), `APPLY AS DELETE WHEN`, "
      "`STORED AS SCD TYPE 1` (overwrite) or `TYPE 2` (keep history).",
  q="Which AUTO CDC clause handles records that arrive out of order?",
  opts=["KEYS", "SEQUENCE BY", "APPLY AS DELETE WHEN", "STORED AS SCD TYPE 1"],
  a=1, ex="SEQUENCE BY orders the changes (slide 84)."),
 "4a": dict(
  why="Modular code = small functions that take a DataFrame and return a DataFrame. They are easy to reuse and, "
      "most important, easy to **unit test**.",
  q="Main benefit of moving PySpark logic into small functions?",
  opts=["Faster clusters", "Each function can be unit tested and reused", "No need for Git", "Smaller tables"],
  a=1, ex="Course 4, modularizing PySpark code."),
 "4b": dict(
  why="pytest finds `test_*.py` files and `test_*` functions. `assertDataFrameEqual(actual, expected)` compares "
      "rows and schema; a shared `spark` fixture lives in `conftest.py`.",
  q="Which helper compares two DataFrames in a PySpark test?",
  opts=["df1 == df2", "assertDataFrameEqual", "df.compare()", "assertSchemaEqual only"],
  a=1, ex="pyspark.testing.utils.assertDataFrameEqual (Course 4)."),
 "4c": dict(
  why="Tests only help if they **fail when the code is wrong**. Edge cases (NULL, rounding, unexpected values) are "
      "where bugs hide. In CI, these tests run automatically on every change.",
  q="Code passes tests and deploys to staging automatically; production needs a manual approval. This is:",
  opts=["Continuous integration only", "Continuous delivery", "Continuous deployment", "Manual release"],
  a=1, ex="Delivery = manual step before prod; Deployment = fully automatic."),
 "5a": dict(
  why="`OPTIMIZE` compacts small files (`ZORDER BY` co-locates data). `RESTORE` rolls back to a version. "
      "`VACUUM` deletes files not used by the current version (default 7 days) — after that, time travel to "
      "those versions fails.",
  q="After VACUUM, what may no longer work?",
  opts=["SELECT on the current table", "Time travel to old versions", "OPTIMIZE", "INSERT"],
  a=1, ex="VACUUM removes old files needed for older versions."),
 "5b": dict(
  why="Latest row per key: `row_number() OVER (PARTITION BY key ORDER BY ts DESC)` then keep `rn = 1`. "
      "A very common exam de-duplication pattern.",
  q="Which keeps only the newest row per user?",
  opts=["SELECT DISTINCT *", "row_number() … ORDER BY ts DESC, keep rn = 1", "GROUP BY user_id", "LIMIT 1"],
  a=1, ex="DISTINCT only removes exact duplicates."),
 "5c": dict(
  why="Higher-order functions work on arrays without exploding: `size`, `transform`, `filter`, `exists`, "
      "`aggregate(arr, start, (acc, x) -> …)`.",
  q="Keep only array items with price > 1000:",
  opts=["transform(items, x -> x.price > 1000)", "filter(items, x -> x.price > 1000)", "explode(items)", "aggregate(items, 1000)"],
  a=1, ex="filter returns the matching elements; transform changes each element."),
 "5d": dict(
  why="Output modes: **append** = only new rows, **complete** = whole result each time (aggregations), "
      "**update** = only changed rows. The checkpoint stores progress and state.",
  q="A streaming count per customer must write the full result table each trigger. Output mode?",
  opts=["append", "complete", "update", "overwrite"],
  a=1, ex="complete rewrites the entire aggregated result."),
}

C.update({
 "6a": dict(
  why="Silver = bronze after cleaning: drop rows missing keys (`na.drop`), fill missing values (`na.fill`), "
      "**standardize types** (`cast`, `to_date`), trim/split/rename/drop columns. Then write a new silver table.",
  q="A bronze column `amount` is STRING. You need it as a number in silver. Use:",
  opts=["F.col('amount').alias('double')", "F.col('amount').cast('double')", "F.split('amount')", "df.na.fill('amount')"],
  a=1, ex="cast() changes the data type; alias() only renames."),
 "6b": dict(
  why="inner = matches only; left = all left rows; multi-key join = list of columns; cross = every combination; "
      "`F.broadcast(small)` sends the small table to every worker (BroadcastHashJoin, no big shuffle). "
      "PySpark `union` = SQL UNION ALL (keeps duplicates, by position); `unionByName` matches by column name.",
  q="In SQL, which keeps duplicate rows?",
  opts=["UNION", "UNION ALL", "UNION DISTINCT", "INTERSECT"],
  a=1, ex="UNION removes duplicates; UNION ALL keeps them."),
 "6c": dict(
  why="`dropDuplicates([keys])` keeps one row per key; `distinct()` only removes fully identical rows. "
      "`approx_count_distinct` is a fast estimate for big data. `summary()` adds percentiles to `describe()`.",
  q="You need a fast, approximate count of unique users over billions of rows. Use:",
  opts=["count('*')", "countDistinct('user_id')", "approx_count_distinct('user_id')", "distinct().count()"],
  a=2, ex="approx_count_distinct trades a tiny error for much better speed."),
 "6d": dict(
  why="`spark.sql.shuffle.partitions` (default 200) = tasks after a shuffle. `spark.sql.autoBroadcastJoinThreshold` "
      "(default 10 MB, -1 = off) = auto-broadcast size. Executor/driver memory are set at cluster start. "
      "Change one thing, then re-measure in the plan and Spark UI.",
  q="A join between a 5 GB table and a 2 MB table is slow and shows SortMergeJoin. Best first fix?",
  opts=["Increase spark.sql.shuffle.partitions", "Broadcast the 2 MB table", "Add more driver memory", "Use crossJoin"],
  a=1, ex="Broadcasting the small side removes the expensive shuffle of the big table."),
 "7a": dict(
  why="Skew = one hot key makes one giant task (Max shuffle read ≫ median). Salting spreads the key over several "
      "tasks; a second aggregation combines the partial results. AQE skew handling covers joins, not groupBy.",
  q="(Official sample) groupBy on customer_id; one task 10 min, others 30 s; Max shuffle read 5 GB vs median 400 MB; AQE is on. Fix?",
  opts=["Add more executors", "Rely on AQE skew-join handling", "Reduce spark.sql.shuffle.partitions", "Salt the aggregation key"],
  a=3, ex="AQE skew handling is for joins only; salting splits the hot key across tasks (exam guide, Q1)."),
 "7b": dict(
  why="Liquid clustering (`CLUSTER BY`) groups similar values in files for data skipping and the key can be changed "
      "any time (`ALTER TABLE … CLUSTER BY`). `OPTIMIZE` does the clustering. Predictive optimization runs "
      "OPTIMIZE/VACUUM automatically on UC managed tables.",
  q="Main advantage of liquid clustering over partitioning + Z-ORDER?",
  opts=["It removes the need for Delta", "You can change the clustering key without rewriting the table design", "It disables OPTIMIZE", "It only works on external tables"],
  a=1, ex="Liquid clustering keys are flexible and can be redefined with ALTER TABLE."),
 "7c": dict(
  why="Driver OOM → stop collecting big data. Library errors → pin versions. Cluster won't start → event log "
      "(init script, quota). Timed Out → raise the task timeout. One slow task + spill → skew.",
  q="(Official sample) A task fails 'Timed Out' after 45 min; it needs ~60 min now. What to change?",
  opts=["The upstream dependency condition", "The task run duration (timeout) threshold", "Max concurrent runs", "Cluster auto-termination"],
  a=1, ex="Timed Out = the configured timeout was exceeded; raise it with headroom (exam guide, Q9)."),
 "7d": dict(
  why="SQL analysts → SQL warehouse (serverless, autoscaling). Scheduled ETL → job cluster or serverless jobs. "
      "Interactive development → all-purpose cluster.",
  q="(Official sample) Many analysts run ad-hoc SQL all day; need fast start, concurrency, controlled cost. Choose:",
  opts=["Job cluster with autoscaling", "All-purpose cluster, fixed workers", "Serverless SQL warehouse with autoscaling", "Single-node cluster"],
  a=2, ex="Serverless SQL warehouses are built for many concurrent SQL users (exam guide, Q4)."),
 "8a": dict(
  why="Git folders let you clone, branch, commit, push and pull inside the workspace; the pull request is reviewed "
      "and merged in the Git provider, then you pull main.",
  q="Where is a pull request reviewed and merged when using Databricks Git folders?",
  opts=["Inside the notebook revision history", "In the Git provider (e.g. GitHub)", "In Unity Catalog", "In the Jobs UI"],
  a=1, ex="Databricks creates/links the PR; the review and merge happen in the Git provider."),
 "8b": dict(
  why="One `databricks.yml`: `variables` with defaults, `resources` (jobs, pipelines) using `${var.x}` and "
      "`${bundle.target}`, and `targets` (dev/test/prod) that **override** variables and resources. Same code, "
      "promoted across environments.",
  q="(Official sample) A team wants a modular, versioned, CI/CD-friendly way to deploy and promote ETL pipelines. Use:",
  opts=["Models in Unity Catalog", "Wheel files in volumes", "Notebook revision history + Jobs API", "Declarative Automation Bundles in Git"],
  a=3, ex="Bundles define resources and code as versioned config promoted by CI/CD (exam guide, Q5)."),
 "8c": dict(
  why="Secrets never go in YAML or notebooks: declare a variable without default and pass `BUNDLE_VAR_<name>` "
      "from CI secrets. CLI: `bundle validate`, `bundle deploy -t <target>`, `bundle run -t <target> <job>`.",
  q="(Official sample) How should a bundle get a database password safely during automated deployment?",
  opts=["A variable whose value comes from a BUNDLE_VAR_ environment variable", "A passwords.txt file in the bundle", "A 'bundle encrypt' command", "spark.conf.set in the notebook"],
  a=0, ex="BUNDLE_VAR_<name> injects the value at deploy time (exam guide, Q6)."),
 "9a": dict(
  why="Reading a table needs USE CATALOG + USE SCHEMA + SELECT. MODIFY = write rows. REVOKE … FROM removes a "
      "privilege. Grant to groups and service principals, not individual users.",
  q="A user has SELECT on main.sales.orders but gets 'permission denied'. Most likely missing?",
  opts=["MODIFY on the table", "USE CATALOG / USE SCHEMA on the parents", "OWNER on the catalog", "CREATE TABLE"],
  a=1, ex="Every parent level needs USE privileges."),
 "9b": dict(
  why="Managed: UC owns the files, DROP deletes data. External: you own the LOCATION, DROP keeps files. "
      "`SET MANAGED` converts external → managed; `UNSET MANAGED` rolls back within 14 days.",
  q="(Official sample) You converted an external table to managed and must undo it. In newer runtimes:",
  opts=["ALTER TABLE … UNSET MANAGED", "Drop and recreate as external", "ALTER TABLE … SET EXTERNAL", "RESTORE TABLE … TO VERSION AS OF"],
  a=0, ex="UNSET MANAGED is the documented rollback, within 14 days (exam guide, Q8)."),
 "9c": dict(
  why="Column masks and row filters are SQL functions attached to a table; `is_account_group_member()` makes the "
      "result depend on who is querying — one table, different views per group.",
  q="(Official sample) Only finance_team may see full credit card numbers; others see a masked value. Use:",
  opts=["A separate table per group", "AWS IAM roles on the column", "A column mask using is_account_group_member('finance_team')", "DENY on the column"],
  a=2, ex="Column masking with is_account_group_member (exam guide, Q7)."),
 "9d": dict(
  why="ABAC policies use governed tags to apply row filters and column masks centrally to every matching table "
      "in a catalog or schema — the scalable choice for sensitive data.",
  q="Hundreds of tables have columns tagged 'pii'; new tables appear weekly. Best way to mask them all?",
  opts=["A mask function per column", "An ABAC policy based on the pii tag", "GRANT SELECT to fewer users", "Separate masked copies"],
  a=1, ex="ABAC applies one tag-based policy across many tables automatically."),
})
