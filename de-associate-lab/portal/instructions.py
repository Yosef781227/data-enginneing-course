"""Step-by-step task instructions (replace the old `do` texts).

Rules used here so a first-time reader can't misread them:
- Every gap in the code is numbered: <FILL-IN 1>, <FILL-IN 2>, …  One numbered item per gap.
- Each item shows the FINISHED LINE exactly as it should look after typing.
- No "...", no "e.g." inside things to type. Quotes are shown exactly.
"""

D = {}

D["1a"] = """
**Gap 1** — create an empty table named `lab1.demo_delta` with two columns.
```python
spark.sql(\"\"\"CREATE TABLE lab1.demo_delta (id INT, name STRING)\"\"\")
```
**Gap 2** — add three rows to it.
```python
spark.sql(\"\"\"INSERT INTO lab1.demo_delta VALUES (1, 'peter'), (2, 'zebi'), (3, 'samarth')\"\"\")
```
Then press **▶ Run**. No red error = it worked. Then press **✔ Check my answer**.
"""

D["1b"] = """
**Gap 1** — read all the Parquet files in the folder. Keep the `f` before the quotes and the back-ticks around the path.
The finished code:
```python
spark.sql(f\"\"\"
CREATE TABLE lab1.users_bronze_ctas AS
SELECT * FROM parquet.`{users_path}`
\"\"\")
```
Then **Run** and **Check**. After the check you will see what `DROP TABLE` does to a managed and an external table.
"""

D["1c"] = """
**Gap 1** — load the files that have landed:
```python
copy_into(spark, "lab1.users_bronze_ci", vol, "parquet")
```
**Gap 2** — type the exact same line again (we want to see what happens on a second run):
```python
copy_into(spark, "lab1.users_bronze_ci", vol, "parquet")
```
**Gap 3** — a new file with an extra column `country` just landed. First try the normal load (it fails), then load with `merge_schema=True`:
```python
try:
    copy_into(spark, "lab1.users_bronze_ci", vol, "parquet")
except Exception as e:
    print("ERROR:", e)
copy_into(spark, "lab1.users_bronze_ci", vol, "parquet", merge_schema=True)
```
**Run** and read the terminal: the second load inserts **0 rows**. Then **Check** (150 rows expected).
"""

D["1d"] = """
**Gap 1** — the files that land are Parquet files:
```python
        .format("parquet")
```
**Gap 2** — the checkpoint folder (the stream's memory):
```python
        .option("checkpointLocation", checkpoint("lab1", "users_stream"))
```
**Run** (this only creates the function), then **Check**. Watch the counts: 50 → 100 → 100.
"""

D["1e"] = """
**Gap 1** — the columns in these files are separated by a pipe `|`:
```python
    .option("sep", "|")
```
**Gaps 2, 3 and 4** — the three new columns. The finished `.select(...)` looks like this:
```python
    .select("*",
            F.col("_metadata.file_name").alias("source_file"),
            F.col("_metadata.file_modification_time").alias("file_modification_time"),
            F.current_timestamp().alias("ingestion_time")))
```
Keep the commas at the end of the lines exactly as shown. **Run**, then **Check**.
"""

D["1f"] = """
**Gap 1** — a value for `price_fixed` that is never empty: take `price`; if it is NULL, take the 3rd value of the raw line and remove the `$`.
The finished line:
```sql
       coalesce(price, cast(regexp_replace(split(_corrupt_record, ',')[2], '[$]', '') AS DOUBLE)) AS price_fixed,
```
Read it from the inside out: `split` cuts the line at commas → `[2]` takes the 3rd piece (counting starts at 0) → `regexp_replace` removes `$` → `cast` makes it a number → `coalesce` uses it only when `price` is NULL.
**Run**, then **Check**.
"""

D["1g-1"] = """
**Gap 1** — turn the base64 `value` into readable text:
```sql
       cast(unbase64(value) AS STRING) AS decoded_value
```
**Run**, then **Check**.
"""

D["1g-2"] = """
**Gap 1** — the shape (schema) of the JSON. Copy this whole line:
```python
event_schema = "STRUCT<device: STRING, event_name: STRING, event_timestamp: BIGINT, geo: STRUCT<city: STRING, state: STRING>, items: ARRAY<STRUCT<item_id: STRING, price_usd: DOUBLE, quantity: BIGINT>>, user_id: STRING>"
```
(It is the same text that `schema_of_json` printed in the setup output.)

**Gap 2** — one row per item, but keep events that have no items:
```sql
     exploded AS (SELECT e, explode_outer(e.items) AS item FROM parsed)
```
**Run** — rows with an empty `item_id` are the events without items. Then **Check**.
"""

