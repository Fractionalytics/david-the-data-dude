"""Yearly state Silver Alert table from the monthly-report totals: alerts issued vs. direct recoveries.

Input:  data/interim/silver_monthly_totals.csv (parse_silver_monthly.py)
Output: data/processed/silver_alerts_yearly.csv

alerts = December's "Total for the year"; direct_recoveries = change in FDLE's cumulative direct-recovery count
from the previous December. 2011 is left out of the per-year rate: FDLE redefined "direct" in July 2011
(splitting out "indirect"), so the January-June 2011 counts aren't comparable.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1] / "data"
t = pd.read_csv(ROOT / "interim" / "silver_monthly_totals.csv")
dec = t[t.month == 12].set_index("year")

y = pd.DataFrame({
    "alerts": dec.alerts_ytd,
    "direct_recoveries_cum": dec.direct_recoveries_to_date,
    "alerts_since_oct_2008": dec.alerts_since_2008,
})
y["direct_recoveries"] = y.direct_recoveries_cum.diff()
y.loc[2011, "direct_recoveries"] = None
y["direct_rate"] = (y.direct_recoveries / y.alerts).round(3)

out = ROOT / "processed" / "silver_alerts_yearly.csv"
out.parent.mkdir(exist_ok=True)
y.reset_index().to_csv(out, index=False)
print(y.to_string())

span = y.loc[2012:2020]
print(f"\n2012-2020: {int(span.alerts.sum())} alerts, {int(span.direct_recoveries.sum())} direct recoveries "
      f"= {span.direct_recoveries.sum() / span.alerts.sum():.1%}")
last = t.iloc[-1]
print(f"Oct 2008 - Dec 2020 (FDLE cumulative): {int(last.alerts_since_2008)} alerts, "
      f"{int(last.direct_recoveries_to_date)} direct (+{int(last.indirect_recoveries_to_date)} indirect) "
      f"= {last.direct_recoveries_to_date / last.alerts_since_2008:.1%} direct, "
      f"{(last.direct_recoveries_to_date + last.indirect_recoveries_to_date) / last.alerts_since_2008:.1%} direct+indirect")
