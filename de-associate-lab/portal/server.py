"""DE Lab Portal — a local, Udemy-style guided lab for the study notebooks.

Start:  .venv/bin/python -m portal.server      then open http://localhost:8800
Your code runs in a real Python kernel (kernel "de-lab") with Spark + Delta.
"""
import json
import queue
import re
import threading
import time
import traceback
import os
import tempfile
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from jupyter_client.manager import KernelManager

from portal.content import C
from portal.lessons import L as LESSONS
from portal.visuals import V as VISUALS
from portal.instructions import D as INSTRUCTIONS
from portal.steps import LAB, all_labs
from portal.question_bank import catalog, load_bank, public_question, check_answer, record_attempt
from portal.knowledge_base import overview, section_guide
from portal.study_topics import TOPICS
from portal import mock_exam

PORT = 8800
STATIC = Path(__file__).parent / "static"
PROGRESS = LAB / "progress" / "progress.json"
PROGRESS_LOCK = threading.RLock()
ANSI = re.compile(r"\x1b\[[0-9;]*m")


# ------------------------------------------------------------------ kernel
class Kernel:
    def __init__(self):
        self.lock = threading.Lock()
        self.km = None
        self.kc = None
        self.loaded_lab = None
        self.start()

    def start(self):
        self.km = KernelManager(kernel_name="de-lab")
        self.km.start_kernel(cwd=str(LAB / "notebooks"))
        self.kc = self.km.client()
        self.kc.start_channels()
        self.kc.wait_for_ready(timeout=120)
        self.loaded_lab = None

    def restart(self):
        with self.lock:
            try:
                self.kc.stop_channels()
                self.km.shutdown_kernel(now=True)
            except Exception:
                pass
            self.start()

    def run(self, code, timeout=900):
        """Execute code; return {ok, outputs:[{type,text|html}], error}."""
        with self.lock:
            return self._run(code, timeout)

    def _run(self, code, timeout):
        msg_id = self.kc.execute(code, store_history=False)
        outputs, error = [], None
        deadline = time.time() + timeout
        while True:
            try:
                msg = self.kc.get_iopub_msg(timeout=max(1, deadline - time.time()))
            except queue.Empty:
                self.km.interrupt_kernel()
                error = {"ename": "Timeout", "evalue": f"cell took longer than {timeout}s", "traceback": ""}
                break
            if msg["parent_header"].get("msg_id") != msg_id:
                continue
            t, c = msg["msg_type"], msg["content"]
            if t == "stream":
                text = c["text"]
                if outputs and outputs[-1]["type"] == "text":
                    outputs[-1]["text"] += text
                else:
                    outputs.append({"type": "text", "text": text})
            elif t in ("execute_result", "display_data"):
                d = c["data"]
                if "text/html" in d:
                    outputs.append({"type": "html", "html": d["text/html"]})
                elif "text/plain" in d:
                    outputs.append({"type": "text", "text": d["text/plain"] + "\n"})
            elif t == "error":
                tb = ANSI.sub("", "\n".join(c.get("traceback", [])))
                error = {"ename": c["ename"], "evalue": ANSI.sub("", c["evalue"]), "traceback": tb[-3000:]}
            elif t == "status" and c["execution_state"] == "idle":
                break
        return {"ok": error is None, "outputs": outputs, "error": error}


KERNEL = None
LABS = {lab["id"]: lab for lab in all_labs()}


# ------------------------------------------------------------------ progress
def load_progress():
    try:
        return json.loads(PROGRESS.read_text())
    except Exception:
        return {}


def save_progress(p):
    PROGRESS.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w',dir=PROGRESS.parent,delete=False,encoding='utf-8') as tmp:
        json.dump(p,tmp,indent=2)
        temporary=tmp.name
    os.replace(temporary,PROGRESS)


def portal_state():
    p = load_progress()
    return p.setdefault("portal", {"steps": {}, "quiz": {}})


