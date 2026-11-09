"""Download whole Eurostat datasets as SDMX-CSV from the free dissemination API
(cached; never re-fetched) and print their dimensions and year range.

    python scripts/fetch_eurostat.py DATASET [DATASET ...]
      -> data/raw/eurostat/<DATASET>.csv
"""

import sys
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "eurostat"
UA = {"User-Agent": "content-engine-research-bot/1.0"}
API = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{}/?format=SDMX-CSV&compressed=false"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for ds in sys.argv[1:]:
        dest = OUT / f"{ds}.csv"
        if not dest.exists():
            r = requests.get(API.format(ds), headers=UA, timeout=300)
            print(ds, r.status_code, len(r.content))
            if r.status_code in (403, 429):
                raise SystemExit("blocked, stopping")
            r.raise_for_status()
            dest.write_bytes(r.content)
        d = pd.read_csv(dest, low_memory=False)
        print(ds, d.shape, "years", d.TIME_PERIOD.min(), "-", d.TIME_PERIOD.max())
        for c in d.columns:
            if c not in ("DATAFLOW", "LAST UPDATE", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "geo"):
                print("  ", c, sorted(d[c].astype(str).unique())[:30])


if __name__ == "__main__":
    main()
