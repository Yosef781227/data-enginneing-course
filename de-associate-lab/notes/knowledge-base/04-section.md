# Section 4: Working with Lakeflow Jobs — 16%

Run tasks in the right order at the right time.

A task performs work. A job coordinates tasks. Arrows describe dependencies; triggers start runs. Retries and repairs handle failure differently.

You should draw a task graph, explain a conditional branch, select a trigger and recover a failed run without unnecessary repetition.


## Tasks, dependencies and repair runs

**Questions:** 37, 41, 60, 84, 128, 129, 135, 153, 172, 175, 206, 218, 223, 239, 252, 253, 261, 264, 276

**Think of it like this:** A job is a checklist with arrows: unpack deliveries before cooking; independent preparation tasks can run together.

**What the question tests:** Interpret task dependencies, run-if conditions, parameters, concurrency, retries and repair semantics.

**Example:** A and B can run in parallel if neither depends on the other. C can wait for both. Task values pass a result such as record_count to a later conditional task. A repair can rerun failed work and affected downstream tasks without repeating every successful task.

**Common trap:** A retry is not a full new job run. A skipped or excluded branch does not mean every downstream run-if rule will pass. Notifications belong to job configuration; mentioning an owner does not make the question about table permissions.

**Try the lab:** lab2_jobs / 2c (some platform features are simulated)

**Explain without looking:** Tasks 1 and 2 succeeded, task 3 failed. Why consider repair rather than Run now?

**Self-check:** To reuse the successful work and complete the failed/dependent tasks, where repair is supported.


## When should the job start?

**Questions:** 27, 38, 40, 55, 86, 88, 90, 235, 246, 274

**Think of it like this:** An alarm clock starts work at a time; a doorbell starts work because something arrived.

**What the question tests:** Choose a schedule, file-arrival event or table-update event based on what makes the next run meaningful.

**Example:** A nightly deadline suits a time schedule. New cloud files may suit a file-arrival trigger. A silver job that should follow changes to an upstream Unity Catalog table may suit a table-update trigger.

**Common trap:** A file-arrival trigger is not a table-update trigger. A polling interval alone does not guarantee end-to-end latency: include processing time, queues and source delays.

**Try the lab:** lab2_jobs / 2b (some platform features are simulated)

**Explain without looking:** What is the key question before choosing a trigger?

**Self-check:** Should the job start because a time has arrived, or because the relevant data has changed?


## Sources

Local curriculum: ../../curriculum.md; official objective map: ../exam-guide-map.md

Current exam outline: https://www.databricks.com/learn/certification/data-engineer-associate

Post-May 2026 guide: https://www.databricks.com/sites/default/files/2026-05/databricks-certified-data-engineer-associate-exam-guide-may-2026.pdf

These learning explanations do not independently certify the third-party answer key.
