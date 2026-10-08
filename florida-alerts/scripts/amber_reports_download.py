"""Download the 19 national AMBER Alert annual reports (2006-2024) linked from amberalert.ojp.gov/statistics.

Checks missingkids.org's robots.txt for the PDF path first. 2s between requests; skips files already on disk;
stops on 429/5xx. Saves to data/raw/amber/<year>_amber_report.pdf.
"""
from pathlib import Path
import re
import sys
import time
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (research; David the Data Dude)"}
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "amber"
client = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=120)

robots = client.get("https://www.missingkids.org/robots.txt").text
blocked = [l for l in robots.splitlines() if l.lower().startswith("disallow") and re.search(r"content|dam|pdf", l, re.I)]
print("missingkids.org robots.txt disallow lines touching content/dam/pdf:", blocked or "none")
SKIP_HOSTS = ("missingkids.org",) if any(re.search(r"/content/dam|\.pdf", l) for l in blocked) else ()
# missingkids.org disallows /content/dam/missingkids/pdfs/ (checked 2026-10-07), so those years are skipped here.
# David can download them by hand in a browser into data/raw/amber/<year>_amber_report.pdf.

soup = BeautifulSoup((OUT / "statistics.html").read_text(encoding="utf-8"), "html.parser")
links = {}
for a in soup.find_all("a", href=True):
    m = re.fullmatch(r"(20\d\d) AMBER Alert Report", a.get_text(" ", strip=True))
    if m:
        links[int(m.group(1))] = urljoin("https://amberalert.ojp.gov/statistics", a["href"])

for year, url in sorted(links.items()):
    path = OUT / f"{year}_amber_report.pdf"
    if path.exists():
        continue
    if any(h in url for h in SKIP_HOSTS):
        print(f"{year}: skipped (robots.txt disallows) {url}")
        continue
    r = client.get(url)
    if r.status_code == 429 or r.status_code >= 500:
        sys.exit(f"Stopping at {year}: HTTP {r.status_code}")
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        print(f"{year}: not a PDF (HTTP {r.status_code}) {url}")
    else:
        path.write_bytes(r.content)
        print(f"{year}: ok ({len(r.content) // 1024} KB)")
    time.sleep(2)
print(f"{len(list(OUT.glob('*_amber_report.pdf')))} of {len(links)} reports on disk")
