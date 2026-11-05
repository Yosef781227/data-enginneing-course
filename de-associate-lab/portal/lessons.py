"""Beginner-friendly lessons for every portal step.

read = taught BEFORE the task (plain words, analogy, tiny example, words to know)
do   = the task as small numbered instructions (shown after "I've read this")
"""

L = {}

# ======================================================================== LAB 1
L["1a"] = dict(read="""
### What is a table?
A **table** is data in rows and columns, like a spreadsheet:

| id | name |
|----|------|
| 1 | peter |
| 2 | zebi |

### What is a Delta table?
On Databricks, every table you create is a **Delta table** by default. A Delta table is stored as two things in a folder:

1. **Data files** (format: **Parquet**) — they hold the rows.
2. A **`_delta_log/` folder** — a diary. Every time the table changes, Delta writes a new page in the diary.

Each page in the diary = one **version** of the table. Version 0 = created, version 1 = first insert, and so on.

### Why does the diary matter?
Because of the diary, Delta tables can:
- **Undo / look back in time** (*time travel*): "show me the table as it was at version 1".
- **Show history**: `DESCRIBE HISTORY my_table` lists every change.
- **Be safe**: a write either fully happens or does not happen at all (**ACID transactions**).

### How do you create one? (SQL)
```sql
CREATE TABLE my_table (id INT, name STRING);       -- empty table with 2 columns
INSERT INTO my_table VALUES (1, 'peter'), (2, 'zebi');
```
In this lab we run SQL from Python like this: `spark.sql("SELECT 1")` — the SQL goes **between the quotes**. **spark** is the engine that runs your code.

### Words to know
- **Delta Lake** — the storage format behind every Databricks table.
- **Parquet** — the file format for the data.
- **Transaction log** = `_delta_log` = the diary.
- **Version** — one change in the diary.
""", do="""
1. In the first `spark.sql(...)`, replace the `<FILL-IN…>` with a **CREATE TABLE** for `lab1.demo_delta` with columns `id INT` and `name STRING`.
   (`lab1` is the schema — a folder for tables. Write it as `lab1.demo_delta`.)
2. In the second `spark.sql(...)`, write an **INSERT INTO** that adds **3 rows**.
3. Press **▶ Run** — no error means it worked.
4. Press **✔ Check my answer**. After checking, you will see the data files, the `_delta_log` files and the history.
""")

L["1b"] = dict(read="""
### What is "ingestion"?
**Ingestion** = taking raw files (CSV, JSON, Parquet…) and loading them into a table. It is the first job of a data engineer.

Raw files usually land in **cloud storage**. On Databricks they sit in a **volume**, with a path like `/Volumes/catalog/schema/volume/folder`.

### The simplest way: CTAS
**CTAS** = **C**REATE **T**ABLE **A**S **S**ELECT. You create a table *from the result of a query*:
On Databricks you read the files with **`read_files()`**:
```sql
CREATE TABLE users_bronze AS
SELECT * FROM read_files('/Volumes/shop/raw/users', format => 'parquet');
```
In this lab (on your Mac) `read_files()` doesn't exist, so we use another form that also works on Databricks:
```sql
SELECT * FROM parquet.`/path/to/files`        -- note the back-ticks ` `
```

### Important: CTAS is **batch**
**Batch** = it reads **all** files **every time**. Run it tomorrow → it reads yesterday's files again. That's fine for a one-time load, but not for daily new files (next steps solve that).

### Managed vs external table
- **Managed** table: Databricks owns the files. `DROP TABLE` → **data is deleted**.
- **External** table: you give a `LOCATION`. `DROP TABLE` → only the table name is removed; **files stay**.

### Words to know
**Ingestion**, **volume**, **CTAS**, **batch**, **managed**, **external**.
""", do="""
1. The variable `users_path` already holds the folder with the Parquet files (the setup printed it).
2. Replace `<FILL-IN>` with a `SELECT` that reads all those files: ``SELECT * FROM parquet.`{users_path}` ``
   (keep the `f` in front of the string so `{users_path}` becomes the real path).
3. **Run**, then **Check**. After checking you'll see a demo: what `DROP TABLE` does to a managed vs an external table.
""")

L["1c"] = dict(read="""
### The problem with CTAS
New files arrive every day. CTAS reads **everything again** each time → slow, and it can create **duplicates**.

### COPY INTO: load only NEW files
`COPY INTO` is a SQL command that **remembers which files it already loaded** and skips them.
```sql
CREATE TABLE users_bronze;                 -- empty table, no columns needed
COPY INTO users_bronze
  FROM '/Volumes/shop/raw/users'
  FILEFORMAT = parquet;
```
- Day 1: loads file1, file2.
- Day 2: file3 arrives → loads **only file3**.
- Run it twice by mistake → second run loads **0 rows**. This is called **idempotent** (safe to repeat).

### When files get a new column
If new files have an extra column (e.g. `country`), COPY INTO stops with a **schema mismatch** error. You allow the new column with:
```sql
COPY_OPTIONS ('mergeSchema' = 'true')
```
⚠ Exam trap: there are two option groups —
- `FORMAT_OPTIONS` = **how to read** the files (header, separator…)
- `COPY_OPTIONS` = **how COPY INTO behaves** (`mergeSchema`, `force` = reload everything)

### In this lab
`COPY INTO` exists only on Databricks, so you use a look-alike Python function with the same rules:
```python
copy_into(spark, "lab1.users_bronze_ci", vol, "parquet")                     # normal
copy_into(spark, "lab1.users_bronze_ci", vol, "parquet", merge_schema=True)  # allow new columns
```
`landing.land("users", 1)` = "a new file arrives in the volume".

### Words to know
**Incremental** (only new data), **idempotent** (safe to run again), **schema** (the list of columns and types), **mergeSchema**.
""", do="""
1. **First `<FILL-IN>`**: load the files → `copy_into(spark, "lab1.users_bronze_ci", vol, "parquet")`
2. **Second `<FILL-IN>`**: write the **same line again**. Predict: how many rows will it load? (Look at the output.)
3. The next line lands a new file that has an extra column `country`.
4. **Third `<FILL-IN>`**: load again — it will fail. Wrap it in `try: … except Exception as e: print(e)` to see the error, then load once more **with** `merge_schema=True`.
5. **Run** and read the terminal, then **Check** (expected: 150 rows, no duplicates).
""")

