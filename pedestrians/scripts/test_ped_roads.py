"""Pre-registered test P23 (docs/hypothesis-test.md, 2026-11-14): are stimulant-positive pedestrians killed on
faster roads than tested stimulant-negative pedestrians, and was the stimulant-positive rise on fast roads?

    python scripts/test_ped_roads.py
      reads  data/raw/fars/FARS<YEAR>NationalCSV.zip, 2010-2024
      writes data/final/test_ped_roads.csv   one row per year x drug group x road-speed group

Fast road = striking vehicle's posted speed limit (VEHICLE.VSPD_LIM) 40 mph or more; 98/99 = unknown.
Stimulant = P9 "primary" definition (test_ped_drugs.classify). Striking vehicle as in fars_pedestrians.year_peds.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fars_pedestrians import FINAL, load, year_peds  # noqa: E402
from test_ped_drugs import INVALID, KEY, classify, results  # noqa: E402

YEARS = range(2010, 2025)
EARLY, LATE = [2010, 2011, 2012], [2022, 2023, 2024]


def year_table(y: int) -> pd.DataFrame:
    peds, _ = year_peds(y)
    v = load(y, "vehicle", ["ST_CASE", "VEH_NO", "VSPD_LIM"]).rename(columns={"VEH_NO": "str_veh"})
    peds = peds.merge(v, on=["ST_CASE", "str_veh"], how="left", validate="m:1")
    lim = peds.VSPD_LIM
    peds["speed"] = "unknown"
    peds.loc[lim.between(0, 39), "speed"] = "under40"   # 0 = no statutory limit; rare for pedestrians
    peds.loc[lim.between(40, 97), "speed"] = "fast40"
    acc = load(y, "accident", ["ST_CASE", "RUR_URB", "ROAD_FNC"])
    peds = peds.merge(acc[["ST_CASE"] + [c for c in ("RUR_URB", "ROAD_FNC") if c in acc and c not in peds]],
                      on="ST_CASE", how="left")
    if "RUR_URB" in peds and peds.RUR_URB.notna().any():
        peds["urban"] = peds.RUR_URB == 2
    else:
        peds["urban"] = peds.ROAD_FNC.between(11, 19)

    _, r, _ = results(y)
    r = r.assign(code=r.code.astype(int))
    valid = r[~r.code.isin(INVALID)].copy()
    valid["stim"] = [classify(c, y >= 2022, "primary")[1] for c in valid.code]
    per = valid.groupby(KEY).stim.any().rename("stim_pos").reset_index()
    peds = peds.merge(per, on=KEY, how="left")
    peds["drug"] = peds.stim_pos.map({True: "stim_pos", False: "stim_neg"}).fillna("untested")

    if y >= 2015:  # ALC_RES in thousandths from 2015; only used for 2022-24 (unscored)
        p = load(y, "person", KEY + ["ALC_RES"])
        peds = peds.merge(p, on=KEY, how="left")
        a = peds.ALC_RES
        peds["alc"] = "untested"
        peds.loc[a == 0, "alc"] = "bac0"
        peds.loc[a.between(80, 939), "alc"] = "bac08"
        peds.loc[a.between(1, 79), "alc"] = "bac_low"
    else:
        peds["alc"] = "na"
    peds["year"] = y
    return peds[["year", "drug", "alc", "speed", "road", "dark", "urban"]]


def fast_share(d: pd.DataFrame, mask) -> tuple[float, int, int]:
    k = d[mask & (d.speed != "unknown")]
    return (k.speed == "fast40").mean(), int((k.speed == "fast40").sum()), len(k)


def main() -> None:
    d = pd.concat([year_table(y) for y in YEARS], ignore_index=True)
    out = d.groupby(["year", "drug", "speed"]).size().rename("n").reset_index()
    out.to_csv(FINAL / "test_ped_roads.csv", index=False)

    late, early = d[d.year.isin(LATE)], d[d.year.isin(EARLY)]
    print("unknown speed share, all peds:", f"{(d.speed == 'unknown').mean():.1%}")

    # P23a
    sp, spn, spd = fast_share(late, late.drug == "stim_pos")
    sn, snn, snd = fast_share(late, late.drug == "stim_neg")
    diff = (sp - sn) * 100
    print(f"\nP23a 2022-24: fast-road share stim+ {sp:.1%} ({spn}/{spd}) vs stim- {sn:.1%} ({snn}/{snd}); "
          f"diff {diff:+.1f} pts => {'PASS' if diff >= 5 else 'FAIL'}")

    # P23b
    def cnt(df, spd):
        return int(((df.drug == "stim_pos") & (df.speed == spd)).sum())
    inc_fast = cnt(late, "fast40") - cnt(early, "fast40")
    inc_slow = cnt(late, "under40") - cnt(early, "under40")
    inc_unk = cnt(late, "unknown") - cnt(early, "unknown")
    share = inc_fast / (inc_fast + inc_slow)
    print(f"P23b stim+ deaths 2010-12 -> 2022-24: fast {cnt(early,'fast40')} -> {cnt(late,'fast40')} (+{inc_fast}); "
          f"under40 {cnt(early,'under40')} -> {cnt(late,'under40')} (+{inc_slow}); unknown +{inc_unk}; "
          f"fast share of rise {share:.1%} => {'PASS' if share >= 0.70 else 'FAIL'}")

    # unscored
    print("\n-- unscored --")
    a1, a1n, a1d = fast_share(late, late.alc == "bac08")
    a0, a0n, a0d = fast_share(late, late.alc == "bac0")
    print(f"1. alcohol 2022-24: fast share BAC.08+ {a1:.1%} ({a1n}/{a1d}) vs BAC 0 {a0:.1%} ({a0n}/{a0d}); "
          f"diff {(a1 - a0) * 100:+.1f}")
    for lab, df in (("2. arterial share", None),):
        for g in ("stim_pos", "stim_neg"):
            k = late[late.drug == g]
            print(f"{lab} 2022-24 {g}: {(k.road == 'arterial').mean():.1%} of {len(k)}")
    for lab, m in (("3a. dark only", late.dark), ("3b. urban only", late.urban)):
        p_, _, pdn = fast_share(late, m & (late.drug == "stim_pos"))
        n_, _, ndn = fast_share(late, m & (late.drug == "stim_neg"))
        print(f"{lab}: stim+ {p_:.1%} (n={pdn}) vs stim- {n_:.1%} (n={ndn}); diff {(p_ - n_) * 100:+.1f}")
    for spd in ("fast40", "under40", "unknown"):
        k = late[late.speed == spd]
        print(f"4. testing rate 2022-24, {spd}: {(k.drug != 'untested').mean():.1%} of {len(k)}")
    print("5. fast-road share by year (stim+ / stim-) and stim+ count:")
    for y in YEARS:
        k = d[d.year == y]
        p_, pn, _ = fast_share(k, k.drug == "stim_pos")
        n_, _, _ = fast_share(k, k.drug == "stim_neg")
        print(f"   {y}: {p_:.1%} / {n_:.1%}   stim+ fast {pn}")


if __name__ == "__main__":
    main()
