"""Step 1 recon, round 4: Silver Alert monthly reports + one success-stories page; grep the newsletter PDF for stats.

Fetches 2 pages. Lists every link on the monthly-reports page (likely PDFs).
"""
from pathlib import Path
import re

import httpx
import pdfplumber
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (research; David the Data Dude)"}
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "recon"
client = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=60)

for url in ["https://www.fdle.state.fl.us/silver-alert-plan/monthly-reports",
            "https://www.fdle.state.fl.us/silver-alert-plan/2022-success-stories"]:
    r = client.get(url)
    name = re.sub(r"[^A-Za-z0-9]+", "_", url.split("//", 1)[1]).strip("_") + ".html"
    (OUT / name).write_text(r.text, encoding="utf-8")
    soup = BeautifulSoup(r.text, "html.parser")
    main = soup.find("main") or soup.find(id=re.compile("content", re.I)) or soup
    for tag in main(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    text = re.sub(r"\s+", " ", main.get_text(" ", strip=True))
    print(f"\n== {url} {r.status_code} ({len(r.text)} chars)")
    i = text.find("Monthly Reports") if "monthly" in url else text.find("Success Stories")
    print("TEXT:", text[max(0, i):i + 2500])
    links = [(a.get_text(" ", strip=True), a["href"]) for a in main.find_all("a", href=True)
             if "getContentAsset" in a["href"] or a["href"].lower().endswith(".pdf")]
    print(f"DOC LINKS ({len(links)}):")
    for t, h in links:
        print(f"   {t[:60]} | {h}")

pdf_path = OUT / "www_fmcdf_org_files_ugd_bd5f91_93c8113f253e41149f84381028ad49a9_pdf.pdf"
print("\n== Newsletter Summer 2026: lines mentioning stats")
with pdfplumber.open(pdf_path) as pdf:
    for n, page in enumerate(pdf.pages, 1):
        for line in (page.extract_text() or "").splitlines():
            if re.search(r"recover|located|found|activat|issued|statistic|\b20\d\d\b.*alert|alerts? (in|during)", line, re.I):
                print(f"p{n}: {line}")
