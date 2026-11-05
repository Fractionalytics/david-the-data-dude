"""Veteran tables from ACS 2024 1-year PUMS (person weights only, no replicate-weight margins yet).

MIL: 1 now on active duty, 2 past active duty, 3 Reserve/Guard training only, 4 never served.
ACS counts MIL=2 as veterans. MIL=3 is the only national count of Guard/Reserve-only service.
"""
from pathlib import Path
import zipfile
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ZIP = ROOT / "data" / "raw" / "cache" / "acs2024_pums_csv_pus.zip"
OUT = ROOT / "data"
# Labels are from PUMS_Data_Dictionary_2024.txt. The 2024 file merged and relabelled these columns, so earlier years' meanings don't apply.
PERIODS = {"MLPA": "Sep 2001 or later", "MLPB": "Aug 1990-Aug 2001", "MLPCD": "Jun 1975-Jul 1990", "MLPE": "Aug 1964-May 1975 (Vietnam)",
           "MLPFG": "Feb 1955-Jul 1964", "MLPHJ": "Dec 1941-Jan 1955 wartime (WWII, Korea)", "MLPIK": "Peacetime before May 1950"}
COLS = ["STATE", "AGEP", "SEX", "MIL", "PWGTP", "SCHL", "DRAT", "PINCP"] + list(PERIODS)

frames = []
with zipfile.ZipFile(ZIP) as z:
    names = [n for n in z.namelist() if n.endswith(".csv")]
    print(names)
    for n in names:
        with z.open(n) as f:
            head = pd.read_csv(f, nrows=0).columns
        use = [c for c in COLS if c in head]
        print("missing:", set(COLS) - set(use))
        with z.open(n) as f:
            for chunk in pd.read_csv(f, usecols=use, chunksize=500_000, low_memory=False):
                frames.append(chunk[chunk.AGEP >= 17])
p = pd.concat(frames)
w = "PWGTP"
print("people 17+:", f"{p[w].sum():,}")

mil = p.groupby("MIL", dropna=False)[w].sum()
print(mil)
mil.rename("people").to_csv(OUT / "pums_mil_status.csv")

v = p[p.MIL == 2]
g = p[p.MIL == 3]
print("veterans", f"{v[w].sum():,}", " guard/reserve training only", f"{g[w].sum():,}")
print("guard-only women share", round(g.loc[g.SEX == 2, w].sum() / g[w].sum(), 4))
age_bins = pd.cut(g.AGEP, [16, 34, 49, 64, 74, 200], labels=["17-34", "35-49", "50-64", "65-74", "75+"])
print("guard-only by age:", g.groupby(age_bins, observed=True)[w].sum().to_dict())

rows = [(PERIODS[c], v.loc[v[c] == 1, w].sum()) for c in PERIODS if c in v]
t = pd.DataFrame(rows, columns=["period", "veterans"])
print(t)
t.to_csv(OUT / "pums_period.csv", index=False)
flags = [c for c in PERIODS if c in v]
print("served in more than one period:", f"{v.loc[(v[flags] == 1).sum(axis=1) > 1, w].sum():,}")

adults = p[p.AGEP >= 18]
st = pd.DataFrame({"veterans": adults[adults.MIL == 2].groupby("STATE")[w].sum(), "adults": adults.groupby("STATE")[w].sum()})
st["share"] = (st.veterans / st.adults).round(4)
st.sort_values("share", ascending=False).to_csv(OUT / "pums_state_share.csv")
print(st.sort_values("share", ascending=False).head(8), st.sort_values("share").head(5))
print("US share of adults:", round(st.veterans.sum() / st.adults.sum(), 4))
for label, frame in [("men", adults[adults.SEX == 1]), ("men 75-84", adults[(adults.SEX == 1) & adults.AGEP.between(75, 84)]), ("men 25-34", adults[(adults.SEX == 1) & adults.AGEP.between(25, 34)]), ("women", adults[adults.SEX == 2])]:
    print(label, "share veterans:", round(frame.loc[frame.MIL == 2, w].sum() / frame[w].sum(), 4))

bachelors = v[v.AGEP >= 25]
print("veterans 25+ with bachelor's+:", round(bachelors.loc[bachelors.SCHL >= 21, w].sum() / bachelors[w].sum(), 4))
nv = p[(p.MIL == 4) & (p.AGEP >= 25)]
print("non-veterans 25+ with bachelor's+:", round(nv.loc[nv.SCHL >= 21, w].sum() / nv[w].sum(), 4))
drat = v.groupby("DRAT", dropna=False)[w].sum()
print("VA disability rating DRAT:", drat)
