"""A tiny local simulator of Lakeflow Jobs — to practice the *concepts* without a workspace.

Real Lakeflow Jobs are configured in the Jobs UI / API / bundles. This simulator copies the
behaviour the exam asks about:
  * tasks + depends_on form a DAG (cycles are rejected)
  * run_if: ALL_SUCCEEDED (default), AT_LEAST_ONE_SUCCEEDED, NONE_FAILED, ALL_DONE,
            AT_LEAST_ONE_FAILED, ALL_FAILED
  * task parameters + job parameters (job parameters WIN on the same key)
  * task values: ctx.task_values.set(key, value) / ctx.task_values.get(task_key, key)
  * dynamic value references: {{job.parameters.x}}, {{tasks.<t>.values.<k>}}, {{input}},
    {{task.name}}, {{job.run_id}}, {{job.start_time.day}}
  * If/else condition tasks, For each tasks (with concurrency), retries, repair runs

Example
-------
    job = Job("retail", parameters={"catalog": "lab2"})

    @job.task("ingest")
    def ingest(ctx):
        ctx.task_values.set("rows", 10)

    job.if_else("has_rows", left="{{tasks.ingest.values.rows}}", op=">", right="0",
                depends_on=["ingest"])

    @job.task("report", depends_on=[("has_rows", True)])
    def report(ctx): ...

    run = job.run()
    run = job.repair(run)        # re-runs only failed tasks
"""
from __future__ import annotations

import itertools
import re
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional

SUCCEEDED, FAILED, UPSTREAM_FAILED, EXCLUDED = "SUCCEEDED", "FAILED", "UPSTREAM_FAILED", "EXCLUDED"
RUN_IF = {"ALL_SUCCEEDED", "AT_LEAST_ONE_SUCCEEDED", "NONE_FAILED", "ALL_DONE",
          "AT_LEAST_ONE_FAILED", "ALL_FAILED"}
_run_ids = itertools.count(1001)


class TaskValues:
    def __init__(self, store: dict, current: str):
        self._store, self._current = store, current

    def set(self, key: str, value: Any):
        self._store.setdefault(self._current, {})[key] = value

    def get(self, taskKey: str, key: str, default: Any = None):
        return self._store.get(taskKey, {}).get(key, default)


@dataclass
class Context:
    task_key: str
    params: dict
    task_values: TaskValues
    run_id: int
    input: Any = None

    def widget(self, name: str):
        """Like dbutils.widgets.get(name) inside a notebook task."""
        return self.params[name]


@dataclass
class Task:
    key: str
    fn: Optional[Callable] = None
    depends_on: list = field(default_factory=list)   # "key" or ("condition_key", True/False)
    run_if: str = "ALL_SUCCEEDED"
    parameters: dict = field(default_factory=dict)
    max_retries: int = 0
    kind: str = "notebook"                            # notebook | condition | for_each
    condition: tuple = ()                             # (left, op, right)
    inputs: Any = None                                # list or "{{...}}" for for_each
    concurrency: int = 1


@dataclass
class TaskRun:
    status: str = ""
    attempts: int = 0
    seconds: float = 0.0
    note: str = ""
    outcome: Optional[bool] = None   # for condition tasks


@dataclass
class Run:
    job: "Job"
    run_id: int
    params: dict
    tasks: dict
    values: dict
    start: datetime
    repaired_from: Optional[int] = None

    @property
    def status(self):
        st = [t.status for t in self.tasks.values()]
        return FAILED if any(s in (FAILED, UPSTREAM_FAILED) for s in st) else SUCCEEDED

    def show(self):
        title = f"Job '{self.job.name}'  run {self.run_id}"
        if self.repaired_from:
            title += f"  (repair of run {self.repaired_from})"
        print(f"{title}  →  {self.status}")
        icons = {SUCCEEDED: "✅", FAILED: "❌", UPSTREAM_FAILED: "⛔", EXCLUDED: "➖"}
        for key in self.job._order():
            tr = self.tasks[key]
            t = self.job.tasks[key]
            deps = ", ".join(d if isinstance(d, str) else f"{d[0]}={d[1]}" for d in t.depends_on) or "-"
            extra = f" outcome={tr.outcome}" if tr.outcome is not None else ""
            print(f"  {icons.get(tr.status, '?')} {key:<28} {tr.status:<16} attempts={tr.attempts} "
                  f"depends_on=[{deps}] run_if={t.run_if}{extra} {tr.note}")
        return self

    def save(self, exercise_id: str):
        """Save this run so `check(exercise_id)` can grade it."""
        import json
        from labutils import LAB_ROOT

        out = {
            "job": self.job.name, "run_id": self.run_id, "status": self.status,
            "repaired_from": self.repaired_from, "params": self.params,
            "values": {k: {kk: str(vv) for kk, vv in v.items()} for k, v in self.values.items()},
            "tasks": {
                k: {"status": tr.status, "attempts": tr.attempts, "outcome": tr.outcome,
                    "kind": self.job.tasks[k].kind, "run_if": self.job.tasks[k].run_if,
                    "depends_on": [d if isinstance(d, str) else list(d) for d in self.job.tasks[k].depends_on],
                    "parameters": {pk: str(pv) for pk, pv in self.job.tasks[k].parameters.items()}}
                for k, tr in self.tasks.items()
            },
        }
        f = LAB_ROOT / ".lab_state" / "runs" / f"{exercise_id}.json"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(out, indent=2))
        print(f"Saved run {self.run_id} for exercise {exercise_id}.")
        return self


