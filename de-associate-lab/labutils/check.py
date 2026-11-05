"""Exercise checker.

In a notebook:      from labutils.check import check; check("1b")
From the terminal:  .venv/bin/python -m labutils.check 1b      (or: env, all)

Tables are read by their folder path, so the checker also works from a second process while
your notebook is still running.
"""
import json
import subprocess
import sys
from pathlib import Path

from labutils import LAB_ROOT, RAW, WAREHOUSE

STATE = LAB_ROOT / ".lab_state"
CHECKS = {}


class Fail(Exception):
    pass


def exercise(eid, title):
    def wrap(fn):
        CHECKS[eid] = (title, fn)
        return fn
    return wrap


def _spark():
    from labutils import get_spark
    return get_spark()


def _table(schema, name):
    p = WAREHOUSE / f"{schema}.db" / name
    if not (p / "_delta_log").exists():
        raise Fail(f"Delta table {schema}.{name} not found (expected files in {p}). Did you run the cell?")
    return _spark().read.format("delta").load(str(p))


def _history(schema, name):
    from delta.tables import DeltaTable
    return DeltaTable.forPath(_spark(), str(WAREHOUSE / f"{schema}.db" / name)).history()


def _need(cond, msg):
    if not cond:
        raise Fail(msg)


def _cols(df, *cols):
    missing = [c for c in cols if c not in df.columns]
    _need(not missing, f"missing column(s): {missing}. Columns found: {df.columns}")


def _run_state(eid):
    f = STATE / "runs" / f"{eid}.json"
    _need(f.exists(), f"No saved job run for {eid}. End your exercise with run.save('{eid}').")
    return json.loads(f.read_text())


# ---------------------------------------------------------------- environment
@exercise("env", "Environment: Java, PySpark, Delta Lake")
def _check_env():
    out = subprocess.run(["/usr/libexec/java_home", "-v", "17"], capture_output=True, text=True)
    _need(out.returncode == 0 or Path("/opt/homebrew/opt/openjdk@17").exists(),
          "Java 17 not found. Install with: brew install openjdk@17")
    spark = _spark()
    v = spark.range(3).selectExpr("sum(id) AS s").collect()[0].s
    _need(v == 3, "Spark did not compute correctly")
    import delta  # noqa: F401
    return f"Spark {spark.version} with Delta Lake is working."


# ---------------------------------------------------------------- lab 1 ingestion
@exercise("1a", "Delta basics: table + history")
def _1a():
    df = _table("lab1", "demo_delta")
    _need(df.count() == 3, f"demo_delta should have 3 rows, found {df.count()}")
    v = _history("lab1", "demo_delta").count()
    _need(v >= 2, f"expected at least 2 versions (CREATE + INSERT), found {v}")


@exercise("1b", "CTAS from Parquet files")
def _1b():
    df = _table("lab1", "users_bronze_ctas")
    _cols(df, "user_id", "user_first_touch_timestamp", "email")
    _need(df.count() == 300, f"expected 300 rows, found {df.count()}")


@exercise("1c", "COPY INTO (simulated): idempotent + mergeSchema")
def _1c():
    df = _table("lab1", "users_bronze_ci")
    _cols(df, "user_id", "country")
    n, d = df.count(), df.select("user_id").distinct().count()
    _need(n == d, f"{n - d} duplicate rows — COPY INTO should skip files already loaded")
    _need(n == 150, f"expected 150 rows (3 batches x 50), found {n}")


@exercise("1d", "Auto Loader idea: incremental Structured Streaming with a checkpoint")
def _1d():
    df = _table("lab1", "users_bronze_stream")
    n, d = df.count(), df.select("user_id").distinct().count()
    _need(n == d, "duplicates found — the checkpoint should stop files being read twice")
    _need(n >= 100, f"expected at least 100 rows (2 landed batches), found {n}")
    _need(_history("lab1", "users_bronze_stream").filter("operation = 'STREAMING UPDATE'").count() >= 2,
          "expected at least 2 streaming runs (land a file, run, land another file, run again)")


