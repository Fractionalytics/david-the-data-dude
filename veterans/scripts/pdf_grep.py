"""Search the source PDFs for the service-history figures. Usage: pdf_grep.py <file> <regex> [max_lines]"""
from pathlib import Path
import re
import sys
from pypdf import PdfReader

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
name, pat = sys.argv[1], sys.argv[2]
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 40
reader = PdfReader(RAW / name)
print(f"== {name}: {len(reader.pages)} pages")
n = 0
for i, page in enumerate(reader.pages):
    lines = (page.extract_text() or "").splitlines()
    for j, line in enumerate(lines):
        if re.search(pat, line, re.I) and n < limit:
            print(f"p{i+1}: {' '.join(l.strip() for l in lines[j:j+3])[:260]}")
            n += 1
