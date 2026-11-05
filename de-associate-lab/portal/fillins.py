"""Number the gaps in starter code: every `<FILL-IN …>` becomes `<FILL-IN 1>`, `<FILL-IN 2>`, … in order,
so each numbered instruction points to exactly one gap. Hints inside the old placeholder are dropped
(the instructions explain each gap)."""
import re

PATTERN = re.compile(r"<FILL-IN(?:[^<>\n]|<[^<>\n]*>)*>")


def number(code: str) -> str:
    n = iter(range(1, 1000))
    return PATTERN.sub(lambda m: f"<FILL-IN {next(n)}>", code)