L["1d"] = dict(read="""
### Auto Loader: COPY INTO's big brother
For **millions** of files or **near real-time** data, Databricks uses **Auto Loader**. Same idea — only new files — but:
- scales to millions of files per hour
- can run **continuously** (streaming) or **on demand**
- handles **new columns automatically**

### How does it remember files? The checkpoint
Auto Loader is built on **Spark Structured Streaming**. A stream keeps a **checkpoint** folder = its memory: "I already processed file1 and file2". Next run starts after them.

### Python on Databricks
```python
(spark.readStream                       # readStream = read as a stream
   .format("cloudFiles")                # "cloudFiles" means Auto Loader
   .option("cloudFiles.format", "json") # type of the files
   .load("/Volumes/shop/raw/events")
 .writeStream
   .option("checkpointLocation", "/path/to/checkpoint")   # the memory
   .trigger(availableNow=True)          # process what is new, then STOP
   .toTable("events_bronze"))
```
### SQL on Databricks
```sql
CREATE OR REFRESH STREAMING TABLE events_bronze
AS SELECT * FROM STREAM read_files('/Volumes/shop/raw/events', format => 'json');
```
The word **STREAM** is what makes it Auto Loader.

### In this lab
`cloudFiles` is Databricks-only, so we use the normal file stream (`format("parquet")`). The checkpoint works exactly the same way.

### Words to know
**Auto Loader** = `cloudFiles`, **Structured Streaming**, **checkpoint** (memory), **availableNow** (run once on new data and stop).
""", do="""
1. **First `<FILL-IN>`** (`.format(...)`): the landed files are Parquet → write `"parquet"`.
2. **Second `<FILL-IN>`** (checkpoint): write `checkpoint("lab1", "users_stream")` — a helper that gives a checkpoint folder.
3. **Run** (this only defines the function), then **Check**.
   The check lands a file and runs your stream, lands another file and runs it again, then runs it a third time with no new files. Watch the counts: **50 → 100 → 100**. The checkpoint stopped the old files being read twice.
""")

L["1e"] = dict(read="""
### Why add extra columns at ingestion?
Imagine a wrong number shows up in a report. You ask: *"Which file did this row come from? When did we load it?"* If the table has that information, you find the answer in seconds.

### The `_metadata` column
Every file you read has a hidden column called **`_metadata`**. It knows things about the file:
- `_metadata.file_name` → the file name
- `_metadata.file_modification_time` → when the file was last changed

And `current_timestamp()` gives **now** = when you loaded it.

### Example (Databricks SQL)
```sql
SELECT *,
       _metadata.file_name AS source_file,
       _metadata.file_modification_time AS file_modification_time,
       current_timestamp() AS ingestion_time
FROM read_files('/Volumes/shop/raw/sales', format => 'csv', sep => '|', header => true);
```
- `sep => '|'` → columns are separated by `|` instead of a comma.
- `header => true` → the first line has the column names.

### The same in Python (what you write here)
```python
from pyspark.sql import functions as F
F.col("_metadata.file_name").alias("source_file")      # pick a column and rename it
F.current_timestamp().alias("ingestion_time")
```
`.alias("x")` = give the column the name x.

### Words to know
**Bronze table** (raw data + these audit columns), **`_metadata`**, **alias**.
""", do="""
1. `.option("sep", <FILL-IN>)` → the files use a pipe: `"|"`
2. Replace the three `<FILL-IN>`s in `.select(...)`:
   - `F.col("_metadata.file_name").alias("source_file")`
   - `F.col("_metadata.file_modification_time").alias("file_modification_time")`
   - `F.current_timestamp().alias("ingestion_time")`
3. **Run**, then **Check**. You'll see how many rows came from each file.
""")

L["1f"] = dict(read="""
### Real data is messy
Look at this CSV:
```
item_id,name,price
M_PREM_A,Premium Queen Mattress,1795.0
M_STAN_F,Standard Full Mattress,$945.00      ← "$945.00" is not a number!
```
We told Spark `price` is a **DOUBLE** (a decimal number). `$945.00` can't become a number.

### Databricks: the rescued data column
Instead of failing or losing the value, Databricks puts it in a special column **`_rescued_data`**:

| item_id | price | _rescued_data |
|---|---|---|
| M_PREM_A | 1795.0 | NULL |
| M_STAN_F | **NULL** | `{"price":"$945.00"}` |

So the row is **kept**, and nothing is lost. Later you clean it:
```sql
coalesce(price, cast(replace(_rescued_data:price, '$', '') AS DOUBLE))
```
- `coalesce(a, b)` → use `a`; if `a` is NULL, use `b`.
- `replace(x, '$', '')` → remove the dollar sign.
- `cast('945.00' AS DOUBLE)` → turns the text `'945.00'` into the number 945.0.

### In this lab
Open-source Spark has a similar column called **`_corrupt_record`**. It keeps the **whole raw line**: `M_STAN_F,Standard Full Mattress,$945.00`. The setup already read the file into the view `items_raw`.

### Words to know
**Malformed data**, **schema** (the expected columns + types), **`_rescued_data`**, **coalesce**, **cast**.
""", do="""
Goal: make a column `price_fixed` that always has a number.
1. Replace `<FILL-IN>` with an expression that uses `price`, and when it's NULL takes the **3rd value** of the raw line without `$`:
   - get the 3rd value: `split(_corrupt_record, ',')[2]` (counting starts at 0)
   - remove `$`: `regexp_replace(…, '[$]', '')`
   - make it a number: `cast(… AS DOUBLE)`
   - combine: `coalesce(price, …)`
2. **Run** — look at the table: no NULLs in `price_fixed`. Then **Check**.
""")

L["1g-1"] = dict(read="""
### JSON in one minute
**JSON** is text that describes data with keys and values:
```json
{"user_id": "UA001", "geo": {"city": "Austin"}, "items": [{"item_id": "P1", "price_usd": 59}]}
```
- `{ }` = an **object** (keys + values) → in SQL a **STRUCT**
- `[ ]` = a **list** → in SQL an **ARRAY**

### Data from Kafka is encoded
Streaming systems like **Kafka** often send the message as **base64** — text that looks like random letters, for example `eyJkZXZpY2UiOiJpT1MifQ==`. It protects special characters, but humans can't read it.

To read it:
```sql
cast(unbase64(value) AS STRING)
```
- `unbase64(value)` → turns base64 back into raw bytes (BINARY)
- `cast(unbase64(value) AS STRING)` → turns those bytes into readable text (the JSON)

### Words to know
**JSON**, **STRUCT** (object), **ARRAY** (list), **base64**, **Kafka**.
""", do="""
1. Replace `<FILL-IN>` with `cast(unbase64(value) AS STRING)`.
2. **Run**, then **Check**. In the next part you'll turn this JSON text into real columns.
""")