def mark_step(key, **fields):
    p = load_progress()
    st = p.setdefault("portal", {"steps": {}, "quiz": {}})["steps"].setdefault(key, {})
    st.update(fields)
    st["date"] = date.today().isoformat()
    p.setdefault("profile", {})["last_session"] = date.today().isoformat()
    save_progress(p)


# ------------------------------------------------------------------ lab logic
def step_by_key(lab_id, key):
    return next(s for s in LABS[lab_id]["steps"] if s["key"] == key)


def ensure_lab(lab_id):
    """Load a lab into the kernel: run setup, then replay finished steps so the data exists."""
    if KERNEL.loaded_lab == lab_id:
        return {"ok": True, "replayed": 0}
    lab = LABS[lab_id]
    r = KERNEL.run(lab["setup"])
    if not r["ok"]:
        return r
    done = portal_state()["steps"]
    KERNEL.prepped = set()
    replayed = 0
    for s in lab["steps"]:  # rebuild tables from finished steps (in order), stop at the first unfinished one
        if s["type"] != "code":
            continue
        if not done.get(f"{lab_id}:{s['key']}", {}).get("done"):
            break
        for code in (s["prep"], s["solution"], s["after"]):
            if code:
                KERNEL.run(code)
        KERNEL.prepped.add(f"{lab_id}:{s['key']}")
        replayed += 1
    KERNEL.loaded_lab = lab_id
    return {"ok": True, "replayed": replayed}


def prep_step(lab_id, key):
    s = step_by_key(lab_id, key)
    tag = f"{lab_id}:{key}"
    if not s["prep"] or tag in getattr(KERNEL, "prepped", set()):
        return {"ok": True, "outputs": []}
    r = KERNEL.run(s["prep"])
    if r["ok"]:
        KERNEL.prepped.add(tag)
    return r


def grade(lab_id, key, code):
    s = step_by_key(lab_id, key)
    res = {"passed": False, "outputs": [], "message": ""}
    if s["type"] == "file":
        (LAB / s["file"]).write_text(code)
    else:
        r = KERNEL.run(code)
        res["outputs"] += r["outputs"]
        if not r["ok"]:
            res["error"] = r["error"]
            res["message"] = "Your code raised an error — read it, fix the code, and check again."
            if "ALREADY_EXISTS" in (r["error"] or {}).get("evalue", ""):
                res["message"] = ("This table already exists — probably from an earlier run of this step. "
                                  "To do the step again from the start, click “✕ Reset lab” at the bottom left.")
            return res
        if s["after"]:
            r = KERNEL.run(s["after"])
            res["outputs"] += r["outputs"]
            if not r["ok"]:
                res["error"] = r["error"]
                res["message"] = "Your code ran, but the follow-up step failed. Look at the error."
                return res
    if s["check"]:
        r = KERNEL.run(f"from labutils.check import run_check as _rc\nprint('__RESULT__', _rc({s['check']!r}))", timeout=600)
        text = "".join(o.get("text", "") for o in r["outputs"])
        res["passed"] = "__RESULT__ True" in text
        lines = [l for l in text.splitlines() if not l.startswith("__RESULT__")]
        res["message"] = ANSI.sub("", "\n".join(lines)).strip()
        if not r["ok"]:
            res["error"] = r["error"]
    else:
        res["passed"] = True
        res["message"] = "✅ Code ran without errors."
    if res["passed"]:
        mark_step(f"{lab_id}:{key}", done=True)
    return res


def answer(lab_id, gid, choice):
    item = C.get(gid)
    if not item:
        return {"correct": True}
    correct = int(choice) == item["a"]
    p = load_progress()
    p.setdefault("portal", {"steps": {}, "quiz": {}})["quiz"][gid] = correct
    p.setdefault("answers", []).append({"date": date.today().isoformat(), "topic": LABS[lab_id]["topic"],
                                        "lesson": gid, "correct": correct, "question": item["q"],
                                        "type": "portal"})
    wt = p.setdefault("weak_topics", [])
    if not correct and LABS[lab_id]["topic"] not in wt:
        wt.append(LABS[lab_id]["topic"])
    save_progress(p)
    return {"correct": correct, "answer": item["a"], "explain": item["ex"]}


