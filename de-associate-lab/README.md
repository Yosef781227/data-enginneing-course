# Databricks Data Engineer Associate — Interactive Study Lab

A study lab you use **with Claude Code in the terminal**. Claude is your tutor: it teaches each lesson
from your own course material, quizzes you, runs hands-on labs on your Mac, and tracks your progress.

## Start studying
```bash
cd ~/joc_project/de-associate-lab
claude
```
Then type **`/start`**.

| Command | What it does |
|---|---|
| `/start` | Where am I? What next? (first time: asks your exam date) |
| `/lesson 1.4` | Interactive lesson, one concept at a time with check questions |
| `/explain COPY INTO vs Auto Loader` | Simple explanation + example + exam traps + source slide |
| `/quiz jobs 5` | Exam-style questions, one at a time, with explanations |
| `/lab 1` | Guided hands-on notebook (Spark + Delta on your Mac) |
| `/flashcards sdp` | Quick recall drill |
| `/exam` | Timed 45-question mock exam |
| `/progress` | Scores, weak topics, plan for the next sessions |
| `/review` | Re-teach and re-test your weak topics |

You can also just talk: *"I don't understand materialized views"*, *"give me a hint for 1c"*.

## What's inside
| Folder | Contents |
|---|---|
| `curriculum.md` | 33 lessons mapped to your slides, course notebooks, notes and labs |
| `notes/` | Study notes per course + `extra-exam-topics.md` (exam topics the 4 courses don't fully cover) |
| `notebooks/` | 5 hands-on Jupyter labs, 25 auto-checked exercises (`solutions/` has answers) |
| `lab4_project/` | Small Python project for modular code + pytest (course 4) |
| `quiz-bank/` | ~50 exam-style questions + ~70 flashcards |
| `databricks/FREE_EDITION_GUIDE.md` | How to run the original course notebooks on real Databricks |
| `source/text/` | Searchable text of all 396 slides (OCR) and 60 course notebooks |
| `labutils/` | Local Spark helpers, simulators (COPY INTO, Jobs, expectations), exercise checker |
| `progress/progress.json` | Your progress (Claude updates it) |

Your original training folder `../Data enginner/` is read-only and is never changed.

## Hands-on lab portal (recommended)
```bash
cd ~/joc_project/de-associate-lab && .venv/bin/python -m portal.server
```
Open **http://localhost:8800**. Each step: analogy → diagram → your course slides → lesson → task → check ✓ → exam question.

### Imported PDF questions by section

The recommended route is now **Read the beginner introduction → Learn this section
first → Try the related lab → Explain it in your own words → Practise linked
questions → Return when review is due**. There are 26 learning topics covering all
280 PDF questions, assigned question by question rather than by keyword alone.

The knowledge base is also readable outside the portal:
`notes/knowledge-base/00-start-here.md` and `01-section.md` through `07-section.md`.
Each topic includes an analogy, the decision being tested, a small example, a
common wrong turn, a recall prompt and a specific existing lab link. Full course
notes remain available in each section. Self-checks record your own assessment;
they do not claim independently verified mastery.

**45-question closed-book rehearsal** samples the current seven sections with
approximate counts `3 / 9 / 10 / 7 / 5 / 4 / 7`. It lasts 90 minutes, saves choices,
and hides lessons, hints and feedback until you finish. Reloading or leaving the
view does not reset the clock. The result is scored against the imported source
key; it is not an official score or an assertion about your eventual exam paper.
Five flagged, ambiguous/version-sensitive source questions remain available for
learning but are excluded from this rehearsal.

Practice review dates use spaced intervals of 1, 3, 7 and 14 days for consecutive
source-key matches. A miss returns to a one-day interval. Use **Due for review**
to revisit those questions. Existing notebook and lab completion stays separate.

Click **Section practice** in the top bar. The imported Examice bank contains 280
questions, grouped by the current seven exam sections and linked to course lessons
and hands-on labs. The dropdown also offers the older five-section study crosswalk.
Each lab has a shortcut back to its relevant practice sections. Existing lab steps
still unlock in order; practice does not mark a lab complete.

Answer one question, press **Check answer**, then review the source explanation.
Use **Not tried yet** or **Last answer missed** to focus your practice. Attempts
are saved separately in `progress/progress.json`; existing progress is preserved.
PDF images preserve picture-based code and tables without showing answer badges.

These are third-party practice questions. The suggested answers are **not independently
verified**. Section/topic assignments are study aids. Review the mapping in
`notes/examice-section-map.md`. Imported question counts do not represent official
exam weights. Keep this personal bank local; it is not published by this integration.

To rebuild the import from your own PDF (does not overwrite notebooks or progress):

```bash
.venv/bin/python -B scripts/import_examice.py "/path/to/Examice _ Certification Exam Practice Questions & Answers.pdf"
```

Restart the portal after updating its Python code, then refresh your browser.

| Lab | Official exam section | Steps |
|---|---|---|
| 1 Data Ingestion | §2 Ingestion & Loading · 21% | Delta, CTAS, COPY INTO, Auto Loader, metadata, rescued data, JSON, MERGE |
| 2 Lakeflow Jobs | §4 Lakeflow Jobs · 16% | DAG, parameters & task values, if/else + for each + run-if, retries & repair |
| 3 Declarative Pipelines | §3 Transformation · 22% | streaming tables + MV, expectations, joins, CDC |
| 4 DevOps & Testing | (course 4, not in exam outline) | modular code, pytest |
| 5 Delta, SQL & Streaming | §3 + §6 | OPTIMIZE/RESTORE/VACUUM, window dedupe, higher-order functions, output modes |
| 6 Transform & Tune | §3 Transformation · 22% | cleaning, joins/unions, aggregations, Spark tuning |
| 7 Troubleshoot & Compute | §6 · 10% + §1 · 6% | skew & salting, liquid clustering, diagnosing failures, choosing compute |
| 8 CI/CD & Bundles | §5 CI/CD · 10% | Git folders, bundle variables/targets/overrides, BUNDLE_VAR_ secrets, CLI |
| 9 Governance & Security | §7 Governance · 15% | GRANT/REVOKE, managed↔external, masks & row filters, ABAC |

Official exam guide (Aug 2026): `source/exam-guide/` · objective-by-objective map: `notes/exam-guide-map.md`.
The same labs also exist as Jupyter notebooks in `notebooks/`.

## Setup (already done)
Java 17 (Homebrew), Python venv in `.venv`, Jupyter kernel `de-lab`. To rebuild: `scripts/setup.sh`.