L["1g-2"] = dict(read="""
### Three ways to work with a JSON text column
1. **Keep it as text (STRING)** and pick fields:
   - Databricks: `decoded_value:user_id`, `decoded_value:geo:city` (colon syntax)
   - here: `get_json_object(decoded_value, '$.user_id')` (you saw it in the setup output)
2. **Turn it into a STRUCT** with a fixed shape — faster and safer:
   ```sql
   from_json(decoded_value, 'STRUCT<user_id: STRING, geo: STRUCT<city: STRING>>')
   ```
   You don't have to type the shape yourself: `schema_of_json('{"a": 1}')` prints it (you give one example of the JSON). The setup already printed it for you — scroll up in the terminal.
3. **VARIANT** (newer, Databricks): flexible and fast — `parse_json(decoded_value)`.

### One row per list item: explode
An event can have several `items`. To get **one row per item**:
- `explode(items)` → one row per item. ⚠ If the list is **empty**, the event **disappears**.
- `explode_outer(items)` → same, but events with an empty list are **kept** (with NULL item).

### Words to know
**from_json**, **schema_of_json**, **explode** vs **explode_outer**.
""", do="""
1. **`event_schema`**: copy the `STRUCT<...>` text printed by `schema_of_json` in the setup output (or build it: device, event_name, event_timestamp, geo{city,state}, items[{item_id, price_usd, quantity}], user_id).
2. In the SQL, replace `<FILL-IN>(e.items)` with the function that **keeps events with no items**: `explode_outer`.
3. **Run** — look at rows where `item_id` is NULL (events without items). Then **Check**.
""")

L["1h-1"] = dict(read="""
### Updating a table: MERGE INTO
Every day you get a list of **changes**: some users changed email, some must be deleted, some are new. Doing UPDATE, DELETE and INSERT separately is hard. **MERGE** does all three in one command. It is also called **upsert** (update + insert).

```sql
MERGE INTO target t                 -- the table you change
USING source s                      -- the list of changes
ON t.id = s.id                      -- how to match rows
WHEN MATCHED AND s.status = 'update' THEN UPDATE SET t.email = s.email
WHEN MATCHED AND s.status = 'delete' THEN DELETE
WHEN NOT MATCHED THEN INSERT (id, email) VALUES (s.id, s.email);
```
- **MATCHED** = the id exists in both → update or delete it.
- **NOT MATCHED** = the id is only in the source → it's new → insert it.

### Words to know
**MERGE / upsert**, **target**, **source**, **matched**, **not matched**.
""", do="""
The setup created `main_users_target` (ids 1, 2, 3) and `update_users_source` (1 = update, 2 = delete, 4 = new).
1. `ON <FILL-IN>` → match on id: `t.id = s.id`
2. update → `UPDATE SET t.email = s.email, t.status = s.status`
3. delete → `DELETE`
4. new → `INSERT (id, first_name, email, sign_up_date, status) VALUES (s.id, s.first_name, s.email, s.sign_up_date, s.status)`
5. **Run** and look at the table: id 1 has a new email, id 2 is gone, id 4 is new. Then **Check**.
""")

L["1h-2"] = dict(read="""
### Schema enforcement
Delta **protects** your table: if the source has a column the table doesn't have (like `country`), MERGE **fails**. This is **schema enforcement** — no surprise columns.

### Schema evolution (allow the new column)
- Databricks (new): start the command with `MERGE WITH SCHEMA EVOLUTION INTO main_users_target t` instead of `MERGE INTO main_users_target t`
- Databricks / here: turn on the setting
  `spark.databricks.delta.schema.autoMerge.enabled = true`

`INSERT *` = insert **all** columns of the source (including the new one).

### Time travel
Each MERGE made a new **version**. You can read old versions:
```sql
SELECT * FROM main_users_target VERSION AS OF 0;
```

### Words to know
**Schema enforcement** (block new columns), **schema evolution** (allow them), **VERSION AS OF**.
""", do="""
1. First `<FILL-IN>`: `spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")`
2. Second `<FILL-IN>`: `INSERT *`
3. **Run** — the table now has a `country` column. **Check** shows the history and version 0 (the original data).
""")

# ======================================================================== LAB 2
L["2a"] = dict(read="""
### Why "jobs"?
A data pipeline has many steps: load orders, load customers, join them, build a report. You don't want to click "run" on each one every morning. A **Lakeflow Job** (old name: *Workflows*) runs them **automatically, in the right order**.

### Job and tasks
- **Job** = the whole plan.
- **Task** = one step (a notebook, a SQL query, a pipeline…).
- **Depends on** = "run this task only after that one".

```
ingest_orders ─┐
               ├─► join_customers_orders
ingest_customers ┘
```
The two ingest tasks don't depend on each other → they run **at the same time** (in parallel). The join waits for **both**.

### DAG
This drawing is a **DAG** — *Directed Acyclic Graph*:
- **Directed**: arrows have a direction.
- **Acyclic**: no loops (A can't wait for B while B waits for A).

### In this lab
The real Jobs UI is on Databricks. Here, a small Python simulator follows the same rules:
```python
@job.task("join", depends_on=["task_a", "task_b"])
def join(ctx):
    print("both tasks are done, now joining")
```
""", do="""
1. Replace `<FILL-IN>` in `depends_on=` with a **list of the two tasks** the join needs: `["ingest_orders", "ingest_customers"]`
2. **Run** — the job runs and prints each task with ✅.
3. **Check**. After checking, you'll see what happens if you create a loop (it's refused: not a DAG).
""")

L["2b"] = dict(read="""
### Parameters = settings you pass into a task
Instead of writing `prod` inside the code, the task reads a **parameter**. Same code, different setting → runs for dev or prod.
- **Task parameter**: belongs to one task.
- **Job parameter**: belongs to the whole job and goes to **every** task.
- ⚠ Same name in both? The **job parameter wins**.

In a Databricks notebook you read a parameter with `dbutils.widgets.get("catalog")`. Here: `ctx.widget("catalog")`.

### Task values = pass a result to a later task
Task A counts rows; task B needs the number.
```python
dbutils.jobs.taskValues.set(key="row_count", value=n)          # in task A
dbutils.jobs.taskValues.get(taskKey="A", key="row_count")      # in task B
```
Or in task B's parameters, a **dynamic reference** (filled in when the job runs):
```
{{tasks.A.values.row_count}}
```

### Words to know
**Task parameter**, **job parameter** (wins), **task values**, **dynamic value reference** `{{ }}`.
""", do="""
1. First `<FILL-IN>` (inside count_orders): save the count → `ctx.task_values.set("row_count", n)`
2. `"rows": "<FILL-IN>"` → a reference to that value: `"{{tasks.count_orders.values.row_count}}"`
3. `job.run(parameters=<FILL-IN>)` → run with job parameter catalog = lab2_prod: `{"catalog": "lab2_prod"}`
4. Predict before **Run**: will count_orders print `task_default` or `lab2_prod`? Then **Check**.
""")

