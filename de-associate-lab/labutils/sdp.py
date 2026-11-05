"""Local stand-in for Spark Declarative Pipelines (SDP) data-quality expectations.

In Databricks you write:
    CONSTRAINT valid_id EXPECT (customer_id IS NOT NULL) ON VIOLATION DROP ROW
Here you call:
    df_out, metrics = expect(df, [("valid_id", "customer_id IS NOT NULL", "drop")])

action: "warn" (default — keep bad rows), "drop" (remove bad rows), "fail" (stop the update).
`metrics` looks like the data-quality part of the pipeline event log.
"""
from pyspark.sql import DataFrame, functions as F


class ExpectationFailed(Exception):
    """Raised for ON VIOLATION FAIL UPDATE — the pipeline update stops."""


def expect(df: DataFrame, expectations, dataset: str = "dataset"):
    df = df.cache()
    total = df.count()
    metrics = {"dataset": dataset, "input_rows": total, "expectations": []}
    keep = F.lit(True)
    for name, condition, *rest in expectations:
        action = (rest[0] if rest else "warn").lower()
        if action not in ("warn", "drop", "fail"):
            raise ValueError("action must be 'warn', 'drop' or 'fail'")
        ok = F.coalesce(F.expr(condition), F.lit(False))  # NULL result counts as a violation
        failed = df.filter(~ok).count()
        metrics["expectations"].append(
            {"name": name, "condition": condition, "action": action,
             "passed_records": total - failed, "failed_records": failed})
        if action == "fail" and failed:
            _print(metrics)
            raise ExpectationFailed(
                f"Expectation '{name}' ({condition}) failed for {failed} row(s) — "
                "ON VIOLATION FAIL UPDATE stops the pipeline update; nothing is written.")
        if action == "drop":
            keep = keep & ok
    out = df.filter(keep)
    metrics["output_rows"] = out.count()
    metrics["dropped_rows"] = total - metrics["output_rows"]
    _print(metrics)
    return out, metrics


def _print(m):
    print(f"[event log] data quality for '{m['dataset']}': input={m['input_rows']} "
          f"output={m.get('output_rows', '-')} dropped={m.get('dropped_rows', '-')}")
    for e in m["expectations"]:
        print(f"   - {e['name']:<22} {e['action'].upper():<5} passed={e['passed_records']:<4} "
              f"failed={e['failed_records']:<4} ({e['condition']})")
