"""Find live MEPIC "Missing & Endangered" newsletters on fdle.state.fl.us by trying /MEPIC/Documents/<year>-<season>.

32 requests (2019-2026 x 4 seasons), 1s apart. Saves any PDF found to data/raw/newsletters/.
"""
from pathlib import Path
import time

import httpx

HEADERS = {"User-Agent": "Mozilla/5.0 (research; David the Data Dude)"}
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "newsletters"
OUT.mkdir(parents=True, exist_ok=True)

client = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=60)
for year in range(2019, 2027):
    for season in ("Spring", "Summer", "Fall", "Winter"):
        slug = f"{year}-{season}"
        path = OUT / f"{slug}.pdf"
        if path.exists():
            print(f"have {slug}")
            continue
        r = client.get(f"https://www.fdle.state.fl.us/MEPIC/Documents/{slug}")
        is_pdf = r.content.startswith(b"%PDF")
        print(f"{slug}: HTTP {r.status_code} {'PDF' if is_pdf else ''}")
        if is_pdf:
            path.write_bytes(r.content)
        time.sleep(1)