D["1h-1"] = """
**Gap 1** — how a target row matches a source row:
```sql
ON t.id = s.id
```
**Gap 2** — what to do for `update`:
```sql
WHEN MATCHED AND s.status = 'update' THEN UPDATE SET t.email = s.email, t.status = s.status
```
**Gap 3** — what to do for `delete`:
```sql
WHEN MATCHED AND s.status = 'delete' THEN DELETE
```
**Gap 4** — new rows:
```sql
WHEN NOT MATCHED THEN INSERT (id, first_name, email, sign_up_date, status) VALUES (s.id, s.first_name, s.email, s.sign_up_date, s.status)
```
**Run** — id 1 has a new email, id 2 is gone, id 4 is new. Then **Check**.
"""

D["1h-2"] = """
**Gap 1** — switch on schema evolution:
```python
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
```
**Gap 2** — insert all columns of the new rows:
```sql
WHEN NOT MATCHED THEN INSERT *
```
**Run** — the table now has a `country` column. Then **Check**.
"""

D["2a"] = """
**Gap 1** — the join task must wait for both ingest tasks. Write the two task names as a Python list:
```python
@job.task("join_customers_orders", depends_on=["ingest_orders", "ingest_customers"])
```
**Run** — every task shows ✅. Then **Check**.
"""

D["2b"] = """
**Gap 1** — save the count so later tasks can use it:
```python
    ctx.task_values.set("row_count", n)
```
**Gap 2** — give the `report` task that saved value. The double curly brackets are part of the text:
```python
@job.task("report", depends_on=["count_orders"], parameters={"rows": "{{tasks.count_orders.values.row_count}}"})
```
**Gap 3** — run the job with the job parameter `catalog` set to `lab2_prod`:
```python
run = job.run(parameters={"catalog": "lab2_prod"})
```
Before you **Run**, guess: will `count_orders` print `task_default` or `lab2_prod`? Then **Run** and **Check**.
"""

D["2c"] = """
**Gap 1** — the If/else task compares the value saved by `check_duplicates`:
```python
job.if_else("duplicates_exist", left="{{tasks.check_duplicates.values.has_duplicates}}", op="==", right="true",
```
**Gap 2** — the For each task waits for both branches, but one branch is always skipped. The rule that still lets it run:
```python
             depends_on=["drop_duplicates", "no_duplicates"], run_if="NONE_FAILED")
```
Want to see why? Type `ALL_SUCCEEDED` first and **Run** — the loop gets skipped. Then change it to `NONE_FAILED`, **Run**, **Check**.
"""

D["2d"] = """
**Gap 1** — repair the run and give the correct table name (the old one had a typo: `orders_bronz`):
```python
run = job.repair(run, parameters={"source_table": "lab2.orders_bronze"})
```
**Run** — only `transform` and `publish` run again. Then **Check**.
"""

D["3a"] = """
**Gap 1** — silver reads the bronze table as a stream:
```python
    (spark.readStream.table("lab3.orders_bronze")
```
**Gap 2** — the gold table counts orders per day:
```sql
                 SELECT date(order_timestamp) AS order_date, count(*) AS total_daily_orders
```
**Run** (this only creates the functions), then **Check**. The check lands files and runs the pipeline twice: 20 → 40 rows.
"""

D["3b"] = """
**Gap 1** — wrong notifications only give a warning:
```python
    ("valid_notifications", "notifications IN ('Y','N')", "warn"),
```
**Gap 2** — rows without a customer are removed:
```python
    ("valid_id",            "customer_id IS NOT NULL",    "drop"),
```
**Run** — read the numbers: how many rows were dropped? Then **Check**.
"""

D["3c"] = """
**Gaps 1 and 2** — the join type, and which columns must be equal. The finished line:
```sql
INNER JOIN lab3.status_silver s ON o.order_id = s.order_id
```
**Run**, then **Check**.
"""