@exercise("1e", "Metadata columns on ingest")
def _1e():
    df = _table("lab1", "sales_bronze")
    _cols(df, "order_id", "source_file", "file_modification_time", "ingestion_time")
    _need(df.count() == 100, f"expected 100 rows, found {df.count()} (did you set sep='|' and header?)")
    _need(df.select("source_file").distinct().count() == 4, "expected 4 distinct source files")


@exercise("1f", "Rescue malformed data")
def _1f():
    df = _table("lab1", "items_bronze")
    _cols(df, "item_id", "price", "price_fixed")
    _need(df.count() == 5, f"expected 5 rows, found {df.count()}")
    _need(df.filter("price_fixed IS NULL").count() == 0, "price_fixed still has NULLs")
    total = round(df.selectExpr("sum(price_fixed) s").collect()[0].s, 2)
    _need(total == 4893.0, f"sum(price_fixed) should be 4893.0, found {total}")


@exercise("1g", "Decode + flatten JSON")
def _1g():
    import base64
    df = _table("lab1", "events_flat")
    _cols(df, "user_id", "event_name", "city", "item_id")
    expected = 0
    for f in sorted((RAW / "events-kafka").glob("*.json")):
        for line in f.read_text().splitlines():
            ev = json.loads(base64.b64decode(json.loads(line)["value"]))
            expected += max(1, len(ev["items"]))
    _need(df.count() == expected,
          f"expected {expected} rows (explode_OUTER keeps events with no items), found {df.count()}")


@exercise("1h", "MERGE INTO + schema evolution + time travel")
def _1h():
    df = _table("lab1", "main_users_target")
    _cols(df, "id", "email", "status", "country")
    rows = {r.id: r for r in df.collect()}
    _need(2 not in rows, "id 2 had status 'delete' — it should be deleted")
    _need(rows.get(1) and rows[1].email == "peter@new.com", "id 1 should have the updated email")
    _need(5 in rows and rows[5].country == "CA", "id 5 (new user with country) should be inserted")
    _need(_history("lab1", "main_users_target").filter("operation = 'MERGE'").count() >= 2, "expected 2 MERGE versions")


# ---------------------------------------------------------------- lab 2 jobs
@exercise("2a", "First multi-task job (DAG)")
def _2a():
    r = _run_state("2a")
    _need(r["status"] == "SUCCEEDED", "the run did not succeed")
    _need(len(r["tasks"]) >= 3, "use at least 3 tasks")
    _need(any(len(t["depends_on"]) >= 2 for t in r["tasks"].values()), "one task should depend on 2 tasks (funnel)")
    _table("lab2", "customers_orders")


@exercise("2b", "Parameters and task values")
def _2b():
    r = _run_state("2b")
    _need(r["status"] == "SUCCEEDED", "the run did not succeed")
    _need(any(v for v in r["values"].values()), "no task values were set (ctx.task_values.set)")
    _need(r["params"].get("catalog") == "lab2_prod", "run the job with job parameter catalog='lab2_prod'")
    _need(any("{{tasks." in str(p) for t in r["tasks"].values() for p in t["parameters"].values()),
          "one task parameter should use a {{tasks.<task>.values.<key>}} reference")


@exercise("2c", "If/else, For each, run-if")
def _2c():
    r = _run_state("2c")
    kinds = [t["kind"] for t in r["tasks"].values()]
    _need("condition" in kinds, "add an If/else condition task")
    _need("for_each" in kinds, "add a For each task")
    _need(any(t["run_if"] != "ALL_SUCCEEDED" for t in r["tasks"].values()), "use a run_if other than ALL_SUCCEEDED")
    _need(any(t["status"] == "EXCLUDED" for t in r["tasks"].values()), "one branch of the If/else should be excluded")
    _need(r["status"] == "SUCCEEDED", "the run did not succeed")


@exercise("2d", "Repair a failed run")
def _2d():
    r = _run_state("2d")
    _need(r.get("repaired_from"), "save the REPAIRED run (run = job.repair(run); run.save('2d'))")
    _need(r["status"] == "SUCCEEDED", "the repaired run did not succeed")


