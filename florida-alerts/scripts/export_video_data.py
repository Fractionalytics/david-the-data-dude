"""Export the numbers the Reel's charts draw, from the checked pipeline outputs, to video/src/data/silver.json.

Every on-screen number comes from here, so a re-run of the pipeline flows straight into the charts.
- years:    state Silver Alerts per year, 2011-2020 from FDLE's monthly reports, 2021 from the Spring 2022
            newsletter (287). (2022 has no calendar-year total, so the chart stops at 2021.)
- dots:     per 100 Silver Alerts, how many were found (527 of 536 in 2020-2021, newsletters) and how many
            found because of the alert (222 of 2,070 in 2012-2020, monthly reports), rounded.
- foundBy:  who spotted the person, in FDLE's 197 success stories (2014-2022).
- channels: how they knew, in the success stories that name a channel.
- states:   where state Silver Alert subjects were recovered, 2011-2020.
"""
from pathlib import Path
import json

import pandas as pd

P = Path(__file__).resolve().parents[1]
D = P / "data"

yearly = pd.read_csv(D / "processed" / "silver_alerts_yearly.csv")
by_type = pd.read_csv(D / "processed" / "alerts_yearly_by_type.csv")
silver_nl = by_type[by_type.alert_type == "Silver"].set_index("year")
years = [{"year": int(r.year), "alerts": int(r.alerts)} for r in yearly.itertuples()]
years.append({"year": 2021, "alerts": int(silver_nl.loc[2021, "alerts_issued"])})

found = int(silver_nl.loc[[2020, 2021], "recovered"].sum())
issued = int(silver_nl.loc[[2020, 2021], "alerts_issued"].sum())
span = yearly[yearly.year.between(2012, 2020)]
dots = {
    "found": round(100 * found / issued),
    "direct": round(100 * span.direct_recoveries.sum() / span.alerts.sum()),
    "foundSource": f"{found} of {issued} found, 2020-2021",
    "directSource": f"{int(span.direct_recoveries.sum())} of {int(span.alerts.sum())}, 2012-2020",
}

stories = pd.read_csv(D / "interim" / "silver_success_stories.csv")
found_by = stories.found_by.value_counts().to_dict()
channels = stories.channel.value_counts().to_dict()

states = pd.read_csv(D / "processed" / "silver_recovery_states.csv")
states = states[states.recovered_state.str.fullmatch(r"[A-Z]{2}")]

out = {
    "years": years,
    "dots": dots,
    "foundBy": {k: int(v) for k, v in found_by.items()},
    "stories": int(len(stories)),
    "channels": {k: int(v) for k, v in channels.items()},
    "states": {r.recovered_state: int(r.people) for r in states.itertuples()},
    "casesTotal": int(pd.read_csv(D / "interim" / "silver_monthly_cases.csv").shape[0]),
    # Which 2011-2020 monthly reports were recovered from the Internet Archive (carousel slide 4).
    "reportMonths": sorted([int(r.year), int(r.month)] for r in pd.read_csv(D / "interim" / "silver_monthly_totals.csv").itertuples()),
}
dest = P / "video" / "src" / "data" / "silver.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
