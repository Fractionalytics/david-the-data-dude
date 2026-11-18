"""Numbers for Reel 2's Remotion clips (video/src/reel2/assets.json).

    python scripts/prep_reel2_assets.py

Card 12: meth (T43.6) overdose deaths per million by state, 2009 / 2016 / 2024
(data/final/meth_per_million_state_year.csv, from scripts/meth_per_million_state_year.py),
placed on the tile grid in scripts/tilegrid.py. Suppressed state-years (under 10 deaths) are null.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from tilegrid import GRID  # noqa: E402

YEARS = [2009, 2016, 2024]
d = pd.read_csv(ROOT / "data" / "final" / "meth_per_million_state_year.csv")
d = d[d.year.isin(YEARS)]
tiles = []
for ab, (c, r) in GRID.items():
    s = d[d.abbr == ab].set_index("year")
    tiles.append({"abbr": ab, "col": c, "row": r,
                  "v": [None if bool(s.loc[y, "suppressed"]) else float(s.loc[y, "per_million"]) for y in YEARS]})
nat = [round(float(g.deaths.sum() / g.population.sum() * 1e6), 1) for _, g in d.groupby("year")]
out = {"methMap": {"years": YEARS, "national": nat, "tiles": tiles}}

# Cards 35-36: the 13x split into pieces, US 2024 on Europe's definition. The three named slices come from
# data/final/gap_14x_breakdown.csv (scripts/gap_14x_breakdown.py, US definition). Europe's definition only drops
# deaths that name no narcotic or stimulant, and those all sit in "everything else", so that slice is the
# Europe-definition total (74,362 deaths, data/raw/cdc_wonder/SOURCE.md, 2026-11-14) minus the other three.
EUROPE, EU_DEF_TOTAL = 16.7, 74362
b = pd.read_csv(ROOT / "data" / "final" / "gap_14x_breakdown.csv").set_index("slice")
pop = b.loc["fentanyl + stimulant", "deaths"] / b.loc["fentanyl + stimulant", "per_million"] * 1e6
named = ["fentanyl + stimulant", "fentanyl, no stimulant", "stimulant, no fentanyl"]
rest = EU_DEF_TOTAL - b.loc[named, "deaths"].sum()
split = [{"slice": s, "deaths": int(b.loc[s, "deaths"]), "per_million": round(float(b.loc[s, "per_million"]), 2)} for s in named]
split.append({"slice": "everything else", "deaths": int(rest), "per_million": round(float(rest / pop * 1e6), 2)})
for s in split:
    s["x_europe"] = round(s["per_million"] / EUROPE, 2)
total = sum(s["per_million"] for s in split)
out["split"] = {"europe": EUROPE, "us": round(total, 1), "x": round(total / EUROPE, 2), "slices": split}

# Cards 44-45: Deadly Pair deaths (MCD T40.4 AND (T40.5 or T43.6)), 2010-2020 from the 1999-2020 database,
# 2021-2024 from the 2018-2024 one (the overlap 2018-2020 matches exactly).
W = ROOT / "data" / "raw" / "cdc_wonder"
tr = pd.concat([pd.read_csv(W / "wonder_fent_and_stim_2010_2020.csv"), pd.read_csv(W / "wonder_fent_and_stim_2018_2024.csv")])
tr = tr[tr.Notes.isna() & tr["Year Code"].notna()].drop_duplicates("Year Code")
out["deadlyPair"] = [{"year": int(r["Year Code"]), "deaths": int(r.Deaths)} for _, r in tr.sort_values("Year Code").iterrows()]
print("split", [(s["slice"], s["x_europe"]) for s in split], out["split"]["x"])
print("deadly pair", [(r["year"], r["deaths"]) for r in out["deadlyPair"]])
p = ROOT / "video" / "src" / "reel2" / "assets.json"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(out, indent=1))
print(p, len(tiles), "tiles; national", nat)
