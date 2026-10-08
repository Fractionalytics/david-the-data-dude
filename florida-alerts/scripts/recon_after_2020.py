"""Hunt for Silver Alert numbers after 2020.

1. FDLE anniversary news releases (cumulative issued / direct recoveries), incl. FDLE news listings for 2023-2025.
2. Success-story pages for 2023-2025 on FDLE's site.
3. Wayback index retries: MEPIC newsletter folder, and the new-site monthly-reports page.
All requests 1-2s apart; Wayback stops on any non-200.
"""
from pathlib import Path
import json
import re
import time

import httpx
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (research; David the Data Dude)"}
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "after_2020"
OUT.mkdir(parents=True, exist_ok=True)
client = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=90)
STAT = re.compile(r"[^.]*\b(Silver Alerts?|recover(?:y|ies))\b[^.]*\d[^.]*\.", re.I)


def text_of(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" ", strip=True))


def save(name, r):
    (OUT / name).write_text(r.text, encoding="utf-8")


print("== 1. Anniversary releases")
for url in ["https://www.fdle.state.fl.us/news/2015/october/florida-celebrates-seven-years-of-the-silver-alert-program",
            "https://www.fdle.state.fl.us/news/2022/october/fdle-issues-3-000-florida-silver-alerts-in-14-year-history"]:
    r = client.get(url)
    save(url.rsplit("/", 1)[1][:60] + ".html", r)
    print(f"\n{r.status_code} {url}")
    for s in STAT.findall(text_of(r.text)) and [m.group(0) for m in STAT.finditer(text_of(r.text))][:6]:
        print("   ", s.strip()[:300])
    time.sleep(1)

for year in (2023, 2024, 2025, 2026):
    for month in ("october", "november"):
        url = f"https://www.fdle.state.fl.us/news/{year}/{month}"
        r = client.get(url)
        links = sorted({a["href"] for a in BeautifulSoup(r.text, "html.parser").find_all("a", href=True)
                        if re.search(r"silver", a["href"] + a.get_text(), re.I) and "/news/" in a["href"]})
        print(f"\n{r.status_code} {url}: {len(links)} Silver links {links[:5]}")
        time.sleep(1)

print("\n== 2. Success stories after 2022")
for year in (2023, 2024, 2025):
    r = client.get(f"https://www.fdle.state.fl.us/silver-alert-plan/{year}-success-stories")
    print(f"{year}: HTTP {r.status_code}")
    time.sleep(1)

print("\n== 3. Wayback index retries")
for key, pattern in {"mepic_docs": "fdle.state.fl.us/MEPIC/Documents/*",
                     "monthly_reports_new": "fdle.state.fl.us/silver-alert-plan/monthly-reports",
                     "silver_news": "fdle.state.fl.us/news/*silver*"}.items():
    params = {"url": pattern, "output": "json", "fl": "timestamp,original,statuscode,mimetype", "filter": "statuscode:200"}
    if key != "silver_news":
        params["collapse"] = "urlkey" if key == "mepic_docs" else "digest"
    else:
        params.update({"url": "fdle.state.fl.us/news/", "matchType": "prefix", "collapse": "urlkey"})
    r = client.get("https://web.archive.org/cdx/search/cdx", params=params)
    print(f"{key}: HTTP {r.status_code}")
    if r.status_code != 200:
        print("   stopping Wayback queries")
        break
    rows = r.json()[1:] if r.text.strip() else []
    if key == "silver_news":
        rows = [x for x in rows if "silver" in x[1].lower()]
    (OUT / f"cdx_{key}.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print(f"   {len(rows)} rows")
    for ts, orig, _, mime in rows[:30]:
        print(f"   {ts[:8]} {mime:18} {orig}")
    time.sleep(3)
