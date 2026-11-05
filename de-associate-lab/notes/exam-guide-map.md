# Official exam guide → where you learn it

Exam: Databricks Certified Data Engineer Associate · live **May 4, 2026** · guide updated **Aug 6, 2026**
(`source/exam-guide/exam-guide-august-2026.pdf`). 45 scored questions, 90 min.
Legend: 🟢 hands-on lab · 🟡 lesson/notes + quiz only (needs real Databricks) · Portal step IDs in `code`.

## §1 Databricks Intelligence Platform — 6% (~3 questions)
| Objective | Where |
|---|---|
| Core components: architecture, Delta Lake, Unity Catalog | 🟢 `1a` Delta basics · 🟡 notes/c1 §1, extra §3 · sample Q2 |
| Compute services: characteristics, limits, cost; pick per workload | 🟢 `7d` · 🟡 notes/c2 §1, extra §3 · sample Q4 |

## §2 Data Ingestion and Loading — 21% (~9–10)
| Objective | Where |
|---|---|
| Batch, streaming, incremental patterns; local files, standard & managed connectors | 🟢 `1b` `1c` `1d` · 🟡 notes/c1 §1, §8 · sample Q3 |
| COPY INTO from cloud storage into UC tables | 🟢 `1c` |
| Auto Loader with schema enforcement/evolution; **directory listing vs file notification** | 🟢 `1d` · 🟡 below ① |
| Configure Lakeflow Connect for enterprise sources | 🟡 notes/c1 §8 |
| **JDBC/ODBC or REST clients in notebooks**, scheduled with Jobs | 🟡 below ② |
| Choose Auto Loader vs Lakeflow Connect vs partner connectors vs others | 🟡 cheatsheet + notes/c1 §4, §8 |
| Semi-structured / nested data (JSON) | 🟢 `1g-1` `1g-2` |

## §3 Data Transformation and Modeling — 22% (~10)
| Objective | Where |
|---|---|
| Clean bronze → silver (nulls, types) | 🟢 `6a` `1f` |
| Joins: inner, left, broadcast, multiple keys, cross; union, union all | 🟢 `6b` `3c` |
| Add/drop/split/rename columns, filters, explode arrays | 🟢 `6a` `1g-2` `5c` |
| De-duplication; count, approx count distinct, mean, summary | 🟢 `6c` `5b` |
| Tuning: shuffle.partitions, default.parallelism, executor/driver memory, autoBroadcastJoinThreshold | 🟢 `6d` |
| Gold objects: materialized views, views, streaming tables, tables | 🟢 `3a` · 🟡 notes/c3 §1 |
| Data quality checks for silver/gold | 🟢 `3b` · 🟡 notes/c3 §3 |

## §4 Working with Lakeflow Jobs — 16% (~7)
| Objective | Where |
|---|---|
| Control flow: retries, branching (if/else), looping (for each) | 🟢 `2c` `2d` |
| Notebook, SQL, dashboard, pipeline tasks + DAG dependencies | 🟢 `2a` · 🟡 notes/c2 §1–2 |
| Schedules & triggers: scheduled, file arrival, table update | 🟡 notes/c2 §4 · sample Q10 |
| Time-based vs data-driven triggers | 🟡 notes/c2 §4 · sample Q10 |

## §5 Implementing CI/CD — 10% (~4–5)
| Objective | Where |
|---|---|
| Git folders: branches, commit/push, pull requests | 🟢 `8a` · 🟡 notes/c4 §6 |
| Bundle variables & overrides across dev/test/prod targets | 🟢 `8b` |
| Deploy bundles to package/promote jobs & pipelines | 🟢 `8b` `8c` · sample Q5 |
| Databricks CLI: validate, deploy, manage bundles in CI/CD | 🟢 `8c` · sample Q6 |

## §6 Troubleshooting, Monitoring, and Optimization — 10% (~4–5)
| Objective | Where |
|---|---|
| Job run history: compare durations with a baseline | 🟡 `7c` lesson · notes/c2 §6 |
| Jobs UI: statuses, task graph, upstream blockers, run times, failure rates | 🟢 `2d` (statuses) · 🟡 `7c` · sample Q9 |
| Spark UI: skew, shuffle, disk spill (stage metrics) | 🟢 `7a` · sample Q1 |
| Liquid clustering and predictive optimization | 🟢 `7b` `5a` |
| Cluster startup failures, library conflicts, out-of-memory | 🟢 `7c` |

## §7 Governance and Security — 15% (~7)
| Objective | Where |
|---|---|
| Managed vs external tables; create/modify/delete/**convert** | 🟢 `1b` (DROP demo) `9b` · sample Q8 |
| GRANT, REVOKE, DENY to users, groups, service principals | 🟢 `9a` · 🟡 notes/extra §1 |
| Column masking and row-level security by group | 🟢 `9c` · sample Q7 |
| Unity Catalog ABAC policies | 🟡 `9d` |

---
### ① Auto Loader file discovery modes (not in your course folder)
- **Directory listing** (default): Auto Loader lists the input folder to find new files. Simple, no extra setup.
- **File notification**: uses cloud events/queues (e.g. S3 events + SQS) so it does not list folders —
  better for **very large** directories with many files. Needs cloud permissions to set up.
- Schema: inferred and stored at `cloudFiles.schemaLocation`; new columns handled by
  `cloudFiles.schemaEvolutionMode` (default `addNewColumns`: the stream stops once, then restarts with the
  new column; `rescue` puts them in `_rescued_data`; `failOnNewColumns`; `none`).
  Schema **enforcement**: give a schema / `schemaHints` and bad values go to `_rescued_data`.

### ② JDBC/ODBC and REST ingestion from notebooks
- **JDBC** (read a database table): `spark.read.format("jdbc").option("url", …).option("dbtable", …)
  .option("user", …).option("password", dbutils.secrets.get(scope, key)).load()` → write to a UC table.
- **REST API**: call it with Python `requests` in a notebook, turn the JSON into a DataFrame, write to a
  volume or table. Schedule the notebook with a **Lakeflow Job**.
- Never hard-code passwords: use **secret scopes** (`dbutils.secrets.get`).
- Managed **Lakeflow Connect** connectors are preferred when one exists for the source.

### Sample Q3 fact: audit logs
Databricks delivers audit logs as **JSON**, typically within ~15 minutes, and a later delivery **can
overwrite** an existing file — ingestion must tolerate overwrites.
