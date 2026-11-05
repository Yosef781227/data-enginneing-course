# Section 1: Databricks Intelligence Platform — 6%

Understand the platform before choosing a tool.

Storage keeps data; compute processes it; the workspace helps you author and organize work; Unity Catalog governs objects. Learn the distinction before memorizing product names.

You should be able to draw the platform, explain Delta’s log, and choose compute for development, scheduled jobs and SQL analytics.


## What Databricks is

**Questions:** 3, 4, 9, 15, 29, 47, 54, 69, 74, 91, 93, 95, 140, 203, 241, 251

**Think of it like this:** A restaurant has an office that organizes work and a kitchen that prepares food. Databricks similarly separates management services from data-processing compute.

**What the question tests:** Identify which component stores data, manages a workspace, computes results or governs access. Architecture details depend on classic versus serverless deployment.

**Example:** An order file sits in cloud storage. Spark computes totals using compute resources. The workspace UI helps you write and schedule the code; the UI is not the worker executing a join.

**Common trap:** Delta Lake is a storage layer, not a replacement for every Databricks service. Do not apply a classic-plane statement to every serverless design.

**Try the lab:** lab1_ingestion / 1a (some platform features are simulated)

**Explain without looking:** Is a notebook editor the same thing as the compute that runs its code?

**Self-check:** No. Authoring and executing are separate responsibilities.


## Choose the right compute

**Questions:** 49, 77, 92, 148, 157, 162, 166, 167, 173, 180, 191, 192, 193, 201, 207, 220, 259, 272, 275

**Think of it like this:** Choose a vehicle for the trip: a bicycle for a short errand, a bus for many passengers. Bigger is not automatically better.

**What the question tests:** Choose for the actual workload: interactive development, scheduled ETL, or concurrent SQL analytics. Also consider startup delay, compatibility and operational overhead.

**Example:** While debugging a notebook you need quick iteration. A nightly automated task has a different lifecycle. Many analysts sending SQL queries need a suitable SQL warehouse. Serverless reduces infrastructure management when the workload and region support it.

**Common trap:** ‘Cheapest’ does not mean ‘smallest’ in every case. Startup time, concurrency, runtime and feature support matter. Legacy cluster names are not universal current recommendations.

**Try the lab:** lab7_troubleshooting / 7d (some platform features are simulated)

**Explain without looking:** What two things would you check before recommending serverless?

**Self-check:** Workload/feature compatibility and availability/security requirements; then compare its cost and operating model.


## Notebooks and languages

**Questions:** 56, 147

**Think of it like this:** A notebook is a workbook with separate pages, called cells. Each cell can hold an explanation or code.

**What the question tests:** Distinguish the notebook’s default language from the language of one cell. Keep Python logic and SQL syntax in their proper execution context.

**Example:** A Python notebook can contain a `%sql` cell. Python variables do not automatically become SQL column names. `spark.sql(...)` runs SQL from Python and returns a DataFrame.

**Common trap:** Putting Python and SQL together as raw text does not make one valid program. Parameter passing and language switching require explicit supported mechanisms.

**Try the lab:** lab7_troubleshooting / 7d (some platform features are simulated)

**Explain without looking:** Does changing one cell to SQL require rewriting every Python cell?

**Self-check:** No. A cell-level language marker can select SQL for that cell.


## Sources

Local curriculum: ../../curriculum.md; official objective map: ../exam-guide-map.md

Current exam outline: https://www.databricks.com/learn/certification/data-engineer-associate

Post-May 2026 guide: https://www.databricks.com/sites/default/files/2026-05/databricks-certified-data-engineer-associate-exam-guide-may-2026.pdf

These learning explanations do not independently certify the third-party answer key.
