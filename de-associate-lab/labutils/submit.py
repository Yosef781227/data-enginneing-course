"""Save an answer (SQL text, list, dict…) so the checker can grade it: submit("9a", sql)."""
import json

from labutils import LAB_ROOT


def submit(eid, answer):
    f = LAB_ROOT / ".lab_state" / "answers" / f"{eid}.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(answer))
    print(f"Answer for {eid} saved — press Check.")


def load(eid):
    f = LAB_ROOT / ".lab_state" / "answers" / f"{eid}.json"
    return json.loads(f.read_text()) if f.exists() else None
