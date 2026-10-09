"""Write the numbers the Remotion charts draw to video/src/data/ideabrowser.json.

Featured ideas only (one per daily email), Jev definitions v3. One dataset per
storyboard card that calls for a chart:
  eras     cards 2 and 7: share of featured ideas classified as services, per era
  strip    card 4: one entry per day from 74 days before July 28 through the cut-off
  seesaw   card 6: services vs software, August vs September 2026
  conveyor card 3: 25 real newsletter-era ideas (July 28 to the cut-off), sampled in
           proportion to the era's mix (evenly spaced within each bin), in date order, with
           the bin Jev sorted each into, so the bins fill in the era's true proportions

Usage: python projects/ideabrowser/scripts/make_chart_data.py
"""
import json
from pathlib import Path

import pandas as pd

from classify import ANSWERS, load_ideas

OUT = Path(__file__).resolve().parents[1] / "video" / "src" / "data" / "ideabrowser.json"
SWITCH = pd.Timestamp("2026-07-28")  # first newsletter-format email
CONVEYOR_ITEMS = 25


def featured():
    a = pd.DataFrame(map(json.loads, ANSWERS.open(encoding="utf-8")))
    main = a[(a.definitions_version == "v3") & (a["mode"] == "main")].drop_duplicates("key", keep="last")
    d = load_ideas().merge(main[["key", "business_type"]], on="key")
    d = d[d.role == "featured"].copy()
    d["day"] = pd.to_datetime(d.date_utc.str[:10])
    return d


def main():
    d = featured()
    service = d.business_type == "Service"
    cutoff = d.day.max()

    eras = [{"era": int(e), "service": int(service[d.era == e].sum()), "total": int((d.era == e).sum())}
            for e in (1, 2, 3)]

    days = (cutoff - SWITCH).days + 1
    start = SWITCH - pd.Timedelta(days=days)
    by_day = d.set_index("day").business_type
    strip = [{"date": f"{day:%Y-%m-%d}",
              "type": by_day.get(day, None) if day in by_day.index else None}
             for day in pd.date_range(start, cutoff)]

    seesaw = []
    for month in ("2026-08", "2026-09"):
        m = d[d.day.dt.strftime("%Y-%m") == month]
        seesaw.append({"month": month, "service": int((m.business_type == "Service").sum()),
                       "software": int((m.business_type == "Software / app").sum()), "total": len(m)})

    bins = {"Service": "service", "Software / app": "software", "Marketplace": "marketplace"}
    era = d[d.day >= SWITCH].sort_values("day").copy()
    era["bin"] = era.business_type.map(bins).fillna("other")
    quota = (era.bin.value_counts() * CONVEYOR_ITEMS / len(era))
    take = quota.astype(int)  # largest-remainder rounding to exactly CONVEYOR_ITEMS
    for b in (quota - take).sort_values(ascending=False).index[: CONVEYOR_ITEMS - take.sum()]:
        take[b] += 1
    picked = []
    for b, n in take.items():
        rows = era[era.bin == b]
        picked += [rows.iloc[round(i * (len(rows) - 1) / max(n - 1, 1))] for i in range(n)] if n else []
    conveyor = [r.bin for r in sorted(picked, key=lambda r: r.day)]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"cutoff": f"{cutoff:%Y-%m-%d}", "switch": f"{SWITCH:%Y-%m-%d}",
                               "window_days": days, "eras": eras, "strip": strip, "seesaw": seesaw,
                               "conveyor": conveyor},
                              indent=1), encoding="utf-8")
    before = sum(1 for s in strip if s["date"] < f"{SWITCH:%Y-%m-%d}" and s["type"] == "Service")
    after = sum(1 for s in strip if s["date"] >= f"{SWITCH:%Y-%m-%d}" and s["type"] == "Service")
    print(f"cutoff {cutoff:%Y-%m-%d}; eras {eras}; strip {len(strip)} days, services {before} before / {after} after;"
          f" seesaw {seesaw}; conveyor {len(conveyor)} items {pd.Series(conveyor).value_counts().to_dict()} -> {OUT}")


if __name__ == "__main__":
    main()
