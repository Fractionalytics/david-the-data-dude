"""Where VA's VetPop and the Census ACS disagree: totals, geography and age, FY2024 VetPop vs ACS 2024 PUMS."""
from pathlib import Path
import zipfile
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

vp = pd.read_csv(RAW / "vetpop_state_6L.csv")
vp = vp[vp.Date.str.startswith("09/30/2024")]
vp["Veterans"] = pd.to_numeric(vp["Veterans"].astype(str).str.replace(",", ""))
states = vp.groupby("State")["Veterans"].sum()
print("VetPop FY2024 total:", f"{states.sum():,}")
print(len(states), "areas; outside the 50 states and DC:", states[states.index.str.contains("Puerto|Island|Foreign|Territor|Guam|Virgin", case=False)].to_dict())

frames = []
with zipfile.ZipFile(RAW / "cache" / "acs2024_pums_csv_pus.zip") as z:
    for n in [n for n in z.namelist() if n.endswith(".csv")]:
        with z.open(n) as f:
            for chunk in pd.read_csv(f, usecols=["AGEP", "MIL", "RELSHIPP", "PWGTP"], chunksize=500_000):
                frames.append(chunk[chunk.MIL == 2])
v = pd.concat(frames)
print("ACS 2024 veterans:", f"{v.PWGTP.sum():,}", " of which in group quarters (RELSHIPP 37-38):", f"{v.loc[v.RELSHIPP.isin([37, 38]), 'PWGTP'].sum():,}")

bins = [16, 44, 64, 84, 200]
labels = ["17 to 44", "45 to 64", "65 to 84", "85 and older"]
acs = v.groupby(pd.cut(v.AGEP, bins, labels=labels), observed=True).PWGTP.sum()
vpa = vp.copy()
vpa["band"] = pd.cut(vpa["Age Group"].str.extract(r"^(\d+)")[0].astype(int), [16, 44, 64, 84, 200], labels=labels)
vpa = vpa.groupby("band", observed=True).Veterans.sum()
t = pd.DataFrame({"VetPop FY2024": vpa, "ACS 2024": acs})
t["gap"] = t["VetPop FY2024"] - t["ACS 2024"]
t["VetPop/ACS"] = (t["VetPop FY2024"] / t["ACS 2024"]).round(2)
t.loc["Total"] = t.sum()
t.loc["Total", "VetPop/ACS"] = round(t.loc["Total", "VetPop FY2024"] / t.loc["Total", "ACS 2024"], 2)
t.to_csv(ROOT / "data" / "va_vs_census_by_age.csv")
print(t.to_string())