L["2c"] = dict(read="""
### If/else task = a decision
"If there are duplicates → remove them, else → continue." The **If/else condition task** compares two values (`==, !=, >, <, >=, <=`) and gives **True** or **False**. Each next task hangs on one branch. The branch not taken is **Excluded** (skipped).

### For each task = a loop
"Do the same work for CA, NY and VA." The **For each task** runs one inner task per item. The current item is called `{{input}}`. Items can run **at the same time** (concurrency).

### Run if = when may a task start?
Normally a task runs only if **all** tasks before it succeeded (**All succeeded**). Other options:
- **At least one succeeded**
- **None failed** — none failed and at least one ran ← useful after an If/else!
- **All done** — run no matter what
- **At least one failed / All failed** — e.g. send an alert

⚠ After an If/else, one branch is **excluded**, not "succeeded". So a task that waits for **both** branches with *All succeeded* would be skipped. Use **None failed**.
""", do="""
1. `left="<FILL-IN…>"` → compare the task value from check_duplicates: `"{{tasks.check_duplicates.values.has_duplicates}}"`
2. `run_if="<FILL-IN>"` for the For each task → it waits for both branches, one is excluded: `"NONE_FAILED"`
3. Tip: first try `"ALL_SUCCEEDED"` and **Run** — see the loop get skipped. Then fix it, **Run**, **Check**.
""")

L["2d"] = dict(read="""
### Things fail in production
A network hiccup, a typo in a table name… Lakeflow Jobs gives you two tools:

**1. Retries** — the task tries again automatically.
`max retries = 2` → up to 3 attempts. Good for *temporary* problems (network).

**2. Repair run** — after a run **failed**, you fix the problem and click **Repair run**. It re-runs **only the failed tasks and the tasks after them**. Tasks that already succeeded are **not** run again → saves time and money. You can also change parameters for the repair.

### What happened here
The setup already ran a job:
- `ingest` failed once, **retried**, and succeeded on attempt 2.
- `transform` failed: its parameter has a typo — `lab2.orders_bronz` (missing "e").
- `publish` didn't run (**upstream failed**).
""", do="""
1. Repair the run with the correct table name. Replace `<FILL-IN>` with `{"source_table": "lab2.orders_bronze"}`
2. **Run** — only `transform` and `publish` run again. **Check**.
""")

# ======================================================================== LAB 3
L["3a"] = dict(read="""
### The medallion architecture
Data moves through 3 layers:
- **Bronze** = raw data, as it arrived
- **Silver** = cleaned (right types, bad rows fixed)
- **Gold** = business answers (totals, reports)

### Spark Declarative Pipelines (SDP)
Old name: **DLT / Delta Live Tables**. You only **declare** *what* each table is. SDP handles *how*: the order, checkpoints, retries, only processing new data.

### Two kinds of tables in a pipeline
**Streaming table** — append-only; each new file/row is processed **once**. Good for bronze and silver.
```sql
CREATE OR REFRESH STREAMING TABLE orders_bronze AS
SELECT * FROM STREAM read_files('/Volumes/shop/raw/orders', format => 'json');

CREATE OR REFRESH STREAMING TABLE orders_silver AS
SELECT order_id, timestamp(order_timestamp) AS order_timestamp, customer_id
FROM STREAM orders_bronze;              -- STREAM = read only the new rows
```
**Materialized view** — the result is **recalculated** so it is always correct. Good for gold totals.
```sql
CREATE OR REFRESH MATERIALIZED VIEW gold_orders_by_date AS
SELECT date(order_timestamp) AS order_date, count(*) AS total_daily_orders
FROM orders_silver GROUP BY date(order_timestamp);
```

### In this lab
No SDP on your Mac, so you build the same 3 tables by hand with streams. You'll see what SDP does for you.
""", do="""
1. Silver reads bronze as a stream: replace `<FILL-IN>` in `spark.readStream.table(...)` with `"lab3.orders_bronze"`
2. Gold: replace `<FILL-IN>` after SELECT with `date(order_timestamp) AS order_date, count(*) AS total_daily_orders`
3. **Run** (defines the functions), then **Check**: it lands 2 files and runs the pipeline, then 2 more files and runs again. Watch the counts grow: 20 → 40.
""")

L["3b"] = dict(read="""
### Data quality rules = expectations
In a pipeline you write rules about your data, called **expectations**:
```sql
CONSTRAINT valid_id EXPECT (customer_id IS NOT NULL) ON VIOLATION DROP ROW
```
What to do with a row that breaks the rule:

| Action | Bad row | Pipeline |
|---|---|---|
| *(nothing written)* = **WARN** (default) | **kept** | continues, problem is counted |
| `ON VIOLATION DROP ROW` | **removed** | continues |
| `ON VIOLATION FAIL UPDATE` | — | **stops** |

The counts (passed / failed) are saved in the pipeline **event log**, so you can monitor quality.

### In this lab
`expect(df, [(name, condition, action)])` works the same way and prints event-log-style numbers.
""", do="""
1. `valid_notifications` should only **warn** → `"warn"`
2. `valid_id` should **drop** bad rows → `"drop"`
3. **Run** — read the printed numbers (how many rows were dropped?). **Check** also shows what **fail** does.
""")

L["3c"] = dict(read="""
### Joining data in a pipeline
We have two streaming tables: **orders** and **order status** (placed, preparing, delivered…). We want one table with both.

- A **join** combines rows from two tables where a key matches: `ON o.order_id = s.order_id`.
- **INNER JOIN** = keep only rows that match in both tables.

In SDP, to join **all rows** of two streaming tables every time the pipeline runs, you use a **materialized view** (it is recalculated, so it always sees everything).
""", do="""
1. First `<FILL-IN>`: the join type → `INNER JOIN`
2. Second `<FILL-IN>`: the match condition → `o.order_id = s.order_id`
3. **Run**, then **Check** — you'll see how many orders are in each status.
""")

