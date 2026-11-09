"""Pre-registered test P8 (docs/hypothesis-test.md, Round 2): across states, does
the change in the age-adjusted drug overdose death rate track the change in the
pedestrian death rate?

    python scripts/test_overdose.py
      reads  data/raw/cdc_overdose/nchs_drug_poisoning_by_state_xbxb-epbu.csv
                 NCHS "Drug Poisoning Mortality by State: United States",
                 data.cdc.gov dataset xbxb-epbu, 1999-2016 (used for 2009-2011)
             data/raw/cdc_overdose/nchs_drug_overdose_mortality_by_state_map.json
                 NCHS "Drug Overdose Mortality by State" map data (cdc.gov
                 state-stats page), 1999, 2005, 2014-2024 (used for 2020-2022)
             data/final/test_homeless.csv   pedestrian side, built by
                 scripts/test_homeless.py (FARS PER_TYP 5 / INJ_SEV 4 by PERSON.STATE,
                 average deaths per year / average FRED population x 100,000)
      writes data/final/test_overdose.csv        one row per state (50 + DC)
             charts/test_overdose_scatter.png    (not pre-registered)
    Both raw files are downloaded on first run (see data/raw/cdc_overdose/SOURCE.md).

Steps (fixed in the pre-registration before any data was seen)
  1. Overdose rate per period = mean of the three yearly age-adjusted rates
     (per 100,000, 2000 US standard population): 2009, 2010, 2011 from
     xbxb-epbu (rows Both Sexes / All Ages / All Races-All Origins);
     2020, 2021, 2022 from the NCHS map data. Change = late - early.
     Both sources are NCHS final NVSS mortality, ICD-10 underlying cause
     X40-X44, X60-X64, X85, Y10-Y14. Consistency is checked on the overlap
     years 2014-2016 (printed).
  2. Pedestrian rate change from data/final/test_homeless.csv (same build as P4).
  3. Pre-registered: Pearson r across 51, and with West Virginia left out.
     PASS if both r > 0.3. Also reports which state has the largest overdose
     rise; if it isn't WV, r without that state too (not pre-registered).
  4. Not pre-registered extras: Spearman r; scatter plot.
"""

import json
import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fars_pedestrians import FINAL, ROOT  # noqa: E402
from fars_decompose import FIPS  # noqa: E402

RAW = ROOT / "data" / "raw" / "cdc_overdose"
UA = {"User-Agent": "content-engine-research-bot/1.0"}
EARLY_URL = "https://data.cdc.gov/api/views/xbxb-epbu/rows.csv?accessType=DOWNLOAD"
LATE_URL = "https://www.cdc.gov/nchs/pressroom/sosmap/drug_poisoning_mortality/Drug_Overdose_dfe.json"
EARLY_FILE = RAW / "nchs_drug_poisoning_by_state_xbxb-epbu.csv"
LATE_FILE = RAW / "nchs_drug_overdose_mortality_by_state_map.json"
EARLY, LATE = [2009, 2010, 2011], [2020, 2021, 2022]
STATES = sorted(FIPS.values())
NAMES = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
         "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
         "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
         "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
         "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
         "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
         "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
         "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
         "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
         "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
         "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}


def fetch(url: str, path: Path) -> None:
    if path.exists():
        return
    RAW.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, headers=UA, timeout=120)
    if r.status_code != 200:
        raise SystemExit(f"{url}: HTTP {r.status_code}; not retrying (see SOURCE.md)")
    path.write_bytes(r.content)
    print("downloaded", path.name, len(r.content), "bytes")


def early_rates() -> pd.DataFrame:
    d = pd.read_csv(EARLY_FILE)
    d.columns = [c.strip() for c in d.columns]
    d = d[(d.Sex == "Both Sexes") & (d["Age Group"] == "All Ages")
          & (d["Race and Hispanic Origin"] == "All Races-All Origins")]
    d = d[d.State.isin(NAMES)].assign(state=lambda x: x.State.map(NAMES))
    return d.rename(columns={"Year": "year", "Age-adjusted Rate": "rate"})[["state", "year", "rate"]]


def late_rates() -> pd.DataFrame:
    d = pd.DataFrame(json.loads(LATE_FILE.read_text(encoding="utf-8"))["data"])
    d["STATE"] = d.STATE.replace({"District of Columbia": "DC"})
    d["year"] = d.YEAR.astype(int)
    d["rate"] = pd.to_numeric(d.RATE)
    return d.rename(columns={"STATE": "state"})[["state", "year", "rate"]]


