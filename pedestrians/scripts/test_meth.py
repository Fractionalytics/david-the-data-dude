"""Pre-registered test P10 (docs/hypothesis-test.md, Round 3): across states, does
the change in the psychostimulant (ICD-10 T43.6, mostly methamphetamine) overdose
death rate track the change in the pedestrian death rate?

    python scripts/test_meth.py
      reads  data/raw/cdc_meth/vsrr_provisional_drug_overdose_xkb8-kh2a.csv
                 NCHS "VSRR Provisional Drug Overdose Death Counts", data.cdc.gov
                 dataset xkb8-kh2a (downloaded on first run; see data/raw/cdc_meth/SOURCE.md)
             data/raw/fars/FARS2015NationalCSV.zip, FARS2022NationalCSV.zip
             data/raw/fred/<ST>POP.csv   (state population, thousands)
      writes data/final/test_meth.csv      one row per state (50 + DC), with an
                                           `included` flag and the reason for any exclusion
             charts/test_meth_scatter.png  (not pre-registered)

Which branch of the rule applied, and why: FALLBACK.
  The rule uses 2009-11 vs. 2020-22 only if official CDC/NCHS state figures for
  T43.6 deaths exist for 2009, 2010, 2011 and 2020-22. Outside CDC WONDER (barred
  by the pre-registration) none were found: the VSRR provisional counts start in
  2015 (checked in code below); NCHS's state overdose tables (xbxb-epbu, the
  state map) give all-drug totals only; NCHS Data Briefs 406 and 474 give
  psychostimulant rates for the nation, not states; MMWR/CDC state tables by drug
  start in 2016-2017. So the fallback applies: the earliest year with official
  state figures (2015) vs. 2022, single years, on both sides.

Steps (fixed in the pre-registration, or by the task brief, before results were seen)
  1. Psychostimulant deaths: VSRR rows Indicator "Psychostimulants with abuse
     potential (T43.6)", Period "12 month-ending", Month "December" (= the
     calendar year), column "Data Value" (reported deaths; "Predicted Value", the
     NCHS adjustment for reporting delay, is used only in an extra).
     VSRR splits New York into "NY" (excluding New York City) and "YC" (New York
     City); New York state = NY + YC, usable only if both are.
  2. Exclusions (pre-registered: leave out states the source flags as unreliable):
     a state is left out if, in 2015 or 2022, its value is withheld with the
     footnote "Data not shown due to low data quality" (NCHS's flag for too few
     death certificates naming specific drugs). States whose value is withheld as
     "Data suppressed (<10)" have no published number either, so they are also
     left out, and reported separately. No 2015/2022 December row carries
     "Underreported due to incomplete data" (asserted).
  3. Rates per 100,000 = deaths / FRED population that year x 100,000 (crude,
     not age-adjusted: VSRR has counts only). Change = 2022 - 2015.
  4. Pedestrian deaths (FARS PER_TYP 5, INJ_SEV 4) by PERSON.STATE for 2015 and
     2022, built as in scripts/test_homeless.py, over the same FRED population.
     Change = 2022 rate - 2015 rate.
  5. Pre-registered: Pearson r across the included states, and with the state
     with the largest psychostimulant rate rise left out. PASS if both > 0.3.
  6. Not pre-registered extras: Spearman r; the same test on "Predicted Value";
     scatter plot. The primary-period version (2009-11) can't be run for any
     state: the VSRR data start in 2015.
"""

import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fars_pedestrians import FINAL, ROOT, load, year_peds  # noqa: E402
from fars_decompose import FIPS, state_pop  # noqa: E402

RAW = ROOT / "data" / "raw" / "cdc_meth"
UA = {"User-Agent": "content-engine-research-bot/1.0"}
URL = "https://data.cdc.gov/api/views/xkb8-kh2a/rows.csv?accessType=DOWNLOAD"
FILE = RAW / "vsrr_provisional_drug_overdose_xkb8-kh2a.csv"
IND = "Psychostimulants with abuse potential (T43.6)"
BASE, LATE = 2015, 2022
STATES = sorted(FIPS.values())


def fetch() -> None:
    if FILE.exists():
        return
    RAW.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=300)
    if r.status_code != 200:
        raise SystemExit(f"{URL}: HTTP {r.status_code}; not retrying (see SOURCE.md)")
    FILE.write_bytes(r.content)
    print("downloaded", FILE.name, len(r.content), "bytes")


