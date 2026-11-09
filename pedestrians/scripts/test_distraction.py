"""Pre-registered test P5 (docs/hypothesis-test.md): is the striking driver in
pedestrian deaths more often recorded as distracted by a phone in 2020-22
than in 2010-12?

    python scripts/test_distraction.py
      reads  data/raw/fars/FARS<YEAR>NationalCSV.zip, 2010-2024 (PERSON, VEHICLE via
             fars_pedestrians.year_peds; DISTRACT)
      writes data/final/test_distraction.csv   one row per year, then one per period
                                                (2010-12, 2020-22): counts by class,
                                                phone share of known, unknown share

Steps
  1. Pedestrian deaths (PER_TYP 5, INJ_SEV 4) and their striking vehicle
     (N_MOT_NO through 2010, STR_VEH from 2011) from fars_pedestrians.year_peds.
  2. DISTRACT has one row per distraction reported for each vehicle's driver
     (a vehicle can have several). Field MDRDSTRD through 2019, DRDISTRACT from
     2020; same codes. Labels checked against the *NAME columns (2015 on).
  3. Classify the striking vehicle's driver, highest precedence first:
       phone          5 talking/listening to cellular (mobile) phone,
                      6 manipulating cellular phone (2010-11 manual: "dialing"),
                      15 other cellular (mobile) phone related
       distracted_other  1 looked but did not see (dropped after 2017),
                      3 other occupant, 4 moving object in vehicle, 7 audio /
                      climate controls, 9 other vehicle controls, 10 device or
                      object brought into vehicle, 12 outside person/object/event,
                      13 eating/drinking, 14 smoking, 17 distraction/inattention,
                      18 distraction/careless, 19 careless/inattentive,
                      92 distracted, details unknown, 93 inattentive, details
                      unknown, 97 lost in thought, 98 other distraction
       not_distracted 0
       unknown        16 no driver present / unknown if driver present,
                      96 not reported, 99 unknown if distracted, or no DISTRACT
                      row for the vehicle
  4. Period figures pool the three years (sum of counts / sum of counts), which
     equals the share of the average-per-year counts used in the common setup.
     "Known" = phone + distracted_other + not_distracted.

Pass rule (pre-registered): phone share of known striking drivers is higher
in 2020-22 than in 2010-12.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fars_pedestrians import FINAL, load, year_peds  # noqa: E402

YEARS = range(2010, 2025)
PHONE = {5, 6, 15}
OTHER = {1, 3, 4, 7, 9, 10, 12, 13, 14, 17, 18, 19, 92, 93, 97, 98}
CLASSES = ["phone", "distracted_other", "not_distracted", "unknown"]
PERIODS = {"2010-12": [2010, 2011, 2012], "2020-22": [2020, 2021, 2022]}


def driver_class(codes: set) -> str:
    if codes & PHONE:
        return "phone"
    if codes & OTHER:
        return "distracted_other"
    if 0 in codes:
        return "not_distracted"
    return "unknown"


def year_counts(year: int) -> dict:
    peds, _ = year_peds(year)
    ds = load(year, "distract", ["ST_CASE", "VEH_NO", "MDRDSTRD", "DRDISTRACT"])
    col = "DRDISTRACT" if "DRDISTRACT" in ds else "MDRDSTRD"
    unexpected = set(ds[col].unique()) - PHONE - OTHER - {0, 16, 96, 99}
    if unexpected:
        raise SystemExit(f"{year}: unmapped distraction codes {sorted(unexpected)}")
    codes = ds.groupby(["ST_CASE", "VEH_NO"])[col].agg(set).rename("codes").reset_index()
    peds = peds.merge(codes.rename(columns={"VEH_NO": "str_veh"}), on=["ST_CASE", "str_veh"], how="left", validate="m:1")
    peds["dclass"] = peds.codes.map(lambda c: driver_class(c) if isinstance(c, set) else "unknown")
    n = peds.dclass.value_counts().reindex(CLASSES, fill_value=0)
    raw = peds.codes.map(lambda c: c if isinstance(c, set) else set())
    out = {"period": str(year), "years": str(year), "ped_deaths": len(peds), **n.to_dict(),
           "no_distract_row": int(peds.codes.isna().sum()),
           "unknown_not_reported_96": int(raw.map(lambda c: 96 in c and not (c - {16, 96, 99})).sum()),
           "unknown_99": int(raw.map(lambda c: 99 in c and not (c - {16, 96, 99})).sum()),
           "unknown_16": int(raw.map(lambda c: 16 in c and not (c - {16, 96, 99})).sum()),
           "field": col}
    print(year, out, flush=True)
    return out


def add_shares(t: pd.DataFrame) -> pd.DataFrame:
    t["known"] = t.phone + t.distracted_other + t.not_distracted
    t["phone_share_of_known"] = (t.phone / t.known).round(4)
    t["any_distraction_share_of_known"] = ((t.phone + t.distracted_other) / t.known).round(4)
    t["unknown_share"] = (t.unknown / t.ped_deaths).round(4)
    t["phone_share_of_all"] = (t.phone / t.ped_deaths).round(4)
    return t


def main() -> None:
    yearly = pd.DataFrame([year_counts(y) for y in YEARS])
    num = ["ped_deaths", *CLASSES, "no_distract_row", "unknown_not_reported_96", "unknown_99", "unknown_16"]
    rows = []
    for name, ys in PERIODS.items():
        s = yearly[yearly.period.astype(int).isin(ys)][num].sum()
        rows.append({"period": name, "years": "+".join(map(str, ys)), **s.to_dict(), "field": "pooled"})
    t = add_shares(pd.concat([yearly, pd.DataFrame(rows)], ignore_index=True))
    t.to_csv(FINAL / "test_distraction.csv", index=False)
    print(t.to_string(index=False))
    a, b = t.set_index("period").loc["2010-12"], t.set_index("period").loc["2020-22"]
    print(f"\nP5 phone share of known: 2010-12 {a.phone_share_of_known:.2%} -> 2020-22 {b.phone_share_of_known:.2%}"
          f"  => {'PASS' if b.phone_share_of_known > a.phone_share_of_known else 'FAIL'}")
    print(f"unknown share: {a.unknown_share:.2%} -> {b.unknown_share:.2%}")


if __name__ == "__main__":
    main()
