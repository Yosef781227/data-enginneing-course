"""Plain-language explanations for every practice question, one module per exam section (s1 … s7)."""
import importlib

EXPLAIN = {}
for _n in range(1, 8):
    try:
        EXPLAIN.update(importlib.import_module(f"portal.explain.s{_n}").E)
    except ModuleNotFoundError:
        pass
