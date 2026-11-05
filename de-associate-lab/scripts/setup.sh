#!/bin/zsh
# One-time setup on a Mac. Run from anywhere:   zsh de-associate-lab/scripts/setup.sh
# Needs: Homebrew, Python 3.9+, Xcode command line tools (for swiftc). Course files: the folder that contains
# "1 Data Ingestion with lake flow connect" etc. (the repo root, or ../Data enginner, or set DE_TRAINING=<path>).
set -e
cd "$(dirname "$0")/.."
LAB="$PWD"
T="${DE_TRAINING:-}"
if [ -z "$T" ]; then
  if ls ../"1 Data Ingestion"* >/dev/null 2>&1; then T="$(cd .. && pwd)"; else T="$(cd .. && pwd)/Data enginner"; fi
fi
echo "Lab:     $LAB"; echo "Courses: $T"

brew list openjdk@17 >/dev/null 2>&1 || brew install openjdk@17
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt
SITE=$(.venv/bin/python -c "import site; print(site.getsitepackages()[0])")
echo "$LAB" > "$SITE/de_lab.pth"                                        # lets any notebook import labutils
.venv/bin/python -m ipykernel install --user --name de-lab --display-name "DE Lab (.venv)"

# Course material -> text for the tutor, slide images for the portal (not stored in Git)
if ls "$T"/"1 Data Ingestion"* >/dev/null 2>&1; then
  mkdir -p source/course4 && unzip -q -o "$T/4 DevOps-Essentials-for-Data-Engineering/"*.zip -d source/course4
  swiftc -O scripts/ocr_pdf.swift -o scripts/ocr_pdf
  swiftc -O scripts/render_slides.swift -o scripts/render_slides
  mkdir -p source/text/slides
  scripts/ocr_pdf "$T/0 Accessing-Vocareum-Labs-in-Your-Training-11-slides.pdf" source/text/slides/c0-vocareum.txt
  i=1
  for d in "1 Data Ingestion with lake flow connect" "2 Deploy workloads with lake flow job" \
           "3 Build-Data-Pipelines-with-Lakeflow-Spark-Declarative-Pipelines" "4 DevOps-Essentials-for-Data-Engineering"; do
    pdf=$(ls "$T/$d"/*.pdf | head -1)
    name=$(echo c1-ingestion c2-jobs c3-pipelines c4-devops | cut -d' ' -f$i)
    scripts/ocr_pdf "$pdf" "source/text/slides/$name.txt"
    scripts/render_slides "$pdf" "portal/static/slides/c$i"
    i=$((i+1))
  done
  DE_TRAINING="$T" .venv/bin/python scripts/extract_sources.py
  mkdir -p source/exam-guide
  curl -sfL -o source/exam-guide/exam-guide-august-2026.pdf \
    "https://www.databricks.com/sites/default/files/2026-10/Databricks-Certified-Data-Engineer-Associate-Exam-Guide-August-2026.pdf" || true
  [ -f source/exam-guide/exam-guide-august-2026.pdf ] && .venv/bin/python -c "
import re; from pypdf import PdfReader
r = PdfReader('source/exam-guide/exam-guide-august-2026.pdf')
t = ''.join(f'\n\n=== Page {i+1} ===\n' + (p.extract_text() or '') for i, p in enumerate(r.pages))
t = re.sub(r'\n \n', ' ', t); t = re.sub(r'[ \t]+', ' ', t)
open('source/exam-guide/exam-guide-august-2026.txt', 'w').write(t)" || true
else
  echo "⚠ Course folder not found — skipping slides/text. Set DE_TRAINING=/path/to/course/folder and re-run."
fi
.venv/bin/python scripts/build_notebooks.py
.venv/bin/python -m labutils.check env
echo
echo "Setup done. Start the portal:  .venv/bin/python -m portal.server   → http://localhost:8800"
echo "Start the tutor:               claude   (inside this folder), then type /start"
