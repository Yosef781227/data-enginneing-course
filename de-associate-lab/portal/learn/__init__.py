"""Learn-first content per exam section: a plain-English note per concept, and a
'know this first' card for every practice question (portal/learn/s1.py … s7.py)."""
import importlib

from portal.exam_sections import SECTIONS


def _load(n):
    try:
        return importlib.import_module(f"portal.learn.s{n}")
    except ModuleNotFoundError:
        return None


def payload(section, bank):
    """Everything the Learn page and guided practice need for one section."""
    sec = next(s for s in SECTIONS if s["id"] == section)
    ids = {q["number"]: q["id"] for q in bank if q["section"] == section}
    m = _load(section)
    if m is None:
        return {"id": section, "name": sec["name"], "weight": sec["weight"], "ready": False, "count": len(ids)}
    by_topic = {}
    for q in bank:
        if q["section"] == section:
            by_topic.setdefault(q["topic"], []).append(q["number"])
    concepts = [{**c, "count": len(by_topic.get(c["topic"], []))} for c in m.CONCEPTS]
    return {"id": section, "name": sec["name"], "weight": sec["weight"], "ready": True, "count": len(ids),
            "intro": m.INTRO, "concepts": concepts,
            "order": [ids[n] for n in m.ORDER if n in ids],
            "before": {ids[n]: t for n, t in m.BEFORE.items() if n in ids}}
