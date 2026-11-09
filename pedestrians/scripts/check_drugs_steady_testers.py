"""Robustness check on P9 (not pre-registered; rule fixed before looking):
does the stimulant rise in pedestrians killed hold in states whose testing
didn't change?

    python scripts/check_drugs_steady_testers.py
      reads  data/raw/fars/FARS<YEAR>NationalCSV.zip, 2007-2024
      writes data/final/check_drugs_steady_testers.csv  state x year counts
             data/final/check_drugs_steady_testers_years.csv  steady-state set by year

Steady testers: states that tested >= 70% of pedestrians killed in every year
2009-2022, with at least 10 pedestrian deaths in each of those years. Uses
test_ped_drugs.summarize()'s logic, "primary" definition, first three results
only (so the 2018 switch to unlimited results can't inflate later years).
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ped_drugs import INVALID, KEY, classify, results  # noqa: E402
from fars_pedestrians import FINAL  # noqa: E402


def state_year(y: int) -> pd.DataFrame:
    peds, r, _ = results(y)
    r = r[r.order <= 3].assign(code=lambda x: x.code.astype(int))
    v = r[~r.code.isin(INVALID)]
    f = v.code.apply(lambda c: classify(c, y >= 2022, "primary"))
    v = v.assign(stim=[a[1] for a in f])
    per = v.groupby(KEY).stim.any().reset_index()
    peds = peds.merge(per, on=KEY, how="left")
    peds["tested"] = peds.stim.notna()
    peds["state"] = peds.ST_CASE // 10000
    g = peds.groupby("state").agg(killed=("tested", "size"), tested=("tested", "sum"),
                                  stim=("stim", lambda s: int(s.fillna(False).astype(bool).sum())))
    return g.reset_index().assign(year=y)


def main() -> None:
    t = pd.concat([state_year(y) for y in range(2007, 2025)], ignore_index=True)
    t["rate"] = t.tested / t.killed
    t.to_csv(FINAL / "check_drugs_steady_testers.csv", index=False)
    w = t[t.year.between(2009, 2022)]
    ok = w.groupby("state").apply(lambda x: len(x) == 14 and (x.rate >= 0.7).all() and (x.killed >= 10).all())
    steady = sorted(ok[ok].index)
    print("steady states (FIPS):", steady, len(steady))
    s = t[t.state.isin(steady)].groupby("year")[["killed", "tested", "stim"]].sum()
    a = t.groupby("year")[["killed", "tested", "stim"]].sum()
    out = pd.DataFrame({"steady_killed": s.killed, "steady_testing_rate": s.tested / s.killed,
                        "steady_stim_share": s.stim / s.tested, "all_testing_rate": a.tested / a.killed,
                        "all_stim_share_first3": a.stim / a.tested})
    out.to_csv(FINAL / "check_drugs_steady_testers_years.csv")
    print(out.round(3).to_string())


if __name__ == "__main__":
    main()