def main() -> None:
    fetch(EARLY_URL, EARLY_FILE)
    fetch(LATE_URL, LATE_FILE)
    e, l = early_rates(), late_rates()

    ov = e.merge(l, on=["state", "year"], suffixes=("_xbxb", "_map"))
    ov["diff"] = ov.rate_xbxb - ov.rate_map
    print(f"Overlap check, years {sorted(ov.year.unique())}, n={len(ov)}: "
          f"max |diff| {ov['diff'].abs().max():.2f}, mean diff {ov['diff'].mean():.3f}")
    print(ov.assign(a=ov['diff'].abs()).nlargest(5, "a").round(2).to_string(index=False))

    s = pd.DataFrame(index=STATES)
    for tag, ys, src in (("2009_11", EARLY, e), ("2020_22", LATE, l)):
        p = src[src.year.isin(ys)].pivot(index="state", columns="year", values="rate").reindex(STATES)
        assert p.notna().all().all() and list(p.columns) == ys, p
        for y in ys:
            s[f"od_rate_{y}"] = p[y]
        s[f"od_rate_{tag}"] = p.mean(axis=1)
    s["od_rate_change"] = s.od_rate_2020_22 - s.od_rate_2009_11

    ped = pd.read_csv(FINAL / "test_homeless.csv").set_index("state")
    need = ["ped_deaths_2009_11", "ped_rate_2009_11", "ped_deaths_2020_22", "ped_rate_2020_22", "ped_rate_change"]
    assert set(need) <= set(ped.columns) and set(STATES) == set(ped.index), "test_homeless.csv lacks pedestrian columns"
    s = s.join(ped[need])
    assert len(s) == 51 and s.notna().all().all()
    s.round(4).rename_axis("state").reset_index().to_csv(FINAL / "test_overdose.csv", index=False)

    x, y = s.od_rate_change, s.ped_rate_change
    no_wv = s.index != "WV"
    r_all, r_nowv = x.corr(y), x[no_wv].corr(y[no_wv])
    verdict = "PASS" if r_all > 0.3 and r_nowv > 0.3 else "FAIL"
    print(f"\nP8 (pre-registered) Pearson r, n=51: {r_all:.3f}; without WV, n=50: {r_nowv:.3f} => {verdict}")
    top = x.idxmax()
    print(f"Largest overdose rise: {top} (+{x.max():.1f}); WV +{x['WV']:.1f}; rank of WV: {int(x.rank(ascending=False)['WV'])}")
    if top != "WV":
        m = s.index != top
        print(f"  Not pre-registered: Pearson r without {top}: {x[m].corr(y[m]):.3f}; "
              f"without WV and {top}: {x[m & no_wv].corr(y[m & no_wv]):.3f}")
    print("Extras (not pre-registered):")
    print(f"  Spearman r: {x.corr(y, method='spearman'):.3f}; without WV: {x[no_wv].corr(y[no_wv], method='spearman'):.3f}")
    print(s[["od_rate_2009_11", "od_rate_2020_22", "od_rate_change", "ped_rate_change"]]
          .sort_values("od_rate_change").round(2).to_string())
    scatter(s, r_all, r_nowv)


def scatter(s: pd.DataFrame, r_all: float, r_nowv: float) -> None:
    import matplotlib.pyplot as plt
    from chart_explore import INK, MUTED, RULE, SURFACE, style

    fig, ax = plt.subplots(figsize=(9, 7), facecolor=SURFACE)
    style(ax)
    ax.grid(color=RULE)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.axvline(0, color=MUTED, linewidth=0.8)
    ax.scatter(s.od_rate_change, s.ped_rate_change, s=22, color="#2a78d6", zorder=3)
    for st, (xv, yv) in s[["od_rate_change", "ped_rate_change"]].iterrows():
        ax.annotate(st, (xv, yv), xytext=(3, 2), textcoords="offset points", fontsize=7, color=INK)
    ax.set_xlabel("Change in age-adjusted drug overdose deaths per 100,000, 2009-11 to 2020-22", color=MUTED)
    ax.set_ylabel("Change in pedestrian deaths per 100,000, 2009-11 to 2020-22", color=MUTED)
    ax.set_title(f"States: drug overdoses vs. pedestrian deaths (Pearson r = {r_all:.2f}; "
                 f"{r_nowv:.2f} without WV)", loc="left", color=INK, fontsize=10)
    fig.text(0.01, 0.005, "Sources: CDC/NCHS drug overdose mortality by state; NHTSA FARS; Census via FRED. "
             "Test P8, pre-registered in docs/hypothesis-test.md.", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(ROOT / "charts" / "test_overdose_scatter.png", dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    main()
