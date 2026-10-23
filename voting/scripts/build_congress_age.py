"""Average age of members of Congress at the start of each Congress, 1901-2025.

Input: data/raw/legislators-{historical,current}.yaml from the unitedstates/congress-legislators
project (public domain, CC0), downloaded 2026-10-22.

Membership: everyone holding a House or Senate seat for one of the 50 states on December 31 of each
Congress's first year. (Early terms are dated from the first session, e.g. December 2, 1901 or
April 11, 1921, so an earlier snapshot misses them.) Age is measured at the Congress's official start:
March 4 before 1935, January 3 after. Members who left or arrived mid-year are counted as of Dec 31.
Non-voting delegates (DC, territories) are excluded. Members with no birthday on file are dropped and counted.

Output: data/processed/congress_age.csv, one row per Congress and chamber (House, Senate, All).
"""
from datetime import date
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed"
STATES = set("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ "
             "NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())

people = []
for f in ["legislators-historical.yaml", "legislators-current.yaml"]:
    people += yaml.safe_load((RAW / f).read_text(encoding="utf-8"))

rows = []
for congress in range(57, 120):  # 57th began 1901, 119th began 2025
    year = 1787 + 2 * congress
    snap = date(year, 12, 31)
    start = date(year, 1, 3) if year >= 1935 else date(year, 3, 4)
    for p in people:
        for t in p.get("terms", []):
            if t["state"] in STATES and date.fromisoformat(t["start"]) <= snap <= date.fromisoformat(t["end"]):
                bday = p.get("bio", {}).get("birthday")
                age = (start - date.fromisoformat(bday)).days / 365.25 if bday else None
                rows.append({"congress": congress, "year": year, "chamber": "House" if t["type"] == "rep" else "Senate",
                             "bioguide": p["id"]["bioguide"], "age": age})
                break

m = pd.DataFrame(rows)
missing = m.age.isna().sum()
m = m.dropna(subset=["age"])
both = m.assign(chamber="All")
out = (pd.concat([m, both]).groupby(["congress", "year", "chamber"])
       .agg(members=("age", "size"), mean_age=("age", "mean"), median_age=("age", "median"),
            share_65_plus=("age", lambda a: (a >= 65).mean() * 100))
       .round(1).reset_index())
out.to_csv(OUT / "congress_age.csv", index=False)
print(f"{len(m)} member-snapshots, {missing} dropped for missing birthday")
print(out[out.year >= 2015].to_string(index=False))
