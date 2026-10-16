"""Write the numbers every chart in video/ draws, so charts never hard-code data.

Inputs (all built by other scripts in this folder):
  data/raw/oews/oesm{YY}nat.zip, data/processed/exposure_ledger_occupations.csv,
  data/processed/call_centers_ces.csv, ../radiology/data/releases/2026-10-13-reel/cards.json
Output: video/src/data/charts.json

Run from projects/amara/ after exposure_ledger.py and call_centers_ces.py:  python scripts/video_data.py
"""
import json
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
YEARS = [2019, 2022, 2023, 2024, 2025]
LOANS = ["13-2072", "43-4131", "43-9041", "13-2053"]


def oews(year: int) -> pd.Series:
    with zipfile.ZipFile(ROOT / f"data/raw/oews/oesm{str(year)[2:]}nat.zip") as z:
        name = next(n for n in z.namelist() if n.endswith(".xlsx"))
        with z.open(name) as f:
            df = pd.read_excel(f, dtype=str)
    df.columns = [c.upper() for c in df.columns]
    return pd.to_numeric(df.drop_duplicates("OCC_CODE").set_index("OCC_CODE")["TOT_EMP"], errors="coerce")


tot = {y: oews(y) for y in YEARS}
p = pd.read_csv(ROOT / "data/processed/exposure_ledger_occupations.csv", dtype={"soc": str})
g = lambda d, a, b: d[str(b)].sum() / d[str(a)].sum() - 1

# Waterfall (cards 7-10): raw gap -> pre-trend adjustment -> minus loan processing.
def gap(df, adjust):
    vh, rest = df[df.exposure == "Very high"], df[df.exposure != "Very high"]
    ex = g(vh, 2022, 2025) - g(rest, 2022, 2025)
    if adjust:
        ex -= g(vh, 2019, 2022) - g(rest, 2019, 2022)
    return -ex * vh["2022"].sum()

noloans = p[~p.soc.isin(LOANS)]
raw, adj, final = gap(p, False), gap(p, True), gap(noloans, True)

# Card 11: the biggest actual job declines (May 2022 -> May 2025) among very-high-exposure
# occupations, loan processing excluded. (A by-group split of the 870K gap doesn't hold up: groups
# offset each other, e.g. sales grew, so the parts don't honestly sum to the total. See data-challenges.)
SHORT = {"43-4051": "Customer service reps", "43-3031": "Bookkeeping clerks",
         "43-6014": "Secretaries & admin assistants", "43-4171": "Receptionists"}
vh = noloans[noloans.exposure == "Very high"].sort_values("chg_2022_25").head(4)
breakdown = [{"soc": r.soc, "label": SHORT.get(r.soc, r.title), "change": round(r.chg_2022_25),
              "pct": round(r.pct_2022_25, 1)} for r in vh.itertuples()]

# Card 16: office & admin vs. all other jobs, indexed to May 2019 = 100.
office = {y: tot[y]["43-0000"] for y in YEARS}
bench = {y: tot[y]["00-0000"] - tot[y]["43-0000"] for y in YEARS}
line = [{"year": y, "office": round(office[y] / office[2019] * 100, 1), "rest": round(bench[y] / bench[2019] * 100, 1)} for y in YEARS]

# Card 17: slow lane.
cs = lambda soc, a, b: round((tot[b][soc] / tot[a][soc] - 1) * 100, 1)
rad = json.loads((ROOT.parent / "radiology/data/releases/2026-10-13-reel/cards.json").read_text())

# Card 19: call-center industry, same month (series isn't seasonally adjusted).
cc = pd.read_csv(ROOT / "data/processed/call_centers_ces.csv", parse_dates=["date"]).set_index("date")["employment_k"]
a, b = cc[pd.Timestamp("2022-08-01")], cc[pd.Timestamp("2026-08-01")]

out = {
    "benchmark": {"outside_office_pct_2022_25": round((bench[2025] / bench[2022] - 1) * 100, 1)},
    "waterfall": {"raw": round(raw), "pretrend": round(raw - adj), "loans": round(adj - final), "final": round(final)},
    "breakdown": breakdown,
    "officeVsRest": line,
    "slowLane": {"paralegals_pct_2022_25": cs("23-2011", 2022, 2025), "lawyers_pct_2022_25": cs("23-1011", 2022, 2025),
                  "radiologists_medicare_pct_2016_24": rad["medicare"]["radiologists"],
                  "physicians_medicare_pct_2016_24": rad["medicare"]["physicians"], "radiology_reading_share_pct": 36},
    "callCenters": {"from": "Aug 2022", "to": "Aug 2026", "from_k": a, "to_k": b, "pct": round((b / a - 1) * 100)},
}
dest = ROOT / "video/src/data/charts.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