L["3d"] = dict(read="""
### Change Data Capture (CDC)
A source system sends **changes**: INSERT a customer, UPDATE an address, DELETE a customer. **CDC** = applying those changes to your table so it matches the source.

### SCD Type 1 vs Type 2
- **Type 1**: overwrite — keep only the **latest** value. No history.
- **Type 2**: keep **history** — old row is closed, new row added.

### The out-of-order problem
Changes can arrive in the wrong order: the address from **May 20** arrives *before* the one from **May 15**. Without care, the old address wins. ✗
Fix: order by a date column → the **newest date wins**.

### In SDP (Databricks)
```sql
CREATE FLOW customers_flow AS AUTO CDC INTO customers_silver
FROM STREAM customers_bronze
KEYS (customer_id)                         -- which row
APPLY AS DELETE WHEN operation = 'DELETE'  -- when to delete
SEQUENCE BY process_date                   -- newest wins (fixes order!)
STORED AS SCD TYPE 1;
```
Old name: `APPLY CHANGES INTO`.

### In this lab
You rebuild it by hand: keep the newest change per customer (window function), then MERGE.
""", do="""
1. `orderBy(<FILL-IN>)` → newest first: `F.col("process_date").desc()`
2. `WHEN MATCHED AND <FILL-IN> THEN DELETE` → `s.operation = 'DELETE'`
3. **Run**, then **Check**: batch 1 inserts 3 customers; batch 2 updates Peter (out of order!), deletes Samarth, adds Kostas. Peter must end with **123 Main St.**
""")

# ======================================================================== LAB 4
L["4a"] = dict(read="""
### Why "DevOps" for data?
Pipelines are code. Code breaks. **DevOps** = habits that keep code reliable: small functions, tests, Git, automatic deployment (CI/CD).

### Modular code
Bad: one long block that reads, cleans and writes. You can't test one part.
Good: **small functions**. Each takes a DataFrame and **returns** a new DataFrame:
```python
def convert_miles_to_km(df, new_column_name, miles_column):
    return df.withColumn(new_column_name, F.round(F.col(miles_column) * 1.60934, 2))
```
- `df.withColumn(name, expression)` → add (or replace) a column.
- `F.round(x, 2)` → round to 2 decimals.
- `F.when(F.col("x") == 0, "zero").when(F.col("x") == 1, "one").otherwise("other")` → like IF / ELSE IF / ELSE.

Small functions can be **reused** and **tested** one by one.
""", do="""
This editor shows the file `lab4_project/src/transforms.py`. Write the 3 functions (delete `raise NotImplementedError`):
1. `convert_miles_to_km` → like the example above.
2. `uppercase_column_names` → `return df.select([F.col(f"`{c}`").alias(c.upper()) for c in df.columns])`
3. `add_high_cholest_flag` → new column `HighCholest_Group`: 0 → "Normal", 1 → "Above Average", 2 → "High", anything else → "Unknown" (use `F.when(...).when(...).when(...).otherwise("Unknown")`).
4. **💾 Save & check**.
""")

L["4b"] = dict(read="""
### What is a unit test?
A small program that checks **one function** with a tiny example:
1. make a small input DataFrame
2. call your function
3. compare with the result you **expect**

```python
def test_convert_miles_to_km(spark):
    df = spark.createDataFrame([(1.0,)], ["miles"])
    actual = convert_miles_to_km(df, "km", "miles")
    expected = spark.createDataFrame([(1.0, 1.61)], ["miles", "km"])
    assertDataFrameEqual(actual, expected)       # fails if different
```
### pytest
**pytest** finds files named `test_*.py` and functions named `test_*` and runs them all. `spark` in `(spark)` is a **fixture** — pytest hands it to the test automatically.

Tests run automatically on every code change in **CI** (continuous integration).
""", do="""
This editor shows `lab4_project/tests/test_transforms.py` (one example test is done).
1. Add a test for `uppercase_column_names`: make a DataFrame with columns like `"id"`, `"My_Column"` and check `.columns` equals the upper-case names (`assert ... == [...]`).
2. Add a test for `add_high_cholest_flag` with values 0, 1, 2, 3 and None (use `"HighCholest INT"` as the schema).
3. **💾 Save & check** (needs at least 3 passing tests).
""")

L["4c"] = dict(read="""
### Good tests catch bugs
A test that always passes is useless. The checker now runs your tests against **6 broken versions** of the code (e.g. no rounding, wrong number, NULL handled wrong). Good tests **fail** on every broken version.

Bugs hide in **edge cases**:
- NULL values
- rounding (3.3 miles = 5.31 km)
- values you didn't expect (3 instead of 0/1/2)
- column names with spaces
""", do="""
1. **💾 Save & check** — read which broken versions "survived" (your tests didn't notice them).
2. Add test cases for those edge cases (see the list above), then check again until none survive.
""")

# ======================================================================== LAB 5
L["5a"] = dict(read="""
### Keeping Delta tables fast and tidy
Many small writes → many small files → slow reads.

| Command | What it does |
|---|---|
| `OPTIMIZE t` | merges small files into big ones |
| `OPTIMIZE t ZORDER BY (col)` | also sorts data by a column so filters skip files |
| `RESTORE TABLE t TO VERSION AS OF 3` | undo: go back to version 3 |
| `VACUUM t` | deletes old files the table doesn't use anymore (default: keep 7 days) |

⚠ After **VACUUM**, time travel to old versions **fails** — their files are gone.
(Newer Databricks feature: **liquid clustering** `CLUSTER BY (col)` instead of ZORDER.)
""", do="""
The setup made a table with 12 tiny inserts (12+ small files).
1. `OPTIMIZE lab5.events_small ZORDER BY (id)`
2. `RESTORE TABLE lab5.events_small TO VERSION AS OF 3`
3. `VACUUM lab5.events_small RETAIN 0 HOURS` (0 hours is only OK in a lab!)
4. **Run** — compare "files before/after". **Check** shows that time travel now fails.
""")

L["5b"] = dict(read="""
### Keep only the newest row per user
A table has several rows per user (old emails and new emails). You want **one row per user — the latest**.

A **window function** looks at a group of rows *without* collapsing them:
```sql
row_number() OVER (PARTITION BY user_id ORDER BY updated_at DESC)
```
- `PARTITION BY user_id` → make a group for each user
- `ORDER BY updated_at DESC` → newest first inside the group
- `row_number()` → number them 1, 2, 3… → newest = **1**

Then keep `WHERE rn = 1`. This pattern is **very common** in the exam.
`SELECT DISTINCT` only removes rows that are **exactly** the same — not enough here.
""", do="""
1. Replace `<FILL-IN>` with `row_number() OVER (PARTITION BY user_id ORDER BY updated_at DESC)`
2. **Run**, then **Check** — u1 must keep `u1@third.com`.
""")

