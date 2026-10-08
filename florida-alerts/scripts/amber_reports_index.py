"""List the national AMBER Alert annual reports (NCMEC for DOJ) linked from amberalert.ojp.gov/statistics.

Checks robots.txt for amberalert.ojp.gov and ojjdp.ojp.gov, then prints every report/PDF link on the statistics
page. No downloads. Saves the page to data/raw/amber/statistics.html.
"""
from pathlib import Path
import re

import httpx
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (research; David the Data Dude)"}
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "amber"
OUT.mkdir(parents=True, exist_ok=True)
client = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=60)

for host in ("https://amberalert.ojp.gov", "https://ojjdp.ojp.gov"):
    r = client.get(f"{host}/robots.txt")
    rules = [l for l in r.text.splitlines() if l.lower().startswith(("user-agent", "disallow", "crawl-delay"))]
    print(f"== {host}/robots.txt {r.status_code}: {len(rules)} rule lines")
    for line in rules:
        if re.search(r"user-agent: \*|disallow: .*(pdf|files|media|document|statistic|library)|crawl", line, re.I):
            print("  ", line)

r = client.get("https://amberalert.ojp.gov/statistics")
(OUT / "statistics.html").write_text(r.text, encoding="utf-8")
soup = BeautifulSoup(r.text, "html.parser")
main = soup.find("main") or soup
print(f"\n== statistics page {r.status_code}")
print(re.sub(r"\s+", " ", main.get_text(" ", strip=True))[:1500])
print("\nLinks:")
for a in main.find_all("a", href=True):
    text = a.get_text(" ", strip=True)
    if re.search(r"report|\.pdf|20\d\d", text + a["href"], re.I):
        print(f"   {text[:70]} | {a['href']}")
