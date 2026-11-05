# Curriculum — lesson map

Each lesson ID links the course slides, the original course notebook, the study notes and a local lab.
- **Slides** → `source/text/slides/<file>.txt` (search `=== Slide N ===`)
- **Notebook** → `source/text/notebooks/<course>/…` (original: `../Data enginner/…`)
- **Notes** → section in `notes/<file>.md`
- **Local lab** → `notebooks/<file>.ipynb` exercise IDs (run with `/lab`)
- **Where**: 🖥 = works on this Mac · ☁ = needs Databricks (Free Edition)

Topic tags for progress tracking are shown in `[brackets]`.

## Course 1 — Data Ingestion with Lakeflow Connect  (`c1-ingestion`)
| ID | Lesson | Slides | Course notebook | Notes | Local lab | Where |
|----|--------|--------|-----------------|-------|-----------|-------|
| 1.1 | Lakeflow overview, Delta Lake, medallion architecture `[platform][delta]` | 8–26 | 01 - Exploring the Lab Environment | notes/c1-ingestion.md §1 | lab1: `1a` | 🖥 + ☁ (UC) |
| 1.2 | Batch ingestion: CTAS + `read_files()`, managed vs external tables `[ingestion]` | 29–32, 39 | 02A - Data Ingestion with CTAS and COPY INTO | §2 | lab1: `1b` | 🖥 (simulated) |
| 1.3 | Incremental batch: `COPY INTO` (idempotent, `mergeSchema`) `[ingestion]` | 33–35, 39 | 02A | §3 | lab1: `1c` | 🖥 (simulated) + ☁ |
| 1.4 | Auto Loader & streaming tables (`STREAM read_files`, `cloudFiles`) `[ingestion][streaming]` | 36–40 | 02B, Appendix A2 | §4 | lab1: `1d` | 🖥 (Structured Streaming) + ☁ |
| 1.5 | Metadata columns on ingest (`_metadata.file_name`, `current_timestamp()`) `[ingestion]` | 41–44 | 03 - Adding Metadata Columns | §5 | lab1: `1e` | 🖥 |
| 1.6 | Rescued data column `_rescued_data`, explicit schemas `[ingestion]` | 45–49 | 04, 05L (lab) | §6 | lab1: `1f` | 🖥 |
| 1.7 | Semi-structured JSON: STRING `:` syntax, STRUCT (`from_json`, `schema_of_json`), VARIANT, `explode` `[transform]` | 50–67 | 06, 07L (lab) | §7 | lab1: `1g` | 🖥 (partly) |
| 1.8 | Enterprise ingestion: managed connectors, Partner Connect, Federation, Delta Sharing, Marketplace `[platform][governance]` | 68–84 | 08 | §8 | — | ☁ (concepts) |
| 1.9 | `MERGE INTO`, schema evolution, `DESCRIBE HISTORY`, time travel `[delta]` | 85–94 | 09 - BONUS MERGE INTO | §9 | lab1: `1h` | 🖥 |

## Course 2 — Deploy Workloads with Lakeflow Jobs  (`c2-jobs`)
| ID | Lesson | Slides | Course notebook | Notes | Local lab | Where |
|----|--------|--------|-----------------|-------|-----------|-------|
| 2.1 | Jobs, tasks, task types, compute choice (all-purpose vs job vs serverless) `[jobs][platform]` | 12–30 | 1 Demo, 2 Lab | notes/c2-jobs.md §1 | lab2: `2a` | ☁ |
| 2.2 | DAGs & dependency patterns (sequence, funnel, fan-out) `[jobs]` | 31–38 | 1 Demo, 2 Lab | §2 | lab2: `2a` | 🖥 (simulated) + ☁ |
| 2.3 | Parameters, task values, dynamic value refs `{{ }}`, notifications, retries `[jobs]` | 42–52 | 3 Demo | §3 | lab2: `2b` | 🖥 (simulated) + ☁ |
| 2.4 | Triggers: scheduled (cron), file arrival, table update, continuous, manual `[jobs]` | 53–61 | 3 Demo | §4 | — | ☁ |
| 2.5 | Run-if dependencies, If/else task, For each task `[jobs]` | 65–76 | 4 Demo, 5 Lab | §5 | lab2: `2c` | 🖥 (simulated) + ☁ |
| 2.6 | Repair runs, monitoring, `system.lakeflow` tables, Spark UI `[jobs]` | 77–84 | 6 Demo | §6 | lab2: `2d` | 🖥 (simulated) + ☁ |
| 2.7 | Production best practices: modular orchestration (Run Job task), Git source, service principals `[jobs][devops]` | 85–101 | 7 BONUS LAB | §7 | — | ☁ |

## Course 3 — Lakeflow Spark Declarative Pipelines (SDP, formerly DLT)  (`c3-pipelines`)
| ID | Lesson | Slides | Course notebook | Notes | Local lab | Where |
|----|--------|--------|-----------------|-------|-----------|-------|
| 3.1 | Why SDP; streaming tables vs materialized views vs (temporary) views; old DLT syntax `[sdp]` | 12–41 | 1 Demo | notes/c3-pipelines.md §1 | lab3: `3a` | 🖥 (simulated) + ☁ |
| 3.2 | Pipeline editor & settings: compute, code assets, default catalog/schema, configuration `${key}` `[sdp]` | 42–52 | 2 Demo | §2 | — | ☁ |
| 3.3 | Data quality expectations: WARN / DROP ROW / FAIL UPDATE `[sdp][governance]` | 53–58 | 3 Demo, 4 Lab | §3 | lab3: `3b` | 🖥 (simulated) + ☁ |
| 3.4 | Streaming joins, triggered vs continuous, full refresh, event log `[sdp][streaming]` | 62–78 | 5 Demo | §4 | lab3: `3c` | 🖥 (partly) + ☁ |
| 3.5 | Change Data Capture: `AUTO CDC INTO` (formerly `APPLY CHANGES INTO`), SCD Type 1 vs 2 `[sdp][delta]` | 79–88 | (6 Demo — not in folder) | §5 | lab3: `3d` | 🖥 (with MERGE) + ☁ |