L["5c"] = dict(read="""
### Working with lists (arrays) without explode
Each event has a list `items`. Instead of exploding, SQL has **higher-order functions** that take a small function written with an arrow, for example `x -> x.price_usd > 1000`:

| Function | Meaning | Example |
|---|---|---|
| `size(arr)` | how many items | `size(items)` |
| `filter(arr, x -> cond)` | keep matching items | `filter(items, x -> x.price_usd > 1000)` |
| `transform(arr, x -> expr)` | change each item | `transform(items, x -> x.price_usd * 2)` |
| `exists(arr, x -> cond)` | true if any match | `exists(items, x -> x.quantity = 0)` |
| `aggregate(arr, start, (acc, x) -> expr)` | add them up | `aggregate(items, 0D, (acc, x) -> acc + x.price_usd)` |

`x` = one item. `acc` = the running total. `0D` = zero as a decimal number.
""", do="""
1. `item_count` → `size(e.items)`
2. `order_value` → `aggregate(e.items, 0D, (acc, x) -> acc + x.price_usd * x.quantity)`
3. `expensive_items` → `filter(e.items, x -> x.price_usd > 1000)`
4. **Run**, then **Check**.
""")

L["5d"] = dict(read="""
### Streaming + counting
A stream that **counts orders per customer** must update the totals when new data arrives. How the result is written is the **output mode**:
- **append** — write only brand-new rows (not allowed for counts like this)
- **complete** — rewrite the **whole** result table each time
- **update** — write only the rows that changed

The **checkpoint** remembers progress *and* the running totals.
""", do="""
1. Replace `<FILL-IN>` in `.outputMode(...)` with `"complete"`
2. **Run**, then **Check**.
""")

# ======================================================================== LAB 6 · exam section 3
L["6a"] = dict(read="""
### Bronze → Silver = cleaning
Bronze tables keep raw data **exactly as it arrived** — messy. The **silver** layer is the cleaned version that other people can trust. Typical cleaning:

| Problem | PySpark fix |
|---|---|
| a row has no id | `df.na.drop(subset=["customer_id"])` — remove rows where that column is NULL |
| a value is missing | `df.na.fill({"email": "unknown"})` — replace NULL with a value |
| a number is stored as text | `F.col("customer_id").cast("int")` — **standardize the data type** |
| extra spaces | `F.trim("full_name")` |
| one column holds two things | `F.split("full_name", " ")` → a list; `.getItem(0)` = first part, `.getItem(1)` = second |
| bad column name | `df.withColumnRenamed("old", "new")` |
| column not needed | `df.drop("raw_note")` |
| a date stored as text | `F.to_date("signup_date")` |

`withColumn("name", expression)` adds a new column, or replaces it if the name already exists.

### Exam objective (section 3)
*"Implement data cleaning by reading bronze tables, cleaning nulls, standardizing data types, and writing to new silver tables."* and *"adding, dropping, splitting, renaming columns, applying filters."*
""", do="""
1. `na.drop(subset=[...])` → `"customer_id"`
2. `na.fill({...})` → `"email": "unknown"`
3. `.cast(...)` → `"int"`
4. last name = the 2nd part → `.getItem(1)`
5. `withColumnRenamed("signup_date", ...)` → `"signed_up"`
6. `.drop(...)` → `"raw_note"`
7. **Run** — look at the clean table — then **Check**.
""")

L["6b"] = dict(read="""
### Joins = combine two tables on a key
| Join | Keeps |
|---|---|
| **inner** | only rows that match in **both** tables |
| **left** | **all** rows of the left table; no match → NULLs |
| multiple keys | match on several columns: `on=["customer_id", "country"]` |
| **cross** | **every** combination (3 sizes × 2 colors = 6 rows) — `a.crossJoin(b)` |

```python
orders.join(customers, "customer_id", "inner")   # how = "inner" | "left" | "right" | "full"
```

### Broadcast join (performance)
If one table is **small**, Spark can send a full copy to every worker → no big shuffle → much faster. You ask for it with `F.broadcast(small_df)`. In the plan it shows as **BroadcastHashJoin**. Spark also does it automatically for tables under `spark.sql.autoBroadcastJoinThreshold` (default 10 MB).

### Union = stack rows
| PySpark | SQL | Duplicates | Columns matched by |
|---|---|---|---|
| `a.union(b)` | `UNION ALL` | kept | **position** |
| `a.unionByName(b)` | — | kept | **name** |
| `.distinct()` after union | `UNION` | removed | |

⚠ Exam trap: in **SQL**, `UNION` removes duplicates but `UNION ALL` keeps them. In **PySpark**, `union()` behaves like UNION ALL.
""", do="""
1. inner join → `"inner"`; left join → `"left"`
2. two keys → `["customer_id", "country"]`
3. broadcast hint → `F.broadcast`
4. every combination → `crossJoin`
5. the second DataFrame has columns in a **different order** → `unionByName`
6. remove duplicates → `distinct`
7. **Run** — compare the row counts. Why is left (8) bigger than inner (6)? Then **Check**.
""")

L["6c"] = dict(read="""
### De-duplication
- `df.distinct()` → removes rows that are **exactly** the same in every column.
- `df.dropDuplicates(["order_id"])` → keeps **one row per order_id** (even if other columns differ).

### Aggregations
`df.groupBy("country").agg(F.count("*"))` makes one row per country. Inside `agg( )` you can put these functions:

| Function | Meaning |
|---|---|
| `F.count("*")` | number of rows |
| `F.countDistinct("x")` | exact number of different values (slow on big data) |
| `F.approx_count_distinct("x")` | **approximate** distinct count — much faster, tiny error |
| `F.avg("x")` / `F.mean("x")` | average |
| `F.sum`, `F.min`, `F.max` | the usual |

### Quick statistics
- `df.describe()` → count, mean, stddev, min, max
- `df.summary()` → the same **plus** percentiles (25%, 50%, 75%)
""", do="""
1. remove the duplicate order → `dropDuplicates`
2. fast distinct count → `F.approx_count_distinct`
3. mean → `avg`
4. statistics with percentiles → `summary`
5. **Run**, then **Check**.
""")

L["6d"] = dict(read="""
### Four tuning settings the exam names
| Setting | What it controls | Default |
|---|---|---|
| `spark.sql.shuffle.partitions` | how many pieces (tasks) data is split into **after a shuffle** (groupBy, join) | 200 |
| `spark.sql.autoBroadcastJoinThreshold` | max size of a table Spark broadcasts automatically; `-1` = never | 10 MB |
| `spark.default.parallelism` | default number of partitions for RDD operations | number of cores |
| `spark.executor.memory` / `spark.driver.memory` | memory per worker / for the driver — set **when the cluster starts** | depends on node |

**Shuffle** = moving data between machines so rows with the same key end up together. It is slow, so we tune it.
- Too **few** shuffle partitions → huge tasks, memory problems, spill to disk.
- Too **many** → thousands of tiny tasks, overhead.
- **AQE** (Adaptive Query Execution, on by default) can change these at runtime.

### How to "re-measure"
Change one setting → run again → compare the **plan** (`df.explain()`) and the time in the Spark UI.
""", do="""
1. disable automatic broadcast → `"-1"`
2. set it back to 10 MB → `str(10 * 1024 * 1024)`
3. the setting for partitions after a shuffle → `"spark.sql.shuffle.partitions"`
4. **Run** — the plan changes from SortMergeJoin to BroadcastHashJoin. Then **Check**.
""")