# ---------------------------------------------------------------- lab 3 pipelines
@exercise("3a", "Bronze/silver streaming tables + gold materialized view")
def _3a():
    b, s, g = _table("lab3", "orders_bronze"), _table("lab3", "orders_silver"), _table("lab3", "gold_orders_by_date")
    _need(b.count() >= 40, f"land 4 order files and refresh twice — bronze has {b.count()} rows (expected 40)")
    _need(b.count() == b.select("order_id").distinct().count(), "bronze has duplicates — is the checkpoint used?")
    _need(s.count() == b.count(), "silver should have the same rows as bronze")
    total = g.selectExpr("sum(total_daily_orders) t").collect()[0].t
    _need(total == s.count(), f"gold total ({total}) must equal silver rows ({s.count()}) — recompute the MV")


@exercise("3b", "Expectations: warn, drop, fail")
def _3b():
    s = _table("lab3", "orders_silver_dq")
    _need(s.filter("customer_id IS NULL").count() == 0, "rows with NULL customer_id should be dropped")
    _need(s.filter("notifications NOT IN ('Y','N')").count() > 0,
          "valid_notifications is WARN — bad rows should still be kept")


@exercise("3c", "Join streaming tables in a materialized view")
def _3c():
    g = _table("lab3", "full_order_info_gold")
    _cols(g, "order_id", "order_status", "customer_id")
    _need(g.count() > 0, "full_order_info_gold is empty")


@exercise("3d", "CDC SCD Type 1 with SEQUENCE BY")
def _3d():
    rows = {r.customer_id: r for r in _table("lab3", "customers_silver").collect()}
    _need(2 not in rows, "customer 2 was DELETED — remove it")
    _need(rows.get(1) and rows[1].address == "123 Main St.",
          "customer 1 must have the LATEST address by process_date (123 Main St.) even though updates arrived out of order")
    _need(4 in rows and 3 in rows, "customers 3 and 4 should exist")
    _need("operation" not in rows[1].asDict(), "do not keep the 'operation' column (COLUMNS * EXCEPT (operation))")


# ---------------------------------------------------------------- lab 4 devops
def _env():
    import os
    return {**os.environ, "PYTHONPATH": str(LAB_ROOT)}


def _pytest(*args):
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *args],
                          cwd=LAB_ROOT / "lab4_project", capture_output=True, text=True, env=_env())


@exercise("4a", "Modular PySpark functions")
def _4a():
    sys.path.insert(0, str(LAB_ROOT / "lab4_project"))
    import importlib
    import src.transforms as t
    importlib.reload(t)
    spark = _spark()
    df = spark.createDataFrame([(1.0, "a"), (10.0, "b")], ["trip_distance", "My Col"])
    try:
        out = t.convert_miles_to_km(df, "trip_distance_km", "trip_distance")
    except NotImplementedError:
        raise Fail("functions are not written yet — edit lab4_project/src/transforms.py (remove the `raise NotImplementedError`)")
    _need(out is not None, "convert_miles_to_km returns None — did you forget `return`?")
    _need([r.trip_distance_km for r in out.collect()] == [1.61, 16.09], "convert_miles_to_km: wrong values (round to 2)")
    try:
        up = t.uppercase_column_names(df)
        hc_in = spark.createDataFrame([(0,), (1,), (2,), (None,)], "HighCholest INT")
        hc = t.add_high_cholest_flag(hc_in)
    except NotImplementedError:
        raise Fail("convert_miles_to_km works ✓ — now write uppercase_column_names and add_high_cholest_flag")
    _need(up.columns == ["TRIP_DISTANCE", "MY COL"], f"uppercase_column_names gave {up.columns}")
    _need([r.HighCholest_Group for r in hc.collect()] == ["Normal", "Above Average", "High", "Unknown"],
          "add_high_cholest_flag: 0→Normal, 1→Above Average, 2→High, anything else→Unknown")


