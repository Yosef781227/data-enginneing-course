"""Turn the lab definitions in scripts/build_notebooks.py into portal steps.

A *group* is one exercise (e.g. "1g"); it can have several *steps* (one per code task, e.g. 1g-1, 1g-2).
Each step: explanation (markdown), prep code (runs automatically), starter code, solution,
and how it is graded (check id, or "runs without error").
"""
import importlib.util
import re
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("bn", LAB / "scripts" / "build_notebooks.py")
bn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bn)

TITLES = {
    "lab1_ingestion": ("Lab 1", "Data Ingestion", "ingestion"),
    "lab2_jobs": ("Lab 2", "Lakeflow Jobs", "jobs"),
    "lab3_pipelines": ("Lab 3", "Declarative Pipelines", "sdp"),
    "lab4_devops": ("Lab 4", "DevOps & Testing", "devops"),
    "lab5_delta_sql_streaming": ("Lab 5", "Delta, SQL & Streaming", "delta"),
    "lab6_transform_tuning": ("Lab 6", "Transform & Tune", "transform"),
    "lab7_troubleshooting": ("Lab 7", "Troubleshoot & Compute", "troubleshooting"),
    "lab8_cicd_bundles": ("Lab 8", "CI/CD & Bundles", "cicd"),
    "lab9_governance": ("Lab 9", "Governance & Security", "governance"),
}
FILES = {"4a": "lab4_project/src/transforms.py", "4b": "lab4_project/tests/test_transforms.py",
         "4c": "lab4_project/tests/test_transforms.py", "8b": "lab8_project/databricks.yml"}
SOLUTION_FILES = {"4a": "labutils/_solutions/transforms.py", "4b": "labutils/_solutions/test_transforms.py",
                  "4c": "labutils/_solutions/test_transforms.py", "8b": "labutils/_solutions/databricks.yml"}

from portal.fillins import number as _number  # noqa: E402

_CHECK = re.compile(r'check\("([^"]+)"\)')


def _strip_checks(code):
    code = re.sub(r';?\s*check\("[^"]+"\)', "", code)
    return "\n".join(l for l in code.splitlines() if l.strip()).strip()


def _strip_legend(md):
    return md.split("**How this lab works**")[0].strip()


def build_lab(lab_id):
    cells = bn.NOTEBOOKS[lab_id]
    intro, setup, groups, cur = "", [], [], None
    for c in cells:
        kind = c[0]
        if kind == "md" and c[1].lstrip().startswith("# "):
            intro = _strip_legend(c[1])
            continue
        if kind == "md" and c[1].lstrip().startswith("## "):
            title = c[1].lstrip().splitlines()[0][3:].strip()
            m = re.match(r"(\d[a-z])\b", title)
            cur = {"gid": m.group(1) if m else re.sub(r"\W+", "-", title.lower())[:20],
                   "title": title, "items": [("md", c[1].lstrip().split("\n", 1)[1] if "\n" in c[1].lstrip() else "")]}
            groups.append(cur)
            continue
        if cur is None:
            if kind == "code":
                setup.append(c[1])
            continue
        cur["items"].append(c)

    steps = []
    for g in groups:
        checks = [m for it in g["items"] if it[0] == "code" for m in _CHECK.findall(it[1])]
        check_id = checks[0] if checks else None
        exes = [i for i, it in enumerate(g["items"]) if it[0] == "ex"]
        base = {"gid": g["gid"], "group_title": g["title"]}
        if check_id in FILES and not exes:
            md = "\n\n".join(it[1] for it in g["items"] if it[0] == "md")
            steps.append({**base, "key": check_id, "title": g["title"], "type": "file", "explain": md,
                          "file": FILES[check_id], "solution_file": SOLUTION_FILES[check_id],
                          "prep": "", "starter": "", "solution": "", "check": check_id, "after": ""})
            continue
        if not exes:  # info page: text + optional demo code
            md = "\n\n".join(it[1] for it in g["items"] if it[0] == "md")
            demo = "\n\n".join(_strip_checks(it[1]) for it in g["items"] if it[0] == "code")
            steps.append({**base, "key": g["gid"], "title": g["title"], "type": "info", "explain": md,
                          "prep": "", "starter": demo, "solution": demo, "check": None, "after": ""})
            continue
        start = 0
        for n, ei in enumerate(exes):
            md = [it[1] for it in g["items"][start:ei] if it[0] == "md"]
            prep = [it[1] for it in g["items"][start:ei] if it[0] == "code"]
            last = n == len(exes) - 1
            after = []
            if last:
                after = [_strip_checks(it[1]) for it in g["items"][ei + 1:] if it[0] == "code"]
                after = [a for a in after if a]
            key = g["gid"] if len(exes) == 1 else f'{g["gid"]}-{n + 1}'
            title = g["title"] if len(exes) == 1 else f'{g["title"]} — part {n + 1}'
            steps.append({**base, "key": key, "title": title, "type": "code", "explain": "\n\n".join(md),
                          "prep": "\n\n".join(_strip_checks(p) for p in prep).strip(),
                          "starter": _number(g["items"][ei][1]), "solution": g["items"][ei][2],
                          "check": check_id if last else None, "after": "\n\n".join(after)})
            start = ei + 1
    label, name, topic = TITLES[lab_id]
    return {"id": lab_id, "label": label, "name": name, "topic": topic, "intro": intro,
            "setup": "\n".join(setup), "steps": steps}


def all_labs():
    return [build_lab(k) for k in bn.NOTEBOOKS]
