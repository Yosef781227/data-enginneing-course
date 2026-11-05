# Section 3: Data Transformation and Modeling — 22%

Turn raw records into trustworthy answers.

Follow rows through an operation. Cleaning fixes records, joins combine matches, aggregates summarize groups, and views/tables expose results. Bronze/silver/gold describes increasing readiness.

You should predict tiny query outputs, explain null behaviour, select deduplication keys and choose a useful gold-layer object.


## Bronze, silver and gold

**Questions:** 26, 50, 65, 73, 81, 119, 124, 141, 152, 154, 159, 183, 202, 204, 213

**Think of it like this:** Bronze is unopened deliveries, silver is cleaned ingredients, gold is a ready-to-serve meal.

**What the question tests:** Recognize how ready the data is, not just the names of its columns. Preserve raw input, create trustworthy reusable records, then prepare business summaries.

**Example:** Keep source order events in bronze. Standardize timestamps, remove invalid identifiers and join customer details in silver. Sum weekly sales by product for a dashboard in gold.

**Common trap:** Silver can contain joins and conformed datasets. Gold is not merely ‘any table with clean data’. Layers describe responsibilities, not guaranteed row counts.

**Try the lab:** lab6_transform_tuning / 6a (some platform features are simulated)

**Explain without looking:** Where should you keep source events so you can rebuild a transformation later?

**Self-check:** Bronze, with sufficient source detail and ingestion metadata for traceability.


## Delta tables and table history

**Questions:** 5, 6, 16, 20, 52, 59, 70, 98, 104, 219, 280

**Think of it like this:** A Delta table is a filing cabinet plus a versioned ledger of changes.

**What the question tests:** Distinguish data files from transaction metadata; insert, update, delete and merge; reading an older version from restoring the current table.

**Example:** INSERT adds rows. MERGE can update matched keys and insert new ones. DESCRIBE HISTORY lists recorded table operations. VERSION AS OF reads an earlier snapshot; RESTORE makes a supported historical state current again.

**Common trap:** A blind append is not an upsert. Time travel needs the necessary history and files. Removing old files can make older snapshots unreadable.

**Try the lab:** lab1_ingestion / 1h (some platform features are simulated)

**Explain without looking:** Does reading VERSION AS OF 4 change the table’s latest state?

**Self-check:** No. It reads an older snapshot. Restoring is a different operation.


## Read SQL and Python step by step

**Questions:** 8, 12, 13, 18, 28, 48, 53, 57, 66, 75, 99, 100, 105, 110, 111, 114, 134, 145, 150, 174, 217, 222

**Think of it like this:** Treat a query like a recipe: identify the ingredients, then follow each operation in order.

**What the question tests:** Predict which rows survive, which columns are produced and what is counted. Understand functions, expressions and data types rather than spotting familiar words.

**Example:** With values 10, NULL and 20, COUNT(*) counts three rows; COUNT(value) counts two non-null values. GROUP BY groups rows before aggregation. A window function can compute a ranking or running total without collapsing every group into one row.

**Common trap:** NULL is not zero. WHERE filters rows; an aggregate summarizes rows. Python `and` is not interchangeable with every DataFrame column-expression operator.

**Try the lab:** lab5_delta_sql_streaming / 5b (some platform features are simulated)

**Explain without looking:** How would you count rows where a value is missing?

**Self-check:** Use an explicit null predicate, such as count_if(value IS NULL), instead of expecting COUNT(value) to count nulls.


## Tables, views and materialized views

**Questions:** 10, 24, 102, 245, 273

**Think of it like this:** A view is a saved recipe; a materialized view also keeps the prepared result.

**What the question tests:** Choose based on persistence, scope, freshness and whether results must be stored or recomputed.

**Example:** A temporary view suits a session-local reusable query. A normal view saves query logic. A table stores data. A materialized view stores query results and must be refreshed to reflect source changes.

**Common trap:** A normal view does not automatically store a new copy of all result rows. A materialized view is not guaranteed to be fresh without the required refresh behaviour.

**Try the lab:** lab3_pipelines / 3a (some platform features are simulated)

**Explain without looking:** Which object helps avoid repeating an expensive dashboard aggregation on every read?

**Self-check:** A suitable materialized view or prepared aggregate table, with a refresh strategy that meets freshness needs.


## Joins, unions and broadcast

**Questions:** 1, 39, 68, 112, 258, 266, 267, 278

**Think of it like this:** Match orders to customers like matching receipts to loyalty cards. Decide which unmatched receipts must remain.

**What the question tests:** Choose matching keys and which side’s unmatched rows to keep. Distinguish joins, which combine columns, from unions, which stack compatible rows.

**Example:** With customer IDs [1,2] on the left and [2,3] on the right, an inner join keeps the match for 2. A left join also keeps 1 with missing right-hand values. A left anti join returns left rows without a match.