def labs_payload():
    st = portal_state()
    out = []
    for lab in LABS.values():
        steps = []
        for s in lab["steps"]:
            tag = f"{lab['id']}:{s['key']}"
            starter = s["starter"]
            if s["type"] == "file":
                starter = (LAB / s["file"]).read_text()
            steps.append({**s, "starter": starter, "done": bool(st["steps"].get(tag, {}).get("done")),
                          "learn": C.get(s["gid"]), "quiz_done": s["gid"] in st["quiz"],
                          "lesson": ({**LESSONS[s["key"]], "do": INSTRUCTIONS.get(s["key"], LESSONS[s["key"]]["do"])}
                                     if s["key"] in LESSONS else None),
                          "visual": VISUALS.get(s["key"])})
        out.append({k: lab[k] for k in ("id", "label", "name", "intro")} | {"steps": steps})
    return out


def solution(lab_id, key):
    s = step_by_key(lab_id, key)
    if s["type"] == "file":
        return (LAB / s["solution_file"]).read_text()
    return s["solution"]


# ------------------------------------------------------------------ http
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == '/api/study/overview':
            return self._send(200,overview())
        if path == '/api/study/section':
            value=parse_qs(urlsplit(self.path).query).get('id',[''])[0]
            if value not in [str(i) for i in range(1,8)]:
                return self._send(400,{'error':'Choose a section from 1 to 7'})
            return self._send(200,section_guide(int(value),load_progress()))
        if path == "/api/learn":
            from portal import learn
            value = parse_qs(urlsplit(self.path).query).get("section", [""])[0]
            if value not in [str(i) for i in range(1, 8)]:
                return self._send(400, {"error": "Choose a section from 1 to 7"})
            return self._send(200, learn.payload(int(value), load_bank()))
        if path == '/api/mock':
            identifier=parse_qs(urlsplit(self.path).query).get('id',[''])[0]
            try:return self._send(200,mock_exam.payload(load_progress(),identifier))
            except ValueError as exc:return self._send(404,{'error':str(exc)})
        if path == "/api/exam/sections":
            return self._send(200, catalog(load_progress()))
        if path == "/api/exam/questions":
            query = parse_qs(urlsplit(self.path).query)
            progress = load_progress()
            questions = load_bank()
            section = query.get("section", [""])[0]
            legacy = query.get("legacy", [""])[0]
            if section:
                questions = [q for q in questions if str(q["section"]) == section]
            if legacy:
                questions = [q for q in questions if str(q["legacy_section"]) == legacy]
            return self._send(200, [public_question(q, progress) for q in questions])
        if path == "/api/labs":
            return self._send(200, labs_payload())
        if path == "/api/dashboard":
            from portal import dashboard
            return self._send(200, dashboard.build(load_progress(), labs_payload()))
        f = STATIC / ("index.html" if path == "/" else path.lstrip("/"))
        if f.is_file() and STATIC in f.resolve().parents:
            ctype = {".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8",
                     ".css": "text/css; charset=utf-8", ".jpg": "image/jpeg", ".png": "image/png"}.get(f.suffix, "text/plain")
            return self._send(200, f.read_bytes(), ctype)
        self._send(404, {"error": "not found"})

    def do_POST(self):
        # Serialize read-modify-write operations so quick answers/self-checks
        # cannot overwrite one another or existing lab progress.
        with PROGRESS_LOCK:
            self._post()

    def _post(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        try:
            path = self.path
            if path in ('/api/mock/start','/api/mock/save','/api/mock/finish'):
                p=load_progress()
                try:
                    if path.endswith('/start'):
                        identifier=mock_exam.begin(p);r=mock_exam.payload(p,identifier)
                    elif path.endswith('/save'):
                        mock_exam.save(p,body.get('id'),body.get('question'),body.get('choices'));r={'saved':True}
                    else:r=mock_exam.finish(p,body.get('id'))
                except ValueError as exc:return self._send(400,{'error':str(exc)})
                save_progress(p)
                return self._send(200,r)
            if path == "/api/heartbeat":
                p = load_progress()
                day = date.today().isoformat()
                act = p.setdefault("activity", {})
                act[day] = act.get(day, 0) + max(0, min(int(body.get("minutes", 1)), 5))
                save_progress(p)
                return self._send(200, {"ok": True, "today": act[day]})
            if path == "/api/profile":
                p = load_progress()
                prof = p.setdefault("profile", {})
                if "exam_date" in body:
                    v = body["exam_date"]
                    if v is not None and not (isinstance(v, str) and len(v) == 10 and v[4] == "-" and v[7] == "-"):
                        return self._send(400, {"error": "Use the format YYYY-MM-DD"})
                    prof["exam_date"] = v
                save_progress(p)
                return self._send(200, {"ok": True, "profile": prof})
            if path == '/api/study/topic':
                topic=body.get('topic')
                if topic not in TOPICS or not isinstance(body.get('understood'),bool):
                    return self._send(400,{'error':'Choose a valid topic and self-check status'})
                p=load_progress();p.setdefault('study_topics',{})[topic]={'understood':body['understood'],'date':date.today().isoformat()}
                save_progress(p)
                return self._send(200,{'ok':True})
            if path == "/api/exam/answer":
                question = next((q for q in load_bank() if q["id"] == body.get("id")), None)
                if question is None:
                    return self._send(404, {"error": "Question not found"})
                try:
                    result = check_answer(question, body.get("choices"))
                except ValueError as exc:
                    return self._send(400, {"error": str(exc)})
                p = load_progress()
                record_attempt(p,question,body['choices'],result)
                result['next_review']=p['question_bank'][question['id']]['next_review']
                p.setdefault("answers", []).append({"date": date.today().isoformat(), "topic": f"exam-section-{question['section']}",
                    "lesson": question["id"], "correct": result["correct"], "question": question["q"], "source": "examice-unverified"})
                save_progress(p)
                return self._send(200, result)
            if path == "/api/open":
                r = ensure_lab(body["lab"])
                if r.get("ok") and body.get("step"):
                    r = {**r, "prep": prep_step(body["lab"], body["step"])}
                return self._send(200, r)
            if path == "/api/run":
                ensure_lab(body["lab"])
                return self._send(200, KERNEL.run(body["code"]))
            if path == "/api/check":
                ensure_lab(body["lab"])
                prep_step(body["lab"], body["step"])
                return self._send(200, grade(body["lab"], body["step"], body["code"]))
            if path == "/api/solution":
                return self._send(200, {"code": solution(body["lab"], body["step"])})
            if path == "/api/answer":
                return self._send(200, answer(body["lab"], body["gid"], body["choice"]))
            if path == "/api/restart":
                KERNEL.restart()
                return self._send(200, {"ok": True})
            if path == "/api/reset_lab":
                p = load_progress()
                steps = p.setdefault("portal", {"steps": {}, "quiz": {}})["steps"]
                for k in [k for k in steps if k.startswith(body["lab"] + ":")]:
                    del steps[k]
                save_progress(p)
                KERNEL.loaded_lab = None
                return self._send(200, {"ok": True})
            self._send(404, {"error": "unknown endpoint"})
        except Exception as e:  # noqa: BLE001
            self._send(500, {"error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()[-2000:]})


def main():
    global KERNEL
    print("Starting the Python/Spark kernel…")
    KERNEL = Kernel()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"DE Lab Portal running →  http://localhost:{PORT}   (Ctrl+C to stop)")
    try:
        srv.serve_forever()
    finally:
        KERNEL.km.shutdown_kernel(now=True)


if __name__ == "__main__":
    main()