D["3d"] = """
**Gap 1** — sort each customer's changes with the newest date first:
```python
    w = Window.partitionBy("customer_id").orderBy(F.col("process_date").desc())
```
**Gap 2** — delete the row when the change says DELETE:
```sql
      WHEN MATCHED AND s.operation = 'DELETE' THEN DELETE
```
**Run**, then **Check**. Peter must end with the address **123 Main St.**
"""

D["4a"] = """
This step has **no numbered gaps**. The editor shows the file `lab4_project/src/transforms.py` with three empty functions.
In each function, **delete the line** `raise NotImplementedError` and write the code below in its place.

**Function 1:**
```python
    return df.withColumn(new_column_name, F.round(F.col(miles_column) * 1.60934, 2))
```
**Function 2:**
```python
    return df.select([F.col(f"`{c}`").alias(c.upper()) for c in df.columns])
```
**Function 3:**
```python
    return df.withColumn(
        "HighCholest_Group",
        F.when(F.col("HighCholest") == 0, "Normal")
        .when(F.col("HighCholest") == 1, "Above Average")
        .when(F.col("HighCholest") == 2, "High")
        .otherwise("Unknown"),
    )
```
Keep the 4 spaces at the start of each line (Python uses spaces to know what is inside a function). Then press **💾 Save & check**.
"""

D["4b"] = """
This step has **no numbered gaps**. The editor shows `lab4_project/tests/test_transforms.py`; one test is already written.
Add two more tests at the end of the file (under the `# TODO` lines).

**Test 2** — copy this:
```python
def test_uppercase_column_names(spark):
    df = spark.createDataFrame([(1, 2)], ["id", "My_Column"])
    assert uppercase_column_names(df).columns == ["ID", "MY_COLUMN"]
```
**Test 3** — copy this:
```python
def test_add_high_cholest_flag(spark):
    df = spark.createDataFrame([(0,), (1,), (2,), (3,), (None,)], "HighCholest INT")
    expected = spark.createDataFrame(
        [(0, "Normal"), (1, "Above Average"), (2, "High"), (3, "Unknown"), (None, "Unknown")],
        "HighCholest INT, HighCholest_Group STRING")
    assertDataFrameEqual(add_high_cholest_flag(df), expected)
```
Leave one empty line between tests. Then **💾 Save & check**.
"""

D["4c"] = """
This step has **no numbered gaps**. Press **💾 Save & check** first.
The result lists the broken versions your tests did **not** notice (names like `m1_no_round`).
For each one, add a test that would fail on it. Example for `m1_no_round` (the km value is not rounded):
```python
def test_convert_miles_to_km_rounding(spark):
    df = spark.createDataFrame([(10.0,)], ["miles"])
    expected = spark.createDataFrame([(10.0, 16.09)], ["miles", "km"])
    assertDataFrameEqual(convert_miles_to_km(df, "km", "miles"), expected)
```
Save & check again until no broken version is left.
"""

D["5a"] = """
**Gap 1** — merge the small files and sort by `id`:
```python
spark.sql("OPTIMIZE lab5.events_small ZORDER BY (id)")
```
**Gap 2** — go back to version 3:
```python
spark.sql("RESTORE TABLE lab5.events_small TO VERSION AS OF 3")
```
**Gap 3** — delete old files now (0 hours is only safe in a practice lab):
```python
spark.sql("VACUUM lab5.events_small RETAIN 0 HOURS")
```
**Run** — compare "files before" and "files after". Then **Check**.
"""

D["5b"] = """
**Gap 1** — number each user's rows, newest first:
```sql
  SELECT *, row_number() OVER (PARTITION BY user_id ORDER BY updated_at DESC) AS rn FROM user_updates)
```
**Run**, then **Check** — user u1 must keep `u1@third.com`.
"""

D["5c"] = """
**Gap 1** — how many items:
```sql
       size(e.items) AS item_count,
```
**Gap 2** — add up price × quantity:
```sql
       aggregate(e.items, 0D, (acc, x) -> acc + x.price_usd * x.quantity) AS order_value,
```
**Gap 3** — keep only items above 1000:
```sql
       filter(e.items, x -> x.price_usd > 1000) AS expensive_items
```
**Run**, then **Check**.
"""

D["5d"] = """
**Gap 1** — write the whole result table every time:
```python
 .writeStream.outputMode("complete")
```
**Run**, then **Check**.
"""

