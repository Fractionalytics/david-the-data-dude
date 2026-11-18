"""How the US-vs-EU pedestrian gap splits, year by year, and how much the answer depends on method.

    python scripts/gap_split_over_time.py
      reads  data/final/us_eu_decompose.csv   (from scripts/us_eu_decompose.py)
      writes data/final/gap_split_over_time.csv

Two methods, both per 100,000 people, "other road users" = everyone killed on the road who isn't a pedestrian.
- Additive (the 60/40 in docs/research-drugs/pedestrian-link.md): if US pedestrians had tracked other US road
  users since the base year, their rate would be ped_base * other_now / other_base. Actual minus that is the
  "break-away"; that minus the EU pedestrian rate is the "general" part.
- Ratio: US/EU pedestrian ratio = (US/EU other-road-user ratio) x (pedestrian-specific factor), where the
  pedestrian-specific factor = (US ped/other) / (EU ped/other). Shares of the CHANGE since the base year are
  log shares.
"""
from math import log
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
d = pd.read_csv(ROOT / "data" / "final" / "us_eu_decompose.csv")
r = d.pivot_table(index="year", columns=["geo", "group"], values="rate_per_100k")
usp, uso = r[("US", "pedestrian")], r[("US", "other road users")]
eup, euo = r[("EU fixed", "pedestrian")], r[("EU fixed", "other road users")]

rows = []
for y in range(2009, 2025):
    row = dict(year=y, us_ped=usp[y], eu_ped=eup[y], us_other=uso[y], eu_other=euo[y], gap=usp[y] - eup[y])
    for base in (2000, 2009):
        cf = usp[base] * uso[y] / uso[base]
        row[f"breakaway_share_base{base}"] = (usp[y] - cf) / row["gap"]
    row["general_ratio"] = uso[y] / euo[y]
    row["ped_specific_ratio"] = (usp[y] / uso[y]) / (eup[y] / euo[y])
    if y > 2009:
        ch = log((usp[y] / eup[y]) / (usp[2009] / eup[2009]))
        row["ped_specific_share_of_change_since_2009"] = log(row["ped_specific_ratio"] / rows[0]["ped_specific_ratio"]) / ch
    rows.append(row)
out = pd.DataFrame(rows)
out.to_csv(ROOT / "data" / "final" / "gap_split_over_time.csv", index=False)
pd.options.display.float_format = "{:.2f}".format
print(out.to_string(index=False))
