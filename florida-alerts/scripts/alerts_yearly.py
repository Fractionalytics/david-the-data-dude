"""Yearly all-alert-types table (2020-2025) from the checked newsletter figures, cross-checked against the
Silver Alert monthly reports where they overlap.

Input:  data/interim/newsletter_stats.csv (checked by check_newsletter_stats.py)
        data/processed/silver_alerts_yearly.csv (silver_yearly.py)
Output: data/processed/alerts_yearly_by_type.csv   one row per year x alert type, full calendar years only
        data/processed/alerts_yearly_direct.csv    one row per year: all alerts vs. direct recoveries, where stated
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1] / "data"
s = pd.read_csv(ROOT / "interim" / "newsletter_stats.csv")
s["year"] = s.period_start.str[:4].astype(int)
yearly = s[s.period_kind == "calendar_year"]

# Where two issues report the same year and type, keep the one with recoveries (the stat box) and note the conflict.
by_type = (yearly[~yearly.alert_type.str.startswith(("All", "State alerts"))]
           .sort_values("recovered", na_position="last")
           .groupby(["year", "alert_type"], as_index=False).first())
conflicts = (yearly.groupby(["year", "alert_type"]).alerts_issued.nunique() > 1)
by_type["conflicting_sources"] = by_type.set_index(["year", "alert_type"]).index.map(conflicts).fillna(False)
by_type = by_type[["year", "alert_type", "alerts_issued", "recovered", "direct_recoveries", "direct_share_stated",
                   "conflicting_sources", "source_issue", "page"]]
by_type.to_csv(ROOT / "processed" / "alerts_yearly_by_type.csv", index=False)
print(by_type.to_string(index=False))

direct = yearly[yearly.direct_recoveries.notna() & yearly.alert_type.str.startswith("All")].copy()
sums = by_type.groupby("year")[["alerts_issued", "recovered"]].sum(min_count=1)
direct["alerts_issued"] = direct.alerts_issued.fillna(direct.year.map(sums.alerts_issued))
direct["recovered"] = direct.recovered.fillna(direct.year.map(sums.recovered))
direct["direct_rate"] = (direct.direct_recoveries / direct.alerts_issued).round(3)
direct = direct[["year", "alert_type", "alerts_issued", "recovered", "direct_recoveries", "direct_rate", "source_issue"]]
direct.to_csv(ROOT / "processed" / "alerts_yearly_direct.csv", index=False)
print("\nAll alert types, direct recoveries:\n" + direct.to_string(index=False))

# Cross-check: newsletter Silver totals vs. the monthly reports, and newsletter "direct" vs. Silver-only direct.
silver = pd.read_csv(ROOT / "processed" / "silver_alerts_yearly.csv").set_index("year")
for year in sorted(set(silver.index) & set(by_type.year)):
    nl = by_type[(by_type.year == year) & (by_type.alert_type == "Silver")]
    if len(nl):
        print(f"\n{year} Silver alerts: newsletter {int(nl.alerts_issued.iloc[0])} vs monthly reports {int(silver.alerts[year])}")
    d = direct[direct.year == year]
    if len(d):
        print(f"{year} direct: newsletter all-types {int(d.direct_recoveries.iloc[0])} vs Silver-only monthly {int(silver.direct_recoveries[year])}")