D["6a"] = """
**Gap 1** — remove rows that have no customer_id:
```python
    .na.drop(subset=["customer_id"])
```
**Gap 2** — an empty email becomes "unknown":
```python
    .na.fill({"email": "unknown"})
```
**Gap 3** — make customer_id a whole number:
```python
    .withColumn("customer_id", F.col("customer_id").cast("int"))
```
**Gap 4** — the last name is the 2nd part (counting starts at 0, so the 2nd part is number 1):
```python
    .withColumn("last_name", F.split("full_name", " ").getItem(1))
```
**Gap 5** — the new column name:
```python
    .withColumnRenamed("signup_date", "signed_up")
```
**Gap 6** — the column to remove:
```python
    .drop("raw_note"))
```
**Run** — look at the clean table. Then **Check**.
"""

D["6b"] = """
Type each answer **with** the quotes or brackets shown.

**Gap 1** — only matching rows: `"inner"`
**Gap 2** — all orders, even without a customer: `"left"`
**Gap 3** — match on two columns: `["customer_id", "country"]`
**Gap 4** — copy the small table to every worker: `F.broadcast`
**Gap 5** — every size with every color: `crossJoin`
**Gap 6** — stack two tables whose columns are in a different order: `unionByName`
**Gap 7** — remove duplicate rows: `distinct`

Finished lines for gaps 4 to 7:
```python
bcast_df = orders.join(F.broadcast(customers), "customer_id", "left")
cross_df = sizes.crossJoin(colors)
union_all = eu.unionByName(us)
union_distinct = union_all.distinct()
```
**Run** — why does `left` give 8 rows but `inner` only 6? Then **Check**.
"""

D["6c"] = """
**Gap 1** — keep one row per order_id:
```python
clean = orders.dropDuplicates(["order_id"])
```
**Gap 2** — fast approximate count of different customers:
```python
         F.approx_count_distinct("customer_id").alias("approx_customers"),
```
**Gap 3** — the average:
```python
         F.avg("amount").alias("avg_amount")))
```
**Gap 4** — statistics with percentiles:
```python
show(clean.select("amount").summary())
```
**Run**, then **Check**.
"""

D["6d"] = """
**Gap 1** — switch off automatic broadcast (the value is the text `-1`):
```python
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
```
**Gap 2** — set it back to 10 MB (10 × 1024 × 1024 bytes, given as text):
```python
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", str(10 * 1024 * 1024))
```
**Gap 3** — the setting for the number of pieces after a shuffle:
```python
spark.conf.set("spark.sql.shuffle.partitions", "8")
```
**Run** — the join type changes from SortMergeJoin to BroadcastHashJoin. Then **Check**.
"""

D["7a"] = """
**Gap 1** — first sum per customer **and** salt:
```python
partial = salted.groupBy("customer_id", "salt").agg(F.sum("amount").alias("partial_amount"))
```
**Gaps 2 and 3** — then sum the partial sums per customer:
```python
totals = partial.groupBy("customer_id").agg(F.sum("partial_amount").alias("total_amount"))
```
**Run** — compare the rows per task with the table above (much more even now). Then **Check**.
"""

D["7b"] = """
**Gap 1** — create the table with liquid clustering on `event_date`:
```python
spark.sql(\"\"\"CREATE TABLE lab7.events (event_id BIGINT, event_date DATE, customer_id BIGINT) CLUSTER BY (event_date)\"\"\")
```
**Gap 2** — change the clustering column to `customer_id`:
```python
spark.sql(\"\"\"ALTER TABLE lab7.events CLUSTER BY (customer_id)\"\"\")
```
**Gap 3** — cluster the data now:
```python
spark.sql(\"\"\"OPTIMIZE lab7.events\"\"\")
```
**Run**, then **Check**.
"""

D["7c"] = """
Read the 5 errors (**E1**–**E5**) and the 5 fixes (**A**–**E**) in the terminal output above.
Each gap is **one capital letter** between the quotes that are already there.

How to type it — for example, if you think the fix for E1 is D, gap 1 becomes `"E1": "D"`
(D is only an example, not the answer). Fill all 5 gaps, **Run**, then **Check**.
"""

D["7d"] = """
Read the 4 situations (**S1**–**S4**) and the 4 compute types (**W**, **J**, **P**, **S**) in the terminal output above.
Each gap is **one capital letter** between the quotes that are already there.

For example, if you think situation S1 needs compute J, gap 1 becomes `"S1": "J"` (only an example, not the answer).
Fill all 4 gaps, **Run**, then **Check**.
"""

