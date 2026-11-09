"""Pre-registered test P17 (docs/hypothesis-test.md, Round 5): did meth overdose
deaths and pedestrian deaths fall together from 2022 to 2024?

    python scripts/test_meth_decline.py
      reads  data/raw/cdc_meth/vsrr_provisional_drug_overdose_xkb8-kh2a.csv (VSRR)
             data/raw/fars/FARS2022NationalCSV.zip, FARS2024NationalCSV.zip
             data/raw/fred/<ST>POP.csv
      writes data/final/test_meth_decline.csv   one row per state, `included` flag

Same definitions as P10 (scripts/test_meth.py): T43.6, 12 months ending
December, reported deaths ("Data Value"); NY = NY + YC; states withheld for low
data quality, suppressed (<10) or with no drug-specific rows are excluded.
P17a: national (VSRR "US") falls >= 5%. P17b: Pearson r of the rate changes
> 0.3, and > 0.3 without the state with the largest psychostimulant decline.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_meth import FILE, IND, STATES, ped_counts  # noqa: E402
import test_meth  # noqa: E402
from fars_pedestrians import FINAL  # noqa: E402
from fars_decompose import state_pop  # noqa: E402

A, B = 2022, 2024


def meth(d: pd.DataFrame) -> pd.DataFrame:
    d = d[(d.Indicator == IND) & (d.Period == "12 month-ending") & (d.Month == "December") & d.Year.isin([A, B])].copy()
    fn = d.Footnote.fillna("")
    d["flag"] = "ok"
    d.loc[fn.str.contains("suppressed"), "flag"] = "suppressed (<10)"
    d.loc[fn.str.contains("low data quality"), "flag"] = "low data quality"
    d.loc[fn.str.contains("Underreported"), "flag"] = "underreported"
    d.loc[d["Data Value"].isna() & (d.flag == "ok"), "flag"] = "withheld"
    return d.rename(columns={"State": "st", "Year": "year", "Data Value": "deaths"})[["st", "year", "deaths", "flag"]]


def main() -> None:
    raw = pd.read_csv(FILE)
    latest = raw[raw.Indicator == IND][["Year", "Month"]].drop_duplicates()
    print("VSRR T43.6 latest rows:", latest.tail(3).to_dict("records"))
    m = meth(raw)
    us = m[m.st == "US"].set_index("year").deaths
    print(f"\nP17a national psychostimulant deaths: {A} {us[A]:,.0f} -> {B} {us[B]:,.0f} "
          f"({us[B] / us[A] - 1:+.1%}) -> {'PASS' if us[B] <= 0.95 * us[A] else 'FAIL'}")

    ny = m[m.st.isin(["NY", "YC"])]
    rows = []
    for y, g in ny.groupby("year"):
        ok = (g.flag == "ok").all() and len(g) == 2
        rows.append({"st": "NY", "year": y, "deaths": g.deaths.sum() if ok else float("nan"),
                     "flag": "ok" if ok else "; ".join(sorted(set(g.flag) - {"ok"})) or "missing"})
    m = pd.concat([m[~m.st.isin(["NY", "YC", "US"])], pd.DataFrame(rows)])
    m = m[m.st.isin(STATES)]
    full = pd.MultiIndex.from_product([STATES, [A, B]], names=["st", "year"])
    m = m.set_index(["st", "year"]).reindex(full).reset_index()
    m["flag"] = m.flag.fillna("no drug-specific rows published")

    test_meth.BASE, test_meth.LATE = A, B  # ped_counts() reads these
    t = m.merge(ped_counts(), on=["st", "year"]).merge(state_pop().rename(columns={"state": "st"}), on=["st", "year"])
    t["meth_rate"] = t.deaths / t.population * 1e5
    t["ped_rate"] = t.ped_deaths / t.population * 1e5
    w = t.pivot(index="st", columns="year")
    s = pd.DataFrame({f"meth_rate_{y}": w[("meth_rate", y)] for y in (A, B)})
    for y in (A, B):
        s[f"ped_rate_{y}"] = w[("ped_rate", y)]
        s[f"ped_deaths_{y}"] = w[("ped_deaths", y)]
        s[f"flag_{y}"] = w[("flag", y)]
    s["meth_change"] = s[f"meth_rate_{B}"] - s[f"meth_rate_{A}"]
    s["ped_change"] = s[f"ped_rate_{B}"] - s[f"ped_rate_{A}"]
    s["included"] = (s[f"flag_{A}"] == "ok") & (s[f"flag_{B}"] == "ok")
    s.round(4).to_csv(FINAL / "test_meth_decline.csv")
    inc = s[s.included]
    print(f"\nIncluded n={len(inc)}; excluded: " + ", ".join(
        f"{k} [{r[f'flag_{A}']}/{r[f'flag_{B}']}]" for k, r in s[~s.included].iterrows()))
    print(f"States with meth rate down: {(inc.meth_change < 0).sum()} of {len(inc)}; "
          f"pedestrian rate down: {(inc.ped_change < 0).sum()} of {len(inc)}")
    x, y = inc.meth_change, inc.ped_change
    top = x.idxmin()
    k = inc.index != top
    r1, r2 = x.corr(y), x[k].corr(y[k])
    print(f"P17b Pearson r n={len(inc)}: {r1:.3f}; without {top} (largest decline {x.min():.1f}): {r2:.3f} -> "
          f"{'PASS' if r1 > 0.3 and r2 > 0.3 else 'FAIL'}")
    print(f"Extra (not pre-registered): Spearman {x.corr(y, method='spearman'):.3f}")
    print(inc[["meth_rate_2022", "meth_rate_2024", "meth_change", "ped_rate_2022", "ped_rate_2024", "ped_change"]]
          .sort_values("meth_change").round(2).to_string())


if __name__ == "__main__":
    main()
