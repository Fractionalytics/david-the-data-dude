"""Pre-registered tests P11 (unlicensed drivers) and P12 (old vehicles),
docs/hypothesis-test.md round 4.

    python scripts/test_drivers.py
      reads  data/raw/fars/FARS<YEAR>NationalCSV.zip (2009-11, 2020-22)
      writes data/final/test_drivers.csv   one row per group x period x measure

Pedestrian group: the vehicle that struck each pedestrian killed (PER_TYP 5,
INJ_SEV 4), via N_MOT_NO (to 2010) / STR_VEH (2011 on); one row per death.
Control group: every vehicle in a fatal crash with no PER_TYP 5 record.
L_STATUS: invalid 0-4, valid 6, unknown 7/9. Age = year - MOD_YEAR
(9998/9999 dropped, negatives set to 0); old = 15+.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fars_pedestrians import FINAL, load  # noqa: E402

PERIODS = {"2009_11": [2009, 2010, 2011], "2020_22": [2020, 2021, 2022]}


def year_rows(y: int) -> pd.DataFrame:
    p = load(y, "person", ["ST_CASE", "PER_TYP", "INJ_SEV", "N_MOT_NO", "STR_VEH"])
    v = load(y, "vehicle", ["ST_CASE", "VEH_NO", "L_STATUS", "MOD_YEAR", "HIT_RUN"])
    peds = p[(p.PER_TYP == 5) & (p.INJ_SEV == 4)].copy()
    sv = peds.STR_VEH if "STR_VEH" in peds and peds.STR_VEH.notna().any() else peds.N_MOT_NO
    peds["VEH_NO"] = sv
    ped = peds[["ST_CASE", "VEH_NO"]].merge(v, on=["ST_CASE", "VEH_NO"], how="left", validate="m:1")
    unmatched = ped.L_STATUS.isna().sum()
    ped["group"] = "pedestrian"
    ped_cases = set(p.loc[p.PER_TYP == 5, "ST_CASE"])
    ctl = v[~v.ST_CASE.isin(ped_cases)].copy()
    ctl["group"] = "control"
    out = pd.concat([ped, ctl], ignore_index=True)
    out["year"] = y
    print(y, "ped deaths", len(ped), "unmatched", unmatched, "control vehicles", len(ctl), flush=True)
    return out


def main() -> None:
    rows = []
    for period, years in PERIODS.items():
        d = pd.concat([year_rows(y) for y in years], ignore_index=True)
        for g, x in d.groupby("group"):
            ls = x.L_STATUS
            known = ls.isin([0, 1, 2, 3, 4, 6])
            invalid = ls.isin([0, 1, 2, 3, 4])
            age = (x.year - x.MOD_YEAR).where(x.MOD_YEAR < 9998).clip(lower=0)
            rows.append(dict(group=g, period=period, n=len(x),
                             license_known=int(known.sum()), license_invalid=int(invalid.sum()),
                             invalid_share_of_known=invalid.sum() / known.sum(),
                             license_unknown_share=1 - known.mean(),
                             hit_run_share=(x.HIT_RUN == 1).mean(),
                             age_known=int(age.notna().sum()), age_15plus=int((age >= 15).sum()),
                             old_share_of_known=(age >= 15).sum() / age.notna().sum(),
                             mean_age=age.mean()))
    t = pd.DataFrame(rows)
    t.to_csv(FINAL / "test_drivers.csv", index=False)
    pd.set_option("display.width", 200)
    print(t.round(4).to_string(index=False))

    s = t.set_index(["group", "period"])
    def chg(col, g):
        return 100 * (s.loc[(g, "2020_22"), col] - s.loc[(g, "2009_11"), col])
    p11p, p11c = chg("invalid_share_of_known", "pedestrian"), chg("invalid_share_of_known", "control")
    p12p, p12c = chg("old_share_of_known", "pedestrian"), chg("old_share_of_known", "control")
    print(f"\nP11: ped {p11p:+.2f} pts, control {p11c:+.2f} pts, gap {p11p - p11c:+.2f} -> "
          f"{'PASS' if p11p >= 2 and p11p - p11c >= 1 else 'FAIL'}")
    print(f"P12: ped {p12p:+.2f} pts, control {p12c:+.2f} pts, gap {p12p - p12c:+.2f} -> "
          f"{'PASS' if p12p - p12c >= 2 else 'FAIL'}")


if __name__ == "__main__":
    main()
