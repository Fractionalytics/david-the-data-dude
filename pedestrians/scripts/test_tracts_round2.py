"""Pre-registered tests P6 (night workers) and P7 (transit riders), round 2 of
docs/hypothesis-test.md. Reuses the round-1 definitions in test_tracts.py
(deaths placed in 2010 tracts, P1 poverty quintiles, quintile(), qtable()).

    python scripts/test_tracts_round2.py vars      print the Census labels of the new variables
    python scripts/test_tracts_round2.py acs       download ACS 2008-12 commute data (cached)
    python scripts/test_tracts_round2.py analyze   stratified tables and PASS/FAIL
      reads  data/final/test_tracts_deaths.csv, data/final/test_tracts_tracts.csv (round 1)
             data/raw/acs/acs5_2012_round2_<SS>.json  (api.census.gov, one per state)
      writes data/final/test_tracts_p6_night.csv      cells: poverty quintile x night quintile
             data/final/test_tracts_p7_transit.csv    cells: poverty quintile x transit quintile
             data/final/test_tracts_round2_extras.csv (not pre-registered)
             data/final/test_tracts_round2_tracts.csv tract shares and quintiles

Definitions (fixed before running)
  night   = B08302_002E / B08302_001E  (left home 12:00-4:59am, of workers who
            did not work at home); no value when the denominator is 0.
  transit = B08301_010E / B08301_001E  (public transportation excluding taxicab,
            of all workers 16+); no value when the denominator is 0.
  Quintiles: test_tracts.quintile(), national, weighted by tract population
  (B01003), ties broken by GEOID, exactly as in round 1.
  Within each P1 poverty quintile p: qtable() on the deaths and tracts with
  q_poverty == p, grouped by the national night (transit) quintile. Compare
  pct_change_rate of quintile 5 with quintile 1. PASS if 5 > 1 in >= 4 of 5.
  Deaths in a tract with no poverty or no night/transit quintile are excluded.
  Tie diagnostic and sensitivity (decided before seeing results): many tracts
  have a share of exactly 0, and round 1's GEOID tie-break then fills the
  bottom quintile with zero-share tracts from low-numbered states first. We
  report the population share at exactly 0 and, labeled as a sensitivity, the
  same test with ties broken by a fixed pseudo-random order (seed 2026)
  instead of GEOID. The GEOID version decides PASS/FAIL.
"""

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_tracts import ACS, FINAL, ROOT, STATES, get, qtable, quintile  # noqa: E402

VARS = ["B08302_001E", "B08302_002E", "B08301_001E", "B08301_010E"]
EXPECT = {"B08302_001E": ("total", "time leaving home"), "B08302_002E": ("12:00 a.m. to 4:59 a.m.", "time leaving home"),
          "B08301_001E": ("total", "means of transportation"),
          "B08301_010E": ("public transportation (excluding taxicab)", "means of transportation")}
MEASURES = {"night": ("B08302_002E", "B08302_001E", "p6_night"), "transit": ("B08301_010E", "B08301_001E", "p7_transit")}


def key() -> str:
    k = os.environ.get("CENSUS_DATA_API_KEY")
    env = ROOT.parents[1] / ".env"
    if not k and env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("CENSUS_DATA_API_KEY="):
                k = line.split("=", 1)[1].strip()
    if not k or k == "REPLACE_ME":
        raise SystemExit("no CENSUS_DATA_API_KEY in the root .env")
    return k


def check_vars() -> None:
    bad = []
    for v in VARS:
        j = get(f"https://api.census.gov/data/2012/acs/acs5/variables/{v}.json").json()
        label, concept = j.get("label", ""), j.get("concept", "")
        print(f"  {v}: label={label!r} concept={concept!r}")
        want_label, want_concept = EXPECT[v]
        if want_label not in label.lower() or want_concept not in (label + concept).lower():
            bad.append(v)
        time.sleep(1)
    if bad:
        raise SystemExit(f"variable labels don't match expectations: {bad}")
    print("all four variables match")


def fetch() -> None:
    check_vars()
    k = key()
    for s in STATES:
        dest = ACS / f"acs5_2012_round2_{s}.json"
        if dest.exists():
            continue
        url = f"https://api.census.gov/data/2012/acs/acs5?get={','.join(VARS)}&for=tract:*&in=state:{s}&key={k}"
        dest.write_text(json.dumps(get(url).json()))  # get() prints the URL without the query string
        time.sleep(1)


def tracts() -> pd.DataFrame:
    t = pd.read_csv(FINAL / "test_tracts_tracts.csv", dtype={"GEOID10": str})
    rows = []
    for s in STATES:
        js = json.loads((ACS / f"acs5_2012_round2_{s}.json").read_text())
        rows.append(pd.DataFrame(js[1:], columns=js[0]))
    a = pd.concat(rows, ignore_index=True)
    a["GEOID10"] = a.state + a.county + a.tract
    for c in VARS:
        a[c] = pd.to_numeric(a[c], errors="coerce").where(lambda x: x >= 0)
    unmatched = len(set(a.GEOID10) - set(t.GEOID10))
    print(f"ACS round-2 rows {len(a)}, not in round-1 tract table {unmatched}")
    t = t.merge(a[["GEOID10"] + VARS], on="GEOID10", how="left", validate="1:1")
    rng = np.random.default_rng(2026)
    t["tiebreak"] = rng.permutation(len(t))
    for m, (num, den, _) in MEASURES.items():
        t[m] = (t[num] / t[den]).where(t[den] > 0)
        t[f"q_{m}"] = quintile(t, m)
        # sensitivity: same function, ties ordered by the random key instead of GEOID
        tmp = t[["pop_", m, "tiebreak"]].rename(columns={"tiebreak": "GEOID10"})
        t[f"q_{m}_randtie"] = quintile(tmp, m)
    return t


