"""List Wayback Machine snapshots of the lost FDLE pages (Silver Alert monthly reports, newsletter archive).

Uses the CDX index API: one request per URL pattern, no page downloads. Writes data/raw/wayback/cdx_*.json.
Stops on any non-200 (e.g. 429) instead of retrying.
"""
from pathlib import Path
import json
import sys
import time

import httpx

HEADERS = {"User-Agent": "Mozilla/5.0 (research; David the Data Dude)"}
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "wayback"
OUT.mkdir(parents=True, exist_ok=True)
CDX = "https://web.archive.org/cdx/search/cdx"
QUERIES = {
    "silver_monthly": "fdle.state.fl.us/Silver-Alert-Plan/Monthly-Reports*",
    "newsletter_archive": "fdle.state.fl.us/MCIC/AdvisoryBoardNewsletter*",
    "silver_pdfs": "fdle.state.fl.us/Silver-Alert-Plan/Documents/*",
    "mcic_pdfs": "fdle.state.fl.us/MCIC/Documents/*",
    "mepic_docs": "fdle.state.fl.us/MEPIC/Documents/*",
}

client = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=90)
for key, pattern in QUERIES.items():
    if (OUT / f"cdx_{key}.json").exists():
        continue
    params = {"url": pattern, "output": "json", "fl": "timestamp,original,statuscode,mimetype",
              "filter": "statuscode:200", "collapse": "urlkey"}
    r = client.get(CDX, params=params)
    print(f"== {key}: {pattern} HTTP {r.status_code}")
    if r.status_code != 200:
        print("Stopping: non-200 from the Wayback index.", r.text[:300])
        sys.exit(1)
    rows = r.json()[1:] if r.text.strip() else []
    (OUT / f"cdx_{key}.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print(f"   {len(rows)} distinct URLs")
    for ts, orig, _, mime in rows[:40]:
        print(f"   {ts[:8]} {mime:22} {orig}")
    time.sleep(2)
