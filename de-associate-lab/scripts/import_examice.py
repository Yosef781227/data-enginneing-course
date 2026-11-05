"""Import the learner's PDF. Never execute document text. Source key is unverified."""
import argparse
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from portal.exam_sections import SECTIONS
from portal.study_topics import attach_learning

# Transparent topic mapping: metadata is a study aid, not an official classification.
RULES = [
    (7, r"\bgrant\b|\brevoke\b|permission|ownership|owner|metastore|delta sharing|lineage|row filter|column mask|\babac\b|federation|audit log|personal.*data|data governance|external table|managed table|sensitive|\bPII\b"),
    (5, r"asset bundle|automation bundle|databricks bundle|databricks.yml|bundle_var|\bci/cd\b|git folder|version control|pull request|git branch|deployment target"),
    (4, r"repair run|lakeflow job|databricks job|job run|task value|taskValues|task depend|\bDAG\b|job cluster|job compute|jobs compute|job parameter|task parameter|scheduled job|schedule.*job|job.*schedule|job.*fail|task.*fail|cron|file arrival trigger|table update trigger|workflow|orchestrat"),
    (6, r"\boptimize\b|\bvacuum\b|z.order|liquid cluster|predictive optim|spark ui|data skew|spill|out.of.memory|troubleshoot|shuffle|query performance|query profile|slow.*query|slow.*stage|executor.*memory|partition pruning"),
    (2, r"auto loader|autoloader|cloudfiles|copy into|read_files|ingest|rescued.data|schema inference|lakeflow connect|file.*load|load.*file|readstream.*format"),
    (1, r"control plane|data plane|lakehouse platform|intelligence platform|cluster polic|which.*compute|compute.*option|sql warehouse|photon|databricks runtime|databricks connect|notebook.*feature|data lakehouse|delta lake.*benefit|cloud account"),
    (3, r"\bjoin\b|\bunion\b|\bmerge\b|\bdelete\b|\binsert\b|\bupdate\b|\bselect\b|\bdataframe\b|array function|delta table|delta live table|\bdlt\b|\bsdp\b|streaming|bronze|silver|gold|aggregate|aggregation|\bfunction\b|\bpivot\b|\bsql\b|\bjson\b"),
]

# Image-based prompts and legacy terminology need explicit topic assignments.
# These overrides classify topics only; they do not certify the answer key.
SECTION_OVERRIDES = {
    2:3,19:2,21:2,23:7,35:5,37:4,38:4,40:4,43:6,46:5,49:1,56:1,
    77:1,82:6,86:4,87:6,90:4,92:1,94:5,95:1,97:5,103:2,106:7,107:7,
    108:2,127:6,128:4,130:6,131:6,139:6,140:1,147:1,164:6,166:6,173:1,
    185:6,230:7,266:6,267:6,268:6,280:7,
}

def classify(text):
    for section, pattern in RULES:
        if re.search(pattern, text, re.I):
            return section, "keyword match"
    return 3, "default transformation; review mapping"

def clean(text):
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if re.search(r"Issued to .*@|Personal copy|https://examice.com/|Examice \| Certification|^\d+/\d+/\d+,|^Q\d+\s*·|^\d+/\d+$", line):
            continue
        lines.append(line.replace("CORRECT", "").rstrip())
    return "\n".join(lines).strip()

def parse_question(number, segments):
    text = clean("\n".join(s[2] for s in segments))
    text = re.sub(r"^QUESTION\s+\d+[^\n]*\n?", "", text)
    parts = re.split(r"SUGGESTED ANSWER", text, maxsplit=1)
    prompt_options = parts[0].strip()
    explanation = parts[1].strip() if len(parts) > 1 else ""
    answer_line = re.search(r"suggested answer is\s+([^\.\n]+)", explanation, re.I)
    answers = re.findall(r"\b[A-F]\b", answer_line.group(1)) if answer_line else []
    # Option labels occupy their own PDF text line. An article such as
    # "A data engineer..." is part of the stem, never option A.
    matches = list(re.finditer(r"(?m)^([A-F])[ \t]*$", prompt_options))
    choices = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(prompt_options)
        choices.append({"label": match.group(1), "text": prompt_options[match.end():end].strip()})
    prompt = prompt_options[:matches[0].start()].strip() if matches else prompt_options
    section, reason = classify(prompt)
    if reason.startswith("default"):
        answer_text = " ".join(c["text"] for c in choices if c["label"] in answers)
        section, fallback = classify(answer_text)
        if fallback == "keyword match":
            reason = "suggested-answer topic; review mapping"
        elif re.search(r"unity catalog", prompt, re.I):
            section, reason = 7, "catalog topic; review mapping"
    if number in SECTION_OVERRIDES:
        section, reason = SECTION_OVERRIDES[number], "explicit topic mapping (answer unverified)"
    return {"id": f"examice-{number:03}", "number": number, "q": prompt, "choices": choices,
            "answers": answers, "explanation": explanation, "section": section,
            "legacy_section": SECTIONS[section - 1]["legacy"], "mapping": reason,
            "pages": sorted({s[0] + 1 for s in segments}), "images": [], "answer_status": "source-suggested-unverified"}

