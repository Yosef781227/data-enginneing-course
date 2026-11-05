---
description: Quick flashcard drill, e.g. /flashcards jobs
argument-hint: [topic]
---
Flashcard drill for **$ARGUMENTS** (default: weak topics).

Use `quiz-bank/flashcards.md` plus facts from `notes/`. Show the FRONT of one card, wait for the
learner to answer in their own words, then show the BACK and say if they got the key idea.
Do 10 cards. Track which cards they missed and repeat the missed ones once at the end.
Log results to `progress/progress.json` (`answers`, topic tag, `"type": "flashcard"`).
