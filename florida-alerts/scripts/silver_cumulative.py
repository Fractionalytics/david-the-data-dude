"""Silver Alert running totals since October 2008, from every source that states them, through October 2023.

Inputs:  data/interim/silver_anniversary_releases.csv  (hand-typed from FDLE's October news releases; checked here)
         data/interim/silver_monthly_totals.csv         (December of each year, 2011-2020)
         data/interim/newsletter_stats.csv              (Fall 2021 newsletter's since-inception figure)
Output:  data/processed/silver_cumulative.csv           as_of, alerts, direct, direct_rate, qualifier, source

The 2022 release states only the direct count; its alert count comes from its headline ("FDLE issues 3,000
Florida Silver Alerts") and the text ("activated its 3,000th Silver Alert over the weekend").
"""
from pathlib import Path
import re
import sys

import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1] / "data"
rel = pd.read_csv(ROOT / "interim" / "silver_anniversary_releases.csv")


def page_text(name):
    html = (ROOT / "raw" / "after_2020" / name).read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", BeautifulSoup(html, "html.parser").get_text(" ", strip=True))


problems = 0
for _, r in rel.iterrows():
    text = page_text(r.source_file)
    if r.quote not in text:
        print(f"quote not found in {r.source_file}: {r.quote[:80]}")
        problems += 1
    for v in (r.alerts_since_2008, r.direct_since_2008):
        if f"{v:,}" not in text and str(v) not in text:
            print(f"{v} not found in {r.source_file}")
            problems += 1
print(f"{len(rel)} releases checked, {problems} problems")
if problems:
    sys.exit(1)

rows = [{"as_of": r.as_of, "alerts": r.alerts_since_2008, "direct": r.direct_since_2008,
         "qualifier": "" if r.alerts_qualifier == "exact" else "more than", "source": f"FDLE release ({r.url})"}
        for _, r in rel.iterrows()]

t = pd.read_csv(ROOT / "interim" / "silver_monthly_totals.csv")
dec = t[(t.month == 12) & t.alerts_since_2008.notna() & (t.year >= 2012)]
rows += [{"as_of": f"{int(r.year)}-12-31", "alerts": int(r.alerts_since_2008), "direct": int(r.direct_recoveries_to_date),
          "qualifier": "", "source": f"FDLE monthly report ({r.file})"} for _, r in dec.iterrows()]

nl = pd.read_csv(ROOT / "interim" / "newsletter_stats.csv")
s = nl[(nl.period_kind == "cumulative") & (nl.alert_type == "Silver")].iloc[0]
rows.append({"as_of": s.period_end, "alerts": int(s.alerts_issued), "direct": int(s.direct_recoveries),
             "qualifier": "", "source": f"MEPIC newsletter {s.source_issue} p{s.page}"})

out = pd.DataFrame(rows).sort_values("as_of")
out["direct_rate"] = (out.direct / out.alerts).round(3)
out.to_csv(ROOT / "processed" / "silver_cumulative.csv", index=False)
print(out[["as_of", "qualifier", "alerts", "direct", "direct_rate", "source"]].to_string(index=False))

# Cross-check: the 2015 release against the monthly report for the same point in time.
sep15 = t[(t.year == 2015) & (t.month == 9)].iloc[0]
print(f"\nSep 2015 monthly report: {int(sep15.alerts_since_2008)} alerts, {int(sep15.direct_recoveries_to_date)} direct "
      f"vs Oct 8 2015 release: 1134, 110")