def meth_counts() -> pd.DataFrame:
    """One row per state and year: reported and predicted deaths, flag."""
    d = pd.read_csv(FILE)
    first = int(d[d.Indicator == IND].Year.min())
    assert first == BASE, f"VSRR T43.6 starts in {first}, not {BASE}; the fallback base year would change"
    d = d[(d.Indicator == IND) & (d.Period == "12 month-ending") & (d.Month == "December")
          & d.Year.isin([BASE, LATE])].copy()
    fn = d.Footnote.fillna("")
    assert not fn.str.contains("Underreported").any()
    d["flag"] = "ok"
    d.loc[fn.str.contains("suppressed"), "flag"] = "suppressed (<10)"
    d.loc[fn.str.contains("low data quality"), "flag"] = "low data quality"
    assert (d["Data Value"].isna() == (d.flag != "ok")).all(), "a withheld value without a flag, or vice versa"
    d = d.rename(columns={"State": "st", "Year": "year", "Data Value": "deaths", "Predicted Value": "predicted"})
    d = d[["st", "year", "deaths", "predicted", "flag"]]

    # New York state = NY (excluding NYC) + YC (New York City)
    ny = d[d.st.isin(["NY", "YC"])]
    rows = []
    for y, g in ny.groupby("year"):
        assert len(g) == 2
        ok = (g.flag == "ok").all()
        rows.append({"st": "NY", "year": y, "deaths": g.deaths.sum() if ok else float("nan"),
                     "predicted": g.predicted.sum() if ok else float("nan"),
                     "flag": "ok" if ok else "; ".join(sorted(set(g.flag) - {"ok"}))})
    d = pd.concat([d[~d.st.isin(["NY", "YC"])], pd.DataFrame(rows)])
    d = d[d.st.isin(STATES)]
    # Louisiana has no drug-specific rows at all in VSRR (only totals and "Percent
    # with drugs specified": 46% in 2015, 70% in 2022). Treated like a low-quality flag.
    missing = sorted(set(STATES) - set(d.st))
    print("no T43.6 rows at all:", missing)
    d = pd.concat([d, pd.DataFrame([{"st": s, "year": y, "flag": "no drug-specific rows published"}
                                    for s in missing for y in (BASE, LATE)])])
    assert len(d) == 2 * len(STATES), len(d)
    return d


def ped_counts() -> pd.DataFrame:
    rows = []
    for y in (BASE, LATE):
        d, _ = year_peds(y)
        p = load(y, "person", ["ST_CASE", "VEH_NO", "PER_NO", "STATE"])
        d = d.merge(p, on=["ST_CASE", "VEH_NO", "PER_NO"], how="left", validate="1:1")
        if d.STATE.isna().any():
            raise SystemExit(f"{y}: {d.STATE.isna().sum()} pedestrian deaths without PERSON.STATE")
        c = d.STATE.map(FIPS).value_counts()
        rows += [{"st": s, "year": y, "ped_deaths": int(c.get(s, 0))} for s in STATES]
        print(y, len(d), "pedestrian deaths,", c.size, "states", flush=True)
    return pd.DataFrame(rows)


