"""Step 1 recon, round 5: the newsletter archive iframe, and a count of Silver Alert success stories per year.

Fetches 1 archive page + 9 success-story pages (2014-2022), 1s apart.
"""
from pathlib import Path
import re
import time

import httpx
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (research; David the Data Dude)"}
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "recon"
client = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=60)

url = "https://www.fdle.state.fl.us/mcic/AdvisoryBoardNewsletter.aspx"
r = client.get(url)
(OUT / "mcic_AdvisoryBoardNewsletter.html").write_text(r.text, encoding="utf-8")
soup = BeautifulSoup(r.text, "html.parser")
print(f"== {url} {r.status_code} -> {r.url}")
for a in soup.find_all("a", href=True):
    h = a["href"]
    if "getContentAsset" in h or ".pdf" in h.lower() or "newsletter" in (a.get_text() + h).lower():
        print(f"   {a.get_text(' ', strip=True)[:60]} | {h}")

STORY = re.compile(r"(January|February|March|April|May|June|July|August|September|October|November|December) (20\d\d)\s*[—–-]\s*([A-Za-z.\- ]+?) County")
for year in range(2014, 2023):
    time.sleep(1)
    u = f"https://www.fdle.state.fl.us/silver-alert-plan/{year}-success-stories"
    r = client.get(u)
    (OUT / f"silver_success_{year}.html").write_text(r.text, encoding="utf-8")
    text = re.sub(r"\s+", " ", BeautifulSoup(r.text, "html.parser").get_text(" ", strip=True))
    print(f"{year}: HTTP {r.status_code}, {len(STORY.findall(text))} dated county entries")