@exercise("4b", "Unit tests with pytest")
def _4b():
    out = _pytest("tests")
    _need(out.returncode == 0, "pytest failed:\n" + out.stdout[-1500:])
    import re
    m = re.search(r"(\d+) passed", out.stdout)
    _need(m and int(m.group(1)) >= 3, "write at least 3 tests in lab4_project/tests/")
    return out.stdout.strip().splitlines()[-1]


@exercise("4c", "Your tests catch bugs (mutation test)")
def _4c():
    import shutil
    import tempfile
    proj = LAB_ROOT / "lab4_project"
    base = _pytest("tests")
    _need(base.returncode == 0, "your tests must pass on your own code first (make check 4b pass)")
    mutants = (Path(__file__).parent / "_mutants").glob("*.py")
    survived = []
    for m in sorted(mutants):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(proj / "tests", Path(tmp) / "tests")
            (Path(tmp) / "src").mkdir()
            shutil.copy(proj / "src" / "__init__.py", Path(tmp) / "src" / "__init__.py")
            shutil.copy(m, Path(tmp) / "src" / "transforms.py")
            for f in ("pytest.ini",):
                if (proj / f).exists():
                    shutil.copy(proj / f, Path(tmp) / f)
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
                               cwd=tmp, capture_output=True, text=True, env=_env())
            if r.returncode == 0:
                survived.append(m.stem)
    _need(not survived, f"these buggy versions still PASS your tests: {survived}. Add tests that catch them "
                        "(see the docstring at the top of each file in labutils/_mutants/).")


# ---------------------------------------------------------------- lab 5 extras
@exercise("5a", "OPTIMIZE / RESTORE / VACUUM")
def _5a():
    ops = {r.operation for r in _history("lab5", "events_small").collect()}
    _need("OPTIMIZE" in ops, "run OPTIMIZE on lab5.events_small")
    _need("RESTORE" in ops, "run RESTORE TABLE ... TO VERSION AS OF ...")
    _need(any(o.startswith("VACUUM") for o in ops), "run VACUUM")


@exercise("5b", "Window function de-duplication")
def _5b():
    df = _table("lab5", "users_latest")
    _need(df.count() == df.select("user_id").distinct().count() == 3, "one row per user (3 users)")
    rows = {r.user_id: r.email for r in df.collect()}
    _need(rows.get("u1") == "u1@third.com", "u1 should keep the LATEST email (by updated_at)")


@exercise("5c", "Higher-order functions")
def _5c():
    df = _table("lab5", "event_item_totals")
    _cols(df, "user_id", "item_count", "order_value", "expensive_items")
    _need(df.filter("item_count = 0").count() > 0, "keep events with no items (item_count = 0)")


@exercise("5d", "Streaming aggregation (complete output mode)")
def _5d():
    df = _table("lab5", "orders_per_customer")
    _cols(df, "customer_id", "n_orders")
    _need(df.count() > 0, "no rows")


# ---------------------------------------------------------------- labs 6-9 (official exam guide gaps)
import re as _re


def _answer(eid):
    from labutils.submit import load
    a = load(eid)
    _need(a is not None, f"no answer saved yet — run your code (it calls submit('{eid}', ...))")
    return a


def _sql_has(sql, pattern, msg):
    _need(_re.search(pattern, " ".join(sql.split()), _re.I), msg)


@exercise("6a", "Clean bronze → silver")
def _6a():
    df = _table("lab6", "customers_silver")
    types = dict(df.dtypes)
    _need("raw_note" not in df.columns, "drop the raw_note column")
    _cols(df, "customer_id", "first_name", "last_name", "signed_up", "email", "country")
    _need(types["customer_id"] == "int", f"customer_id should be int, it is {types['customer_id']}")
    _need(types["signed_up"] == "date", "signed_up should be a DATE (to_date) and renamed from signup_date")
    _need(df.count() == 4, f"expected 4 rows (the row with no customer_id removed), found {df.count()}")
    _need(df.filter("email IS NULL").count() == 0, "NULL emails should be filled with 'unknown'")
    ana = df.filter("customer_id = 1").first()
    _need(ana.first_name == "Ana" and ana.last_name == "Silva", "split full_name: first_name='Ana', last_name='Silva' (index 1)")


