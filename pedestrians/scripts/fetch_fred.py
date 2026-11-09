"""Download FRED series as CSV (cached; never re-fetched) and print annual means.
For the sedans-to-SUVs project (copied from box-office, 2026-11-05).

    python scripts/fetch_fred.py SERIES [SERIES ...]
      -> data/raw/fred/<SERIES>.csv
"""

import sys
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "fred"
UA = {"User-Agent": "content-engine-research-bot/1.0"}


def main() -> None:
    for sid in sys.argv[1:]:
        dest = OUT / f"{sid}.csv"
        if not dest.exists():
            r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", headers=UA, timeout=60)
            r.raise_for_status()
            dest.write_text(r.text)
        d = pd.read_csv(dest, parse_dates=[0]).set_index("observation_date").iloc[:, 0]
        d = pd.to_numeric(d, errors="coerce")
        a = d.groupby(d.index.year).mean().loc[1998:]
        print(sid, " ".join(f"{y}:{v:.4g}" for y, v in a.items()))


if __name__ == "__main__":
    main()
