"""Download the inputs for H11 / P14 (speed cameras), all from census.gov.

    python scripts/fetch_h11.py
      writes data/raw/census_places/sub-est00int.csv      place population 2000-2010 (intercensal)
             data/raw/census_places/SUB-EST2020_ALL.csv   place population 2010-2020 (Vintage 2020)
             data/raw/census_places/sub-est2024.csv       place population 2020-2024 (Vintage 2024)
             data/raw/census_places/acs5_2012_place_<SS>.json  poverty, ACS 2008-12
             data/raw/tiger/tl_2010_<SS>_place10.zip      2010 place boundaries (only states that
                                                          have a 2010 city of 250,000+)
One request at a time, honest bot User-Agent, stops on 403/429 or an HTML reply.
"""

import json
import os
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
PLACES = ROOT / "data" / "raw" / "census_places"
TIGER = ROOT / "data" / "raw" / "tiger"
UA = {"User-Agent": "content-engine-research-bot/1.0 (data journalism)"}
POP = {
    "sub-est00int.csv": "https://www2.census.gov/programs-surveys/popest/datasets/2000-2010/intercensal/cities/sub-est00int.csv",
    "SUB-EST2020_ALL.csv": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/cities/SUB-EST2020_ALL.csv",
    "sub-est2024.csv": "https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/cities/totals/sub-est2024.csv",
}


def get(url: str) -> requests.Response:
    r = requests.get(url, headers=UA, timeout=300)
    print(r.status_code, r.headers.get("content-type"), len(r.content), url.split("?")[0], flush=True)
    if r.status_code in (403, 429) or "text/html" in (r.headers.get("content-type") or ""):
        raise SystemExit(f"blocked or not data ({r.status_code}), stopping: {url.split('?')[0]}")
    r.raise_for_status()
    return r


def big_city_states() -> list[str]:
    p = pd.read_csv(PLACES / "SUB-EST2020_ALL.csv", encoding="latin-1", dtype={"STATE": str, "PLACE": str})
    p = p[(p.SUMLEV == 162)]
    p["CENSUS2010POP"] = pd.to_numeric(p.CENSUS2010POP, errors="coerce")  # some rows carry "A" (annexation) flags
    return sorted(p.loc[p.CENSUS2010POP >= 250_000, "STATE"].unique())


def main() -> None:
    load_dotenv(ROOT.parents[1] / ".env")
    PLACES.mkdir(parents=True, exist_ok=True)
    for name, url in POP.items():
        if not (PLACES / name).exists():
            (PLACES / name).write_bytes(get(url).content)
            time.sleep(1)
    states = big_city_states()
    print("states with a 2010 city of 250,000+:", states, len(states))
    key = os.environ.get("CENSUS_DATA_API_KEY")
    if not key:
        raise SystemExit("add CENSUS_DATA_API_KEY to the root .env")
    for s in states:
        dest = TIGER / f"tl_2010_{s}_place10.zip"
        if not dest.exists():
            dest.write_bytes(get(f"https://www2.census.gov/geo/tiger/TIGER2010/PLACE/2010/{dest.name}").content)
            time.sleep(1)
        acs = PLACES / f"acs5_2012_place_{s}.json"
        if not acs.exists():
            url = (f"https://api.census.gov/data/2012/acs/acs5?get=NAME,B01003_001E,B17001_001E,B17001_002E"
                   f"&for=place:*&in=state:{s}&key={key}")
            acs.write_text(json.dumps(get(url).json()))
            time.sleep(1)


if __name__ == "__main__":
    main()