@exercise("6b", "Joins and unions")
def _6b():
    a = _answer("6b")
    exp = {"inner": 6, "left": 8, "multi": 5, "cross": 6, "union_all": 4, "union_distinct": 3}
    for k, v in exp.items():
        _need(a.get(k) == v, f"{k}: expected {v} rows, got {a.get(k)} — check the join type / method")
    _need("BroadcastHashJoin" in a["bcast_plan"], "the broadcast join plan should show BroadcastHashJoin (use F.broadcast)")


@exercise("6c", "De-duplicate and aggregate")
def _6c():
    rows = {r.country: r for r in _table("lab6", "country_stats").collect()}
    _need(set(rows) == {"US", "EU"}, "group by country (US and EU)")
    _need(rows["US"].n_orders == 5, f"US should have 5 orders after removing the duplicate, found {rows['US'].n_orders}")
    _need(rows["US"].approx_customers == 4, "approx_customers for US should be 4 (approx_count_distinct)")
    _need(abs(float(rows["US"].avg_amount) - 64.98) < 0.01, "avg_amount for US should be 64.98 (avg / mean)")


@exercise("6d", "Spark tuning parameters")
def _6d():
    a = _answer("6d")
    _need("SortMergeJoin" in a["off"], "with autoBroadcastJoinThreshold = -1 the plan should be a SortMergeJoin")
    _need("BroadcastHashJoin" in a["on"], "with a 10 MB threshold the small table should be broadcast")
    _need(a["parts"] == 8, f"set spark.sql.shuffle.partitions to 8 (got {a['parts']} partitions)")


@exercise("7a", "Fix data skew with salting")
def _7a():
    p, t = _table("lab7", "partial_totals"), _table("lab7", "customer_totals")
    _cols(p, "customer_id", "salt", "partial_amount")
    _need(p.filter("customer_id = 1").select("salt").distinct().count() > 1, "the hot key (customer 1) should be split over several salts")
    _cols(t, "customer_id", "total_amount")
    want = {r.customer_id: r.s for r in _table("lab7", "sales").groupBy("customer_id").agg({"amount": "sum"})
            .withColumnRenamed("sum(amount)", "s").collect()}
    got = {r.customer_id: r.total_amount for r in t.collect()}
    _need(t.count() == t.select("customer_id").distinct().count(), "one row per customer in customer_totals (2nd groupBy only by customer_id)")
    if want:
        _need(all(abs(got.get(k, -1) - v) < 1e-6 for k, v in want.items()), "totals are wrong — step 2 must SUM the partial_amount")


@exercise("7b", "Liquid clustering")
def _7b():
    d = _spark().read.format("delta").load(str(WAREHOUSE / "lab7.db" / "events"))
    from delta.tables import DeltaTable
    det = DeltaTable.forPath(_spark(), str(WAREHOUSE / "lab7.db" / "events")).detail().first()
    _need(list(det.clusteringColumns) == ["customer_id"], f"clustering columns should be ['customer_id'], found {list(det.clusteringColumns)}")
    _need(_history("lab7", "events").filter("operation = 'OPTIMIZE'").count() >= 1, "run OPTIMIZE to cluster the data")
    _need(d.count() == 5000, "the table should have 5000 rows")


def _match(eid, expected, why):
    a = _answer(eid)
    wrong = [k for k, v in expected.items() if str(a.get(k, "")).strip().upper() != v]
    _need(not wrong, f"not right yet: {wrong}. {why}")


@exercise("7c", "Diagnose failures")
def _7c():
    _match("7c", {"E1": "B", "E2": "C", "E3": "D", "E4": "A", "E5": "E"}, "Re-read each error: where does it happen — driver, libraries, cluster start, timeout, or one slow task?")


