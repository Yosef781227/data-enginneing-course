"""Numbers for the Today / Progress screens, computed from progress.json.

Exam readiness (shown with its formula in the UI):
  70% × Σ_section (exam weight × share of that section's questions whose LAST answer was right)
+ 30% × share of lab steps done
"""
from datetime import date, timedelta

from portal.exam_sections import SECTIONS
from portal.mock_exam import ALLOCATION
from portal.question_bank import load_bank
from portal.study_topics import TOPICS


def _activity_days(progress):
    """Minutes studied per ISO date (from the heartbeat), plus days with any recorded activity."""
    minutes = dict(progress.get("activity", {}))
    active = set(k for k, v in minutes.items() if v)
    for st in progress.get("portal", {}).get("steps", {}).values():
        if st.get("date"):
            active.add(st["date"])
    for a in progress.get("question_bank", {}).values():
        if a.get("date"):
            active.add(a["date"])
    for a in progress.get("answers", []):
        if a.get("date"):
            active.add(a["date"])
    return minutes, active


def _streak(active, today):
    n, d = 0, today
    if d.isoformat() not in active:      # today not done yet: the streak still counts up to yesterday
        d -= timedelta(days=1)
    while d.isoformat() in active:
        n += 1
        d -= timedelta(days=1)
    return n


def build(progress, labs):
    today = date.today()
    bank = load_bank()
    qb = progress.get("question_bank", {})

    # ---------------------------------------------------------------- labs
    lab_rows, total_steps, done_steps, next_step = [], 0, 0, None
    for lab in labs:
        gated = [s for s in lab["steps"] if s["type"] != "info"]
        d = sum(s["done"] for s in gated)
        total_steps += len(gated)
        done_steps += d
        first_open = next((s for s in lab["steps"] if not s["done"]), None)
        row = {"id": lab["id"], "label": lab["label"], "name": lab["name"], "total": len(gated), "done": d,
               "next": first_open["key"] if first_open else None,
               "steps": [{"key": s["key"], "title": s["title"], "done": s["done"], "type": s["type"]} for s in lab["steps"]]}
        lab_rows.append(row)
        if next_step is None and first_open is not None and d < len(gated):
            next_step = {"lab": lab["id"], "key": first_open["key"], "title": first_open["title"]}
    if next_step is None:
        for row in lab_rows:
            if row["next"]:
                next_step = {"lab": row["id"], "key": row["next"], "title": next(s["title"] for s in row["steps"] if s["key"] == row["next"])}
                break

    # ---------------------------------------------------------------- questions
    by_id = {q["id"]: q for q in bank}
    sec_rows = []
    readiness_q = 0.0
    for s in SECTIONS:
        qs = [q for q in bank if q["section"] == s["id"]]
        tried = [q for q in qs if q["id"] in qb]
        right = [q for q in tried if qb[q["id"]].get("correct")]
        sec_rows.append({"id": s["id"], "name": s["name"], "weight": s["weight"], "total": len(qs),
                         "tried": len(tried), "right": len(right),
                         "pct": round(100 * len(right) / len(tried)) if tried else None})
        readiness_q += s["weight"] / 100 * (len(right) / len(qs) if qs else 0)
    topic_rows = []
    for key, (section, title, numbers, lab, gid) in TOPICS.items():
        ids = [f"examice-{n:03d}" for n in numbers]
        tried = [i for i in ids if i in qb]
        right = [i for i in tried if qb[i].get("correct")]
        topic_rows.append({"id": key, "title": title, "section": section, "lab": lab, "gid": gid,
                           "total": len(ids), "tried": len(tried), "right": len(right)})

    def due_between(a, b):
        return sum(1 for v in qb.values() if a <= v.get("next_review", "9999") <= b)
    t = today.isoformat()
    due = {"today": sum(1 for v in qb.values() if v.get("next_review", "9999") <= t),
           "tomorrow": due_between((today + timedelta(1)).isoformat(), (today + timedelta(1)).isoformat()),
           "week": due_between((today + timedelta(2)).isoformat(), (today + timedelta(7)).isoformat())}

    # first-attempt accuracy from the answer log
    first = {}
    for a in progress.get("answers", []):
        if a.get("source") == "examice-unverified" and a.get("lesson") not in first:
            first[a["lesson"]] = a.get("correct", False)
    first_pct = round(100 * sum(first.values()) / len(first)) if first else None

    weak = sorted([r for r in topic_rows if r["tried"] >= 3],
                  key=lambda r: (r["right"] / r["tried"], -r["tried"]))[:3]
    weakest_section = min([r for r in sec_rows if r["tried"]], key=lambda r: r["pct"], default=None)

    # ---------------------------------------------------------------- activity
    minutes, active = _activity_days(progress)
    week = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        week.append({"date": d.isoformat(), "day": d.strftime("%a"), "minutes": minutes.get(d.isoformat(), 0),
                     "active": d.isoformat() in active})
    yesterday = (today - timedelta(1)).isoformat()

    # ---------------------------------------------------------------- mock exams
    mocks = []
    for ident, ex in progress.get("mock_exams", {}).items():
        if not ex.get("finished"):
            continue
        res = ex.get("result", {})
        per = {}
        for r in res.get("results", []):
            p = per.setdefault(r["section"], [0, 0])
            p[0] += r["correct"]
            p[1] += 1
        weakest = min(per.items(), key=lambda kv: kv[1][0] / kv[1][1], default=(None, None))[0]
        mocks.append({"id": ident, "started": ex.get("started"), "finished_at": ex.get("finished_at"),
                      "correct": res.get("correct", 0), "total": res.get("total", 45),
                      "weakest": next((s["name"] for s in SECTIONS if s["id"] == weakest), None)})
    mocks.sort(key=lambda m: m["started"] or 0, reverse=True)
    active_mock = next((i for i, ex in progress.get("mock_exams", {}).items() if not ex.get("finished")), None)

    readiness = round(100 * (0.7 * readiness_q + 0.3 * (done_steps / total_steps if total_steps else 0)))
    return {
        "today": t,
        "profile": progress.get("profile", {}),
        "labs": lab_rows, "steps": {"done": done_steps, "total": total_steps}, "next_step": next_step,
        "questions": {"total": len(bank), "tried": len(qb), "first_pct": first_pct, "new": len(bank) - len(qb)},
        "sections": sec_rows, "topics": topic_rows, "weak": weak, "weakest_section": weakest_section,
        "due": due,
        "week": week, "streak": _streak(active, today), "today_active": t in active,
        "yesterday_minutes": minutes.get(yesterday, 0), "week_minutes": sum(w["minutes"] for w in week),
        "readiness": readiness,
        "mock_allocation": [{"id": s["id"], "name": s["name"], "count": ALLOCATION[s["id"]]} for s in SECTIONS],
        "mocks": mocks, "active_mock": active_mock,
    }
