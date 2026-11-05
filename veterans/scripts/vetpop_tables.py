"""Build tidy FY2026 VetPop tables (VA's projection for 30 Sep 2026) in data/, and print them."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "raw", ROOT / "data"
AS_OF = "09/30/2026"


def load(name):
    df = pd.read_csv(name)
    if "Date" in df:
        df = df[df["Date"].str.startswith(AS_OF)]
    df["Veterans"] = pd.to_numeric(df["Veterans"].astype(str).str.replace(",", ""))
    return df


def share(s):
    t = s.to_frame("veterans")
    t["share"] = (t["veterans"] / t["veterans"].sum()).round(4)
    return t


nat = load(RAW / "vetpop_national_1L.csv")
total = nat["Veterans"].sum()
print(f"Total FY2026: {total:,}")

age = nat.pivot_table(index="Age Group", columns="Sex", values="Veterans", sort=False)
age["Total"] = age.sum(axis=1)
age["Share"] = (age["Total"] / total).round(4)
age["FemaleShare"] = (age["Female"] / age["Total"]).round(4)
age.to_csv(OUT / "age_sex_fy2026.csv")
print(age, "\n", share(nat.groupby("Sex")["Veterans"].sum()))

for label, file, col in [("branch", "vetpop_branch_4L.csv", "Branch of Service"), ("rank", "vetpop_rank_5L.csv", "Rank")]:
    t = share(load(RAW / file).groupby(col, sort=False)["Veterans"].sum())
    t.to_csv(OUT / f"{label}_fy2026.csv")
    print(t, "\n")

p = load(RAW / "vetpop_period_2L.csv").groupby("Period of Service", sort=False)["Veterans"].sum()
p.to_frame("veterans").to_csv(OUT / "period_fy2026.csv")
print(p, "\n")

st = load(RAW / "vetpop_state_6L.csv").groupby("State")["Veterans"].sum().sort_values(ascending=False)
share(st).to_csv(OUT / "state_fy2026.csv")
print(share(st).head(12), "\n", share(st).tail(6), "\n", "state sum", st.sum())

c = load(RAW / "cache" / "vetpop_county_9L.csv").groupby(["FIPS", "County, State"])["Veterans"].sum().sort_values(ascending=False)
c.to_frame("veterans").to_csv(OUT / "county_fy2026.csv")
print(c.head(12))

# Living veterans over time
est = pd.read_csv(RAW / "vetpop_estimates_2000_2023.csv")
yrs = [x for x in est.columns if x.startswith("FY")]
tot = est[yrs].apply(lambda col: pd.to_numeric(col.astype(str).str.replace(",", ""))).sum()
print(tot[["FY2000", "FY2010", "FY2020", "FY2023"]])
allyrs = pd.read_csv(RAW / "vetpop_national_1L.csv")
allyrs["FY"] = allyrs["Date"].str[6:10].astype(int)
print(allyrs.groupby("FY")["Veterans"].sum().loc[[2023, 2026, 2030, 2040, 2053]])