def stratified(d: pd.DataFrame, t: pd.DataFrame, qcol: str) -> pd.DataFrame:
    out = []
    for p in range(1, 6):
        tab = qtable(d[d.q_poverty == p], t[t.q_poverty == p], qcol)
        out.append(tab.assign(poverty_quintile=p).reset_index())
    o = pd.concat(out).rename(columns={"quintile": qcol.replace("q_", "") + "_quintile"})
    return o[["poverty_quintile"] + [c for c in o.columns if c != "poverty_quintile"]]


def verdict(cells: pd.DataFrame, m: str) -> tuple[int, pd.DataFrame]:
    qc = f"{m}_quintile" if f"{m}_quintile" in cells else [c for c in cells if c.endswith("_quintile") and c != "poverty_quintile"][0]
    rows = []
    for p in range(1, 6):
        c = cells[cells.poverty_quintile == p].set_index(qc)
        lo, hi = c.loc[1] if 1 in c.index else None, c.loc[5] if 5 in c.index else None
        rows.append({"poverty_quintile": p,
                     "bottom_pct_change": lo.pct_change_rate, "top_pct_change": hi.pct_change_rate,
                     "bottom_deaths_yr_09_11": lo.deaths_2009_11, "bottom_deaths_yr_20_22": lo.deaths_2020_22,
                     "top_deaths_yr_09_11": hi.deaths_2009_11, "top_deaths_yr_20_22": hi.deaths_2020_22,
                     "bottom_pop": lo.pop_2010, "top_pop": hi.pop_2010,
                     "top_gt_bottom": hi.pct_change_rate > lo.pct_change_rate})
    v = pd.DataFrame(rows)
    return int(v.top_gt_bottom.sum()), v


def analyze() -> None:
    t = tracts()
    keep = ["GEOID10", "pop_", "poverty", "q_poverty", "q_density"] + VARS + \
           [c for m in MEASURES for c in (m, f"q_{m}", f"q_{m}_randtie")]
    t[keep].to_csv(FINAL / "test_tracts_round2_tracts.csv", index=False)
    d = pd.read_csv(FINAL / "test_tracts_deaths.csv", dtype={"GEOID10": str})
    d = d[d.GEOID10.notna()].merge(t[keep], on="GEOID10", how="left")
    print("deaths in a tract with no quintile:", {c: int(d[c].isna().sum()) for c in ["q_poverty", "q_night", "q_transit"]})

    extras = []
    for m, (num, den, fname) in MEASURES.items():
        qc = f"q_{m}"
        pos = t[t.pop_ > 0]
        print(f"\n######## {m}")
        print(f"tracts with pop but no {m} value: {int(pos[m].isna().sum())} ({pos.loc[pos[m].isna(), 'pop_'].sum():.0f} people)")
        print(f"population share in tracts where {m} share is exactly 0: {pos.loc[pos[m] == 0, 'pop_'].sum() / pos.pop_.sum():.3f}")
        cut = pos.groupby(qc)[m].agg(["min", "max", "median"])
        cut["pop"] = pos.groupby(qc).pop_.sum()
        print("quintile cut points:\n" + cut.to_string())
        q1 = pos[pos[qc] == 1]
        print("state mix of bottom quintile (top 8 by pop share):\n" +
              (q1.groupby(q1.GEOID10.str[:2]).pop_.sum() / q1.pop_.sum()).sort_values(ascending=False).head(8).round(3).to_string())

        cells = stratified(d, t, qc)
        cells.to_csv(FINAL / f"test_tracts_{fname}.csv", index=False)
        n, v = verdict(cells, m)
        print(f"\n== {fname} cells\n{cells.to_string(index=False)}")
        print(f"\n== {fname} top vs bottom\n{v.round(2).to_string(index=False)}")
        print(f"\n{fname.upper()}: top > bottom in {n} of 5 poverty quintiles -> {'PASS' if n >= 4 else 'FAIL'}")
        extras.append(v.assign(test=fname, version="preregistered_rule"))

        # Not pre-registered
        un = qtable(d, t, qc)
        print(f"\n== NOT PRE-REGISTERED {m}: unstratified\n{un.to_string()}")
        extras.append(un.reset_index().assign(test=fname, version="not_prereg_unstratified"))
        dk = d[d.dark == True]  # noqa: E712
        dcells = stratified(dk, t, qc)
        nd, vd = verdict(dcells, m)
        print(f"\n== NOT PRE-REGISTERED {m}: dark-only, stratified\n{vd.round(2).to_string(index=False)}\n -> {nd} of 5")
        extras.append(vd.assign(test=fname, version="not_prereg_dark_only"))
        rc = stratified(d, t, f"{qc}_randtie")
        nr, vr = verdict(rc, f"{m}_randtie")
        print(f"\n== SENSITIVITY {m}: random tie-break, stratified\n{vr.round(2).to_string(index=False)}\n -> {nr} of 5")
        extras.append(vr.assign(test=fname, version="sensitivity_random_tiebreak"))
    ex = pd.concat(extras, ignore_index=True)
    ex = ex[["test", "version"] + [c for c in ex.columns if c not in ("test", "version")]]
    ex.round(4).to_csv(FINAL / "test_tracts_round2_extras.csv", index=False)


if __name__ == "__main__":
    {"vars": check_vars, "acs": fetch, "analyze": analyze}[sys.argv[1]]()
