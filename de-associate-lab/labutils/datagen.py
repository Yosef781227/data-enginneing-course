"""Create small synthetic datasets shaped like the course data (deterministic, no downloads).

data/raw/
  users-historical/   parquet   user_id, user_first_touch_timestamp (micros), email
  users-batches/      parquet   3 single-file batches (batch 3 has an extra `country` column)
  sales-csv/          csv '|'   4 files, header
  malformed/          csv ','   item_id,name,price  with a "$" price and a bad row
  events-kafka/       json      key/value base64-encoded like Kafka
  orders-batches/     json      6 files of orders (some bad notifications / null customer_id)
  status-batches/     json      order status events
  customers-cdc/      json      2 batches of CDC changes (INSERT/UPDATE/DELETE)

Files are "landed" into a fake volume folder with labutils.landing.land(...).
"""
import base64
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from labutils import RAW

VERSION = "1"


def _w(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _users(rng, start, n):
    base = datetime(2020, 6, 1, tzinfo=timezone.utc)
    rows = []
    for i in range(start, start + n):
        ts = base + timedelta(minutes=rng.randint(0, 60 * 24 * 30))
        rows.append((f"UA{i:09d}", int(ts.timestamp() * 1_000_000), f"user{i}@example.com"))
    return rows


def _write_parquet(spark, rows, schema, folder: Path, files=1):
    df = spark.createDataFrame(rows, schema)
    df.repartition(files).write.mode("overwrite").parquet(str(folder))


def _sales_csv(rng):
    for f in range(4):
        lines = ["order_id|email|transactions_timestamp|total_item_quantity|purchase_revenue_in_usd|unique_items"]
        for i in range(25):
            oid = 257000 + f * 25 + i
            ts = 1592500000000000 + rng.randint(0, 10**12)
            q = rng.randint(1, 4)
            lines.append(f"{oid}|user{rng.randint(1, 300)}@example.com|{ts}|{q}|{q * rng.choice([19.95, 49.5, 595.0]):.2f}|{rng.randint(1, q)}")
        _w(RAW / "sales-csv" / f"sales_{f:02d}.csv", "\n".join(lines) + "\n")


def _malformed():
    _w(
        RAW / "malformed" / "lab_malformed_data.csv",
        "item_id,name,price\n"
        "M_PREM_A,Premium Queen Mattress,1795.0\n"
        "M_STAN_F,Standard Full Mattress,$945.00\n"
        "P_FOAM_S,Foam Pillow,59.0\n"
        "M_PREM_K,Premium King Mattress,$1995.00\n"
        "P_DOWN_S,Down Pillow,99.0\n",
    )


def _events_kafka(rng):
    devices = ["iOS", "Android", "macOS", "Windows", "Linux"]
    names = ["main", "add_item", "cart", "checkout", "finalize"]
    cities = [("New York", "NY"), ("Austin", "TX"), ("Seattle", "WA"), ("Denver", "CO")]
    for f in range(3):
        lines = []
        for i in range(20):
            uid = f"UA{rng.randint(1, 300):09d}"
            ts = 1593880000000000 + rng.randint(0, 10**10)
            items = [] if rng.random() < 0.4 else [
                {"item_id": rng.choice(["M_STAN_Q", "P_FOAM_K", "M_PREM_F"]),
                 "price_usd": rng.choice([1045.0, 59.0, 1795.0]), "quantity": rng.randint(1, 2)}
                for _ in range(rng.randint(1, 3))
            ]
            city, state = rng.choice(cities)
            event = {"device": rng.choice(devices), "event_name": rng.choice(names),
                     "event_timestamp": ts, "geo": {"city": city, "state": state},
                     "items": items, "user_id": uid}
            lines.append(json.dumps({
                "key": base64.b64encode(uid.encode()).decode(),
                "offset": 219255030 + f * 100 + i, "partition": f % 2,
                "timestamp": ts // 1000, "topic": "clickstream",
                "value": base64.b64encode(json.dumps(event).encode()).decode(),
            }))
        _w(RAW / "events-kafka" / f"{f:03d}.json", "\n".join(lines) + "\n")


def _orders(rng):
    oid = 75000
    for f in range(6):
        lines, status = [], []
        for i in range(10):
            oid += 1
            ts = datetime(2024, 3, 1) + timedelta(days=f, minutes=rng.randint(0, 1400))
            notif = rng.choice(["Y", "N", "Y", "N", "X"]) if i % 4 == 0 else rng.choice(["Y", "N"])
            cust = None if i == 7 and f % 2 == 0 else rng.randint(1, 40)
            lines.append(json.dumps({"order_id": oid, "order_timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                                     "customer_id": cust, "notifications": notif}))
            for st in ["placed", "preparing", rng.choice(["delivered", "cancelled"])]:
                ts = ts + timedelta(hours=rng.randint(1, 20))
                status.append(json.dumps({"order_id": oid, "order_status": st,
                                          "status_timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")}))
        _w(RAW / "orders-batches" / f"{f:02d}.json", "\n".join(lines) + "\n")
        _w(RAW / "status-batches" / f"{f:02d}.json", "\n".join(status) + "\n")


def _customers_cdc():
    b1 = [
        {"customer_id": 1, "name": "Peter", "address": "1 Blue Rd.", "operation": "INSERT", "process_date": "2025-05-01"},
        {"customer_id": 2, "name": "Samarth", "address": "22 Front St", "operation": "INSERT", "process_date": "2025-05-01"},
        {"customer_id": 3, "name": "Zebi", "address": "7 Oak Ave", "operation": "INSERT", "process_date": "2025-05-01"},
    ]
    b2 = [  # note: the two Peter updates arrive OUT OF ORDER
        {"customer_id": 1, "name": "Peter", "address": "123 Main St.", "operation": "UPDATE", "process_date": "2025-05-20"},
        {"customer_id": 1, "name": "Peter", "address": "99 Sunny St.", "operation": "UPDATE", "process_date": "2025-05-15"},
        {"customer_id": 2, "name": None, "address": None, "operation": "DELETE", "process_date": "2025-05-20"},
        {"customer_id": 4, "name": "Kostas", "address": "100 Athens Dr.", "operation": "INSERT", "process_date": "2025-05-20"},
    ]
    for i, b in enumerate([b1, b2]):
        _w(RAW / "customers-cdc" / f"{i:02d}.json", "\n".join(json.dumps(r) for r in b) + "\n")


def ensure_data(force=False):
    marker = RAW / f".generated_v{VERSION}"
    if marker.exists() and not force:
        return
    from labutils import get_spark

    spark = get_spark()
    rng = random.Random(42)
    schema = "user_id STRING, user_first_touch_timestamp BIGINT, email STRING"
    _write_parquet(spark, _users(rng, 1, 300), schema, RAW / "users-historical", files=3)
    for b in range(3):
        rows = _users(rng, 1000 + b * 50, 50)
        target = RAW / "users-batches" / f"batch_{b + 1}"
        if b == 2:
            rows = [r + (rng.choice(["US", "CA", "MX"]),) for r in rows]
            _write_parquet(spark, rows, schema + ", country STRING", target)
        else:
            _write_parquet(spark, rows, schema, target)
    _sales_csv(rng)
    _malformed()
    _events_kafka(rng)
    _orders(rng)
    _customers_cdc()
    marker.write_text("ok")
