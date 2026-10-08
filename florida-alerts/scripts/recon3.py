"""Step 1 recon, round 3: newsletter archive, Silver Alert success stories, per-alert pages, FMCDF PDFs.

One request per URL. Saves raw files to data/raw/recon/; prints text excerpts and links.
"""
from pathlib import Path
import io
import re
import time

import httpx
import pdfplumber
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (research; David the Data Dude)"}
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "recon"
OUT.mkdir(parents=True, exist_ok=True)
URLS = [
    "https://www.fdle.state.fl.us/mcicsearch/ABNewsLetter.asp",
    "http://www.fdle.state.fl.us/Silver-Alert-Plan/Silver-Alert-Plan.aspx",
    "https://www.fdle.state.fl.us/mepic/alerts/silver-alert",
    "https://www.fdle.state.fl.us/mepic/alerts/amber-alert",
    "https://www.fdle.state.fl.us/mepic/about",
    "https://www.fmcdf.org/_files/ugd/f16d03_ae8b768df07044598df37d6032996228.pdf",
    "https://www.fmcdf.org/_files/ugd/bd5f91_93c8113f253e41149f84381028ad49a9.pdf",
]
SKIP_NAV = re.compile(r"facebook|twitter|instagram|youtube|linkedin|mailto:|^#|javascript:|^/(Home|cjstc|contact-us|site-map|open-government)", re.I)

client = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=60)
for url in URLS:
    try:
        r = client.get(url)
    except Exception as e:
        print(f"\n== {url} ERROR {e}")
        continue
    is_pdf = "pdf" in r.headers.get("content-type", "") or url.endswith(".pdf")
    name = re.sub(r"[^A-Za-z0-9]+", "_", url.split("//", 1)[1]).strip("_")[-80:] + (".pdf" if is_pdf else ".html")
    print(f"\n== {url} {r.status_code} -> {r.url} ({len(r.content)} bytes) -> {name}")
    if is_pdf:
        (OUT / name).write_bytes(r.content)
        with pdfplumber.open(io.BytesIO(r.content)) as pdf:
            print(f"PDF pages: {len(pdf.pages)}")
            for i, page in enumerate(pdf.pages[:3]):
                print(f"--- page {i + 1}:", re.sub(r"\s+", " ", page.extract_text() or "")[:900])
    else:
        (OUT / name).write_text(r.text, encoding="utf-8")
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
        print("TEXT:", text[:1500])
        links = sorted({a["href"] for a in soup.find_all("a", href=True) if not SKIP_NAV.search(a["href"])})
        print(f"LINKS ({len(links)}):")
        for h in links[:80]:
            print("  ", h)
    time.sleep(1)
