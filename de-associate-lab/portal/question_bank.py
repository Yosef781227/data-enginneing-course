"""Private answer key and public question payloads for section practice."""
import json
from datetime import date, timedelta
from pathlib import Path
from portal.exam_sections import SECTIONS, LEGACY
from portal.study_topics import attach_learning
from portal.knowledge_base import concept, QUESTION_NOTES
from portal.explain import EXPLAIN
from portal.study_topics import TOPICS as _TOPICS

_TOPIC_LAB = {k: (v[3], v[4], v[1]) for k, v in _TOPICS.items()}

BANK_PATH = Path(__file__).resolve().parents[1] / "quiz-bank/examice.json"

def load_bank():
    if not BANK_PATH.exists():
        return []
    return attach_learning(json.loads(BANK_PATH.read_text())["questions"])

def catalog(progress):
    questions = load_bank()
    answers = progress.get("question_bank", {})
    sections = []
    for section in SECTIONS:
        items = [q for q in questions if q["section"] == section["id"]]
        sections.append({**section, "count": len(items), "attempted": sum(q["id"] in answers for q in items),
                         "correct": sum(answers.get(q["id"], {}).get("correct", False) for q in items),
                         "due": sum(answers.get(q['id'],{}).get('next_review','9999')<=date.today().isoformat() for q in items)})
    return {"sections": sections, "legacy": LEGACY, "total": len(questions),
            "source_notice": "Questions have been assigned to learning topics individually. Examice's suggested answers are still unverified; no guarantee these questions appear on your exam."}

def public_question(question, progress):
    return {k: v for k, v in question.items() if k not in ("answers", "explanation")} | {
        "multiple": len(question["answers"]) > 1,
        "attempt": progress.get("question_bank", {}).get(question["id"]),
        "concept": concept(question['topic']),
        "review_note": QUESTION_NOTES.get(question['number']),
        "lab": _TOPIC_LAB.get(question.get("topic"), (None, None, None))[0],
        "gid": _TOPIC_LAB.get(question.get("topic"), (None, None, None))[1],
        "topic_title": _TOPIC_LAB.get(question.get("topic"), (None, None, None))[2],
        "doubtful": bool((EXPLAIN.get(question["number"]) or {}).get("flag")),
    }

def check_answer(question, choices):
    if not isinstance(choices, list) or not choices or any(not isinstance(c, str) for c in choices):
        raise ValueError("Choose at least one option.")
    allowed = {c["label"] for c in question["choices"]}
    if not set(choices) <= allowed or len(set(choices)) != len(choices):
        raise ValueError("Invalid answer choices.")
    if len(question["answers"]) == 1 and len(choices) != 1:
        raise ValueError("This question has one answer.")
    return {"correct": set(choices) == set(question["answers"]), "answers": question["answers"],
            "explanation": question["explanation"], "answer_status": question["answer_status"],
            "explained": EXPLAIN.get(question["number"])}

def record_attempt(progress, question, choices, result):
    prior=progress.setdefault('question_bank',{}).get(question['id'],{})
    streak=prior.get('streak',0)+1 if result['correct'] else 0
    interval=[1,3,7,14][min(max(streak-1,0),3)] if result['correct'] else 1
    progress['question_bank'][question['id']]={'correct':result['correct'],'choices':choices,
        'attempts':prior.get('attempts',0)+1,'date':date.today().isoformat(),'streak':streak,
        'next_review':(date.today()+timedelta(days=interval)).isoformat()}