## Course 4 — DevOps Essentials for Data Engineering  (`c4-devops`)
| ID | Lesson | Slides | Course notebook | Notes | Local lab | Where |
|----|--------|--------|-----------------|-------|-----------|-------|
| 4.1 | Software-engineering best practices; modularizing PySpark code `[devops]` | 6–26 | M02 2.1, 2.2L | notes/c4-devops.md §1 | lab4: `4a` | 🖥 |
| 4.2 | DevOps, DataOps, MLOps; CI vs Continuous Delivery vs Continuous Deployment `[devops]` | 27–45 | — | §2 | — | concepts |
| 4.3 | Planning a project; dev/stage/prod isolation (workspaces vs catalogs) `[devops][governance]` | 46–60 | M02 2.3 | §3 | — | concepts |
| 4.4 | Unit tests: `pytest`, `assertDataFrameEqual`, `assertSchemaEqual` `[devops]` | 61–68 | M02 2.4, 2.5L | §4 | lab4: `4b`, `4c` | 🖥 |
| 4.5 | Integration tests with SDP expectations or Jobs tasks `[devops][sdp]` | 69–73 | M02 2.6 | §5 | — | ☁ |
| 4.6 | Version control: Git folders, branches, PAT, pull requests `[devops]` | 74–84 | M02 2.7L | §6 | — | ☁ + GitHub |
| 4.7 | CD: REST API vs CLI vs SDK; Declarative Automation Bundles (DABs) `[devops]` | 85–96 | M03 3.1 | §7 | — | ☁ |

## Extra — Exam topics not fully covered by these 4 courses  (beyond course material)
| ID | Lesson | Notes | Local lab | Where |
|----|--------|-------|-----------|-------|
| 5.1 | Unity Catalog: metastore → catalog → schema → table/view/volume/function; GRANT/REVOKE; managed vs external; lineage `[governance]` | notes/extra-exam-topics.md §1 | — | ☁ |
| 5.2 | Delta maintenance: OPTIMIZE, Z-ORDER, liquid clustering, VACUUM, RESTORE, table properties `[delta]` | §2 | lab5: `5a` | 🖥 |
| 5.3 | Compute & platform: all-purpose / job clusters, SQL warehouses, serverless, Photon, DBR `[platform]` | §3 | — | concepts |
| 5.4 | Spark SQL & PySpark transformations: joins, window functions, CTEs, higher-order functions, PIVOT, UDFs `[transform][spark]` | §4 | lab5: `5b`, `5c` | 🖥 |
| 5.5 | Structured Streaming basics: triggers, output modes, checkpoints, watermarks `[streaming]` | §5 | lab5: `5d` | 🖥 |


## Exam-guide labs (added for the official May 2026 exam)  — see `notes/exam-guide-map.md`
| ID | Lesson | Exam § | Portal steps | Where |
|----|--------|--------|--------------|-------|
| 6.1 | Clean bronze → silver: nulls, types, split/rename/drop `[transform]` | §3 | `6a` | 🖥 |
| 6.2 | Joins (inner, left, multi-key, broadcast, cross) and unions `[transform]` | §3 | `6b` | 🖥 |
| 6.3 | De-duplication and aggregations (approx_count_distinct, summary) `[transform]` | §3 | `6c` | 🖥 |
| 6.4 | Spark tuning parameters `[transform][troubleshooting]` | §3 | `6d` | 🖥 |
| 7.1 | Data skew in the Spark UI + salting `[troubleshooting]` | §6 | `7a` | 🖥 |
| 7.2 | Liquid clustering & predictive optimization `[troubleshooting][delta]` | §6 | `7b` | 🖥 |
| 7.3 | Diagnose failures: OOM, library conflicts, cluster start, timeouts; job monitoring `[troubleshooting]` | §6 | `7c` | 🖥 (quiz) |
| 7.4 | Choose compute `[platform]` | §1 | `7d` | 🖥 (quiz) |
| 8.1 | Git folders workflow `[cicd]` | §5 | `8a` | 🖥 (quiz) + ☁ |
| 8.2 | Bundles: variables, targets, overrides `[cicd]` | §5 | `8b` | 🖥 |
| 8.3 | Secrets (BUNDLE_VAR_) + CLI validate/deploy/run `[cicd]` | §5 | `8c` | 🖥 |
| 9.1 | GRANT / REVOKE / DENY `[governance]` | §7 | `9a` | 🖥 (SQL check) + ☁ |
| 9.2 | Managed vs external, SET/UNSET MANAGED `[governance]` | §7 | `9b` | 🖥 (SQL check) + ☁ |
| 9.3 | Column masks and row filters `[governance]` | §7 | `9c` | 🖥 (simulated) |
| 9.4 | ABAC policies `[governance]` | §7 | `9d` | 🟡 quiz |

## Suggested study order (by exam weight)
§3 Transform 22% → §2 Ingestion 21% → §4 Jobs 16% → §7 Governance 15% → §5 CI/CD 10% → §6 Troubleshooting 10% → §1 Platform 6%
Portal order: Lab 1 → Lab 6 → Lab 3 → Lab 5 → Lab 2 → Lab 9 → Lab 8 → Lab 7 (Lab 4 = optional testing practice).
Then: `/exam` mock exams until you score ≥ 80% twice.
