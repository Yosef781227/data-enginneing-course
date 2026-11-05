---
description: Start or continue a study session (shows where you are and what to do next)
---
Start a study session.

1. Read `progress/progress.json` and `curriculum.md`.
2. Greet the learner in 2–3 short lines. Show:
   - lessons done / total, last session date, average quiz score (from `answers`)
   - top 3 `weak_topics` (if any)
3. Recommend ONE next step (the next unfinished lesson, or a `/review` if weak topics exist,
   or `/exam` if all lessons are done) and list the other commands in one short line each:
   `/lesson <id>`, `/quiz`, `/lab <id>`, `/explain <topic>`, `/flashcards`, `/exam`, `/progress`.
4. Ask: "Ready to start <recommended step>?" and wait.
If `progress.json` shows this is the first session, briefly explain how the lab works (Claude =
tutor, notebooks = local practice, Databricks Free Edition = real platform) and ask the learner
their exam date and how many hours per week they can study; save both to `profile`.
