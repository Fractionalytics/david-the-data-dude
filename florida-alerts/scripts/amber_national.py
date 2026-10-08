"""National AMBER Alert outcomes by year, plus Florida's alert count, from the NCMEC/DOJ annual reports.

Input:  data/interim/amber/<year>.txt (amber_reports_text.py)
Output: data/processed/amber_national_yearly.csv
        year, alerts, recovered, direct_cases, direct_rate, florida_alerts, plus the source sentences.

The reports give recovery outcomes nationally only; for Florida they give just the number of alerts it issued.
2012's summary page extracts as jumbled columns, so its alert and direct counts come from the success-stories
sentence ("Of the 167 AMBER Alert cases in 2012, ... 52 AMBER Alert cases ...") and "recovered" is left blank.
"""
from pathlib import Path
import re

import pandas as pd

ROOT = Path(__file__).resolve().parents[1] / "data"
NATIONAL = re.compile(r"Of the ([\d,]+) AMBER[- ]Alerts? issued (?:(?:between|from) .{10,60}?\d{4}|in this time frame),\s*"
                      r"([\d,]+) cases resulted in a recovery, ([\d,]+) of which[^.]{0,80}?direct result")
SUCCESS = re.compile(r"Of the ([\d,]+) AMBER[- ]Alert cases in \d{4}, [\d,]+ children involved in ([\d,]+) AMBER[- ]Alert cases "
                     r"were successfully recovered as a direct result")
# State table rows: "Florida 11 5%", "Florida and Ohio 10 each", "Florida, Georgia, and Ohio 18 each",
# "California, Florida and Washington 10 each", "Florida 13".
FLORIDA = re.compile(r"(?:[A-Z][a-z]+(?: [A-Z][a-z]+)?,? (?:and )?)*Florida(?:,? (?:and )?[A-Z][a-z]+(?: [A-Z][a-z]+)?)* (\d{1,2})\b(?! percent)")

rows = []
for txt in sorted((ROOT / "interim" / "amber").glob("*.txt")):
    year = int(txt.stem)
    pages = txt.read_text(encoding="utf-8").split("\f")
    flat = re.sub(r"\s+", " ", " ".join(pages))
    m = NATIONAL.search(flat)
    s = SUCCESS.search(flat)
    alerts, recovered, direct, quote = (None,) * 4
    if m:
        alerts, recovered, direct, quote = int(m[1].replace(",", "")), int(m[2]), int(m[3]), m[0]
    elif s:
        alerts, direct, quote = int(s[1]), int(s[2]), s[0]
    # Florida's count: the first Florida match in the state table (the page that lists "Number of alerts").
    fl, fl_quote = None, None
    for page in pages:
        p = re.sub(r"\s+", " ", page)
        i = p.find("Number of alerts") if "Number of alerts" in p else p.find("Number of Alerts")
        if i >= 0:
            f = FLORIDA.search(p, i)
            if f:
                fl, fl_quote = int(f[1]), f[0]
                break
    rows.append({"year": year, "alerts": alerts, "recovered": recovered, "direct_cases": direct,
                 "florida_alerts": fl, "national_quote": quote, "florida_quote": fl_quote})

df = pd.DataFrame(rows)
df["direct_rate"] = (df.direct_cases / df.alerts).round(3)
df["florida_share"] = (df.florida_alerts / df.alerts).round(3)
out = ROOT / "processed" / "amber_national_yearly.csv"
df.to_csv(out, index=False)
print(df.drop(columns=["national_quote"]).to_string(index=False))
tot = df.dropna(subset=["alerts", "direct_cases"])
print(f"\n{len(tot)} years: {int(tot.alerts.sum())} alerts, {int(tot.direct_cases.sum())} direct = "
      f"{tot.direct_cases.sum() / tot.alerts.sum():.1%}")
