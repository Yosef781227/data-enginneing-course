---
description: Timed mock exam (default 45 questions, 90 minutes)
argument-hint: [number of questions]  (default 45)
---
Run a mock exam with **$ARGUMENTS** questions (default 45). Time limit = 2 minutes per question.

- Record the start time (`date`) in `progress/progress.json` under `exams`.
- Spread questions exactly like the OFFICIAL exam guide (45 questions → round per section):
  §1 Platform 6% (3) · §2 Ingestion & Loading 21% (9) · §3 Transformation & Modeling 22% (10) ·
  §4 Lakeflow Jobs 16% (7) · §5 CI/CD 10% (5) · §6 Troubleshooting/Monitoring/Optimization 10% (4) ·
  §7 Governance & Security 15% (7). Scale down proportionally for shorter exams.
- Base each question on an objective in `notes/exam-guide-map.md`; include some of the 10 official
  sample questions in `quiz-bank/official-samples.md` (rephrased).
- Ask ONE question at a time, 4 options. Do NOT give feedback during the exam — just say
  "Recorded. Question N/M" and ask the next one.
- At the end (or if the learner types `stop`), show: score %, pass/fail vs 70%, time used,
  score per official section (§1–§7), then review EVERY wrong answer with explanation and source.
- Save the result to `exams` and each answer to `answers`; update `weak_topics`.
