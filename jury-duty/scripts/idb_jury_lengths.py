"""How long federal civil jury trials last, from data/idb_civil_trials.csv (built by idb_civil_trials.py).

Days = weekdays from trial start to end, inclusive (weekends skipped; federal holidays not removed).
Calendar days (the `days` column from idb_civil_trials.py) overstate length: a two-week trial spans 12 calendar days.
Run from the repo root: python projects/jury-duty/scripts/idb_jury_lengths.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
t = pd.read_csv(ROOT / "data/idb_civil_trials.csv", dtype={"PROCPROG": str, "DISP": str})
j = t[t.jury & t.days.notna()].copy()
print(f"calendar durations outside 1-365 days (dropped): {((j.days < 1) | (j.days > 365)).sum()} of {len(j)}")
j = j[(j.days >= 1) & (j.days <= 365)]
start = pd.to_datetime(j.TRIBEGAN).values.astype("datetime64[D]")
end = pd.to_datetime(j.TRIALEND).values.astype("datetime64[D]")
j["days"] = np.busday_count(start, end + 1)
print(f"trials starting and ending on a weekend (0 weekdays, dropped): {(j.days == 0).sum()}")
j = j[j.days >= 1]

BINS, LABELS = [0, 1, 2, 3, 9, 19, 10_000], ["1 day", "2 days", "3 days", "4-9 days", "10-19 days", "20+ days"]


def dist(d):
    c = pd.cut(d.days, BINS, labels=LABELS).value_counts().reindex(LABELS)
    return pd.DataFrame({"n": c, "pct": (c / c.sum() * 100).round(1)})


rows = []
for name, d in [("FY2023", j[j.term_fy == 2023]), ("FY2019-2025", j[j.term_fy.between(2019, 2025)])]:
    print(f"===== {name}: n={len(d)}, median {d.days.median():.0f} days, mean {d.days.mean():.1f}")
    out = dist(d)
    print(out.to_string())
    rows.append(out.assign(period=name))
pd.concat(rows).to_csv(ROOT / "data/federal_civil_jury_trial_lengths.csv")

d = j[j.term_fy.between(2019, 2025)]
print("\nBy PROCPROG (7 = ended during jury trial, 9 = after jury trial):")
print(d.groupby("PROCPROG").days.describe()[["count", "50%", "mean"]].to_string())
print("\nDisposition of all jury-trial cases FY2019-2025 (7 = jury verdict, 13 = settled):")
print(t[t.jury & t.term_fy.between(2019, 2025)].DISP.value_counts().head(8).to_string())