D["8a"] = """
**Gap 1** — the six letters (**a** to **f**) in the right order, each in quotes, separated by commas.

How to type it — if you thought the order was a, b, c, d, e, f, the finished line would be:
```python
submit("8a", ["a", "b", "c", "d", "e", "f"])
```
That order is **wrong** — it only shows the format. Put the letters in the order the steps really happen. **Run**, then **Check**.
"""

D["8b"] = """
The editor shows the file `lab8_project/databricks.yml`. It has 6 numbered gaps.
In YAML the **spaces at the start of a line matter** — only replace the `<FILL-IN n>` text, don't move anything.

**Gap 1** → `dev_catalog`  &nbsp; so the line becomes `    default: dev_catalog`
**Gap 2** → `${bundle.target}`  &nbsp; so the line becomes `      name: health_etl_${bundle.target}`
**Gap 3** → `${var.catalog}`  &nbsp; so the line becomes `              catalog: ${var.catalog}`
**Gap 4** → `true`  &nbsp; so the line becomes `    default: true`
**Gap 5** → `test_catalog`  &nbsp; so the line becomes `      catalog: test_catalog`
**Gap 6** → `production`  &nbsp; so the line becomes `    mode: production`

Then press **💾 Save & check** — it checks dev, test and prod, like `databricks bundle validate`.
"""

D["8c"] = """
**Gaps 1 and 2** — validate the **prod** target and pass the secret as environment variables. The finished line:
```python
result = validate(BUNDLE, target="prod", env=github_secrets)
```
**Gaps 3, 4 and 5** — type the three commands between the quotes that are already there:
```python
  "validate": "databricks bundle validate -t prod",
  "deploy":   "databricks bundle deploy -t prod",
  "run":      "databricks bundle run -t prod health_etl_job",
```
**Run** — the output shows where each value came from. Then **Check**.
"""

D["9a"] = """
Write one SQL statement per line and end each one with a semicolon `;`.
Names of groups and principals go between back-ticks: `` `analysts` ``.

**Gap 1** — three statements, so analysts can read the table:
```sql
GRANT USE CATALOG ON CATALOG main TO `analysts`;
GRANT USE SCHEMA ON SCHEMA main.sales TO `analysts`;
GRANT SELECT ON TABLE main.sales.orders TO `analysts`;
```
**Gap 2** — take reading away from contractors (note: REVOKE uses **FROM**):
```sql
REVOKE SELECT ON TABLE main.sales.orders FROM `contractors`;
```
**Gap 3** — let the service principal change rows:
```sql
GRANT MODIFY ON TABLE main.sales.orders TO `etl-sp`;
```
**Run**, then **Check**.
"""

D["9b"] = """
**Gap 1** — an external table needs a LOCATION:
```sql
CREATE TABLE main.raw.events_ext (id INT, ts TIMESTAMP) LOCATION 's3://acme-raw/events';
```
**Gap 2** — convert it to managed:
```sql
ALTER TABLE main.raw.events_ext SET MANAGED;
```
**Gap 3** — undo the conversion:
```sql
ALTER TABLE main.raw.events_ext UNSET MANAGED;
```
**Gaps 4 and 5** — type `True` or `False` (capital first letter, no quotes):
- Gap 4: does `DROP TABLE` on a **managed** table delete the data?
- Gap 5: does `DROP TABLE` on an **external** table delete the data?

**Run**, then **Check**.
"""

D["9c"] = """
**Gap 1** — the condition "this person is in the finance team":
```sql
MASK = \"\"\"CASE WHEN is_account_group_member('finance_team') THEN credit_card_number
```
**Gap 2** — admins see every row, everyone else only rows where region is EU:
```python
ROW_FILTER = \"\"\"is_account_group_member('admins') OR region = 'EU'\"\"\"
```
**Run** — compare what Fiona (finance), Adam (admin) and Eve (no group) see. Then **Check**.
"""

D["9d"] = """
Read the 4 situations (**Q1**–**Q4**) and the 3 tools (**ABAC**, **MASK**, **GRANT**) in the terminal output above.
Each gap is **one word in capitals** between the quotes that are already there.

For example, gap 1 could become `"Q1": "GRANT"` (only an example, not the answer).
Fill all 4 gaps, **Run**, then **Check**.
"""
