"""Write the data files the Remotion charts read (projects/radiology/video/src/data/).

card9.json: radiologists' pay as a multiple of the average doctor's, at the start and end of
each pay survey (from data/processed/pay_by_specialty.csv):
- Doximity: 2017 report (pooled 2014-17 surveys) vs 2026 report (2025 pay). "Average doctor" is
  our own unweighted mean of the 48 specialties in both reports (Doximity publishes no
  all-physician dollar average).
- Medscape: 2018 report (2017 pay) vs 2026 report (2025 pay), against Medscape's all-physician
  average. Both endpoints come from trade-press reprints (Medscape is paywalled).

Run from the repo worktree root:
    python -I -X utf8 projects/radiology/scripts/build_video_data.py
"""
import csv
import json
from pathlib import Path

ROOT = Path("projects/radiology")
OUT = ROOT / "video/src/data"
SURVEYS = [  # source, report years (start, end), pay years shown on the chart
    ("doximity", ("2017", "2026"), ("2017", "2025")),
    ("medscape", ("2018", "2026"), ("2017", "2025")),
]


def cards():
    """Numbers for cards 4, 5 and 11 (cards.json), all read from data/processed/."""
    idx = {r["group"]: r for r in csv.DictReader(open(ROOT / "data/processed/cms_physician_index.csv", encoding="utf-8"))}
    pay = {(r["source"].lower(), r["report_year"], r["series"]): float(r["value"])
           for r in csv.DictReader(open(ROOT / "data/processed/pay_by_specialty.csv", encoding="utf-8"))
           if r["series"] in ("radiology", "all_physicians") and r["unit"].startswith("usd") and r["value"]}
    fda = list(csv.DictReader(open(ROOT / "data/processed/fda_ai_devices_by_year.csv", encoding="utf-8")))[-1]
    pct = lambda a, b: round(100 * (b - a) / a, 1)
    return {
        # Card 4 and 11: clinicians billing traditional Medicare, physicians only, 2016-2024.
        "medicare": {"radiologists": float(idx["radiology (DR+IR)"]["pct_2016_2024"]),
                     "physicians": float(idx["physicians"]["pct_2016_2024"])},
        # Card 4: Doximity 2017 vs 2026 reports; "average doctor" = mean of 48 specialties.
        "pay": {"radiologists": pct(pay[("doximity", "2017", "radiology")], pay[("doximity", "2026", "radiology")]),
                "physicians": pct(pay[("doximity", "2017", "all_physicians")], pay[("doximity", "2026", "all_physicians")])},
        # Card 5: FDA AI-enabled device list through 2026-06-29, radiology review panel.
        "fda": {"all": int(fda["cumulative_all"]), "radiology": int(fda["cumulative_radiology"])},
        # Card 5: mean Medicare services per clinician, 2016-2024 (David's choice of the mean).
        "services": {"radiologists": float(idx["services per diagnostic radiologist"]["pct_2016_2024"]),
                     "physicians": float(idx["services per physician"]["pct_2016_2024"])},
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "cards.json").write_text(json.dumps(cards(), indent=1), encoding="utf-8")
    print(json.dumps(cards()))
    pay = {(r["source"].lower(), r["report_year"], r["series"]): float(r["value"])
           for r in csv.DictReader(open(ROOT / "data/processed/pay_by_specialty.csv", encoding="utf-8"))
           if r["series"] in ("radiology", "all_physicians") and r["unit"].startswith("usd") and r["value"]}
    surveys = []
    for src, (r0, r1), years in SURVEYS:
        pts = []
        for rep in (r0, r1):
            rad, avg = pay[(src, rep, "radiology")], pay[(src, rep, "all_physicians")]
            pts.append({"report": rep, "radiology": rad, "average": avg, "multiple": round(rad / avg, 2)})
        surveys.append({"source": src.capitalize(), "years": list(years), "points": pts})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "card9.json").write_text(json.dumps({"surveys": surveys}, indent=1), encoding="utf-8")
    print(json.dumps(surveys))


if __name__ == "__main__":
    main()
