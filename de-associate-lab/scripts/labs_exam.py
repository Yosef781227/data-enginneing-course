"""Labs 6–9: added to match the official exam guide (May 2026 exam, guide updated Aug 2026).
Lab 6 → Section 3 · Lab 7 → Sections 6 + 1 · Lab 8 → Section 5 · Lab 9 → Section 7
"""


def make(SETUP, LEGEND):
    LAB6 = [
        ("md", "# Lab 6 — Transform, model & tune (Exam section 3 · 22%)\n\n" + LEGEND),
        ("code", SETUP + '''\nreset_lab("lab6")
spark.sql("""CREATE TABLE lab6.customers_bronze AS SELECT * FROM VALUES
  ('1', '  Ana Silva ', 'ana@x.com',  '2024-01-05', 'us', 'vip'),
  ('2', 'Ben Okoro',    NULL,         '2024-02-11', 'eu', NULL),
  (NULL,'Ghost Row',    'g@x.com',    '2024-03-01', 'us', 'bad id'),
  ('3', 'Chen Li',      'chen@x.com', '2024-03-20', 'EU', NULL),
  ('4', 'Dina Haddad',  NULL,         '2024-04-02', 'us', 'new')
  AS t(customer_id, full_name, email, signup_date, country, raw_note)""")
spark.sql("""CREATE TABLE lab6.orders AS SELECT * FROM VALUES
  (101, 1, 'US', 120.0), (102, 1, 'US', 80.0), (103, 2, 'EU', 45.5), (104, 3, 'EU', 300.0),
  (105, 9, 'US', 10.0),  (105, 9, 'US', 10.0), (106, 4, 'US', 99.9), (107, 3, 'US', 15.0)
  AS t(order_id, customer_id, country, amount)""")'''),

        ("md", "## 6a · Clean bronze into silver"),
        ("ex", '''# TODO 6a
bronze = spark.table("lab6.customers_bronze")
silver = (bronze
    .na.drop(subset=[<FILL-IN>])                          # drop rows with no customer_id
    .na.fill({<FILL-IN>})                                 # NULL email -> "unknown"
    .withColumn("customer_id", F.col("customer_id").cast(<FILL-IN>))   # STRING -> INT
    .withColumn("full_name", F.trim("full_name"))
    .withColumn("first_name", F.split("full_name", " ").getItem(0))
    .withColumn("last_name", F.split("full_name", " ").getItem(<FILL-IN>))
    .withColumn("country", F.upper("country"))
    .withColumn("signup_date", F.to_date("signup_date"))
    .withColumnRenamed("signup_date", <FILL-IN>)          # new name: "signed_up"
    .drop(<FILL-IN>))                                     # remove the raw_note column
silver.write.mode("overwrite").saveAsTable("lab6.customers_silver")
show(spark.table("lab6.customers_silver"))''',
         '''bronze = spark.table("lab6.customers_bronze")
silver = (bronze
    .na.drop(subset=["customer_id"])
    .na.fill({"email": "unknown"})
    .withColumn("customer_id", F.col("customer_id").cast("int"))
    .withColumn("full_name", F.trim("full_name"))
    .withColumn("first_name", F.split("full_name", " ").getItem(0))
    .withColumn("last_name", F.split("full_name", " ").getItem(1))
    .withColumn("country", F.upper("country"))
    .withColumn("signup_date", F.to_date("signup_date"))
    .withColumnRenamed("signup_date", "signed_up")
    .drop("raw_note"))
silver.write.mode("overwrite").saveAsTable("lab6.customers_silver")
show(spark.table("lab6.customers_silver"))'''),
        ("code", 'check("6a")'),

        ("md", "## 6b · Joins and unions"),
        ("ex", '''# TODO 6b
from labutils.submit import submit
orders = spark.table("lab6.orders")
customers = spark.table("lab6.customers_silver")
inner_df = orders.join(customers.select("customer_id", "first_name"), "customer_id", <FILL-IN>)
left_df  = orders.join(customers.select("customer_id", "first_name"), "customer_id", <FILL-IN>)
multi_df = orders.join(customers.select("customer_id", "country"), <FILL-IN>, "inner")   # 2 keys
bcast_df = orders.join(<FILL-IN>(customers), "customer_id", "left")                     # broadcast hint
sizes  = spark.createDataFrame([("S",), ("M",), ("L",)], ["size"])
colors = spark.createDataFrame([("red",), ("blue",)], ["color"])
cross_df = sizes.<FILL-IN>(colors)                                                       # every combination
eu = spark.createDataFrame([(1, "EU"), (2, "EU")], ["id", "region"])
us = spark.createDataFrame([("US", 3), ("EU", 2)], ["region", "id"])                    # other column order!
union_all = eu.<FILL-IN>(us)                                                             # match by NAME
union_distinct = union_all.<FILL-IN>()                                                   # remove duplicates
for name, df in [("inner", inner_df), ("left", left_df), ("multi-key", multi_df), ("cross", cross_df),
                 ("union all", union_all), ("union distinct", union_distinct)]:
    print(f"{name:<15} rows = {df.count()}")
submit("6b", {"inner": inner_df.count(), "left": left_df.count(), "multi": multi_df.count(),
              "cross": cross_df.count(), "union_all": union_all.count(),
              "union_distinct": union_distinct.count(),
              "bcast_plan": bcast_df._jdf.queryExecution().executedPlan().toString()})''',
         '''from labutils.submit import submit
orders = spark.table("lab6.orders")
customers = spark.table("lab6.customers_silver")
inner_df = orders.join(customers.select("customer_id", "first_name"), "customer_id", "inner")
left_df  = orders.join(customers.select("customer_id", "first_name"), "customer_id", "left")
multi_df = orders.join(customers.select("customer_id", "country"), ["customer_id", "country"], "inner")
bcast_df = orders.join(F.broadcast(customers), "customer_id", "left")
sizes  = spark.createDataFrame([("S",), ("M",), ("L",)], ["size"])
colors = spark.createDataFrame([("red",), ("blue",)], ["color"])
cross_df = sizes.crossJoin(colors)
eu = spark.createDataFrame([(1, "EU"), (2, "EU")], ["id", "region"])
us = spark.createDataFrame([("US", 3), ("EU", 2)], ["region", "id"])
union_all = eu.unionByName(us)
union_distinct = union_all.distinct()
for name, df in [("inner", inner_df), ("left", left_df), ("multi-key", multi_df), ("cross", cross_df),
                 ("union all", union_all), ("union distinct", union_distinct)]:
    print(f"{name:<15} rows = {df.count()}")
submit("6b", {"inner": inner_df.count(), "left": left_df.count(), "multi": multi_df.count(),
              "cross": cross_df.count(), "union_all": union_all.count(),
              "union_distinct": union_distinct.count(),
              "bcast_plan": bcast_df._jdf.queryExecution().executedPlan().toString()})'''),
        ("code", 'check("6b")'),

        ("md", "## 6c · De-duplicate and aggregate"),
        ("ex", '''# TODO 6c
orders = spark.table("lab6.orders")
clean = orders.<FILL-IN>(["order_id"])                       # remove the duplicate order 105
stats = (clean.groupBy("country")
    .agg(F.count("*").alias("n_orders"),
         <FILL-IN>("customer_id").alias("approx_customers"),   # fast approximate distinct count
         F.<FILL-IN>("amount").alias("avg_amount")))           # mean
stats.write.mode("overwrite").saveAsTable("lab6.country_stats")
show(stats)
show(clean.select("amount").<FILL-IN>())                      # count, mean, stddev, min, 25%, 50%, 75%, max''',
         '''orders = spark.table("lab6.orders")
clean = orders.dropDuplicates(["order_id"])
stats = (clean.groupBy("country")
    .agg(F.count("*").alias("n_orders"),
         F.approx_count_distinct("customer_id").alias("approx_customers"),
         F.avg("amount").alias("avg_amount")))
stats.write.mode("overwrite").saveAsTable("lab6.country_stats")
show(stats)
show(clean.select("amount").summary())'''),
        ("code", 'check("6c")'),

        ("md", "## 6d · Basic Spark tuning"),
        ("ex", '''# TODO 6d
from labutils.submit import submit
spark.conf.set("spark.sql.adaptive.enabled", "false")      # turn AQE off so you can see the raw plan
big = spark.range(100000).withColumn("k", F.col("id") % 100)
small = spark.range(100).withColumnRenamed("id", "k")
plan = lambda df: df._jdf.queryExecution().executedPlan().toString()

spark.conf.set("spark.sql.autoBroadcastJoinThreshold", <FILL-IN>)   # disable automatic broadcast
plan_off = plan(big.join(small, "k"))
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", <FILL-IN>)   # 10 MB again (in bytes, as text)
plan_on = plan(big.join(small, "k"))
spark.conf.set(<FILL-IN>, "8")                                      # number of partitions after a shuffle
parts = big.groupBy("k").count().rdd.getNumPartitions()

print("threshold -1  ->", "SortMergeJoin" if "SortMergeJoin" in plan_off else plan_off[:80])
print("threshold 10MB->", "BroadcastHashJoin" if "BroadcastHashJoin" in plan_on else plan_on[:80])
print("partitions after groupBy:", parts)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.shuffle.partitions", "2")
submit("6d", {"off": plan_off, "on": plan_on, "parts": parts})''',
         '''from labutils.submit import submit
spark.conf.set("spark.sql.adaptive.enabled", "false")
big = spark.range(100000).withColumn("k", F.col("id") % 100)
small = spark.range(100).withColumnRenamed("id", "k")
plan = lambda df: df._jdf.queryExecution().executedPlan().toString()

spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
plan_off = plan(big.join(small, "k"))
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", str(10 * 1024 * 1024))
plan_on = plan(big.join(small, "k"))
spark.conf.set("spark.sql.shuffle.partitions", "8")
parts = big.groupBy("k").count().rdd.getNumPartitions()

print("threshold -1  ->", "SortMergeJoin" if "SortMergeJoin" in plan_off else plan_off[:80])
print("threshold 10MB->", "BroadcastHashJoin" if "BroadcastHashJoin" in plan_on else plan_on[:80])
print("partitions after groupBy:", parts)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.shuffle.partitions", "2")
submit("6d", {"off": plan_off, "on": plan_on, "parts": parts})'''),
        ("code", 'check("6d")'),
    ]

    LAB7 = [
        ("md", "# Lab 7 — Troubleshoot, monitor, optimize + compute (Exam sections 6 · 10% and 1 · 6%)\n\n" + LEGEND),
        ("code", SETUP + '''\nreset_lab("lab7")
from labutils.submit import submit
# 90% of the sales belong to ONE customer -> a "hot key"
sales = (spark.range(200000)
    .withColumn("customer_id", F.when(F.col("id") % 10 < 9, F.lit(1)).otherwise(F.col("id") % 50))
    .withColumn("amount", (F.col("id") % 7 + 1).cast("double")))
sales.write.mode("overwrite").saveAsTable("lab7.sales")'''),

        ("md", "## 7a · Find data skew and fix it with salting"),
        ("code", '''sales = spark.table("lab7.sales")
by_key = sales.repartition(8, "customer_id").groupBy(F.spark_partition_id().alias("task")).count().orderBy("task")
print("Rows per task when we shuffle by customer_id (like a groupBy):")
show(by_key)'''),
        ("ex", '''# TODO 7a
SALTS = 8
salted = sales.withColumn("salt", (F.rand(seed=1) * SALTS).cast("int"))
# step 1: partial sums per (customer_id, salt) -> the hot key is split into 8 pieces
partial = salted.groupBy(<FILL-IN>).agg(F.sum("amount").alias("partial_amount"))
# step 2: combine the pieces -> one total per customer
totals = partial.groupBy(<FILL-IN>).agg(F.sum(<FILL-IN>).alias("total_amount"))
partial.write.mode("overwrite").saveAsTable("lab7.partial_totals")
totals.write.mode("overwrite").saveAsTable("lab7.customer_totals")
print("Rows per task when we shuffle by customer_id + salt:")
show(salted.repartition(8, "customer_id", "salt").groupBy(F.spark_partition_id().alias("task")).count().orderBy("task"))''',
         '''SALTS = 8
salted = sales.withColumn("salt", (F.rand(seed=1) * SALTS).cast("int"))
partial = salted.groupBy("customer_id", "salt").agg(F.sum("amount").alias("partial_amount"))
totals = partial.groupBy("customer_id").agg(F.sum("partial_amount").alias("total_amount"))
partial.write.mode("overwrite").saveAsTable("lab7.partial_totals")
totals.write.mode("overwrite").saveAsTable("lab7.customer_totals")
print("Rows per task when we shuffle by customer_id + salt:")
show(salted.repartition(8, "customer_id", "salt").groupBy(F.spark_partition_id().alias("task")).count().orderBy("task"))'''),
        ("code", 'check("7a")'),

        ("md", "## 7b · Liquid clustering"),
        ("ex", '''# TODO 7b
spark.sql("""<FILL-IN: create lab7.events (event_id BIGINT, event_date DATE, customer_id BIGINT) with liquid clustering on event_date>""")
spark.sql("INSERT INTO lab7.events SELECT id, date_add(DATE'2024-01-01', CAST(id % 30 AS INT)), id % 50 FROM range(5000)")
spark.sql("""<FILL-IN: change the clustering key to customer_id>""")
spark.sql("""<FILL-IN: run the command that (re)clusters the data>""")
print("clustering columns:", spark.sql("DESCRIBE DETAIL lab7.events").first().clusteringColumns)''',
         '''spark.sql("""CREATE TABLE lab7.events (event_id BIGINT, event_date DATE, customer_id BIGINT) CLUSTER BY (event_date)""")
spark.sql("INSERT INTO lab7.events SELECT id, date_add(DATE'2024-01-01', CAST(id % 30 AS INT)), id % 50 FROM range(5000)")
spark.sql("""ALTER TABLE lab7.events CLUSTER BY (customer_id)""")
spark.sql("""OPTIMIZE lab7.events""")
print("clustering columns:", spark.sql("DESCRIBE DETAIL lab7.events").first().clusteringColumns)'''),
        ("code", 'check("7b")'),

        ("md", "## 7c · Diagnose failing jobs"),
        ("code", '''ERRORS = {
  "E1": "java.lang.OutOfMemoryError: Java heap space ... at Dataset.collect / toPandas() on the DRIVER",
  "E2": "ModuleNotFoundError / ImportError: numpy.core.multiarray failed to import (after installing a new library version on the cluster)",
  "E3": "Cluster terminated. Reason: Cloud provider launch failure — instance quota exceeded / init script exited with non-zero code",
  "E4": "Task status: Timed Out after 45 minutes (data volume grew; the task now needs ~60 minutes)",
  "E5": "Spark UI: one task 10 min, others 30 s; Max shuffle read 5 GB vs median 400 MB; 'Spill (disk)' is large",
}
FIXES = {
  "A": "Raise the task's timeout threshold above 60 minutes (with headroom)",
  "B": "Don't collect big data to the driver: write to a table / aggregate first, or use a bigger driver",
  "C": "Fix or pin conflicting library versions (cluster/notebook-scoped libraries, requirements), then restart",
  "D": "Check the cluster event log: fix the init script or cloud quota / instance type / permissions",
  "E": "Data skew: salt the hot key (AQE skew handling helps JOINS, not groupBy) and look for spill",
}
for k, v in ERRORS.items(): print(k, "→", v)
print()
for k, v in FIXES.items(): print(k, "=", v)'''),
        ("ex", '''# TODO 7c: match every error (E1..E5) to the best fix (A..E)
submit("7c", {"E1": "<FILL-IN>", "E2": "<FILL-IN>", "E3": "<FILL-IN>", "E4": "<FILL-IN>", "E5": "<FILL-IN>"})''',
         '''submit("7c", {"E1": "B", "E2": "C", "E3": "D", "E4": "A", "E5": "E"})'''),
        ("code", 'check("7c")'),

        ("md", "## 7d · Pick the right compute (exam section 1)"),
        ("code", '''SCENARIOS = {
  "S1": "Many business analysts run ad-hoc SQL all day on curated Delta tables; fast start, many users, control cost",
  "S2": "A nightly scheduled ETL notebook job in production; cheapest reliable option, no idle cost",
  "S3": "A data engineer explores data and develops notebooks interactively with teammates",
  "S4": "A production job that must start in seconds with no cluster management at all",
}
COMPUTE = {
  "W": "Serverless SQL warehouse (autoscaling)",
  "J": "Job cluster (created for the run, terminates after it)",
  "P": "All-purpose (interactive) cluster",
  "S": "Serverless compute for jobs",
}
for k, v in SCENARIOS.items(): print(k, "→", v)
print()
for k, v in COMPUTE.items(): print(k, "=", v)'''),
        ("ex", '''# TODO 7d: match each scenario to the best compute
submit("7d", {"S1": "<FILL-IN>", "S2": "<FILL-IN>", "S3": "<FILL-IN>", "S4": "<FILL-IN>"})''',
         '''submit("7d", {"S1": "W", "S2": "J", "S3": "P", "S4": "S"})'''),
        ("code", 'check("7d")'),
    ]

    LAB8 = [
        ("md", "# Lab 8 — CI/CD: Git folders and Declarative Automation Bundles (Exam section 5 · 10%)\n\n" + LEGEND),
        ("code", SETUP + '''\nfrom labutils.submit import submit
BUNDLE = os.path.abspath("../lab8_project/databricks.yml")'''),

        ("md", "## 8a · The Git folder workflow"),
        ("code", '''STEPS = {
  "a": "Commit and push the changes to the feature branch",
  "b": "In the Git folder, create a new branch (e.g. feature/add-silver)",
  "c": "Create a Git folder in the workspace by cloning the remote repo",
  "d": "After the PR is merged, pull the latest main into the Git folder",
  "e": "Edit the notebooks/files in the Git folder",
  "f": "Create a pull request (into main) and get it reviewed and merged",
}
for k, v in STEPS.items(): print(k, "→", v)'''),
        ("ex", '''# TODO 8a: put the letters in the right order (first to last)
submit("8a", [<FILL-IN>])''',
         '''submit("8a", ["c", "b", "e", "a", "f", "d"])'''),
        ("code", 'check("8a")'),

        ("md", "## 8b · Write a bundle with variables, targets and overrides"),
        ("code", 'check("8b")'),

        ("md", "## 8c · Secrets, validate and deploy with the CLI"),
        ("ex", '''# TODO 8c
from labutils.bundle import validate
github_secrets = {"BUNDLE_VAR_db_password": "s3cr3t-from-github"}    # like a GitHub Actions secret
result = validate(BUNDLE, target=<FILL-IN>, env=<FILL-IN>)            # validate the PROD target
commands = {
  "validate": "<FILL-IN: CLI command to validate the prod target>",
  "deploy":   "<FILL-IN: CLI command to deploy to prod>",
  "run":      "<FILL-IN: CLI command to run the job health_etl_job in prod>",
}
submit("8c", {"result": result, "commands": commands})''',
         '''from labutils.bundle import validate
github_secrets = {"BUNDLE_VAR_db_password": "s3cr3t-from-github"}
result = validate(BUNDLE, target="prod", env=github_secrets)
commands = {
  "validate": "databricks bundle validate -t prod",
  "deploy":   "databricks bundle deploy -t prod",
  "run":      "databricks bundle run -t prod health_etl_job",
}
submit("8c", {"result": result, "commands": commands})'''),
        ("code", 'check("8c")'),
    ]

    LAB9 = [
        ("md", "# Lab 9 — Governance & security in Unity Catalog (Exam section 7 · 15%)\n\n" + LEGEND),
        ("code", SETUP + '''\nreset_lab("lab9")
from labutils.submit import submit'''),

        ("md", "## 9a · GRANT and REVOKE privileges"),
        ("ex", '''# TODO 9a: write the SQL (Databricks syntax). Group/principal names go in back-ticks.
sql = """
-- 1) group `analysts` must be able to READ main.sales.orders  (3 statements)
<FILL-IN>
-- 2) group `contractors` must NOT read main.sales.orders anymore
<FILL-IN>
-- 3) service principal `etl-sp` must be able to insert/update/delete rows in main.sales.orders
<FILL-IN>
"""
submit("9a", sql)''',
         '''sql = """
-- 1) group `analysts` must be able to READ main.sales.orders  (3 statements)
GRANT USE CATALOG ON CATALOG main TO `analysts`;
GRANT USE SCHEMA ON SCHEMA main.sales TO `analysts`;
GRANT SELECT ON TABLE main.sales.orders TO `analysts`;
-- 2) group `contractors` must NOT read main.sales.orders anymore
REVOKE SELECT ON TABLE main.sales.orders FROM `contractors`;
-- 3) service principal `etl-sp` must be able to insert/update/delete rows in main.sales.orders
GRANT MODIFY ON TABLE main.sales.orders TO `etl-sp`;
"""
submit("9a", sql)'''),
        ("code", 'check("9a")'),

        ("md", "## 9b · Managed vs external tables and converting between them"),
        ("ex", '''# TODO 9b: write the SQL (Databricks syntax)
sql = """
-- 1) create an EXTERNAL table main.raw.events_ext stored at 's3://acme-raw/events'
CREATE TABLE main.raw.events_ext (id INT, ts TIMESTAMP) <FILL-IN>;
-- 2) convert it to a MANAGED table
ALTER TABLE main.raw.events_ext <FILL-IN>;
-- 3) oops — roll the conversion back (allowed within 14 days)
ALTER TABLE main.raw.events_ext <FILL-IN>;
"""
answers = {
  "drop_managed_deletes_data": <FILL-IN True/False>,
  "drop_external_deletes_data": <FILL-IN True/False>,
}
submit("9b", {"sql": sql, **answers})''',
         '''sql = """
-- 1) create an EXTERNAL table main.raw.events_ext stored at 's3://acme-raw/events'
CREATE TABLE main.raw.events_ext (id INT, ts TIMESTAMP) LOCATION 's3://acme-raw/events';
-- 2) convert it to a MANAGED table
ALTER TABLE main.raw.events_ext SET MANAGED;
-- 3) oops — roll the conversion back (allowed within 14 days)
ALTER TABLE main.raw.events_ext UNSET MANAGED;
"""
answers = {
  "drop_managed_deletes_data": True,
  "drop_external_deletes_data": False,
}
submit("9b", {"sql": sql, **answers})'''),
        ("code", 'check("9b")'),

        ("md", "## 9c · Column masks and row filters"),
        ("code", '''from labutils.governance import login
login("you@corp.com", [])     # registers is_account_group_member() for this lab
spark.sql("""CREATE TABLE lab9.customers AS SELECT * FROM VALUES
  (1, 'Ana',  '4111111111111111', 'EU'),
  (2, 'Ben',  '5500000000000004', 'US'),
  (3, 'Chen', '340000000000009',  'EU')
  AS t(id, name, credit_card_number, region)""")'''),
        ("ex", '''# TODO 9c: write the two SQL expressions
MASK = """CASE WHEN <FILL-IN> THEN credit_card_number
               ELSE concat('****', right(credit_card_number, 4)) END"""      # finance_team sees full number
ROW_FILTER = """<FILL-IN>"""                                                   # admins see all rows, others only region 'EU'

spark.sql(f"""CREATE OR REPLACE TEMP VIEW customers_secure AS
SELECT id, name, {MASK} AS credit_card_number, region FROM lab9.customers WHERE {ROW_FILTER}""")
submit("9c", {"mask": MASK, "row_filter": ROW_FILTER})
for user, groups in [("fiona@corp.com", ["finance_team"]), ("adam@corp.com", ["admins"]), ("eve@corp.com", [])]:
    login(user, groups)
    show(spark.table("customers_secure"))''',
         '''MASK = """CASE WHEN is_account_group_member('finance_team') THEN credit_card_number
               ELSE concat('****', right(credit_card_number, 4)) END"""
ROW_FILTER = """is_account_group_member('admins') OR region = 'EU'"""

spark.sql(f"""CREATE OR REPLACE TEMP VIEW customers_secure AS
SELECT id, name, {MASK} AS credit_card_number, region FROM lab9.customers WHERE {ROW_FILTER}""")
submit("9c", {"mask": MASK, "row_filter": ROW_FILTER})
for user, groups in [("fiona@corp.com", ["finance_team"]), ("adam@corp.com", ["admins"]), ("eve@corp.com", [])]:
    login(user, groups)
    show(spark.table("customers_secure"))'''),
        ("code", 'check("9c")'),

        ("md", "## 9d · ABAC policies (attribute-based access control)"),
        ("code", '''SITUATIONS = {
  "Q1": "500 tables in a catalog contain columns tagged 'pii'. Every new table with a 'pii' column must be masked automatically.",
  "Q2": "One single table needs one column masked for one group.",
  "Q3": "Rows of every table tagged 'region' must be filtered for non-admins, across many schemas.",
  "Q4": "Give analysts permission to read one table.",
}
TOOLS = {
  "ABAC": "An ABAC policy (on catalog/schema) that uses governed tags to apply a mask or row filter to all matching tables",
  "MASK": "A column mask function set on that one table's column",
  "GRANT": "A GRANT SELECT statement",
}
for k, v in SITUATIONS.items(): print(k, "→", v)
print()
for k, v in TOOLS.items(): print(k, "=", v)'''),
        ("ex", '''# TODO 9d
submit("9d", {"Q1": "<FILL-IN>", "Q2": "<FILL-IN>", "Q3": "<FILL-IN>", "Q4": "<FILL-IN>"})''',
         '''submit("9d", {"Q1": "ABAC", "Q2": "MASK", "Q3": "ABAC", "Q4": "GRANT"})'''),
        ("code", 'check("9d")'),
    ]
    return {"lab6_transform_tuning": LAB6, "lab7_troubleshooting": LAB7, "lab8_cicd_bundles": LAB8,
            "lab9_governance": LAB9}
