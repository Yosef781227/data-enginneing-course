"""Convert the read-only training folder into plain-text files the tutor can search.

Writes to source/text/:
  slides/<course>.txt      - text of each slide PDF, one "=== Slide N ===" block per page
  notebooks/<course>/...md - each Databricks notebook as markdown + code blocks
"""
import re
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
def _find_training():
    """The course folder: an env var, the repo root (when the lab sits inside the course repo), or ../Data enginner."""
    import os
    if os.environ.get("DE_TRAINING"):
        return Path(os.environ["DE_TRAINING"])
    for cand in (LAB.parent, LAB.parent / "Data enginner"):
        if any(cand.glob("1 Data Ingestion*")):
            return cand
    return LAB.parent / "Data enginner"


TRAINING = _find_training()
COURSE4 = LAB / "source" / "course4"
OUT = LAB / "source" / "text"

COURSES = {
    "c1-ingestion": TRAINING / "1 Data Ingestion with lake flow connect",
    "c2-jobs": TRAINING / "2 Deploy workloads with lake flow job",
    "c3-pipelines": TRAINING / "3 Build-Data-Pipelines-with-Lakeflow-Spark-Declarative-Pipelines",
    "c4-devops": TRAINING / "4 DevOps-Essentials-for-Data-Engineering",
}


def notebook_to_md(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    lang = "sql" if path.suffix == ".sql" else "python"
    comment = "--" if lang == "sql" else "#"
    cells = re.split(rf"^{re.escape(comment)} COMMAND -+\s*$", text, flags=re.M)
    out = [f"# {path.stem}\n"]
    for cell in cells:
        lines = cell.strip("\n").splitlines()
        lines = [l for l in lines if not l.startswith(f"{comment} Databricks notebook source")]
        lines = [l for l in lines if not l.startswith(f"{comment} DBTITLE")]
        if not any(l.strip() for l in lines):
            continue
        magic = f"{comment} MAGIC"
        if all(l.startswith(magic) or not l.strip() for l in lines):
            body = [re.sub(rf"^{re.escape(magic)} ?", "", l) for l in lines]
            if body and body[0].strip().startswith("%md"):
                body[0] = body[0].strip()[3:]
                md = "\n".join(body).strip()
                if "db-academy-rgb" in md or "Databricks, Inc. All rights" in md:
                    continue
                out.append(md + "\n")
                continue
            out.append("```\n" + "\n".join(body).strip() + "\n```\n")
            continue
        out.append(f"```{lang}\n" + "\n".join(lines).strip() + "\n```\n")
    return "\n".join(out)


def extract_pdf(pdf: Path, dest: Path) -> None:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf))
    parts = []
    for i, page in enumerate(reader.pages, 1):
        txt = (page.extract_text() or "").strip()
        parts.append(f"=== Slide {i} ===\n{txt}\n")
    dest.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    (OUT / "slides").mkdir(parents=True, exist_ok=True)
    pdfs = {"c0-vocareum": TRAINING / "0 Accessing-Vocareum-Labs-in-Your-Training-11-slides.pdf"}
    for key, folder in COURSES.items():
        pdfs.update({key: p for p in folder.glob("*.pdf")})
    for key, pdf in pdfs.items():
        dest = OUT / "slides" / f"{key}.txt"
        if dest.exists() and dest.stat().st_size > 1000:
            continue  # already OCR'd (these PDFs are images; pypdf finds no text — see ocr_pdf.swift)
        extract_pdf(pdf, dest)
        print("slides:", key)

    roots = dict(COURSES)
    roots["c4-devops"] = COURSE4
    for key, folder in roots.items():
        for nb in sorted(list(folder.rglob("*.py")) + list(folder.rglob("*.sql"))):
            if "Classroom-Setup" in nb.name or nb.name.startswith("_") or "Copyrights" in nb.name:
                continue
            rel = nb.relative_to(folder)
            dest = OUT / "notebooks" / key / Path(*[p.replace(" ", "_") for p in rel.parts]).with_suffix(".md")
            dest.parent.mkdir(parents=True, exist_ok=True)
            first = nb.read_text(encoding="utf-8", errors="replace").splitlines()[:1]
            if first and "Databricks notebook source" in first[0]:
                dest.write_text(notebook_to_md(nb), encoding="utf-8")
            else:  # plain .py module / test file
                lang = "sql" if nb.suffix == ".sql" else "python"
                dest.write_text(f"# {nb.name}\n\n```{lang}\n{nb.read_text()}\n```\n", encoding="utf-8")
        print("notebooks:", key)


if __name__ == "__main__":
    sys.exit(main())
