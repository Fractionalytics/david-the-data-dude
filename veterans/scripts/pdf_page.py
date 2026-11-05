"""Print whole pages of a source PDF. Usage: pdf_page.py <file> <page> [page ...]"""
from pathlib import Path
import sys
from pypdf import PdfReader

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
reader = PdfReader(RAW / sys.argv[1])
for p in sys.argv[2:]:
    print(f"\n--- {sys.argv[1]} p{p}\n{reader.pages[int(p) - 1].extract_text()}")
