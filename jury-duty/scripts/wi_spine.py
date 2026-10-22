"""Are Milwaukee, Racine and Waukesha (WI) a fair stand-in for a "typical" state court? And their funnel per 1,000 summoned.

1. For each stage rate, show the three Wisconsin values next to every other source in data/funnel_rates.csv
   (built by build_ranges.py) and where each Wisconsin value falls in the non-Wisconsin spread (percentile rank).
2. Build the spine: each county's funnel per 1,000 summoned, plus the median of the three (equal weight, so
   Milwaukee's size doesn't swamp the others). Racine uses its 2015-2025 pooled counts; for the 2020-2025
   two-step years "summoned" = summonses sent, for 2015-2019 one-step years it's the questionnaire-summons.

Run from the repo root: python projects/jury-duty/scripts/wi_spine.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WI = ["Milwaukee", "Racine", "Waukesha"]
STAGES = ["eligible_per_summoned", "reported_per_summoned", "voir_dire_per_reported", "sworn_per_reported",
          "sworn_per_summoned", "trial_days_per_trial"]

rates = pd.read_csv(ROOT / "data" / "funnel_rates.csv")
is_wi = rates.source.str.contains("|".join(WI))
print("1. Wisconsin vs everyone else (percentile rank of each WI value among non-WI sources)\n")
for s in STAGES:
    others = rates.loc[~is_wi, s].dropna()
    line = f"  {s:24s} others: n={len(others):3d} p10={others.quantile(.1):.3f} med={others.median():.3f} p90={others.quantile(.9):.3f} |"
    for _, r in rates[is_wi].iterrows():
        v = r[s]
        if pd.notna(v):
            pct = (others < v).mean() * 100 if len(others) else float("nan")
            line += f" {r.source.split(' ')[0]} {v:.3f} (p{pct:.0f})"
    print(line)

# --- spine ---
rac = pd.read_csv(ROOT / "data" / "racine_ccap35_2015_2025.csv")
racine = {
    "summoned": rac.summons_sent.sum(), "eligible": rac.eligible_available.sum(), "called_off": rac.called_off.sum(),
    "reported": rac.reported_for_selection.sum(), "not_used": rac.not_used.sum(),
    "sworn": rac.sworn.sum(), "trials": rac.voir_dires_begun.sum(), "trial_days": rac.trial_days.sum(),
}
counties = {
    "Milwaukee 2024": {"summoned": 127_057, "eligible": 46_199, "called_off": 28_102, "reported": 16_306, "not_used": 3_901,
                       "sworn": 6_151, "trials": 524, "trial_days": 869},
    "Racine 2015-25": racine,
    # Waukesha doesn't print a called-off count; qualified (7,652) - postponed (2,664) - required to report (2,801) = 2,187 implied
    "Waukesha 2025": {"summoned": 11_099, "eligible": 7_652 - 2_664, "called_off": 7_652 - 2_664 - 2_801, "reported": 2_801,
                      "not_used": 305, "sworn": 1_028, "trials": 87, "trial_days": 174},
}
# "Sent to voir dire" in CCAP-35 counts seats (one juror can sit in several voir dires), so the spine counts
# people instead: reported minus "Not Used" (reported but never sent to a courtroom).
spine = pd.DataFrame({k: {"eligible & available": v["eligible"] / v["summoned"] * 1000,
                          "called off": v["called_off"] / v["summoned"] * 1000,
                          "reported": v["reported"] / v["summoned"] * 1000,
                          "sent to a courtroom (people)": (v["reported"] - v["not_used"]) / v["summoned"] * 1000,
                          "sworn": v["sworn"] / v["summoned"] * 1000,
                          "trial days per trial": v["trial_days"] / v["trials"]} for k, v in counties.items()})
spine["median of 3"] = spine.median(axis=1)
print("\n2. Spine per 1,000 summoned (last row is trial days per trial):\n")
print(spine.round(1).to_string())
spine.round(2).to_csv(ROOT / "data" / "wi_spine_per_1000.csv")
