"""Extract text from the national AMBER reports and print the national recovery lines and every Florida mention.

Input:  data/raw/amber/<year>_amber_report.pdf
Output: data/interim/amber/<year>.txt (pages separated by form feeds)
"""
from pathlib import Path
import re

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1] / "data"
OUT = ROOT / "interim" / "amber"
OUT.mkdir(parents=True, exist_ok=True)
NATIONAL = re.compile(r"direct(ly)? (result|attributed)|as a (direct )?result of (an |the )?AMBER|recovered as a result|"
                      r"\d+ AMBER Alerts were issued|resulted in (a )?(successful )?recover", re.I)

for pdf in sorted((ROOT / "raw" / "amber").glob("*_amber_report.pdf")):
    year = pdf.name[:4]
    pages = [p.get_text() for p in fitz.open(pdf)]
    (OUT / f"{year}.txt").write_text("\n\f\n".join(pages), encoding="utf-8")
    print(f"\n===== {year} ({len(pages)} pages)")
    seen = set()
    for n, page in enumerate(pages, 1):
        flat = re.sub(r"\s+", " ", page)
        for m in NATIONAL.finditer(flat):
            snippet = flat[max(0, m.start() - 160): m.end() + 120]
            if snippet[:60] not in seen:
                seen.add(snippet[:60])
                print(f"  [nat p{n}] ...{snippet}...")
        for m in re.finditer(r"Florida|\bFL\b", flat):
            snippet = flat[max(0, m.start() - 80): m.end() + 120]
            print(f"  [FL  p{n}] ...{snippet}...")
