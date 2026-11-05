# Practising on real Databricks (Free Edition)

The local labs cover Spark, Delta and the *ideas* of Jobs and pipelines. Some exam topics only exist
on the real platform: Unity Catalog, volumes, `read_files()`, Auto Loader (`cloudFiles`), `COPY INTO`,
streaming tables, materialized views, the Lakeflow Pipelines Editor, the Jobs UI, triggers, system
tables, Git folders. Use **Databricks Free Edition** for those.

## 1. Create a workspace
1. Go to the Databricks Free Edition sign-up page (search "Databricks Free Edition").
2. Sign up with a **personal** email. You get a serverless workspace (no credit card).
3. Free Edition is **serverless only** and has usage limits. Classic clusters are not available, so
   ignore the course's "SELECT CLASSIC COMPUTE" cells and pick **Serverless** instead.

## 2. Import the course notebooks
Your course archives (read-only on this Mac):
| Course | File to import |
|---|---|
| 1 Ingestion | `../Data enginner/1 Data Ingestion with lake flow connect/Data Ingestion with LakeFlow Connect.zip` |
| 2 Jobs | `../Data enginner/2 Deploy workloads with lake flow job/Deploy Workloads with Lakeflow Jobs.zip` |
| 3 Pipelines | folder `../Data enginner/3 Build-Data-Pipelines-…/Build Data Pipelines with …/` (import the `.py`/`.sql` files) |
| 4 DevOps | `../Data enginner/4 DevOps-Essentials-for-Data-Engineering/devops-essentials-for-data-engineering-en_us-2.1.2.zip` |

In the workspace: **Workspace → (your user folder) → ⋮ → Import → File** → choose the `.zip` (or file).

## 3. What to expect
- The course notebooks were written for the **Vocareum lab** (catalog `dbacademy`, shared datasets like
  `dbacademy_ecommerce`). The `Classroom-Setup` cells may fail outside Vocareum. Course 3 says it
  supports Free Edition "as is" (it creates its own catalog if you have permission).
- When setup fails, use the **concepts and SQL** from the notebook with your own data:
  ```sql
  CREATE CATALOG IF NOT EXISTS study;          -- or use the default 'workspace' catalog
  CREATE SCHEMA IF NOT EXISTS study.lab;
  CREATE VOLUME IF NOT EXISTS study.lab.raw;
  ```
  Then upload files from this lab's `data/raw/` folder to the volume
  (**Catalog → study → lab → raw → Upload to this volume**) and run the course queries against
  `/Volumes/study/lab/raw/...`.

## 4. Suggested hands-on list (map to lessons)
| Lesson | Try on Databricks |
|---|---|
| 1.2–1.3 | `read_files()` + CTAS; `CREATE TABLE t; COPY INTO t …` twice — see 0 rows the 2nd time |
| 1.4 | `CREATE OR REFRESH STREAMING TABLE … FROM STREAM read_files(...)`; upload a new file; `REFRESH STREAMING TABLE` |
| 1.6–1.7 | `rescueddatacolumn`, colon syntax `col:field`, `parse_json` / VARIANT |
| 2.1–2.6 | Build the course job in **Jobs & Pipelines → Create → Job**: notebook + SQL tasks, If/else, For each, file-arrival trigger, repair run, query `system.lakeflow.jobs` |
| 3.1–3.5 | **Create → ETL pipeline**: bronze/silver streaming tables, gold MV, expectations, dry run, pipeline graph, event log, `AUTO CDC INTO` |
| 4.6 | **Workspace → Create → Git folder** with a personal GitHub repo |
| 5.1 | `GRANT` / `SHOW GRANTS` on your own catalog |

Tell Claude what you did (`/explain` anything that surprised you) so it can log your progress.