@exercise("7d", "Choose compute")
def _7d():
    _match("7d", {"S1": "W", "S2": "J", "S3": "P", "S4": "S"}, "SQL users → warehouse; scheduled ETL → job cluster; interactive dev → all-purpose; no cluster management + fast start → serverless.")


@exercise("8a", "Git folder workflow")
def _8a():
    a = [str(x).strip().lower() for x in _answer("8a")]
    _need(a == ["c", "b", "e", "a", "f", "d"], f"order {a} is not right. Think: clone → branch → edit → commit/push → PR → pull main")


@exercise("8b", "Bundle with variables, targets, overrides")
def _8b():
    from labutils.bundle import BundleError, validate
    path = LAB_ROOT / "lab8_project" / "databricks.yml"
    _need("<FILL-IN" not in path.read_text(), "replace every <FILL-IN> in databricks.yml")
    env = {"BUNDLE_VAR_db_password": "x"}
    try:
        r = {t: validate(path, t, env=env, quiet=True) for t in ("dev", "test", "prod")}
        default = validate(path, None, env=env, quiet=True)
    except BundleError as e:
        raise Fail(f"bundle validate failed: {e}")
    for t, cat in (("dev", "dev_catalog"), ("test", "test_catalog"), ("prod", "prod_catalog")):
        _need(r[t]["variables"]["catalog"] == cat, f"target {t}: catalog should resolve to {cat}, got {r[t]['variables']['catalog']}")
        job = r[t]["resources"]["jobs"]["health_etl_job"]
        _need(job["name"] == f"health_etl_{t}", f"target {t}: job name should be health_etl_{t} — use ${{bundle.target}}")
        param = job["tasks"][0]["notebook_task"]["base_parameters"]["catalog"]
        _need(param == cat, f"target {t}: task parameter catalog should be {cat} — use ${{var.catalog}}")
    _need(default["target"] == "dev", "dev should be the default target (default: true)")
    _need(r["prod"]["mode"] == "production", "prod must use mode: production")
    _need("schedule" in r["prod"]["resources"]["jobs"]["health_etl_job"] and
          "schedule" not in r["dev"]["resources"]["jobs"]["health_etl_job"], "only prod should get the schedule (target override)")
    try:
        validate(path, "prod", env={}, quiet=True)
        raise Fail("db_password must have NO default (it must come from BUNDLE_VAR_db_password)")
    except BundleError:
        pass


@exercise("8c", "Secrets + CLI validate/deploy/run")
def _8c():
    a = _answer("8c")
    r = a["result"]
    _need(r["target"] == "prod", "validate the prod target")
    _need(r["sources"].get("db_password") == "BUNDLE_VAR_db_password", "the password must come from the BUNDLE_VAR_db_password environment variable")
    c = {k: " ".join(str(v).split()) for k, v in a["commands"].items()}
    _need(_re.fullmatch(r"databricks bundle validate (-t|--target)[ =]prod", c["validate"]), "validate: databricks bundle validate -t prod")
    _need(_re.fullmatch(r"databricks bundle deploy (-t|--target)[ =]prod", c["deploy"]), "deploy: databricks bundle deploy -t prod")
    _need(_re.fullmatch(r"databricks bundle run (-t|--target)[ =]prod health_etl_job", c["run"]), "run: databricks bundle run -t prod health_etl_job")


@exercise("9a", "GRANT / REVOKE")
def _9a():
    sql = _answer("9a")
    _need("<FILL-IN" not in sql, "replace every <FILL-IN>")
    q = r"`?{}`?"
    _sql_has(sql, r"GRANT USE CATALOG ON CATALOG main TO " + q.format("analysts"), "analysts need USE CATALOG on catalog main")
    _sql_has(sql, r"GRANT USE SCHEMA ON SCHEMA main\.sales TO " + q.format("analysts"), "analysts need USE SCHEMA on schema main.sales")
    _sql_has(sql, r"GRANT SELECT ON (TABLE )?main\.sales\.orders TO " + q.format("analysts"), "analysts need SELECT on the table")
    _sql_has(sql, r"REVOKE SELECT ON (TABLE )?main\.sales\.orders FROM " + q.format("contractors"), "REVOKE SELECT … FROM `contractors` (REVOKE uses FROM)")
    _sql_has(sql, r"GRANT MODIFY ON (TABLE )?main\.sales\.orders TO " + q.format("etl-sp"), "writing rows needs MODIFY (for `etl-sp`)")


