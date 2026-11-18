"""Reel 3 skeleton (2026-11-15): split pedestrian deaths per million people into a stimulant bucket and a
no-stimulant bucket, early vs. late, for the US, Spain and Czechia.

    python scripts/three_buckets.py
      reads  data/final/test_ped_drugs.csv (FARS, "primary" stimulant definition)
             data/final/eu_pedestrian_rates.csv (US population)
             data/raw/eurostat/tran_sf_roadus.csv, demo_gind.csv (ES, CZ pedestrian deaths and population)
      writes data/final/three_buckets.csv

Stimulant bucket = all pedestrians killed x stimulant-positive share of those tested. That assumes untested
pedestrians look like tested ones, in every country, so the buckets are for the logic, not exact counts.
Shares outside FARS are hand-entered from the papers (docs/research-drugs/pedestrian-link.md section 2,
czechia-slovakia-pedestrians.md).
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "data" / "final"
RAW = ROOT / "data" / "raw" / "eurostat"

# (country, period label, death years, stimulant share, tested positives per year, tested per year, share source)
# Positives per year give a measured floor (tested and positive only, no assumption about the untested).
CZ_LATE_LOW, CZ_LATE_HIGH = 13 / 418, 13 / 283  # 12 meth + 1 cocaine; denominator not published
ROWS = [
    ("Spain", "early", range(2010, 2014), 29 / 728, 29 / 4, 728 / 4, "INTCF 2010-13 pooled, 29 of 728 tested"),
    ("Spain", "late", range(2023, 2025), 39 / 371, 39 / 2, 371 / 2, "INTCF 2023 + 2025, 39 of 371 tested (deaths 2023-24)"),
    ("Czechia", "early", range(2003, 2006), 0.017, 0.017 * 303 / 3, 303 / 3,
     "Mravcik 2007, meth or MDMA in 1.7% of 303 tested"),
    ("Czechia", "late", range(2016, 2022), (CZ_LATE_LOW + CZ_LATE_HIGH) / 2, 13 / 6, (283 + 418) / 2 / 6,
     "Masilkova & Vorel 2023, 13 of 283-418 tested (midpoint; range 3.1-4.6%)"),
]
US_EARLY, US_LATE = range(2010, 2013), range(2022, 2025)


def eurostat() -> tuple[pd.Series, pd.Series]:
    d = pd.read_csv(RAW / "tran_sf_roadus.csv")
    d = d[(d.sex == "T") & (d.age == "TOTAL") & (d.unit == "NR") & (d.pers_cat == "PED")]
    deaths = d.set_index(["geo", "TIME_PERIOD"]).OBS_VALUE
    p = pd.read_csv(RAW / "demo_gind.csv")
    pop = p[p.indic_de == "AVG"].set_index(["geo", "TIME_PERIOD"]).OBS_VALUE
    return deaths, pop


def main() -> None:
    deaths, pop = eurostat()
    out = []
    for country, period, years, share, pos, tested, src in ROWS:
        geo = {"Spain": "ES", "Czechia": "CZ"}[country]
        k = sum(float(deaths[(geo, y)]) for y in years) / len(years)
        n = sum(float(pop[(geo, y)]) for y in years) / len(years)
        out.append((country, period, f"{years[0]}-{years[-1]}", k, n, share, pos, tested, src))

    f = pd.read_csv(FINAL / "test_ped_drugs.csv")
    f = f[(f.definition == "primary") & f.year.str.isdigit()].astype({"year": int}).set_index("year")
    usp = pd.read_csv(FINAL / "eu_pedestrian_rates.csv")
    usp = usp[usp.geo == "US"].set_index("year").population
    for period, years in (("early", US_EARLY), ("late", US_LATE),  # plus Czechia's years, for a same-years check
                          ("cz_early_years", range(2003, 2006)), ("cz_late_years", range(2016, 2022))):
        g = f.loc[list(years)]
        share = g.stimulant.sum() / g.tested.sum()
        out.append(("US", period, f"{years[0]}-{years[-1]}", g.killed.mean(), usp.loc[list(years)].mean(), share,
                    g.stimulant.mean(), g.tested.mean(), f"FARS, {int(g.stimulant.sum())} of {int(g.tested.sum())} tested"))

    t = pd.DataFrame(out, columns=["country", "period", "years", "ped_deaths_per_year", "population",
                                   "stim_share_tested", "tested_pos_per_year", "tested_per_year", "share_source"])
    t["total_per_million"] = t.ped_deaths_per_year / t.population * 1e6
    t["stim_floor_per_million"] = t.tested_pos_per_year / t.population * 1e6
    # Floor split: tested positive, tested negative, untested. Czechia 2016-21's tested count is a midpoint
    # (283-418 pedestrians; the paper doesn't publish it).
    t["tested_neg_per_million"] = (t.tested_per_year - t.tested_pos_per_year) / t.population * 1e6
    t["untested_per_million"] = (t.ped_deaths_per_year - t.tested_per_year) / t.population * 1e6
    t["stim_bucket_per_million"] = t.total_per_million * t.stim_share_tested
    t["no_stim_bucket_per_million"] = t.total_per_million - t.stim_bucket_per_million
    t.to_csv(FINAL / "three_buckets.csv", index=False)

    with open(FINAL.parent.parent / "data" / "final" / "three_buckets.txt", "w", encoding="utf-8") as fh:
        for c in ("US", "Spain", "Czechia"):
            e, l = (t[(t.country == c) & (t.period == p)].iloc[0] for p in ("early", "late"))
            line = (f"{c}: total {e.total_per_million:.1f} -> {l.total_per_million:.1f} | stim bucket "
                    f"{e.stim_bucket_per_million:.2f} -> {l.stim_bucket_per_million:.2f} "
                    f"[floor {e.stim_floor_per_million:.2f} -> {l.stim_floor_per_million:.2f}] "
                    f"({l.stim_bucket_per_million - e.stim_bucket_per_million:+.2f}) | no-stim bucket "
                    f"{e.no_stim_bucket_per_million:.1f} -> {l.no_stim_bucket_per_million:.1f} "
                    f"({l.no_stim_bucket_per_million - e.no_stim_bucket_per_million:+.1f}) | shares "
                    f"{e.stim_share_tested:.1%} -> {l.stim_share_tested:.1%} | {e.years} vs {l.years}")
            fh.write(line + "\n")
        cz = t[(t.country == "Czechia") & (t.period == "late")].iloc[0]
        lo, hi = cz.total_per_million * CZ_LATE_LOW, cz.total_per_million * CZ_LATE_HIGH
        fh.write(f"Czechia late stim bucket range: {lo:.2f}-{hi:.2f}\n")
        for p, cp in (("cz_early_years", "early"), ("cz_late_years", "late")):
            u = t[(t.country == "US") & (t.period == p)].iloc[0]
            c = t[(t.country == "Czechia") & (t.period == cp)].iloc[0]
            fh.write(f"Same years {u.years}: US stim bucket {u.stim_bucket_per_million:.2f} vs Czechia "
                     f"{c.stim_bucket_per_million:.2f} = {u.stim_bucket_per_million / c.stim_bucket_per_million:.1f}x; "
                     f"floor {u.stim_floor_per_million:.2f} vs {c.stim_floor_per_million:.2f} = "
                     f"{u.stim_floor_per_million / c.stim_floor_per_million:.1f}x\n")
        e, l = (t[(t.country == "US") & (t.period == p)].iloc[0] for p in ("early", "late"))
        rise = l.ped_deaths_per_year - e.ped_deaths_per_year
        pos_rise = l.tested_pos_per_year - e.tested_pos_per_year
        fh.write(f"US rise {e.years} -> {l.years}: all deaths +{rise:.0f}/yr; tested stim+ +{pos_rise:.0f}/yr "
                 f"({pos_rise / rise:.0%} of the rise, a floor)\n")


if __name__ == "__main__":
    main()
