"""Simulate files arriving in cloud storage (a UC volume) one batch at a time.

    from labutils import landing
    vol = landing.reset("orders")   # empty fake volume folder, returns its path
    landing.land("orders", 2)       # copy the next 2 files from data/raw/orders-batches
"""
import shutil
from pathlib import Path

from labutils import LAB_ROOT, RAW

LANDING = LAB_ROOT / ".lab_landing"

SOURCES = {
    "orders": "orders-batches",
    "status": "status-batches",
    "users": "users-batches",
    "users_stream": "users-batches",
    "orders_agg": "orders-batches",
    "customers": "customers-cdc",
}


def volume(name: str) -> str:
    return str(LANDING / name)


def reset(name: str) -> str:
    shutil.rmtree(LANDING / name, ignore_errors=True)
    (LANDING / name).mkdir(parents=True)
    return volume(name)


def land(name: str, n: int = 1) -> list:
    """Copy the next n not-yet-landed files (or batch folders) into the fake volume."""
    src = RAW / SOURCES[name]
    dest = LANDING / name
    dest.mkdir(parents=True, exist_ok=True)
    done = {p.name for p in dest.iterdir()} | {p.stem for p in dest.iterdir()}
    todo = [p for p in sorted(src.iterdir()) if not p.name.startswith(".") and p.name not in done][:n]
    for p in todo:
        if p.is_dir():
            # flatten a parquet batch folder into one file so the volume holds plain files
            part = next(f for f in p.iterdir() if f.suffix == ".parquet")
            shutil.copy(part, dest / f"{p.name}.parquet")
        else:
            shutil.copy(p, dest / p.name)
    landed = sorted(f.name for f in dest.iterdir() if not f.name.startswith("."))
    print(f"Landed {len(todo)} new file(s). Volume '{name}' now has: {landed}")
    return landed
