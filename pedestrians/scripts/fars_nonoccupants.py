"""US deaths of pedestrians and people on personal conveyances (wheelchairs,
skateboards, scooters), 2000-2024, from FARS. The international databases count
both as pedestrians, so this is the US series to compare with Europe.

    python scripts/fars_nonoccupants.py   (needs data/raw/fars/*.zip; see fetch_fars.py)
      -> data/final/fars_nonoccupant_deaths.csv   year, pedestrian, personal_conveyance, ped_plus_conveyance

FARS PERSON file, INJ_SEV = 4 (fatal): PER_TYP 5 = pedestrian, 8 = person on a
personal conveyance. In 2020 and 2021 only, code 8 was split into 11 (motorized),
12 (non-motorized) and 13 (unknown); those are counted as conveyances too.
Checked against CDC MMWR 74(8): 2013 gives 4,911 deaths, 1.55 per 100,000, the
CDC's rate.
"""

from pathlib import Path

import pandas as pd

from fars_pedestrians import load

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    rows = []
    for year in range(2000, 2025):
        p = load(year, "person", ["PER_TYP", "INJ_SEV"])
        dead = p[p.INJ_SEV == 4].PER_TYP
        rows.append({"year": year, "pedestrian": int((dead == 5).sum()), "personal_conveyance": int(dead.isin([8, 11, 12, 13]).sum())})
    d = pd.DataFrame(rows)
    d["ped_plus_conveyance"] = d.pedestrian + d.personal_conveyance
    d.to_csv(ROOT / "data" / "final" / "fars_nonoccupant_deaths.csv", index=False)
    print(d.to_string(index=False))


if __name__ == "__main__":
    main()
