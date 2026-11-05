# Course 2 — Deploy Workloads with Lakeflow Jobs (study notes)

Source: `source/text/slides/c2-jobs.txt` + notebooks in `source/text/notebooks/c2-jobs/`.
Lakeflow Jobs was previously called **Databricks Workflows**.

---
## §1 Jobs, tasks, compute  (slides 12–30)
- **Job** = the main resource for scheduling, coordinating and running work (ETL, analytics, ML).
- **Task** = one unit of work inside a job. A job has one or more tasks.
- **Task types**: Notebook, Python script, Python wheel, JAR, Spark Submit, SQL (query / file /
  alert), **Pipeline** (SDP), **Dashboard**, Power BI, dbt, **Run Job**, **If/else condition**, **For each**.
- Languages: Python, SQL, Scala, Java (JAR).
- Each task can use its own compute, or tasks can share compute.

**Compute choice (slides 28, 87–88)**
| Compute | Use for | Notes |
|---|---|---|
| All-purpose (interactive) cluster | development, ad-hoc analysis | shared by users; **not cost-efficient for production** |
| Job cluster | production jobs | ~50% cheaper; created for the job and **terminates when it ends**; start-up delay |
| Serverless (jobs) | production, simplest | fast start, Photon on, no VM choice, single DBU bill |
| SQL warehouse | SQL tasks, dashboards | serverless by default |

**Serverless performance mode** (slide 29): *Performance optimized* = fast start, time-sensitive.
*Standard* = cheaper, ~4–6 min start-up.

⚠ **Exam trap:** "cheapest reliable option for a scheduled production job" → job cluster or serverless, never all-purpose.

---
## §2 DAG & orchestration patterns  (slides 31–38)
- A job is a **DAG** (Directed Acyclic Graph): tasks = vertices, dependencies = edges, no cycles.
- Set order with **Depends on**. Tasks without dependency between them run **in parallel**.
- Create jobs with the UI, REST API, CLI, SDK or bundles (DABs).
- Patterns: **Sequence** (bronze→silver→gold), **Funnel** (many sources → one task),
  **Fan-out** (one source → many tasks).

---
## §3 Parameters, task values, notifications, retries  (slides 42–52; notebook 3)
- **Task parameters**: key-value at task level. **Job parameters**: key-value at job level, pushed
  to all tasks. **Job parameters override task parameters with the same key.** They can be
  overridden at run time ("Run now with different settings").
- Read in a notebook: `dbutils.widgets.get("catalog_name")`.
- **Task values** = share data between tasks at run time:
  ```python
  dbutils.jobs.taskValues.set(key="row_count", value=42)                    # upstream task
  dbutils.jobs.taskValues.get(taskKey="ingest", key="row_count", default=0)  # downstream task
  ```
- **Dynamic value references** use `{{ }}`: `{{job.id}}`, `{{job.start_time.day}}`,
  `{{task.name}}`, `{{job.trigger.type}}`, `{{tasks.<task_name>.values.<key>}}`.
- **Notifications** on start / success / failure / duration warning / streaming backlog.
  Destinations: email, Slack, Teams, PagerDuty, webhook. Job-level and task-level.
- **Retry policy**: per task, max retries + wait between attempts (e.g. 3 retries = 4 attempts).

---
## §4 Triggers  (slides 53–61)
| Trigger | Starts the job when… |
|---|---|
| Scheduled | at a time/interval; simple UI or **cron** (Quartz) syntax, with time zone |
| File arrival | new files appear in a UC **volume** or external location (S3/ADLS/GCS) |
| Table update | 1–10 UC tables are updated (any table / all tables) |
| Continuous | always on: new run starts as soon as the last finishes/fails (streaming) |
| Manual (None) | someone clicks Run now, or API / CLI / SDK / DABs |
Advanced options: *minimum time between triggers*, *wait after last change*. A trigger can be **Paused**.

---
## §5 Conditional and iterative tasks  (slides 65–76; notebooks 4, 5)
**Run if dependencies** — run a task based on upstream status:
`All succeeded` (default) · `At least one succeeded` · `None failed` · `All done` ·
`At least one failed` · `All failed`.
Example: Task-4 depends on Task-2 and Task-3 with *At least one succeeded* → runs even if Task-3 fails.

**If/else condition task** — boolean branch: compare two values with `==, !=, >, >=, <, <=`.
Usually compares a task value: `{{tasks.checking_for_duplicates.values.has_duplicates}} == "true"`.
Downstream tasks attach to the **True** or **False** branch.

**For each task** — loops over an input array (e.g. `["CA","NY","VA"]`) and runs one nested task
per item; the item is `{{input}}`. Iterations can run **in parallel** (concurrency setting).
Downstream tasks depend on the For each container, not the nested task.

---
## §6 Failures, repair, monitoring  (slides 77–84; notebook 6)
- **Repair run**: re-run **only the failed tasks** (and their dependents) of a run; you may change
  parameters. Saves time and cost — successful tasks are not re-run.
- **System tables** `system.lakeflow` (read-only): `jobs`, `job_tasks`, `job_run_timeline`,
  `job_task_run_timeline`, `pipelines`. Timeline tables slice long runs hourly
  (`period_start_time`, `period_end_time`).
- **Spark UI / query profile**: find slow steps, bytes read/written.

---
## §7 Production best practices  (slides 85–101; notebook 7)
- **Modular orchestration**: break a large job into a parent job that calls child jobs with the
  **Run Job** task.
- **Git source for tasks**: run notebooks from a Git branch/tag/commit → single source of truth,
  no accidental edits in prod.
- Use **service principals** to own jobs and access data.
- Job/serverless compute, Photon, reuse clusters across tasks, parameterize tasks, alerts on
  failure, max 1000 tasks per job, use Repair to avoid re-processing.
