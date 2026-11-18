"""Do European drug users also get hit? Stimulant-positive share of pedestrians killed,
US (FARS) vs Spain (INTCF forensic toxicology). A descriptive comparison, NOT a
pre-registered test: the Spanish figures were seen before this script was written.

    python scripts/compare_ped_tox_spain.py
      reads  data/final/test_ped_drugs.csv        (US, from scripts/test_ped_drugs.py, "primary" definition)
             data/final/eu_pedestrian_rates.csv   (Spain pedestrian deaths, Eurostat)
      writes data/final/compare_ped_tox_spain.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "data" / "final"

# Spain, INTCF annual reports (data/raw/intcf_spain/SOURCE.md): pedestrians tested, and those
# positive for cocaine and for "amphetamine and related". One person can test positive for both,
# so the stimulant-positive count lies between max(cocaine, amph) and cocaine + amph.
ES = {2023: dict(tested=200, cocaine=19, amph=4), 2025: dict(tested=171, cocaine=13, amph=3)}
US_POP_2023 = 334_914_895  # CDC WONDER 2023 population (data/raw/cdc_wonder/)

# P21 early period (docs/hypothesis-test.md, Round 8). INTCF "Memoria Tráfico" 2010-2013, pedestrian
# section "casos con resultados positivos a drogas de abuso": these list each person's combination, so
# counts here are people. "Otros" = anti-inflammatories, analgesics, antihistamines (not stimulants).
ES_EARLY = {
    2010: dict(tested=211, cocaine=7, amph=1),   # 82 positive + 129 negative; PDF p. 48
    2011: dict(tested=192, cocaine=7, amph=1),   # 81 + 111
    2012: dict(tested=164, cocaine=10, amph=0),  # 84 + 80
    2013: dict(tested=161, cocaine=3, amph=0),   # 71 + 90
}

us = pd.read_csv(FINAL / "test_ped_drugs.csv")
us["year"] = pd.to_numeric(us.year, errors="coerce")  # the file also has pooled-period rows
us = us[(us.definition == "primary") & us.year.notna()].astype({"year": int}).set_index("year")
eu = pd.read_csv(FINAL / "eu_pedestrian_rates.csv")
es_eu = eu[eu.geo == "ES"].set_index("year")

rows = []
for y, d in ES.items():
    rows.append(dict(place="Spain", year=y, tested=d["tested"],
                     stim_share_low=max(d["cocaine"], d["amph"]) / d["tested"],
                     stim_share_high=(d["cocaine"] + d["amph"]) / d["tested"],
                     killed=es_eu.deaths.get(y), population=es_eu.population.get(y)))
for y in (2009, 2015, 2023, 2024):
    r = us.loc[y]
    rows.append(dict(place="United States", year=y, tested=int(r.tested), stim_share_low=r.share_stimulant,
                     stim_share_high=r.share_stimulant, killed=int(r.killed),
                     population=US_POP_2023 if y == 2023 else None))
out = pd.DataFrame(rows)
out.to_csv(FINAL / "compare_ped_tox_spain.csv", index=False)
pd.options.display.float_format = "{:.3f}".format
print(out.to_string(index=False))

# Rough per-person split, 2023. ASSUMES untested pedestrians look like tested ones, on both
# sides. For reasoning only, not for publication (playbook: never quote rough estimates).
us23 = out[(out.place == "United States") & (out.year == 2023)].iloc[0]
es23 = out[(out.place == "Spain") & (out.year == 2023)].iloc[0]
us_pm = us23.killed / us23.population * 1e6
es_pm = es23.killed / es23.population * 1e6
us_stim = us_pm * us23.stim_share_low
es_stim_lo, es_stim_hi = es_pm * es23.stim_share_low, es_pm * es23.stim_share_high
print(f"\n2023 pedestrian deaths per million: US {us_pm:.1f}, Spain {es_pm:.1f} ({us_pm / es_pm:.1f}x)")
print(f"  stimulant-positive (rough): US {us_stim:.1f}, Spain {es_stim_lo:.2f}-{es_stim_hi:.2f}")
print(f"  not stimulant-positive (rough): US {us_pm - us_stim:.1f}, Spain {es_pm - es_stim_hi:.1f}-{es_pm - es_stim_lo:.1f}"
      f" ({(us_pm - us_stim) / (es_pm - es_stim_lo):.1f}x-{(us_pm - us_stim) / (es_pm - es_stim_hi):.1f}x)")
gap = us_pm - es_pm
print(f"  stimulant-positive deaths as a share of the per-person gap: "
      f"{(us_stim - es_stim_hi) / gap:.0%}-{(us_stim - es_stim_lo) / gap:.0%}")


# ------------------------------------------------------------------ P21, scored as written
def pooled_es(d):
    return sum(v["cocaine"] + v["amph"] for v in d.values()) / sum(v["tested"] for v in d.values())


def pooled_us(years):
    r = us.loc[list(years)]
    return r.stimulant.sum() / r.tested.sum()


es_early, es_late = pooled_es(ES_EARLY), pooled_es(ES)
us_early, us_late = pooled_us(ES_EARLY), pooled_us((2023, 2024))
p21a = abs(es_early - us_early) <= 0.05
p21b = (es_late - es_early) < 0.5 * (us_late - us_early)
print("\nP21 (pre-registered 2026-11-11)")
for y, v in ES_EARLY.items():
    print(f"  Spain {y}: {v['cocaine'] + v['amph']} of {v['tested']} ({(v['cocaine'] + v['amph']) / v['tested']:.1%});"
          f"  US {y}: {us.loc[y].share_stimulant:.1%}")
print(f"  early 2010-13: Spain {es_early:.1%}, US {us_early:.1%}, difference {100 * (us_early - es_early):.1f} points")
print(f"  late: Spain 2023+2025 {es_late:.1%}, US 2023-24 {us_late:.1%}")
print(f"  change: Spain {100 * (es_late - es_early):+.1f} points (x{es_late / es_early:.1f}),"
      f" US {100 * (us_late - us_early):+.1f} points (x{us_late / us_early:.1f})")
print(f"  P21a within 5 points: {'PASS' if p21a else 'FAIL'};  P21b Spain change < half of US: {'PASS' if p21b else 'FAIL'}")
print(f"  P21 overall: {'PASS' if p21a and p21b else 'FAIL'}")
pd.DataFrame([dict(place="Spain", year=y, tested=v["tested"], stim_share_low=(v["cocaine"] + v["amph"]) / v["tested"],
                   stim_share_high=(v["cocaine"] + v["amph"]) / v["tested"]) for y, v in ES_EARLY.items()]
             ).pipe(lambda e: pd.concat([e, out])).to_csv(FINAL / "compare_ped_tox_spain.csv", index=False)
