"""Veteran shares of the population from ACS 2024 1-year PUMS: all ages, adults, men and women by five-year age,
plus the share of employed people working for the federal government. Person weights only."""
from pathlib import Path
import zipfile
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ZIP = ROOT / "data" / "raw" / "cache" / "acs2024_pums_csv_pus.zip"
OUT = ROOT / "data"
w = "PWGTP"

frames = []
with zipfile.ZipFile(ZIP) as z:
    for n in [n for n in z.namelist() if n.endswith(".csv")]:
        with z.open(n) as f:
            for chunk in pd.read_csv(f, usecols=["AGEP", "SEX", "MIL", "COW", "ESR", w], chunksize=500_000):
                frames.append(chunk)
p = pd.concat(frames)

total = p[w].sum()
vets = p.loc[p.MIL == 2, w].sum()
active = p.loc[p.MIL == 1, w].sum()
adults = p[p.AGEP >= 18]
print(f"population {total:,}  veterans {vets:,} ({vets / total:.2%} of everyone)  active duty {active:,} ({active / total:.2%})")
print(f"veterans 18+ share of adults {adults.loc[adults.MIL == 2, w].sum() / adults[w].sum():.2%}")
print(f"ever served on active duty incl. now (MIL 1-2), share of adults {adults.loc[adults.MIL.isin([1, 2]), w].sum() / adults[w].sum():.2%}")
for s, label in [(1, "men"), (2, "women")]:
    a = adults[adults.SEX == s]
    print(f"{label} 18+: {a.loc[a.MIL == 2, w].sum():,} veterans of {a[w].sum():,} = {a.loc[a.MIL == 2, w].sum() / a[w].sum():.2%}")

bins = list(range(15, 90, 5)) + [200]
labels = ["17 to 19"] + [f"{b} to {b + 4}" for b in range(20, 85, 5)] + ["85 or older"]
a = p[p.AGEP >= 17].copy()
a["age"] = pd.cut(a.AGEP, [16, 19] + list(range(24, 85, 5)) + [200], labels=labels)
rows = []
for (age, sex), g in a.groupby(["age", "SEX"], observed=True):
    rows.append({"age": age, "sex": "men" if sex == 1 else "women", "veterans": g.loc[g.MIL == 2, w].sum(), "people": g[w].sum()})
t = pd.DataFrame(rows).pivot(index="age", columns="sex", values=["veterans", "people"])
out = pd.DataFrame({
    "men_veterans": t["veterans"]["men"], "men_share": (t["veterans"]["men"] / t["people"]["men"]).round(4),
    "women_veterans": t["veterans"]["women"], "women_share": (t["veterans"]["women"] / t["people"]["women"]).round(4),
})
out.to_csv(OUT / "pums_share_by_age_sex.csv")
print(out.to_string())

emp = p[(p.AGEP >= 18) & p.ESR.isin([1, 2])]  # civilian employed
for label, g in [("veterans", emp[emp.MIL == 2]), ("never served", emp[emp.MIL == 4])]:
    print(f"{label}: federal government workers {g.loc[g.COW == 5, w].sum() / g[w].sum():.2%} of employed")
fed = emp[emp.COW == 5]
print(f"veterans' share of federal civilian workers {fed.loc[fed.MIL == 2, w].sum() / fed[w].sum():.2%}")
