"""Stage-by-stage jury funnel rates across every source we have, for the Sankey.

Stages (Johnson's Milwaukee Sankey, plus a trial-length branch):
  summoned -> eligible & available -> reported (asked to come in) -> sent to voir dire -> sworn -> days on trial

Each source's counts are typed in below from the documents in data/raw/ (see docs/sources.md for page refs);
county-level Oregon and Florida rates come from scripts/extract_counties.py.
Writes data/funnel_rates.csv (one row per source) and prints min / median / max per stage.

Run from the repo root: python projects/jury-duty/scripts/build_ranges.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
N = None

# level, source, year, summoned, eligible_available, reported, voir_dire, sworn, trials, trial_days
SOURCES = [
    ("county", "Milwaukee County, WI (CCAP-35)", 2024, 127_057, 46_199, 16_306, 16_927, 6_151, 524, 869),
    # Racine is 2-step: 16,673 questionnaires, then 10,793 summonses; "summoned" = summonses (data/racine_ccap35_2015_2025.csv)
    ("county", "Racine County, WI (CCAP-35)", 2025, 10_793, 7_877, 3_335, 2_137, 617, 55, 131),
    # Waukesha "Qualified Jurors" includes postponed jurors, so eligible_available = qualified - postponed
    ("county", "Waukesha County, WI (Annual Jury Program Report)", 2025, 11_099, 7_652 - 2_664, 2_801, 2_534, 1_028, 87, 174),
    # Jackson: "Jurors Available" = reported; sworn = 13% "Selected as Jurors" x available
    ("county", "Jackson County, MO (16th Circuit)", 2025, N, N, 7_831, 4_498, round(0.13 * 7_831), 73, 310),
    ("state", "Oregon (OJD Jury Data Overview)", 2025, 829_744, 227_786, 105_274, N, N, N, N),
    ("state", "Massachusetts (OJC annual report)", 2015, 656_712, 435_563, 206_909, N, N, N, N),
    ("state", "Massachusetts (OJC demographic report)", 2025, N, N, 181_383, N, 24_510, N, N),
    ("state", "Pennsylvania (AOPC InfoShare)", 2015, 1_238_807, N, 237_749, round(0.81 * 237_749), N, N, N),
    ("state", "Minnesota (House Research, Nov 2025)", 2024, 217_476, N, N, N, 11_179, 1_047, N),
    ("state", "New Mexico (AOC release, trial + grand juries)", 2025, N, N, 45_000, N, 8_200, N, N),
    ("federal", "U.S. district courts (J-2, J-10, T-1)", 2025, N, N, 146_290, round(0.865 * 146_290), round(0.216 * 146_290), 2_701, 12_307),
]
COLS = ["level", "source", "year", "summoned", "eligible_available", "reported", "voir_dire", "sworn", "trials", "trial_days"]
df = pd.DataFrame(SOURCES, columns=COLS)


def ratio(a, b):
    return (df[a] / df[b]).where(df[a].notna() & df[b].notna())


rates = df[["level", "source", "year"]].copy()
rates["eligible_per_summoned"] = ratio("eligible_available", "summoned")
rates["reported_per_summoned"] = ratio("reported", "summoned")
rates["voir_dire_per_reported"] = ratio("voir_dire", "reported")
rates["sworn_per_reported"] = ratio("sworn", "reported")
rates["sworn_per_summoned"] = ratio("sworn", "summoned")
rates["trial_days_per_trial"] = ratio("trial_days", "trials")

# County distributions from extract_counties.py (Oregon 2025, Florida 2024)
orc = pd.read_csv(ROOT / "data" / "oregon_counties_2025.csv")
flc = pd.read_csv(ROOT / "data" / "florida_counties_2024.csv")
flc = flc[flc.trials_2024 > 0]  # Lafayette and Calhoun held no jury trials in 2024; their 0% rates are blanks
extra = pd.concat([
    pd.DataFrame({"level": "county", "source": "Oregon county: " + orc.county, "year": 2025,
                  "eligible_per_summoned": orc.responded_qualified / orc.summoned, "urbanicity": orc.urbanicity}),
    pd.DataFrame({"level": "county", "source": "Florida county: " + flc.county, "year": 2024,
                  "eligible_per_summoned": flc.summoning_yield_pct / 100, "voir_dire_per_reported": flc.pct_to_voir_dire / 100,
                  "urbanicity": flc.urbanicity}),
])
all_rates = pd.concat([rates, extra], ignore_index=True)
all_rates.to_csv(ROOT / "data" / "funnel_rates.csv", index=False)

pd.set_option("display.width", 220)
print("Named sources:")
print(rates.round(3).to_string(index=False))
print("\nRange across named sources + Oregon/Florida counties (min / p10 / median / p90 / max, n):")
for c in [c for c in all_rates.columns if c.endswith(("summoned", "reported", "trial"))]:
    s = all_rates[c].dropna()
    q = s.quantile([0, .1, .5, .9, 1]).round(3).tolist()
    print(f"  {c:24s} {q}  n={len(s)}")
print("\nOregon/Florida eligible-per-summoned by urbanicity (median):")
print(extra.groupby([extra.source.str.split(" ").str[0], "urbanicity"]).eligible_per_summoned.median().round(3).unstack().to_string())