# ======================================================================== LAB 7 · exam sections 6 + 1
L["7a"] = dict(read="""
### What is data skew?
Spark splits work into **tasks**. After a `groupBy("customer_id")`, all rows of one customer go to **one task**. If one customer has 90% of the rows, that one task does 90% of the work while the others wait. This is **skew**.

### How to see it in the Spark UI
In the stage's **task summary**: Min / Median shuffle read ≈ 400 MB but **Max = 5 GB**; one task takes 10 min, others 30 s. You may also see **spill (disk)** — data that did not fit in memory.

### The fix: salting
Add a random number (**salt**, e.g. 0–7) to the key, so the hot customer is spread over 8 tasks:
1. `groupBy("customer_id", "salt")` → 8 partial sums for the hot customer
2. `groupBy("customer_id")` → add the partial sums together

⚠ Exam trap (official sample question): **AQE skew handling only helps JOINS**, not `groupBy`. More executors don't help — the one giant task still runs alone. **Fewer** shuffle partitions makes it **worse**.
""", do="""
The setup printed rows per task — one task has almost everything.
1. partial sums: group by `"customer_id", "salt"`
2. final totals: group by `"customer_id"` and sum `"partial_amount"`
3. **Run** — compare rows per task now. Then **Check**.
""")

L["7b"] = dict(read="""
### Liquid clustering
Delta tables store data in files. If rows with the same `customer_id` are spread over all files, a filter `WHERE customer_id = 7` must read **every** file. **Clustering** puts similar values together, so Spark can **skip** files.

| Old way | New way: **liquid clustering** |
|---|---|
| `PARTITIONED BY` (fixed folders) + `ZORDER` | `CLUSTER BY (col)` |
| changing the key = rewrite everything | `ALTER TABLE t CLUSTER BY (new_col)` — **change any time** |

```sql
CREATE TABLE events (event_id BIGINT, event_date DATE, customer_id BIGINT) CLUSTER BY (event_date);
ALTER TABLE events CLUSTER BY (customer_id);   -- change the key
OPTIMIZE events;                               -- cluster the data
```
(`CLUSTER BY AUTO` lets Databricks choose the key.)

### Predictive optimization
For Unity Catalog **managed** tables, Databricks can run **OPTIMIZE** and **VACUUM** for you automatically, when it predicts they help. You don't schedule maintenance jobs yourself.
""", do="""
1. create the table with `CLUSTER BY (event_date)`:
   `CREATE TABLE lab7.events (event_id BIGINT, event_date DATE, customer_id BIGINT) CLUSTER BY (event_date)`
2. change the key: `ALTER TABLE lab7.events CLUSTER BY (customer_id)`
3. cluster the data: `OPTIMIZE lab7.events`
4. **Run**, then **Check**.
""")

L["7c"] = dict(read="""
### Read the error, find where it happens
| Symptom | Likely cause | Fix |
|---|---|---|
| `OutOfMemoryError` on the **driver** after `collect()` / `toPandas()` | pulling big data into one machine | aggregate or write to a table; bigger driver only if needed |
| OOM / spill on **executors**, one slow task | skew or too-big partitions | salting, more shuffle partitions |
| `ImportError` / version errors after installing a library | **library conflict** | pin compatible versions; notebook- or cluster-scoped libraries; restart |
| cluster won't start: *launch failure*, *quota*, *init script failed* | **cluster startup failure** | read the cluster **event log**; fix init script, quota, instance type, permissions |
| task status **Timed Out** | run took longer than the task's **timeout** | raise the timeout threshold (with headroom) |

### Monitoring jobs (Lakeflow Jobs UI)
- **Run history**: compare today's duration with past runs (a baseline) to spot trends.
- **Task graph (DAG)**: a red task blocks everything after it (*upstream failed*).
- Track **run times** and **failure rates** over time; system tables `system.lakeflow.*` hold the history.
""", do="""
Read E1–E5 and fixes A–E in the setup output.
1. Fill each `<FILL-IN>` with one letter.
2. **Run**, then **Check**.
""")

L["7d"] = dict(read="""
### Compute types (exam section 1 · 6%)
| Compute | Best for | Cost idea |
|---|---|---|
| **All-purpose (interactive) cluster** | development, exploring, shared notebooks | runs while you work — expensive for production |
| **Job cluster** | scheduled production jobs | created for the run, **terminates after** → cheaper |
| **Serverless compute** (jobs, notebooks, pipelines) | no cluster setup, starts in seconds | pay only while running; Databricks manages it |
| **SQL warehouse** (serverless recommended) | BI and ad-hoc **SQL** for many users | autoscales with the number of queries |

The platform itself: **Delta Lake** (storage with ACID + time travel), **Unity Catalog** (one place for access control, lineage, audit), compute on top. Official sample question: rollback + audit + one source of truth for AI and BI → **Delta Lake + Unity Catalog**.
""", do="""
1. Match S1–S4 to W, J, P or S.
2. **Run**, then **Check**.
""")

# ======================================================================== LAB 8 · exam section 5
L["8a"] = dict(read="""
### Git folders (formerly Repos)
A **Git folder** connects a folder in your Databricks workspace to a Git repository (GitHub, GitLab, Azure DevOps, Bitbucket…). Inside Databricks you can:
- **clone** the repo, **create and switch branches**
- **commit and push** your changes
- **pull** the latest changes
- start a **pull request** (the review + merge happens in the Git provider)

### Why branches?
`main` = the code that runs in production. You never edit it directly. You make a **feature branch**, change things there, and ask for a review with a **pull request (PR)**. After the PR is merged, everyone **pulls** the new main.

Authentication: a **personal access token (PAT)** or the Databricks GitHub app.
""", do="""
Put the 6 letters in the right order, e.g. `"c", "b", ...`
1. Replace `<FILL-IN>` with the letters in quotes, separated by commas.
2. **Run**, then **Check**.
""")

