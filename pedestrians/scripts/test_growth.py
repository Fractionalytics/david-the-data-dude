"""Pre-registered test P13 (population growth), docs/hypothesis-test.md round 4.

    python scripts/test_growth.py fetch     ACS 2015-19 tract population (needs
                                            CENSUS_DATA_API_KEY in the root .env; cached)
    python scripts/test_growth.py analyze
      reads  data/final/test_tracts_tracts.csv   (P1-P3 tracts: ACS 2008-12 pop, quintiles)
             data/final/test_tracts_deaths.csv   (pedestrian deaths placed in 2010 tracts)
             data/raw/acs/acs5_2019_<SS>.json    (B01003, 2010 tract boundaries)
      writes data/final/test_growth_p13a.csv     poverty quintile x growth quintile
             data/final/test_growth_p13b.csv     125 cells: growth x poverty x density
             data/final/test_growth_tracts.csv

Growth = pop 2015-19 / pop 2008-12. Growth quintiles: test_tracts.quintile()
(weighted by 2008-12 pop; ties by GEOID). Rates are per resident: 2009-11
deaths over 2008-12 pop, 2020-22 deaths over 2015-19 pop.
P13a PASS: top growth quintile's % change in rate > bottom's in >= 4 of 5
poverty quintiles. P13b PASS: composition share >= 10%, where composition
share = (sum_c rate_pre_c * pop19_c / sum pop19 - rate_pre) / (rate_post - rate_pre)
over the 125 cells; deaths in tracts missing any of the three quintiles excluded.
"""

import json
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_tracts import ACS, FINAL, POST, PRE, STATES, get, quintile  # noqa: E402
from test_tracts_round2 import key  # noqa: E402


def fetch() -> None:
    k = key()
    for s in STATES:
        dest = ACS / f"acs5_2019_{s}.json"
        if dest.exists():
            continue
        url = f"https://api.census.gov/data/2019/acs/acs5?get=B01003_001E&for=tract:*&in=state:{s}&key={k}"
        dest.write_text(json.dumps(get(url).json()))  # get() prints the URL without the query string
        time.sleep(1)


def tracts() -> pd.DataFrame:
    t = pd.read_csv(FINAL / "test_tracts_tracts.csv", dtype={"GEOID10": str})
    rows = []
    for s in STATES:
        js = json.loads((ACS / f"acs5_2019_{s}.json").read_text())
        rows.append(pd.DataFrame(js[1:], columns=js[0]))
    a = pd.concat(rows, ignore_index=True)
    a["GEOID10"] = a.state + a.county + a.tract
    a["pop19"] = pd.to_numeric(a.B01003_001E, errors="coerce").where(lambda x: x >= 0)
    print(f"ACS 2019 rows {len(a)}; not in 2012 tract table {len(set(a.GEOID10) - set(t.GEOID10))}; "
          f"2012 tracts missing from 2019 {len(set(t.GEOID10) - set(a.GEOID10))}")
    t = t.merge(a[["GEOID10", "pop19"]], on="GEOID10", how="left", validate="1:1")
    t["pop19"] = t.pop19.fillna(0)
    t["growth"] = (t.pop19 / t.pop_).where(t.pop_ > 0)
    t["q_growth"] = quintile(t, "growth")
    return t


def rates(d: pd.DataFrame, t: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    pre = d[d.year.isin(PRE)].groupby(by).size() / 3
    post = d[d.year.isin(POST)].groupby(by).size() / 3
    o = t.groupby(by)[["pop_", "pop19"]].sum().rename(columns={"pop_": "pop_2008_12", "pop19": "pop_2015_19"})
    o["deaths_2009_11"] = pre.reindex(o.index).fillna(0)
    o["deaths_2020_22"] = post.reindex(o.index).fillna(0)
    o["rate_2009_11"] = o.deaths_2009_11 / o.pop_2008_12 * 1e5
    o["rate_2020_22"] = o.deaths_2020_22 / o.pop_2015_19 * 1e5
    o["pct_change_rate"] = (o.rate_2020_22 / o.rate_2009_11 - 1) * 100
    return o


def analyze() -> None:
    t = tracts()
    t.to_csv(FINAL / "test_growth_tracts.csv", index=False)
    cut = t[t.q_growth.notna()].groupby("q_growth").growth.agg(["min", "median", "max"])
    print("growth quintile cut points (ratio 2015-19 / 2008-12):\n" + cut.round(3).to_string())
    d = pd.read_csv(FINAL / "test_tracts_deaths.csv", dtype={"GEOID10": str})
    d = d[d.year.isin(PRE + POST)].merge(t[["GEOID10", "q_poverty", "q_density", "q_growth"]], on="GEOID10", how="left")
    q = ["q_growth", "q_poverty", "q_density"]
    print("deaths in tracts missing a quintile, by period:",
          d[d[q].isna().any(axis=1)].groupby(d.year.isin(POST)).size().to_dict())
    d, tq = d.dropna(subset=q), t.dropna(subset=q)

    # P13a
    a = rates(d, tq, ["q_poverty", "q_growth"])
    a.reset_index().to_csv(FINAL / "test_growth_p13a.csv", index=False)
    print("\nP13a: % change in per-resident rate")
    n = 0
    for p in range(1, 6):
        lo, hi = a.loc[(p, 1)], a.loc[(p, 5)]
        win = hi.pct_change_rate > lo.pct_change_rate
        n += win
        print(f"  poverty q{p}: bottom growth {lo.pct_change_rate:+.0f}% ({lo.deaths_2020_22:.0f}/yr post), "
              f"top growth {hi.pct_change_rate:+.0f}% ({hi.deaths_2020_22:.0f}/yr post) {'top' if win else 'bottom'}")
    print(f"P13a: top > bottom in {n} of 5 -> {'PASS' if n >= 4 else 'FAIL'}")
    u = rates(d, tq, ["q_growth"])
    print("not pre-registered, unstratified:\n" + u.round(2).to_string())

    # P13b
    c = rates(d, tq, q)
    c.reset_index().to_csv(FINAL / "test_growth_p13b.csv", index=False)
    r_pre = c.deaths_2009_11.sum() / c.pop_2008_12.sum() * 1e5
    r_post = c.deaths_2020_22.sum() / c.pop_2015_19.sum() * 1e5
    r_cf = (c.rate_2009_11.fillna(0) * c.pop_2015_19).sum() / c.pop_2015_19.sum()
    share = (r_cf - r_pre) / (r_post - r_pre)
    print(f"\nP13b: rate 2009-11 {r_pre:.3f}, 2020-22 {r_post:.3f}, counterfactual {r_cf:.3f}; "
          f"composition share {share:.1%} -> {'PASS' if share >= 0.10 else 'FAIL'}")
    print(f"  empty cells (no 2008-12 pop): {(c.pop_2008_12 == 0).sum()}")


if __name__ == "__main__":
    {"fetch": fetch, "analyze": analyze}[sys.argv[1]]()
