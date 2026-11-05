"""Analogies, course slides and diagrams for each portal step.

analogy = everyday comparison, no technical words
slides  = [(course, slide_number, caption)] → images in portal/static/slides/<course>/<n>.jpg
diagram = Mermaid flowchart code (drawn in the browser)
"""

V = {
# ------------------------------------------------------------------ LAB 1
"1a": dict(
  analogy="A Delta table is like a **notebook with a diary**. The pages (Parquet files) hold your data. "
          "The diary (`_delta_log`) writes down every change: *“Monday: added 3 rows. Tuesday: deleted 1 row.”* "
          "Because of the diary you can always say *“show me the notebook as it was on Monday”* — that is **time travel**.",
  slides=[("c1", 23, "A Delta table = Parquet data files + the _delta_log transaction log"),
          ("c1", 24, "What the log gives you: ACID, DML, time travel, schema enforcement"),
          ("c1", 25, "Medallion architecture: bronze → silver → gold")],
  diagram="""flowchart LR
  A["INSERT / UPDATE / DELETE"] --> L["_delta_log/ (the diary)<br/>000.json · 001.json · 002.json"]
  A --> P["Parquet files (the pages with data)"]
  L --> V0["Version 0"] & V1["Version 1"] & V2["Version 2"]
  V1 -. "VERSION AS OF 1" .-> T["Time travel"]"""),
"1b": dict(
  analogy="CTAS is like **photocopying a whole folder every morning**. Easy and simple — but tomorrow you photocopy "
          "*everything again*, even the pages you already copied yesterday. Good for a one-time copy, wasteful every day.",
  slides=[("c1", 30, "The three ways to load files from cloud storage into Delta"),
          ("c1", 32, "Method 1 — CTAS with read_files()"),
          ("c1", 18, "Batch: all data is re-read every run")],
  diagram="""flowchart LR
  F1["file 1"] & F2["file 2"] & F3["file 3"] --> R["read_files() / parquet.`path`"]
  R --> C["CREATE TABLE … AS SELECT"] --> T[("Delta table")]
  N["Next run"] -. "reads file 1, 2, 3 AGAIN" .-> R"""),
"1c": dict(
  analogy="COPY INTO is like a **librarian with a checklist**. Every book that arrives is ticked off. Tomorrow the "
          "librarian only shelves the books that are **not ticked** yet. Ask twice by mistake? Nothing happens — "
          "everything is already ticked. That is **idempotent**.",
  slides=[("c1", 34, "Method 2 — COPY INTO: create an empty table first"),
          ("c1", 35, "COPY INTO is idempotent; FORMAT_OPTIONS vs COPY_OPTIONS"),
          ("c1", 19, "Incremental batch: only new data")],
  diagram="""flowchart LR
  V["Volume: file1, file2, file3(new)"] --> C{"COPY INTO<br/>checklist"}
  C -- "file1 ✓ already loaded" --> S["skip"]
  C -- "file2 ✓ already loaded" --> S
  C -- "file3 ✗ new" --> T[("Delta table")]
  C -. "new column?  needs mergeSchema" .-> T"""),
"1d": dict(
  analogy="Auto Loader is like a **security guard at a door with a visitor book** (the checkpoint). Every new file "
          "that walks in is written in the book and let through **once**. The guard can stand there all day "
          "(streaming) or come every hour, let in whoever is waiting, and leave (`availableNow`).",
  slides=[("c1", 37, "Auto Loader: incremental, scales to billions of files, built on Structured Streaming"),
          ("c1", 38, "Auto Loader in Python (cloudFiles) and in SQL (STREAM read_files)"),
          ("c1", 39, "CTAS vs COPY INTO vs Auto Loader — the exam comparison table")],
  diagram="""flowchart LR
  V["Cloud storage<br/>new files keep arriving"] --> AL["Auto Loader<br/>format('cloudFiles')"]
  AL <--> CP[("Checkpoint<br/>= list of processed files")]
  AL --> T[("Streaming / Delta table")]
  AL -. "trigger(availableNow=True)<br/>= run once, stop" .-> T"""),
"1e": dict(
  analogy="Like writing **“from: Grandma, arrived: 3 May”** on every letter you put in a box. Months later, when "
          "one letter looks strange, you know exactly where it came from and when.",
  slides=[("c1", 42, "Add the file name and modification time to the bronze table"),
          ("c1", 43, "_metadata.file_name and _metadata.file_modification_time")],
  diagram="""flowchart LR
  F["sales_01.csv"] --> R["read"]
  R --> B["Bronze row + source_file + file_modification_time + ingestion_time"]"""),
"1f": dict(
  analogy="A **lost-and-found box**. When a value does not fit its place (text `$945` in a number column), "
          "Databricks does not throw it away — it puts it in the lost-and-found column `_rescued_data`, "
          "so you can fix it later.",
  slides=[("c1", 46, "read_files, spark.read and Auto Loader can rescue malformed values"),
          ("c1", 47, "The bad value is stored in _rescued_data as JSON; the column becomes NULL")],
  diagram="""flowchart LR
  R["row: M_STAN_F, $945.00"] --> S{"fits the schema?<br/>price DOUBLE"}
  S -- yes --> OK["price = 945.0"]
  S -- no --> N["price = NULL"] & RD["_rescued_data = {price: $945.00}"]"""),
"1g-1": dict(
  analogy="Base64 is like a **message in a sealed envelope** — safe while travelling, but you must open it "
          "(`unbase64`) and read it as text (`CAST … AS STRING`) before you can understand it.",
  slides=[("c1", 51, "JSON objects are enclosed in brackets"),
          ("c1", 53, "JSON values: string, number, boolean, array, object")],
  diagram="""flowchart LR
  K["value = eyJkZXZpY2Ui… (base64)"] --> U["unbase64()"] --> B["bytes"] --> C["CAST AS STRING"] --> J["{ device: iOS, items: [...] }"]"""),
"1g-2": dict(
  analogy="A JSON string is like a **packed suitcase**: everything is inside, but you must dig. `from_json` is "
          "**unpacking into labelled drawers** (a STRUCT). `explode` is taking each item out of a bag and laying "
          "it on its own shelf; `explode_outer` also keeps an empty shelf for an empty bag.",
  slides=[("c1", 56, "JSON as STRING vs as STRUCT"),
          ("c1", 63, "schema_of_json returns the structure"),
          ("c1", 65, "STRING vs STRUCT vs VARIANT")],
  diagram="""flowchart LR
  S["decoded_value (STRING)"] -- "from_json(…, schema)" --> ST["e : STRUCT"]
  ST -- "explode(e.items)" --> R1["1 row per item<br/>(empty lists disappear)"]
  ST -- "explode_outer(e.items)" --> R2["1 row per item<br/>+ events with no items kept"]"""),
"1h-1": dict(
  analogy="MERGE is like **updating your phone's contacts from a new list**: same person → update the number; "
          "marked “delete” → remove; new person → add. One command, three actions.",
  slides=[("c1", 86, "MERGE INTO: matched → UPDATE/DELETE, not matched → INSERT"),
          ("c1", 87, "Example: update, delete and insert in one MERGE")],
  diagram="""flowchart LR
  S["source (changes)"] --> M{"MERGE ON t.id = s.id"}
  T[("target table")] --> M
  M -- "MATCHED + update" --> U["UPDATE"]
  M -- "MATCHED + delete" --> D["DELETE"]
  M -- "NOT MATCHED" --> I["INSERT"]"""),
"1h-2": dict(
  analogy="Schema enforcement is a **bouncer**: a guest (column) not on the list is refused. Schema evolution is "
          "telling the bouncer *“it's fine, add new guests to the list”*.",
  slides=[("c1", 86, "MERGE supports schema enforcement or schema evolution")],
  diagram="""flowchart LR
  S["source has NEW column: country"] --> Q{"schema evolution on?"}
  Q -- "no" --> E["ERROR (schema enforcement)"]
  Q -- "yes (autoMerge / WITH SCHEMA EVOLUTION)" --> OK["table gets column country"]"""),
# ------------------------------------------------------------------ LAB 2
"2a": dict(
  analogy="A job is a **recipe**, tasks are the **steps**. You can boil the pasta and make the sauce **at the same "
          "time**, but you can only mix them when **both** are ready. The recipe never says “go back to step 1” — "
          "no loops, that's the *acyclic* in DAG.",
  slides=[("c2", 21, "A job is made of tasks"),
          ("c2", 33, "Task orchestration with dependencies"),
          ("c2", 34, "Patterns: sequence, funnel, fan-out")],
  diagram="""flowchart LR
  A["ingest_orders"] --> J["join_customers_orders"]
  B["ingest_customers"] --> J
  classDef p fill:#eef,stroke:#88a
  class A,B p"""),
"2b": dict(
  analogy="Parameters are like **settings on a washing machine** — same machine, choose *wool* or *cotton*. "
          "Job parameters are the **house rules** that every room follows (they win). Task values are **notes "
          "you leave on the fridge** for the next person: *“I counted 20 orders.”*",
  slides=[("c2", 44, "Task parameters vs job parameters (job wins)"),
          ("c2", 48, "Task values: set in one task, get in another"),
          ("c2", 49, "Dynamic value references {{ }}")],
  diagram="""flowchart LR
  JP["Job parameter catalog=lab2_prod"] --> T1["count_orders"] & T2["report"]
  T1 -- "taskValues.set(row_count=20)" --> TV[("task values")]
  TV -- "{{tasks.count_orders.values.row_count}}" --> T2"""),
"2c": dict(
  analogy="If/else is a **fork in the road**: you take one path, the other is skipped (*excluded*). For each is a "
          "**post office sorting letters by city** — the same work for CA, NY and VA, several workers at once. "
          "Run-if is the **rule for when you may start**: “only if everyone before me succeeded”, or “if nobody failed”.",
  slides=[("c2", 67, "Run-if dependencies: at least one succeeded"),
          ("c2", 71, "If/else condition task with True and False branches"),
          ("c2", 73, "For each: one nested task per input item ({{input}})")],
  diagram="""flowchart LR
  C["check_duplicates"] --> IF{"has_duplicates == true ?"}
  IF -- True --> D["drop_duplicates"]
  IF -- False --> N["no_duplicates"]
  D & N -- "run_if NONE_FAILED" --> FE["For each [CA, NY, VA]"]
  FE --> CA["report CA"] & NY["report NY"] & VA["report VA"]"""),
"2d": dict(
  analogy="A retry is **knocking on the door again** when nobody answered the first time. A repair run is a "
          "**mechanic who only fixes the broken part** of the car, instead of building a new car.",
  slides=[("c2", 52, "Retry policy: how many times and how long to wait"),
          ("c2", 78, "Repair run: re-run only the failed tasks"),
          ("c2", 80, "After the repair, the whole run is green")],
  diagram="""flowchart LR
  I["ingest ✅ (2nd attempt)"] --> T["transform ❌"] --> P["publish ⛔ upstream failed"]
  R["Repair run"] -. "re-runs only" .-> T
  R -. "and then" .-> P"""),
# ------------------------------------------------------------------ LAB 3
"3a": dict(
  analogy="A **factory line**: raw material (bronze) → cleaned parts (silver) → finished product on the shelf (gold). "
          "A **streaming table** is a conveyor belt — each new item passes **once**. A **materialized view** is the "
          "**shop's stock count**: recounted so it's always right.",
  slides=[("c3", 19, "Bronze & silver = streaming tables, gold = materialized view"),
          ("c3", 21, "Run 2: only the new file flows through"),
          ("c3", 30, "Streaming table vs materialized view vs view"),
          ("c3", 36, "Creating a materialized view")],
  diagram="""flowchart LR
  F["JSON files"] -- "STREAM read_files" --> B[("orders_bronze<br/>streaming table")]
  B -- "FROM STREAM" --> S[("orders_silver<br/>streaming table")]
  S -- "GROUP BY date" --> G[("gold_orders_by_date<br/>materialized view")]"""),
"3b": dict(
  analogy="Expectations are **quality control at the factory**: *warn* = put a sticker on the bad item but keep it; "
          "*drop* = throw the bad item away; *fail* = **stop the whole line**.",
  slides=[("c3", 54, "CONSTRAINT … EXPECT … ON VIOLATION"),
          ("c3", 56, "What happens with each action")],
  diagram="""flowchart LR
  R["row"] --> E{"EXPECT (customer_id IS NOT NULL)"}
  E -- pass --> K["keep"]
  E -- "fail + WARN" --> K2["keep, count in event log"]
  E -- "fail + DROP ROW" --> X["drop row"]
  E -- "fail + FAIL UPDATE" --> STOP["stop the update ⛔"]"""),
"3c": dict(
  analogy="Joining is like **matching socks**: pair each order with its status using the same order number. "
          "Because new socks keep arriving in both baskets, a materialized view **re-pairs everything** each time.",
  slides=[("c3", 64, "Stream–static join: new rows join the full lookup table"),
          ("c3", 67, "Two streaming tables joined in a materialized view")],
  diagram="""flowchart LR
  O[("orders_silver")] --> MV[("full_order_info_gold<br/>materialized view")]
  S[("status_silver")] --> MV"""),
"3d": dict(
  analogy="CDC is like **updating an address book from change slips**. *SCD Type 1* = cross out the old address and "
          "write the new one. *SCD Type 2* = keep the old line and add a new line with dates. If two slips arrive "
          "**in the wrong order**, you check the **date on the slip** (SEQUENCE BY) — the newest date wins.",
  slides=[("c3", 81, "SCD Type 1: overwrite with the latest values"),
          ("c3", 83, "SCD Type 2: keep history with start/end"),
          ("c3", 84, "AUTO CDC INTO: KEYS, SEQUENCE BY, APPLY AS DELETE")],
  diagram="""flowchart LR
  C1["Peter: 123 Main St (May 20)"] --> Q{"SEQUENCE BY process_date"}
  C2["Peter: 99 Sunny St (May 15)<br/>arrives later!"] --> Q
  Q --> R["Peter = 123 Main St ✓ (newest date wins)"]"""),
# ------------------------------------------------------------------ LAB 4
"4a": dict(
  analogy="One giant script is a **ball of tangled cables**. Modular code is **cables with labels in a box** — "
          "you can take one out, test it, and reuse it somewhere else.",
  slides=[("c4", 22, "Before: everything in one block"),
          ("c4", 23, "After: small functions"),
          ("c4", 24, "Benefits: maintenance, reuse, unit testing")],
  diagram="""flowchart LR
  L["load_data()"] --> A["convert_miles_to_km()"] --> U["uppercase_column_names()"] --> W["write"]"""),
"4b": dict(
  analogy="A unit test is a **taste test of one ingredient** before cooking the whole meal: small, fast, and "
          "you know exactly which ingredient is wrong.",
  slides=[("c4", 62, "Unit tests: fast, test one function"),
          ("c4", 65, "Compare actual vs expected"),
          ("c4", 66, "pytest")],
  diagram="""flowchart LR
  I["small input DataFrame"] --> F["your function"] --> A["actual"]
  E["expected DataFrame"] --> C{"assertDataFrameEqual"}
  A --> C
  C -- same --> P["✅ pass"]
  C -- different --> X["❌ fail"]"""),
"4c": dict(
  analogy="A smoke alarm is only useful if it **beeps when there is smoke**. We light 6 small “fires” (broken code); "
          "good tests beep for every one.",
  slides=[("c4", 38, "Testing pyramid: unit → integration → system")],
  diagram="""flowchart LR
  T["your tests"] --> M1["bug 1"] & M2["bug 2"] & M3["bug 3"]
  M1 & M2 & M3 --> Q{"did the tests fail?"}
  Q -- yes --> G["✅ bug caught"]
  Q -- no --> B["❌ bug survived"]"""),
# ------------------------------------------------------------------ LAB 5
"5a": dict(
  analogy="OPTIMIZE is **tidying 100 small piles of paper into 3 neat folders**. RESTORE is the **undo button**. "
          "VACUUM is **emptying the recycle bin** — after that, the old versions can't be brought back.",
  slides=[],
  diagram="""flowchart LR
  S["12 tiny files"] -- OPTIMIZE --> O["1 big file"]
  O -- "RESTORE TO VERSION AS OF 3" --> R["table back at version 3"]
  R -- VACUUM --> V["old files deleted → time travel to them fails"]"""),
"5b": dict(
  analogy="Like keeping **only the newest photo of each friend**: group the photos per friend, sort newest first, "
          "keep number 1.",
  slides=[],
  diagram="""flowchart LR
  A["u1 Jan · u1 Mar · u1 Feb"] -- "PARTITION BY user ORDER BY date DESC" --> B["u1 Mar = 1 · Feb = 2 · Jan = 3"]
  B -- "WHERE rn = 1" --> C["u1 Mar"]"""),
"5c": dict(
  analogy="Higher-order functions are like **working inside a shopping bag without emptying it**: count the items "
          "(`size`), keep only the expensive ones (`filter`), add up the bill (`aggregate`).",
  slides=[],
  diagram="""flowchart LR
  I["items = [59, 1795, 1045]"] -- "size" --> S["3"]
  I -- "filter(x > 1000)" --> F["[1795, 1045]"]
  I -- "aggregate(sum)" --> A["2899"]"""),
"5d": dict(
  analogy="A **scoreboard** at a game: *complete* = repaint the whole board every time; *update* = change only the "
          "scores that moved; *append* = only add new lines (doesn't work for totals that change).",
  slides=[],
  diagram="""flowchart LR
  N["new orders"] --> AG["count per customer (state in checkpoint)"] -- "outputMode complete" --> T[("whole result table rewritten")]"""),
# ------------------------------------------------------------------ LAB 6
"6a": dict(
  analogy="Bronze → silver is **washing vegetables before cooking**: throw away the rotten ones (rows with no id), "
          "fill the gaps, cut them to the same size (types), label the boxes (rename).",
  slides=[("c1", 25, "Medallion: bronze (raw) → silver (cleaned) → gold (business)")],
  diagram="""flowchart LR
  B[("bronze: messy")] --> D["na.drop (no id)"] --> F["na.fill (email)"] --> C["cast types"] --> SP["split / trim / rename / drop"] --> S[("silver: clean")]"""),
"6b": dict(
  analogy="A join is **matching two guest lists** by name. *Inner* = only people on both lists. *Left* = everyone on "
          "my list, even if not on yours. *Cross* = every shirt with every pair of trousers. *Broadcast* = making "
          "**a photocopy of the small list for every helper**, so nobody has to walk around.",
  slides=[],
  diagram="""flowchart LR
  O["orders (8)"] -- "inner" --> I["6 rows: only matches"]
  O -- "left" --> L["8 rows: all orders"]
  SM["small table"] -- "broadcast: copy to every worker" --> W1["worker 1"] & W2["worker 2"] & W3["worker 3"]"""),
"6c": dict(
  analogy="De-duplication = **removing double photos** from your album. `approx_count_distinct` = **guessing the "
          "crowd size at a concert** from the air — very close, much faster than counting every person.",
  slides=[],
  diagram="""flowchart LR
  O["orders with a duplicate 105"] -- "dropDuplicates(order_id)" --> C["clean"] -- "groupBy(country).agg(...)" --> S["count · approx distinct · avg"]"""),
"6d": dict(
  analogy="Shuffle partitions = **how many boxes you sort the mail into**: too few → giant heavy boxes; too many → "
          "thousands of almost-empty boxes. The broadcast threshold = **“if a list is shorter than one page, "
          "just give everyone a copy”**.",
  slides=[],
  diagram="""flowchart LR
  J["join big + small"] --> Q{"small table < autoBroadcastJoinThreshold?"}
  Q -- "yes (10 MB)" --> B["BroadcastHashJoin — fast"]
  Q -- "no / -1" --> S["SortMergeJoin — shuffle both sides"]"""),
# ------------------------------------------------------------------ LAB 7
"7a": dict(
  analogy="Skew is a **supermarket where 9 of 10 customers queue at one cashier**. Adding more cashiers doesn't help "
          "— they all still stand in that one queue. **Salting** gives the customers random ticket numbers so they "
          "spread over all cashiers; at the end you add up the receipts.",
  slides=[("c2", 83, "Spark UI / query profile: find the slow part")],
  diagram="""flowchart LR
  K["customer 1 = 90% of rows"] -- "groupBy customer_id" --> T1["1 task: 10 min ⏳"]
  K -- "+ salt 0..7" --> P["8 tasks: partial sums ⚡"] -- "groupBy customer_id: sum" --> R["total"]"""),
"7b": dict(
  analogy="Liquid clustering is a **library that keeps books on the same topic on the same shelf** — and you can "
          "**change how the shelves are organised any time** without rebuilding the library.",
  slides=[],
  diagram="""flowchart LR
  T[("events")] -- "CLUSTER BY (event_date)" --> A["files grouped by date"]
  A -- "ALTER TABLE … CLUSTER BY (customer_id) + OPTIMIZE" --> B["files grouped by customer → filters skip files"]"""),
"7c": dict(
  analogy="Troubleshooting is being a **doctor**: first find **where it hurts** (driver? one worker? the cluster "
          "start? the clock?) — then the treatment is usually obvious.",
  slides=[("c2", 82, "system.lakeflow tables: job run history"),
          ("c2", 79, "Failed run → repair")],
  diagram="""flowchart TD
  E["error"] --> D{"where?"}
  D -- "driver after collect()" --> A["don't collect big data"]
  D -- "after installing a library" --> B["pin versions"]
  D -- "cluster won't start" --> C["event log: init script / quota"]
  D -- "Timed Out" --> T["raise timeout"]
  D -- "1 slow task + spill" --> S["skew → salting"]"""),
"7d": dict(
  analogy="Compute is like **transport**: a **taxi** you call and pay per ride (serverless), a **bus that runs "
          "one route and parks after** (job cluster), **your own car** you keep running while you explore "
          "(all-purpose), and a **ticket desk built for many customers asking questions** (SQL warehouse).",
  slides=[("c2", 28, "Interactive clusters vs job clusters vs serverless vs SQL warehouse"),
          ("c2", 88, "Serverless: simple, fast start, Photon")],
  diagram="""flowchart LR
  Q{"workload?"} -- "ad-hoc SQL, many users" --> W["SQL warehouse"]
  Q -- "scheduled ETL" --> J["job cluster / serverless jobs"]
  Q -- "interactive development" --> P["all-purpose cluster"]"""),
# ------------------------------------------------------------------ LAB 8
"8a": dict(
  analogy="Git is like **Google Docs “suggest changes” for code**: you work on your own copy (a branch), propose "
          "your changes (pull request), a colleague reviews them, they get accepted into the main document, "
          "and everyone refreshes (pull).",
  slides=[("c4", 77, "Branching protects the main code"),
          ("c4", 81, "Databricks Git folders"),
          ("c4", 82, "Git folders + CI/CD")],
  diagram="""flowchart LR
  C["clone (Git folder)"] --> B["new branch"] --> E["edit"] --> P["commit + push"] --> PR["pull request + review"] --> M["merge to main"] --> PL["pull main"]"""),
"8b": dict(
  analogy="A bundle is **one recipe card with notes for each kitchen**: *“in the test kitchen use the small pan, "
          "in the restaurant use the big pan.”* The recipe (code) is the same everywhere; only the notes "
          "(variables, overrides) change.",
  slides=[("c4", 90, "Declarative Automation Bundles"),
          ("c4", 91, "What are DABs? YAML that describes your project"),
          ("c4", 92, "Development and CI/CD with bundles: dev → staging → prod")],
  diagram="""flowchart LR
  Y["databricks.yml<br/>(one codebase)"] -- "-t dev" --> D["health_etl_dev · dev_catalog"]
  Y -- "-t test" --> T["health_etl_test · test_catalog"]
  Y -- "-t prod (override: schedule)" --> P["health_etl_prod · prod_catalog"]"""),
"8c": dict(
  analogy="A secret is like a **house key**: you don't print it on the front door (the YAML). You keep it in a safe "
          "(GitHub secrets) and hand it over only at the moment you open the door (deploy) — via `BUNDLE_VAR_`.",
  slides=[("c4", 89, "REST API vs CLI vs SDK"),
          ("c4", 92, "CI/CD flow with bundles")],
  diagram="""flowchart LR
  GS["GitHub secret"] -- "env BUNDLE_VAR_db_password" --> CLI["databricks bundle validate / deploy -t prod"]
  Y["databricks.yml (no password inside)"] --> CLI
  CLI --> WS["prod workspace"]"""),
# ------------------------------------------------------------------ LAB 9
"9a": dict(
  analogy="Unity Catalog permissions are like an **office building**: you need a key to the **building** (USE "
          "CATALOG), to the **floor** (USE SCHEMA) and to the **room** (SELECT on the table). Missing one key = "
          "you can't get in.",
  slides=[],
  diagram="""flowchart LR
  U["group analysts"] -- "USE CATALOG" --> C["catalog main"]
  C -- "USE SCHEMA" --> S["schema main.sales"]
  S -- "SELECT" --> T["table orders"]"""),
"9b": dict(
  analogy="A **managed** table is a **hotel room**: the hotel owns the furniture — when you check out (DROP), it's "
          "cleared. An **external** table is **your own apartment** that you registered at the front desk — "
          "un-registering (DROP) doesn't empty your apartment.",
  slides=[],
  diagram="""flowchart LR
  E["external table (your LOCATION)"] -- "ALTER TABLE … SET MANAGED" --> M["managed table"]
  M -- "UNSET MANAGED (within 14 days)" --> E"""),
"9c": dict(
  analogy="Like a **bank statement**: the bank sees your full card number, but on the paper you see `****1234` "
          "(column mask). And a branch manager in Europe only sees **European customers** (row filter).",
  slides=[],
  diagram="""flowchart LR
  Q["SELECT * FROM customers"] --> W{"who is asking?"}
  W -- "finance_team" --> F["full card numbers"]
  W -- "others" --> M["****1234"]
  W -- "not admins" --> R["only region = EU rows"]"""),
"9d": dict(
  analogy="ABAC is like **colour stickers on folders**: put a red “PII” sticker on any folder, and **one office "
          "rule** says *“red stickers are blurred for everyone except HR”*. You don't write a rule per folder.",
  slides=[],
  diagram="""flowchart LR
  P["ONE ABAC policy on catalog:<br/>mask columns tagged pii"] --> T1["table A (pii col)"] & T2["table B (pii col)"] & T3["new table C (pii col)"]"""),
}
