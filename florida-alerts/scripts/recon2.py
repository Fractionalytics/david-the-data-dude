"""Step 1 recon, round 2: fetch the per-alert-type pages and publication pages found in round 1.

One request per page. Saves raw HTML to data/raw/recon/ and prints a text excerpt plus links.
"""
from pathlib import Path
import re
import time

import httpx
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (research; David the Data Dude)"}
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "recon"
OUT.mkdir(parents=True, exist_ok=True)
PAGES = [
    "https://www.fdle.state.fl.us/mcicsearch/AllAlerts.asp",
    "https://www.fdle.state.fl.us/mcicsearch/Amber.asp",
    "https://www.fdle.state.fl.us/mcicsearch/SilverAlerts.asp",
    "https://www.fdle.state.fl.us/mcicsearch/PurpleAlerts.asp",
    "https://www.fdle.state.fl.us/mcicsearch/MCApage.asp",
    "https://www.fdle.state.fl.us/mcicsearch/Search.asp",
    "https://www.fdle.state.fl.us/mepic/publications",
    "https://www.fdle.state.fl.us/mepic/alerts",
    "https://www.fmcdf.org/advisory-board-newsletter",
]
SKIP_NAV = re.compile(r"facebook|twitter|instagram|youtube|linkedin|mailto:|^#|javascript:", re.I)

client = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=30)
for url in PAGES:
    try:
        r = client.get(url)
    except Exception as e:
        print(f"\n== {url} ERROR {e}")
        continue
    name = re.sub(r"[^A-Za-z0-9]+", "_", url.split("//", 1)[1]).strip("_") + ".html"
    (OUT / name).write_text(r.text, encoding="utf-8")
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    print(f"\n== {url} {r.status_code} ({len(r.text)} chars) -> {name}")
    print("TEXT:", text[:1200])
    links = {a["href"] for a in soup.find_all("a", href=True) if not SKIP_NAV.search(a["href"])}
    print(f"LINKS ({len(links)}):")
    for h in sorted(links)[:60]:
        print("  ", h)
    time.sleep(1)