def main() -> None:
    fetch()
    m = meth_counts()
    t = m.merge(ped_counts(), on=["st", "year"], validate="1:1")
    pop = state_pop().rename(columns={"state": "st"})
    t = t.merge(pop, on=["st", "year"], how="left", validate="1:1")
    assert t.population.notna().all()
    for c in ("deaths", "predicted", "ped_deaths"):
        t[f"{c}_rate"] = t[c] / t.population * 1e5

    w = t.pivot(index="st", columns="year")
    s = pd.DataFrame(index=pd.Index(STATES, name="state"))
    for y in (BASE, LATE):
        s[f"population_{y}"] = w[("population", y)]
        s[f"meth_flag_{y}"] = w[("flag", y)]
        s[f"meth_deaths_{y}"] = w[("deaths", y)]
        s[f"meth_rate_{y}"] = w[("deaths_rate", y)]
        s[f"meth_predicted_rate_{y}"] = w[("predicted_rate", y)]
        s[f"ped_deaths_{y}"] = w[("ped_deaths", y)]
        s[f"ped_rate_{y}"] = w[("ped_deaths_rate", y)]
    s["meth_rate_change"] = s[f"meth_rate_{LATE}"] - s[f"meth_rate_{BASE}"]
    s["meth_predicted_rate_change"] = s[f"meth_predicted_rate_{LATE}"] - s[f"meth_predicted_rate_{BASE}"]
    s["ped_rate_change"] = s[f"ped_rate_{LATE}"] - s[f"ped_rate_{BASE}"]

    def reason(r) -> str:
        bad = [f"{y}: {r[f'meth_flag_{y}']}" for y in (BASE, LATE) if r[f"meth_flag_{y}"] != "ok"]
        return "; ".join(bad)
    s["excluded_reason"] = s.apply(reason, axis=1)
    s["included"] = s.excluded_reason == ""
    num = s.select_dtypes("number").columns
    s[num] = s[num].round(4)
    s.reset_index().to_csv(FINAL / "test_meth.csv", index=False)

    inc = s[s.included]
    exc = s[~s.included]
    lowq = exc[exc.excluded_reason.str.contains("low data quality|no drug-specific")]
    supp = exc[~exc.index.isin(lowq.index)]
    print(f"\nIncluded n={len(inc)}: {', '.join(inc.index)}")
    print(f"Excluded n={len(exc)}; low data quality or not published ({len(lowq)}): "
          + ", ".join(f"{k} [{v}]" for k, v in lowq.excluded_reason.items()))
    print(f"  suppressed <10 only ({len(supp)}): " + ", ".join(f"{k} [{v}]" for k, v in supp.excluded_reason.items()))

    x, y = inc.meth_rate_change, inc.ped_rate_change
    top = x.idxmax()
    keep = inc.index != top
    r_all, r_top = x.corr(y), x[keep].corr(y[keep])
    verdict = "PASS" if r_all > 0.3 and r_top > 0.3 else "FAIL"
    print(f"\nLargest psychostimulant rise: {top} (+{x.max():.1f} per 100,000; "
          f"{inc.loc[top, f'meth_rate_{BASE}']:.1f} -> {inc.loc[top, f'meth_rate_{LATE}']:.1f})")
    print(f"P10 (pre-registered, fallback {BASE} vs {LATE}) Pearson r, n={len(inc)}: {r_all:.3f}; "
          f"without {top}, n={keep.sum()}: {r_top:.3f} => {verdict}")
    print("Extras (not pre-registered):")
    print(f"  Spearman r: {x.corr(y, method='spearman'):.3f}; without {top}: "
          f"{x[keep].corr(y[keep], method='spearman'):.3f}")
    xp = inc.meth_predicted_rate_change
    tp = xp.idxmax()
    kp = inc.index != tp
    print(f"  Pearson r on Predicted Value: {xp.corr(y):.3f}; without its top state {tp}: {xp[kp].corr(y[kp]):.3f}")
    print(f"  National: pedestrian rate {s[f'ped_deaths_{BASE}'].sum() / s[f'population_{BASE}'].sum() * 1e5:.2f} -> "
          f"{s[f'ped_deaths_{LATE}'].sum() / s[f'population_{LATE}'].sum() * 1e5:.2f}")
    print(inc[[f"meth_rate_{BASE}", f"meth_rate_{LATE}", "meth_rate_change", f"ped_rate_{BASE}",
               f"ped_rate_{LATE}", "ped_rate_change"]].sort_values("meth_rate_change").round(2).to_string())
    scatter(inc, top, r_all, r_top)


def scatter(s: pd.DataFrame, top: str, r_all: float, r_top: float) -> None:
    import matplotlib.pyplot as plt
    from chart_explore import INK, MUTED, RULE, SURFACE, style

    fig, ax = plt.subplots(figsize=(9, 7), facecolor=SURFACE)
    style(ax)
    ax.grid(color=RULE)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.axvline(0, color=MUTED, linewidth=0.8)
    ax.scatter(s.meth_rate_change, s.ped_rate_change, s=22, color="#2a78d6", zorder=3)
    for st, (xv, yv) in s[["meth_rate_change", "ped_rate_change"]].iterrows():
        ax.annotate(st, (xv, yv), xytext=(3, 2), textcoords="offset points", fontsize=7, color=INK)
    ax.set_xlabel(f"Change in psychostimulant (T43.6) overdose deaths per 100,000, {BASE} to {LATE}", color=MUTED)
    ax.set_ylabel(f"Change in pedestrian deaths per 100,000, {BASE} to {LATE}", color=MUTED)
    ax.set_title(f"{len(s)} states: methamphetamine overdoses vs. pedestrian deaths (Pearson r = {r_all:.2f}; "
                 f"{r_top:.2f} without {top})", loc="left", color=INK, fontsize=10)
    fig.text(0.01, 0.005, "Sources: CDC/NCHS VSRR provisional overdose counts (states with usable drug data); "
             "NHTSA FARS; Census via FRED. Test P10, docs/hypothesis-test.md.", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(ROOT / "charts" / "test_meth_scatter.png", dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    main()