L["8b"] = dict(read="""
### Declarative Automation Bundles (DABs, formerly Databricks Asset Bundles)
A **bundle** is one YAML file, `databricks.yml`, that describes your jobs, pipelines and code. You keep it in **Git**, and deploy the **same** code to **dev → test → prod**.

```yaml
bundle:
  name: health_etl

variables:                    # values that can change per environment
  catalog:
    default: dev_catalog

resources:                    # what to create
  jobs:
    my_job:
      name: my_job_${bundle.target}      # becomes my_job_dev or my_job_prod
      tasks:
        - task_key: ingest
          notebook_task:
            notebook_path: ./src/ingest.py
            base_parameters:
              catalog: ${var.catalog}     # uses the variable

targets:                      # the environments
  dev:
    mode: development         # safe mode: adds a prefix to names, pauses schedules
    default: true             # used when you don't say -t
  prod:
    mode: production
    variables:
      catalog: prod_catalog   # OVERRIDE: prod uses a different catalog
```
- `${var.name}` = a variable. `${bundle.target}` = the target name.
- **Overrides**: a target can change variables and resources → same codebase, different settings.

### Where does a variable's value come from? (highest wins)
1. `--var="catalog=x"` on the command line
2. environment variable **`BUNDLE_VAR_catalog`**
3. the target's `variables:` override
4. the `default`
""", do="""
This editor shows `lab8_project/databricks.yml`. Replace every `<FILL-IN …>`:
1. `default:` of catalog → `dev_catalog`
2. job name → `health_etl_${bundle.target}`
3. task parameter catalog → `${var.catalog}`
4. dev `default:` → `true`
5. test catalog → `test_catalog`
6. prod `mode:` → `production`
7. **💾 Save & check** — it validates dev, test and prod like `databricks bundle validate`.
""")

L["8c"] = dict(read="""
### Secrets: never write passwords in files
A password in `databricks.yml` or a notebook ends up in Git → everyone can read it. Instead:
- declare a variable **without a default** (`db_password`)
- in CI (e.g. GitHub Actions) store the password as a **secret** and pass it as the environment variable **`BUNDLE_VAR_db_password`**
- the CLI injects it at deploy time → it never touches the code
(Official sample question #6 — answer: `BUNDLE_VAR_` environment variable.)

### The Databricks CLI for bundles
| Command | Does |
|---|---|
| `databricks bundle validate -t prod` | checks the YAML and resolves variables for that target |
| `databricks bundle deploy -t prod` | uploads code and creates/updates jobs & pipelines in that target |
| `databricks bundle run -t prod health_etl_job` | starts a job (or pipeline) from the bundle — the last word is the job's name in the YAML |
| `databricks bundle destroy -t dev` | removes what the bundle deployed |

A CI/CD pipeline usually runs: **validate → deploy to test → run tests → deploy to prod**.
""", do="""
1. `target=` → `"prod"`;  `env=` → `github_secrets`
2. write the three CLI commands for the **prod** target (job key: `health_etl_job`)
3. **Run** — see where each variable's value came from. Then **Check**.
""")

# ======================================================================== LAB 9 · exam section 7
L["9a"] = dict(read="""
### Unity Catalog security in one picture
`catalog` → `schema` → `table / view / volume / function`

To **read** a table, a user needs permission on **every level**:
1. `USE CATALOG` on the catalog
2. `USE SCHEMA` on the schema
3. `SELECT` on the table

```sql
GRANT USE CATALOG ON CATALOG main TO `analysts`;
GRANT USE SCHEMA  ON SCHEMA  main.sales TO `analysts`;
GRANT SELECT      ON TABLE   main.sales.orders TO `analysts`;
REVOKE SELECT     ON TABLE   main.sales.orders FROM `contractors`;   -- REVOKE uses FROM
```
| Privilege | Allows |
|---|---|
| `SELECT` | read |
| `MODIFY` | insert / update / delete rows |
| `CREATE TABLE` (on a schema) | create tables |
| `ALL PRIVILEGES` | everything |

**Principals** = who gets the permission: **users**, **groups** (best practice) and **service principals** (for automated jobs). Names go in back-ticks.
The exam guide also lists **DENY** (explicitly block a privilege) next to GRANT/REVOKE — know that it exists.
""", do="""
1. three GRANTs for `analysts` (catalog `main`, schema `main.sales`, table `main.sales.orders`)
2. a REVOKE for `contractors`
3. a GRANT MODIFY for `etl-sp`
4. End each statement with `;`. **Run**, then **Check**.
""")

L["9b"] = dict(read="""
### Managed vs external tables
| | Managed | External |
|---|---|---|
| where the files live | storage **managed by Unity Catalog** | a path **you** give with `LOCATION` |
| `DROP TABLE` | deletes **metadata and data** | deletes metadata only — **files stay** |
| recommended for | new tables (gets predictive optimization) | data shared with other tools |

```sql
CREATE TABLE main.raw.events_ext (id INT) LOCATION 's3://bucket/events';   -- external
```
### Converting
- external → managed: `ALTER TABLE t SET MANAGED` (data moves into managed storage)
- undo within **14 days**: `ALTER TABLE t UNSET MANAGED` (official sample question #8)
""", do="""
1. external table → add `LOCATION 's3://acme-raw/events'`
2. convert → `SET MANAGED`;  roll back → `UNSET MANAGED`
3. the two True/False answers
4. **Run**, then **Check**.
""")

L["9c"] = dict(read="""
### Fine-grained security: the same table, different users see different data
**Column mask** — hide part of a value:
```sql
CREATE FUNCTION mask_cc(cc STRING) RETURN
  CASE WHEN is_account_group_member('finance_team') THEN cc
       ELSE concat('****', right(cc, 4)) END;
ALTER TABLE customers ALTER COLUMN credit_card_number SET MASK mask_cc;
```
**Row filter** — hide whole rows:
```sql
CREATE FUNCTION eu_only(region STRING) RETURN is_account_group_member('admins') OR region = 'EU';
ALTER TABLE customers SET ROW FILTER eu_only ON (region);
```
`is_account_group_member('group')` = true if the person running the query is in that group. (Official sample question #7.)

### In this lab
We simulate users and groups with `login(user, groups)` and apply your two expressions in a view.
""", do="""
1. mask condition → `is_account_group_member('finance_team')`
2. row filter → `is_account_group_member('admins') OR region = 'EU'`
3. **Run** — see what Fiona (finance), Adam (admin) and Eve (nobody) see. Then **Check**.
""")

L["9d"] = dict(read="""
### ABAC = attribute-based access control
Writing a mask for every column of every table does not scale. With **ABAC**:
1. you put **governed tags** on data (e.g. tag columns `pii`, tables `region`)
2. you write **one policy** on a catalog or schema: *"for every column tagged `pii`, apply this mask for everyone except `finance_team`"*
3. it applies **automatically** to all matching tables — also new ones

| Need | Tool |
|---|---|
| one column in one table | a column mask |
| the same rule on many tables, by tag | an **ABAC policy** |
| who may read/write an object at all | `GRANT` / `REVOKE` |
""", do="""
1. Match Q1–Q4 to `"ABAC"`, `"MASK"` or `"GRANT"`.
2. **Run**, then **Check**.
""")
