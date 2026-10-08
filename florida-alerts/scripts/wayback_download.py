"""Download the archived Silver Alert monthly-report PDFs (2011-2020) from the Wayback Machine.

Approved by David 2026-10-07: all 120, ~3s apart. Stops on 429/503 or any non-200; rerun to resume
(already-downloaded files are skipped). Uses the id_ URL form to get the original bytes without the Wayback banner.
"""
from pathlib import Path
import json
import re
import sys
import time

import httpx

HEADERS = {"User-Agent": "Mozilla/5.0 (research; David the Data Dude)"}
ROOT = Path(__file__).resolve().parents[1] / "data" / "raw"
OUT = ROOT / "silver_monthly_pdfs"
OUT.mkdir(parents=True, exist_ok=True)

rows = json.loads((ROOT / "wayback" / "cdx_silver_monthly.json").read_text(encoding="utf-8"))
pdfs = [(ts, orig) for ts, orig, _, mime in rows if mime == "application/pdf"]
print(f"{len(pdfs)} PDFs in index")

client = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=120)
fetched = 0
for ts, orig in pdfs:
    name = re.sub(r"[^A-Za-z0-9]+", "_", orig.split("Monthly-Reports/", 1)[1]).strip("_") + ".pdf"
    path = OUT / name
    if path.exists():
        continue
    r = client.get(f"https://web.archive.org/web/{ts}id_/{orig}")
    fetched += 1
    if r.status_code == 404:
        print(f"MISSING {name}: archived snapshot not retrievable (404)")
        time.sleep(3)
        continue
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        print(f"STOP at {name}: HTTP {r.status_code}, starts {r.content[:20]!r}. Fetched {fetched} this run.")
        sys.exit(1)
    path.write_bytes(r.content)
    print(f"ok {name} ({len(r.content)} bytes)")
    time.sleep(3)
print(f"Done. Fetched {fetched} this run; {len(list(OUT.glob('*.pdf')))} PDFs on disk.")