@exercise("9b", "Managed ↔ external")
def _9b():
    a = _answer("9b")
    sql = a["sql"]
    _need("<FILL-IN" not in sql, "replace every <FILL-IN>")
    _sql_has(sql, r"CREATE TABLE main\.raw\.events_ext \(id INT, ts TIMESTAMP\) LOCATION 's3://acme-raw/events'", "an external table is created with LOCATION '<path>'")
    _sql_has(sql, r"ALTER TABLE main\.raw\.events_ext SET MANAGED", "convert with ALTER TABLE … SET MANAGED")
    _sql_has(sql, r"ALTER TABLE main\.raw\.events_ext UNSET MANAGED", "roll back with ALTER TABLE … UNSET MANAGED")
    _need(a.get("drop_managed_deletes_data") is True and a.get("drop_external_deletes_data") is False,
          "DROP on a managed table deletes the data; on an external table the files stay")


@exercise("9c", "Column mask + row filter")
def _9c():
    from labutils.governance import login
    a = _answer("9c")
    spark = _spark()
    expect = {"finance": (["EU"], True), "admin": (["EU", "US"], False), "other": (["EU"], False)}
    for who, groups in (("finance", ["finance_team"]), ("admin", ["admins"]), ("other", [])):
        login(f"{who}@corp.com", groups)
        rows = spark.sql(f"SELECT {a['mask']} AS cc, region FROM lab9.customers WHERE {a['row_filter']}").collect()
        regions, full = expect[who]
        _need(sorted({r.region for r in rows}) == regions, f"{who}: should see regions {regions}, saw {sorted({r.region for r in rows})}")
        masked = all(r.cc.startswith("****") for r in rows)
        _need((not masked) if full else masked, f"{who}: card numbers should be {'FULL' if full else 'masked (****1234)'}")
    login("you@corp.com", [])


@exercise("9d", "ABAC vs masks vs grants")
def _9d():
    _match("9d", {"Q1": "ABAC", "Q2": "MASK", "Q3": "ABAC", "Q4": "GRANT"}, "ABAC = one tag-based policy for MANY tables; a mask = one column; GRANT = access to an object.")


# ---------------------------------------------------------------- runner
def check(eid: str):
    """Grade one exercise and print the result (use in notebooks)."""
    run_check(eid)


def run_check(eid: str) -> bool:
    if eid == "all":
        return all([run_check(k) for k in CHECKS if k != "env"])
    if eid not in CHECKS:
        print(f"Unknown exercise '{eid}'. Known: {', '.join(CHECKS)}")
        return False
    title, fn = CHECKS[eid]
    try:
        msg = fn()
        print(f"✅ {eid} — {title}: PASSED" + (f"  ({msg})" if msg else ""))
        _record(eid, True)
        return True
    except Fail as e:
        print(f"❌ {eid} — {title}: NOT YET\n   → {e}")
        _record(eid, False)
        return False
    except Exception as e:  # noqa: BLE001
        print(f"❌ {eid} — {title}: ERROR {type(e).__name__}: {str(e)[:400]}")
        _record(eid, False)
        return False


def _record(eid, ok):
    f = LAB_ROOT / "progress" / "progress.json"
    try:
        data = json.loads(f.read_text())
        lab = data.setdefault("labs", {}).setdefault(eid, {"passed": False, "attempts": 0})
        lab["attempts"] += 1
        lab["passed"] = lab["passed"] or ok
        f.write_text(json.dumps(data, indent=2))
    except Exception:
        pass


if __name__ == "__main__":
    ok = all([run_check(a) for a in (sys.argv[1:] or ["env"])])
    sys.exit(0 if ok else 1)