**Common trap:** Duplicate keys can multiply joined rows. UNION and UNION ALL differ in duplicate handling in SQL. Broadcasting a suitably small lookup can avoid a large shuffle; broadcasting the large side is not the same optimization.

**Try the lab:** lab6_transform_tuning / 6b (some platform features are simulated)

**Explain without looking:** You need customers with no orders. What relationship are you looking for?

**Self-check:** An anti-match: customers whose keys have no matching order, such as a left anti join.


## JSON, structs and arrays

**Questions:** 2, 62, 113, 236, 240

**Think of it like this:** JSON can contain boxes inside boxes. A struct is a labelled box; an array is a list of boxes.

**What the question tests:** Know when you are handling JSON text versus a parsed struct or array. Choose field access, parsing, transformation or explosion accordingly.

**Example:** Parse a JSON string with from_json and a suitable schema, then access a field. explode makes a row per array element. Higher-order filter can retain qualifying elements inside an array instead of making extra rows.

**Common trap:** Filtering elements of an array differs from filtering whole table rows. explode and explode_outer differ for empty or null arrays. Reading a nested struct field is not always the same as parsing a string.

**Try the lab:** lab1_ingestion / 1g (some platform features are simulated)

**Explain without looking:** Should filtering an employee array necessarily change the number of parent rows?

**Self-check:** No. An array transformation can keep each parent row while changing the array inside it.


## Nulls and duplicate records

**Questions:** 229, 254, 256, 279

**Think of it like this:** Cleaning a contact book means deciding both what ‘missing’ means and what counts as the same person.

**What the question tests:** Choose null conditions and deduplication keys explicitly. If a particular survivor matters, define ordering too.

**Example:** dropDuplicates(['customer_id','email']) treats those fields as the identity, even when ingestion timestamps differ. Without a subset, differences in any compared column can keep rows distinct. To keep the newest record, use a deterministic ordering rule.

**Common trap:** Dropping duplicates does not guarantee the newest row survives. `a IS NOT NULL AND b IS NOT NULL` requires both fields; using OR allows one field to remain missing.

**Try the lab:** lab6_transform_tuning / 6c (some platform features are simulated)

**Explain without looking:** Two rows share an ID but have different timestamps. Will deduplicating complete rows necessarily remove one?

**Self-check:** No. They differ as full rows. Deduplicate by the intended keys and specify which survivor you need.


## Declarative pipelines and quality rules

**Questions:** 25, 32, 33, 34, 36, 42, 63, 72, 80, 116, 117, 120, 121, 126, 138, 146, 160, 225

**Think of it like this:** Describe the dishes you want, and a kitchen manager works out the preparation order.

**What the question tests:** Understand declared datasets and dependencies, streaming tables versus materialized results, and the action of each quality rule.

**Example:** A rule checks that an ID is present. A warning-style expectation records a violation while keeping the row. DROP removes failing rows. FAIL stops the affected update. The pipeline event log supplies built-in expectation metrics.

**Common trap:** A quality rule is not automatically an access-control rule. Dropping one bad row differs from failing an update. Legacy DLT and newer Lakeflow/SDP naming can refer to related concepts, but syntax must match the actual context.

**Try the lab:** lab3_pipelines / 3b (some platform features are simulated)

**Explain without looking:** If bad sensor readings should be removed while good readings continue, which behaviour fits?

**Self-check:** A drop-on-violation rule, rather than a fail-update rule.


## Streaming reads, writes and progress

**Questions:** 30, 31, 67, 79, 115, 118, 125

**Think of it like this:** A streaming pipeline reads pages as they arrive and keeps a bookmark.

**What the question tests:** Separate source, transformation, trigger, output mode and checkpoint. Determine whether the task is bounded processing of available data or ongoing processing.

**Example:** readStream defines a streaming source. Transformations describe the desired data. writeStream starts or configures the output. A checkpoint preserves progress; a trigger controls when processing happens.

**Common trap:** Calling readStream does not itself write a result. Append, update and complete modes are not interchangeable for every query. An incremental table read is different from a full batch read.

**Try the lab:** lab5_delta_sql_streaming / 5d (some platform features are simulated)

**Explain without looking:** Can a streaming API be used in a run that stops after processing the available backlog?

**Self-check:** Yes, with an appropriate supported bounded trigger such as availableNow.


## Sources

Local curriculum: ../../curriculum.md; official objective map: ../exam-guide-map.md

Current exam outline: https://www.databricks.com/learn/certification/data-engineer-associate

Post-May 2026 guide: https://www.databricks.com/sites/default/files/2026-05/databricks-certified-data-engineer-associate-exam-guide-may-2026.pdf

These learning explanations do not independently certify the third-party answer key.
