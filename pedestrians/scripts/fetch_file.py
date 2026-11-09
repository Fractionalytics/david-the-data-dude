"""Download one public file into data/raw/<name> (cached; never
re-fetched). For the sedans-to-SUVs project (copied from box-office, 2026-11-05).

    python scripts/fetch_file.py URL NAME
"""

import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "content-engine-research-bot/1.0"}


def main() -> None:
    url, name = sys.argv[1], sys.argv[2]
    dest = ROOT / "data" / "raw" / name
    if dest.exists():
        print("cached", dest)
        return
    r = requests.get(url, headers=UA, timeout=120)
    print(r.status_code, r.headers.get("content-type"), len(r.content))
    if r.status_code in (403, 429):
        raise SystemExit("blocked, stopping")
    r.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)
    print("saved", dest)


if __name__ == "__main__":
    main()
