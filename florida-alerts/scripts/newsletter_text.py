"""Extract text from every newsletter PDF to data/interim/newsletters/<name>.txt and print the stat lines.

Stat lines: alert counts, recoveries, "directly attributed", "since inception" totals.
"""
from pathlib import Path
import re

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1] / "data"
SRC = ROOT / "raw" / "newsletters"
OUT = ROOT / "interim" / "newsletters"
OUT.mkdir(parents=True, exist_ok=True)
STAT = re.compile(r"attribut|direct(ly)? (result|responsible|aided)|recover(ed|ies)\b.*\d|\d.*recover(ed|ies)|"
                  r"\d+ (state |statewide )?(AMBER|Silver|Purple|Missing Child|Spectrum)|inception|activated \d|\d+ (state )?alerts", re.I)

for pdf in sorted(SRC.glob("*.pdf")):
    doc = fitz.open(pdf)
    pages = [page.get_text() for page in doc]
    (OUT / f"{pdf.stem}.txt").write_text("\n\f\n".join(pages), encoding="utf-8")
    print(f"\n== {pdf.stem} ({len(pages)} pages)")
    for n, text in enumerate(pages, 1):
        for line in text.splitlines():
            if STAT.search(line):
                print(f"p{n}: {line.strip()}")
