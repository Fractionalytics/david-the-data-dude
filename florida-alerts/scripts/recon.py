"""Step 1 recon: check robots.txt and list alert-related links on the landing pages.

Fetches a handful of pages only. No crawling.
"""
import httpx
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (research; David the Data Dude)"}
ROBOTS = ["https://www.fdle.state.fl.us/robots.txt", "https://www.fmcdf.org/robots.txt"]
PAGES = [
    "https://www.fdle.state.fl.us/mepic",
    "https://www.fdle.state.fl.us/MCICSearch/",
    "https://www.fmcdf.org/florida-alerts",
]
KEYWORDS = ("alert", "mepic", "missing", "amber", "silver", "purple", "pdf", "document",
            "newsletter", "report", "search", "getcontent", "statistic", "annual")

client = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=30)

for url in ROBOTS:
    try:
        r = client.get(url)
        print(f"== {url} {r.status_code} -> {r.url}")
        print(r.text[:1500])
    except Exception as e:
        print(f"== {url} ERROR {e}")

for url in PAGES:
    try:
        r = client.get(url)
        print(f"\n== {url} {r.status_code} -> {r.url} ({len(r.text)} chars)")
        soup = BeautifulSoup(r.text, "html.parser")
        print("TITLE:", soup.title.string.strip() if soup.title and soup.title.string else None)
        for a in soup.find_all("a", href=True):
            text = a.get_text(" ", strip=True)[:70]
            if any(k in (text + a["href"]).lower() for k in KEYWORDS):
                print(f"   {text} | {a['href']}")
    except Exception as e:
        print(f"== {url} ERROR {e}")
