"""US stimulant deaths without opioids by age, and the fentanyl-plus-stimulant pair (CDC WONDER exports
E1-E9 by David, 2026-11-12; see docs/research-drugs/deadly-pair.md section 4).

    python scripts/analyze_wonder_age_pair.py
      reads  data/raw/cdc_wonder/wonder_*_age_2018_2024.csv, wonder_fent_*.csv
      writes data/final/stim_no_opioid_by_age.csv, data/final/fent_pair_by_state_2024.csv

"Without opioids" = all minus with opioids (T40.0-T40.4, T40.6), per year and age group. WONDER suppresses
counts of 1-9; a suppressed "with opioids" cell (only ever in the 75-84 group) is set to 5, the midpoint,
so its "without" count is off by at most 4.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "data" / "raw" / "cdc_wonder"
FINAL = ROOT / "data" / "final"
AGES = ["15-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75-84"]


def read(name, key):
    d = pd.read_csv(W / name)
    d = d[d.Notes.isna()].copy()  # drop Total rows and the footer
    d["Deaths"] = pd.to_numeric(d.Deaths, errors="coerce")
    return d.rename(columns={key: "key"})


def year_totals(name):
    d = pd.read_csv(W / name, nrows=7)
    return dict(zip(d["Year Code"].astype(int), d["Deaths"].astype(int)))


# ---------------------------------------------------------------- age of deaths without opioids
rows = []
for drug, stem in (("meth", "meth"), ("cocaine", "cocaine")):
    a = read(f"wonder_{stem}_all_age_2018_2024.csv", "Ten-Year Age Groups Code")
    w = read(f"wonder_{stem}_with_opioids_age_2018_2024.csv", "Ten-Year Age Groups Code")
    a["Year Code"], w["Year Code"] = a["Year Code"].astype(int), w["Year Code"].astype(int)
    m = a.merge(w[["Year Code", "key", "Deaths"]], on=["Year Code", "key"], suffixes=("_all", "_with"))
    # the age rows must add up to the year totals from the earlier (non-age) exports
    tot_all = year_totals(f"wonder_{stem}_all_2018_2024.csv")
    for y, g in m.groupby("Year Code"):
        s = g.Deaths_all.sum()
        assert abs(s - tot_all[y]) <= 30, (drug, y, s, tot_all[y])  # only suppressed 1-9 cells may be missing
    m["with_suppressed"] = m.Deaths_with.isna()
    m["Deaths_with"] = m.Deaths_with.fillna(5)  # suppressed = 1-9 deaths; midpoint 5 (affects only 75-84)
    m["without"] = m.Deaths_all - m.Deaths_with
    m = m[m.key.isin(AGES)]
    for y, g in m.groupby("Year Code"):
        g = g.set_index("key")
        n = g.without.sum()
        mids = {"15-24": 20, "25-34": 30, "35-44": 40, "45-54": 50, "55-64": 60, "65-74": 70, "75-84": 80}
        rows.append(dict(drug=drug, year=y, without=int(n), with_=int(g.Deaths_with.sum()),
                         share55_without=g.loc[["55-64", "65-74", "75-84"], "without"].sum() / n,
                         share55_with=g.loc[["55-64", "65-74", "75-84"], "Deaths_with"].sum() / g.Deaths_with.sum(),
                         mean_age_without=sum(mids[k] * g.without[k] for k in AGES) / n,
                         mean_age_with=sum(mids[k] * g.Deaths_with[k] for k in AGES) / g.Deaths_with.sum(),
                         **{f"without_{k}": int(g.without[k]) for k in AGES}))
age = pd.DataFrame(rows)
age.to_csv(FINAL / "stim_no_opioid_by_age.csv", index=False)
pd.options.display.float_format = "{:.2f}".format
pd.options.display.width = 250
print(age.to_string(index=False))

# ---------------------------------------------------------------- the pair, nationally
pair, fent = year_totals("wonder_fent_and_stim_2018_2024.csv"), year_totals("wonder_fent_all_2018_2024.csv")
print("\nFentanyl (T40.4) deaths, and those also involving cocaine or meth")
for y in pair:
    print(f"  {y}: fentanyl {fent[y]:>6}, with a stimulant {pair[y]:>6} ({pair[y] / fent[y]:.0%})")

# ---------------------------------------------------------------- the pair, by state, 2024
s = read("wonder_fent_all_state_2024.csv", "State")[["key", "Deaths", "Population"]].rename(columns={"Deaths": "fent"})
for col, f in (("with_meth", "wonder_fent_and_meth_state_2024.csv"), ("with_cocaine", "wonder_fent_and_coc_state_2024.csv")):
    s = s.merge(read(f, "State")[["key", "Deaths"]].rename(columns={"Deaths": col}), on="key")
s["share_meth"], s["share_cocaine"] = s.with_meth / s.fent, s.with_cocaine / s.fent

def leader(r):  # a suppressed count is 1-9 deaths, so any count of 10+ beats it
    if pd.isna(r.with_meth) and pd.isna(r.with_cocaine):
        return "unknown"
    return "meth" if r.with_meth > r.with_cocaine or pd.isna(r.with_cocaine) and r.with_meth >= 10 else "cocaine"


s["leader"] = s.apply(leader, axis=1)
s.rename(columns={"key": "state"}).to_csv(FINAL / "fent_pair_by_state_2024.csv", index=False)
print("\n2024, share of fentanyl deaths also involving meth / cocaine, by state")
print(s.sort_values("share_meth", ascending=False).to_string(index=False))
print("\nstates where meth leads:", (s.leader == "meth").sum(), " cocaine leads:", (s.leader == "cocaine").sum())
