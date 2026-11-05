# Section 6: Troubleshooting, Monitoring, and Optimization — 10%

Use evidence to make work reliable and fast.

Compare today’s run with a baseline. Separate startup delays, task dependencies, skew, shuffle, spills and memory failures. Then choose a targeted change and measure again.

You should identify a likely bottleneck from a symptom and explain the difference between compaction, layout and old-file cleanup.


## Find the cause before changing settings

**Questions:** 43, 82, 87, 127, 130, 131, 139, 164, 177, 178, 181, 185, 186, 224, 237, 243, 268, 269

**Think of it like this:** A mechanic checks the symptom before replacing the engine.

**What the question tests:** Locate the delay or failure: startup, one Spark stage, most tasks, driver memory, worker memory, library compatibility or an upstream dependency.

**Example:** If almost every task finishes quickly but one is much slower and reads far more data, investigate skew. If a large toPandas call exhausts memory, remember that collecting data can overload the driver. Compare run times against a baseline before changing settings.

**Common trap:** More machines do not automatically fix one oversized partition. High concurrency, cold startup and slow computation are different problems. A debugger inspects variables; the Spark UI inspects distributed execution.

**Try the lab:** lab7_troubleshooting / 7a (some platform features are simulated)

**Explain without looking:** Why compare median and maximum task sizes rather than only total runtime?

**Self-check:** A large difference can reveal uneven work that the total hides.


## File layout and automated maintenance

**Questions:** 51, 101, 155, 170, 187, 188, 233

**Think of it like this:** A store can reorganize shelves, combine small boxes or discard obsolete stock; these are different actions.

**What the question tests:** Separate file compaction, data layout, managed maintenance and deletion of old data files.

**Example:** OPTIMIZE can compact small files; layout features influence how data is organized for access. VACUUM removes eligible old files. Predictive optimization can manage supported maintenance for eligible managed tables.

**Common trap:** Compaction is not deleting logical rows. VACUUM is not the command for compacting small files. Aggressive old-file deletion can affect time travel and readers that still need those files.

**Try the lab:** lab7_troubleshooting / 7b (some platform features are simulated)

**Explain without looking:** What should you check before assuming old versions remain queryable after maintenance?

**Self-check:** Whether required historical metadata and data files are still retained.


## Sources

Local curriculum: ../../curriculum.md; official objective map: ../exam-guide-map.md

Current exam outline: https://www.databricks.com/learn/certification/data-engineer-associate

Post-May 2026 guide: https://www.databricks.com/sites/default/files/2026-05/databricks-certified-data-engineer-associate-exam-guide-may-2026.pdf

These learning explanations do not independently certify the third-party answer key.
