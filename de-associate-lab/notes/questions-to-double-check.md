# Practice questions to double-check

These 24 questions have an answer key that looks wrong, conflicts with a twin question, or depends on a
fact that changes over time. The portal shows the same warning after you answer each one.

| Q | Section | Topic | Bank answer | Warning |
|---|---|---|---|---|
| 11 | §7 | Who can use which data? | C | In Unity Catalog the precise answer is a **metastore admin** (or the owner of the parent catalog/schema). In older questions 'workspace administrator' is the expected answer. |
| 26 | §3 | Bronze, silver and gold | D | **Doubtful answer.** Declarative pipelines fully support streaming sources, and one pipeline can mix SQL and Python. Q65 (same scenario) gives the better answer: **different SQL and Python sources are allowed**. Learn that idea. |
| 35 | §5 | Version control and collaboration | C | Git folders have gained more features over time (some merge support now exists). For the exam: **merge / pull request → Git provider**. |
| 37 | §4 | Tasks, dependencies and repair runs | C | **Answer key conflict.** Q128 is the same question and says **B**. B is the correct idea: create the new task and make it a **dependency of the original task** (the original 'depends on' the new one). Option C reverses the order. |
| 63 | §3 | Declarative pipelines and quality rules | B | In real SQL you'd write `location IS NOT NULL` (`!= NULL` is never true). The exam focuses on **ON VIOLATION FAIL UPDATE**. |
| 75 | §3 | Read SQL and Python step by step | A | The table values in this question are garbled in the PDF. Learn the rule, not the numbers: **count(*) = all rows · count(col) = non-NULL only · count_if = rows where true**. |
| 98 | §3 | Delta tables and table history | D | Careful: Delta = **Parquet data files + a JSON transaction log**. If an exam option says 'Delta', pick it; if only Parquet is offered, Parquet is the right idea. |
| 99 | §3 | Read SQL and Python step by step | B | **Doubtful answer.** `WITH COLUMNS` is not valid Databricks SQL. The correct syntax is **A**: `CREATE OR REPLACE TABLE t (employeeId STRING, startDate DATE, avgRating FLOAT)` — Delta is the default format. |
| 106 | §7 | Managed and external data | B | Legacy Hive metastore fact. In Unity Catalog, managed storage locations replace this. |
| 109 | §2 | Load files and database rows | D | Q58 asks the same thing and the bank says **C (well-defined schema)**. The usual Databricks answer is **C**. If you see this question, prefer **C**. |
| 118 | §3 | Streaming reads, writes and progress | D | **Doubtful answer.** Spark's docs say offsets are recorded with **checkpointing and write-ahead logs** — that's **A**, the commonly accepted answer for this question. |
| 124 | §3 | Bronze, silver and gold | D | Not strictly 'always true' — silver can also gain rows from joins. Remember the safe rule from Q81: **Silver = cleaner, more refined than Bronze**. |
| 153 | §4 | Tasks, dependencies and repair runs | C | A pure memory fact. Limits can change — check the Jobs docs before your exam. |
| 157 | §1 | Choose the right compute | B | Today Databricks also recommends **serverless jobs** for small production jobs; the exam answer here is still B. |
| 160 | §3 | Declarative pipelines and quality rules | C | Both **A** and **C** remove the NULL rows. The bank's answer is C (a simple WHERE filter). If the question mentions tracking/monitoring quality, choose the **expectation (A)**. |
| 162 | §1 | Choose the right compute | B | Same scenario as Q201. Serverless can reach private networks with network connectivity configs today; the bank expects **Pro**. |
| 175 | §4 | Tasks, dependencies and repair runs | B | **Answer key conflict:** Q206 (same scenario) says **repair the task**. With one task, both work. For multi-task jobs, the exam always wants **Repair run**. |
| 180 | §1 | Choose the right compute | A, B | Serverless language support grows over time — check the docs close to your exam date. |
| 181 | §6 | Find the cause before changing settings | A, B | Remember the general rule: OOM after `collect()`/`toPandas()` → **driver**; OOM during big joins/shuffles → **executors / shuffle partitions**. |
| 194 | §7 | Sharing, federation and lineage | C | Delta Sharing is **always read-only** for recipients. Internal teams normally don't use a share at all — they get Unity Catalog grants. |
| 196 | §7 | Sharing, federation and lineage | C | Debatable: Databricks also documents **Cloudflare R2** (no egress fees) to reduce cross-cloud sharing costs. Remember both ideas. |
| 201 | §1 | Choose the right compute | C | See Q162 — the bank's expected answer is Pro. |
| 206 | §4 | Tasks, dependencies and repair runs | A | See Q175 — the two keys disagree. Remember: **failed task → Repair run**. |
| 230 | §7 | Protect sensitive rows and columns | A | The option layout in the PDF is garbled. Remember the correct **order**: create the function first, then `ALTER TABLE … SET ROW FILTER fn ON (column)`. |
