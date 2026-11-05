# Official sample questions (exam guide, Aug 2026) — answer key at the bottom

Source: `source/exam-guide/exam-guide-august-2026.txt`, pages 6–11. Tutor: use them in `/exam` and `/quiz`
(rephrase sometimes). Never show the answer before the learner answers.

| # | Section | Objective (short) | Portal step |
|---|---|---|---|
| 1 | §6 | Spark UI: skew / shuffle / spill | 7a |
| 2 | §1 | Platform core: Delta Lake + Unity Catalog | 1a, 7d |
| 3 | §2 | Ingestion patterns (audit log delivery) | notes/exam-guide-map.md |
| 4 | §1 | Choose compute | 7d |
| 5 | §5 | Deploy with bundles | 8b |
| 6 | §5 | CLI + secrets (BUNDLE_VAR_) | 8c |
| 7 | §7 | Column masking | 9c |
| 8 | §7 | Managed ↔ external (UNSET MANAGED) | 9b |
| 9 | §6 | Job statuses (Timed Out) | 7c |
| 10 | §4 | Trigger types (file arrival) | 2c lesson, notes/c2 §4 |

Full question text: see the exam guide file above (pages 6–10).

---
Answer key: 1 D (salt the key; AQE skew handling is for joins) · 2 B (Delta ACID + time travel, governed by
UC) · 3 A (JSON, ~15 min, can overwrite) · 4 C (serverless SQL warehouse) · 5 D (bundles in Git + CI/CD) ·
6 A (BUNDLE_VAR_ env var) · 7 C (mask with is_account_group_member) · 8 A (UNSET MANAGED) ·
9 B (task duration/timeout threshold) · 10 B (file arrival trigger)
