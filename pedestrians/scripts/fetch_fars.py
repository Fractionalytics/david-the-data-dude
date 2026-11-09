"""Download FARS national CSV zips into data/raw/fars/ (cached; never
re-fetched), one request at a time, 3 s apart. Stops on 403/429.

    python scripts/fetch_fars.py 2000 2024
      -> data/raw/fars/FARS<YEAR>NationalCSV.zip
"""

import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "fars"
UA = {"User-Agent": "content-engine-research-bot/1.0"}
URL = "https://static.nhtsa.gov/nhtsa/downloads/FARS/{y}/National/FARS{y}NationalCSV.zip"


def main() -> None:
    first, last = int(sys.argv[1]), int(sys.argv[2])
    OUT.mkdir(parents=True, exist_ok=True)
    for y in range(first, last + 1):
        dest = OUT / f"FARS{y}NationalCSV.zip"
        if dest.exists():
            print("cached", dest.name)
            continue
        r = requests.get(URL.format(y=y), headers=UA, timeout=600)
        print(y, r.status_code, r.headers.get("content-type"), len(r.content), flush=True)
        if r.status_code in (403, 429):
            raise SystemExit("blocked, stopping")
        if r.status_code == 200 and r.content[:2] == b"PK":
            dest.write_bytes(r.content)
        time.sleep(3)


if __name__ == "__main__":
    main()