class Job:
    def __init__(self, name: str, parameters: Optional[dict] = None):
        self.name = name
        self.parameters = dict(parameters or {})
        self.tasks: dict[str, Task] = {}

    # ---------- building the job ----------
    def task(self, key, depends_on=None, run_if="ALL_SUCCEEDED", parameters=None, max_retries=0):
        """Decorator: add a notebook-style task. The function receives a Context."""
        def wrap(fn):
            self.add_task(Task(key, fn, list(depends_on or []), run_if, dict(parameters or {}), max_retries))
            return fn
        return wrap

    def if_else(self, key, left, op, right, depends_on=None, run_if="ALL_SUCCEEDED"):
        if op not in ("==", "!=", ">", ">=", "<", "<="):
            raise ValueError("op must be one of == != > >= < <=")
        self.add_task(Task(key, None, list(depends_on or []), run_if, kind="condition",
                           condition=(left, op, right)))

    def for_each(self, key, inputs, fn, depends_on=None, run_if="ALL_SUCCEEDED", concurrency=1,
                 parameters=None, max_retries=0):
        """Run fn once per item of inputs (a list or a "{{...}}" reference). ctx.input = item."""
        self.add_task(Task(key, fn, list(depends_on or []), run_if, dict(parameters or {}),
                           max_retries, kind="for_each", inputs=inputs, concurrency=concurrency))

    def add_task(self, t: Task):
        if t.run_if not in RUN_IF:
            raise ValueError(f"run_if must be one of {sorted(RUN_IF)}")
        if t.key in self.tasks:
            raise ValueError(f"task key '{t.key}' already exists")
        self.tasks[t.key] = t

    # ---------- DAG ----------
    @staticmethod
    def _dep_key(d):
        return d if isinstance(d, str) else d[0]

    def _order(self):
        indeg = {k: 0 for k in self.tasks}
        for t in self.tasks.values():
            for d in t.depends_on:
                if self._dep_key(d) not in self.tasks:
                    raise ValueError(f"task '{t.key}' depends on unknown task '{self._dep_key(d)}'")
                indeg[t.key] += 1
        ready = [k for k in self.tasks if indeg[k] == 0]
        order = []
        while ready:
            k = ready.pop(0)
            order.append(k)
            for t in self.tasks.values():
                if k in [self._dep_key(d) for d in t.depends_on]:
                    indeg[t.key] -= 1
                    if indeg[t.key] == 0:
                        ready.append(t.key)
        if len(order) != len(self.tasks):
            raise ValueError("The task graph has a cycle — a job must be a DAG (Directed ACYCLIC Graph).")
        return order

    # ---------- dynamic value references ----------
    def _resolve(self, value, run: Run, task_key: str, item=None):
        if not isinstance(value, str):
            return value

        def repl(m):
            ref = m.group(1).strip()
            if ref == "input":
                return str(item)
            if ref == "task.name":
                return task_key
            if ref == "job.run_id":
                return str(run.run_id)
            if ref == "job.name":
                return self.name
            if ref == "job.start_time.day":
                return str(run.start.day)
            if ref.startswith("job.parameters."):
                return str(run.params[ref.split(".", 2)[2]])
            mt = re.fullmatch(r"tasks\.([\w-]+)\.values\.([\w-]+)", ref)
            if mt:
                return str(run.values.get(mt.group(1), {}).get(mt.group(2)))
            raise KeyError(f"Unknown dynamic value reference {{{{{ref}}}}}")

        full = re.fullmatch(r"\{\{(.+?)\}\}", value.strip())
        if full and full.group(1).strip().startswith("tasks.") and ".values." in full.group(1):
            mt = re.fullmatch(r"tasks\.([\w-]+)\.values\.([\w-]+)", full.group(1).strip())
            return run.values.get(mt.group(1), {}).get(mt.group(2))  # keep the real type (e.g. list)
        return re.sub(r"\{\{(.+?)\}\}", repl, value)

    # ---------- running ----------
    def _dep_state(self, d, run: Run):
        key = self._dep_key(d)
        tr = run.tasks[key]
        if isinstance(d, tuple) and tr.status == SUCCEEDED:
            return SUCCEEDED if tr.outcome == d[1] else EXCLUDED
        return tr.status

    def _should_run(self, t: Task, run: Run):
        if not t.depends_on:
            return True, ""
        states = [self._dep_state(d, run) for d in t.depends_on]
        if all(s == EXCLUDED for s in states):
            return None, "branch not taken"
        failed = [s in (FAILED, UPSTREAM_FAILED) for s in states]
        ok = [s == SUCCEEDED for s in states]
        rule = {
            "ALL_SUCCEEDED": all(ok),                    # an EXCLUDED dependency is NOT a success
            "AT_LEAST_ONE_SUCCEEDED": any(ok),
            "NONE_FAILED": not any(failed) and any(ok),  # "none failed and at least one ran"
            "ALL_DONE": True,
            "AT_LEAST_ONE_FAILED": any(failed),
            "ALL_FAILED": all(failed),
        }[t.run_if]
        if rule:
            return True, ""
        if not any(failed):
            return None, f"run_if {t.run_if} not met (a dependency was excluded)"
        return False, f"run_if {t.run_if} not met"

    def _params_for(self, t: Task, run: Run, item=None):
        merged = {**t.parameters, **run.params}  # job parameters override task parameters
        return {k: self._resolve(v, run, t.key, item) for k, v in merged.items()}

    def _call(self, t: Task, run: Run, item=None):
        ctx = Context(t.key, self._params_for(t, run, item), TaskValues(run.values, t.key), run.run_id, item)
        return t.fn(ctx)

    def _execute(self, t: Task, run: Run, tr: TaskRun):
        start = time.time()
        if t.kind == "condition":
            left, op, right = (self._resolve(x, run, t.key) for x in t.condition)
            try:
                l, r = float(left), float(right)
            except (TypeError, ValueError):
                l, r = str(left), str(right)
            tr.outcome = {"==": l == r, "!=": l != r, ">": l > r, ">=": l >= r, "<": l < r, "<=": l <= r}[op]
            tr.status, tr.attempts, tr.note = SUCCEEDED, 1, f"{left!r} {op} {right!r}"
            return
        for attempt in range(1, t.max_retries + 2):
            tr.attempts = attempt
            try:
                if t.kind == "for_each":
                    items = self._resolve(t.inputs, run, t.key)
                    if isinstance(items, str):
                        import json
                        items = json.loads(items)
                    with ThreadPoolExecutor(max_workers=max(1, t.concurrency)) as pool:
                        list(pool.map(lambda it: self._call(t, run, it), items))
                    tr.note = f"{len(items)} iterations, concurrency={t.concurrency}"
                else:
                    self._call(t, run)
                tr.status = SUCCEEDED
                break
            except Exception as e:  # noqa: BLE001 - we want to report any task error
                tr.status = FAILED
                tr.note = f"{type(e).__name__}: {e}"
                last_tb = traceback.format_exc(limit=2)
        tr.seconds = time.time() - start
        if tr.status == FAILED:
            print(f"   task '{t.key}' failed after {tr.attempts} attempt(s):\n{last_tb}")

    def run(self, parameters: Optional[dict] = None, _base: Optional[Run] = None, _rerun=None) -> Run:
        params = {**self.parameters, **(parameters or {})}
        run = Run(self, next(_run_ids), params, {}, {} if _base is None else dict(_base.values),
                  datetime.now(), _base.run_id if _base else None)
        for key in self._order():
            t = self.tasks[key]
            if _base is not None and key not in _rerun:
                run.tasks[key] = _base.tasks[key]
                continue
            tr = run.tasks[key] = TaskRun()
            go, why = self._should_run(t, run)
            if go is None:
                tr.status, tr.note = EXCLUDED, why
            elif not go:
                tr.status, tr.note = UPSTREAM_FAILED, why
            else:
                self._execute(t, run, tr)
        return run.show()

    def repair(self, run: Run, parameters: Optional[dict] = None) -> Run:
        """Repair run: re-run only tasks that did not succeed (and tasks downstream of them)."""
        bad = {k for k, tr in run.tasks.items() if tr.status in (FAILED, UPSTREAM_FAILED)}
        changed = True
        while changed:  # add downstream tasks of anything we re-run
            changed = False
            for t in self.tasks.values():
                if t.key not in bad and any(self._dep_key(d) in bad for d in t.depends_on):
                    bad.add(t.key)
                    changed = True
        if not bad:
            print("Nothing to repair — every task succeeded.")
            return run
        print(f"Repairing run {run.run_id}: re-running {sorted(bad)}; keeping the successful tasks.")
        return self.run({**run.params, **(parameters or {})}, _base=run, _rerun=bad)
