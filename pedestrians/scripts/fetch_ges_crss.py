"""Download NHTSA GES (2009-2015) and CRSS (2016-2024) files for P24 into data/raw/ges_crss/ (cached; never
re-fetched), one request at a time, 3 s apart. Stops on 403/429. Same host as FARS (static.nhtsa.gov).
File names come from the bucket listing (https://static.nhtsa.gov/?prefix=nhtsa/downloads/GES/GES12/).

    python scripts/fetch_ges_crss.py
"""
import time
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "ges_crss"
UA = {"User-Agent": "content-engine-research-bot/1.0"}
BASE = "https://static.nhtsa.gov/nhtsa/downloads/"
FILES = {
    2009: "GES/GES09/GES09 FlatFile.zip",
    2010: "GES/GES10/GES10_flatfile.zip",
    2011: "GES/GES11/GES11_Flatfile.zip",
    2012: "GES/GES12/GES12_Flatfile.zip",
    2013: "GES/GES13/GES13_Flatfile.zip",
    2014: "GES/GES14/GES2014flat.zip",
    2015: "GES/GES15/GES2015csv.zip",
    **{y: f"CRSS/{y}/CRSS{y}CSV.zip" for y in range(2016, 2025)},
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for y, path in FILES.items():
        dest = OUT / f"{'GES' if y < 2016 else 'CRSS'}{y}.zip"
        if dest.exists():
            print("cached", dest.name)
            continue
        r = requests.get(BASE + quote(path), headers=UA, timeout=600)
        print(y, r.status_code, r.headers.get("content-type"), len(r.content), flush=True)
        if r.status_code in (403, 429):
            raise SystemExit("blocked, stopping")
        if r.status_code == 200 and r.content[:2] == b"PK":
            dest.write_bytes(r.content)
        time.sleep(3)


if __name__ == "__main__":
    main()