def main():
    import fitz
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    args = parser.parse_args()
    doc = fitz.open(args.pdf)
    groups = {}
    current = None
    for page_index, page in enumerate(doc):
        text = page.get_text()
        starts = list(re.finditer(r"(?m)^[ \t]*QUESTION\s+(\d+)\b", text))
        if not starts and current:
            groups[current].append((page_index, 0, text))
        for i, match in enumerate(starts):
            if i == 0 and current and match.start():
                groups[current].append((page_index, 0, text[:match.start()]))
            current = int(match.group(1))
            groups[current] = [(page_index, match.start(), text[match.start():starts[i+1].start() if i+1<len(starts) else len(text)])]
    questions = []
    image_dir = ROOT / "portal/static/examice"
    image_dir.mkdir(parents=True, exist_ok=True)
    for number, segments in sorted(groups.items()):
        q = parse_question(number, segments)
        # Render source question/choices only; strip the answer badges and personal watermark.
        # Rendering all question pages also preserves image-only code, tables and options.
        for index, offset, text in segments:
            if "SUGGESTED ANSWER" in text and not re.search(r"(?m)^[A-F](?:\s|$)", text.split("SUGGESTED ANSWER")[0]) and offset == 0:
                continue
            page = doc[index]
            rect = page.rect
            markers = page.search_for(f"QUESTION {number}")
            top = markers[0].y0 - 5 if markers else 25
            ends = [box for box in page.search_for("SUGGESTED ANSWER") if box.y0 > top]
            bottom = ends[0].y0 - 5 if ends else rect.height - 38
            if bottom <= top:
                continue
            # Work on a per-question page copy; redaction must not mutate later imports.
            temp = fitz.open()
            temp.insert_pdf(doc, from_page=index, to_page=index)
            p = temp[0]
            # The publisher also highlights correct rows in green. Removing
            # the word CORRECT alone would still give the answer away.
            def neutralize(match):
                red, green, blue = map(float, match.group(1,2,3))
                return b"1 1 1 " + match.group(4) if green > red + .025 and green > blue + .025 else match.group(0)
            color_pattern = rb"([-+]?(?:\d*\.)?\d+)\s+([-+]?(?:\d*\.)?\d+)\s+([-+]?(?:\d*\.)?\d+)\s+(rg|RG)\b"
            for stream in p.get_contents():
                temp.update_stream(stream, re.sub(color_pattern, neutralize, temp.xref_stream(stream)))
            label_boxes = [(span["text"].strip(), fitz.Rect(span["bbox"]))
                           for block in p.get_text("dict")["blocks"] for ln in block.get("lines", []) for span in ln["spans"]
                           if re.fullmatch(r"[A-F]", span["text"].strip()) and 60 < span["bbox"][0] < 100 and top < span["bbox"][1] < bottom]
            for word in ("CORRECT",):
                for box in p.search_for(word):
                    p.add_redact_annot(box, fill=(1, 1, 1))
            for line in p.get_text("dict")["blocks"]:
                for ln in line.get("lines", []):
                    if any("@" in span["text"] or "Personal copy" in span["text"] for span in ln["spans"]):
                        p.add_redact_annot(fitz.Rect(ln["bbox"]), fill=(1,1,1))
            p.apply_redactions()
            for label, box in label_boxes:
                p.draw_rect(fitz.Rect(box.x0-8,box.y0-5,box.x1+8,box.y1+5), color=(1,1,1), fill=(1,1,1), overlay=True)
                p.insert_text((box.x0,box.y1-2),label,fontsize=10,color=(0,0,0),overlay=True)
            for drawing in p.get_drawings():
                box = drawing["rect"]
                if 50 < box.x0 < 90 and box.width > 350 and 25 < box.height < 500 and top <= box.y0 < bottom:
                    p.draw_rect(box,color=(1,1,1),width=3,overlay=True)
            name = f"q{number:03}-p{index+1}.png"
            p.get_pixmap(matrix=fitz.Matrix(1.3, 1.3), clip=fitz.Rect(0, top, rect.width, bottom)).save(image_dir / name)
            q["images"].append(f"/examice/{name}")
            temp.close()
        # If extraction missed option text, use A…E labels while the source image supplies content.
        if not q["choices"] or any(not c["text"] for c in q["choices"]):
            labels = [c["label"] for c in q["choices"]]
            last = max(labels + q["answers"] + ["D"])
            q["choices"] = [{"label": chr(c), "text": "See this option in the question image"} for c in range(ord("A"), ord(last)+1)]
        else:
            existing = {c["label"]: c for c in q["choices"]}
            last = max(existing)
            q["choices"] = [existing.get(chr(c), {"label":chr(c), "text":"See this option in the question image"}) for c in range(ord("A"),ord(last)+1)]
        questions.append(q)
    if len(questions) != 280 or len({q["id"] for q in questions}) != 280:
        raise ValueError(f"Expected 280 distinct questions; found {len(questions)}")
    issues = [q["id"] for q in questions if not q["answers"] or not q["images"]]
    if issues:
        raise ValueError(f"Incomplete extraction: {issues}")
    attach_learning(questions)
    out = ROOT / "quiz-bank/examice.json"
    out.write_text(json.dumps({"source": args.pdf.name, "imported": "2026-11-03", "questions": questions}, indent=2, ensure_ascii=False))
    report = ["# Imported question map", "", "Questions are assigned individually to learning topics. Examice suggested answers are unverified.", "", "| Question | Current section | Older section | PDF pages | Mapping |", "|---|---|---|---|---|"]
    report += [f"| {q['number']} | {q['section']} | {q['legacy_section']} | {', '.join(map(str,q['pages']))} | {q['mapping']} |" for q in questions]
    (ROOT / "notes/examice-section-map.md").write_text("\n".join(report)+"\n")
    print(json.dumps({"imported": len(questions), "sections": {s["id"]: sum(q["section"]==s["id"] for q in questions) for s in SECTIONS}}))

if __name__ == "__main__":
    main()
