"""Pre-registered tests P18-P20 (docs/hypothesis-test.md, round 6): checks
raised by the Reel's comments.

    python scripts/test_comments.py
      reads  data/raw/fars/FARS<YEAR>NationalCSV.zip (2009-11, 2020-24)
      writes data/final/test_comments.csv   one row per group x year x measure

P18  stimulant share among tested pedestrians killed, 2022 vs 2024 (2023 shown).
P19  meth-positive and amphetamine-without-meth shares, 2009-11 vs 2020-22.
P20  stimulant share among tested drivers of the vehicle that struck each
     pedestrian killed (one row per death), vs drivers in fatal crashes with no
     pedestrian, 2009-11 vs 2020-22.
Drug definitions, result codes and the tested rule are P9's (test_ped_drugs.py,
"primary", all result rows).
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fars_pedestrians import FINAL, load  # noqa: E402
from test_ped_drugs import INVALID, KEY, classify  # noqa: E402

METH = {417, 3053}
AMPH = {400, 401, 408, 3019}
YEARS = [2009, 2010, 2011, 2020, 2021, 2022, 2023, 2024]


def results(year: int, persons: pd.DataFrame) -> pd.DataFrame:
    """Result rows (KEY, code) for the given persons."""
    if year <= 2017:
        cols = [f"DRUGRES{i}" for i in (1, 2, 3)]
        p = load(year, "person", KEY + cols).merge(persons[KEY].drop_duplicates(), on=KEY)
        return p.melt(id_vars=KEY, value_vars=cols, value_name="code").dropna(subset=["code"])[KEY + ["code"]]
    d = load(year, "drugs", KEY + ["DRUGRES"]).rename(columns={"DRUGRES": "code"})
    return d.merge(persons[KEY].drop_duplicates(), on=KEY)


def flags(year: int, r: pd.DataFrame) -> pd.DataFrame:
    """Per tested person: stimulant, meth, amphetamine without meth."""
    r = r.assign(code=r.code.astype(int))
    v = r[~r.code.isin(INVALID)].copy()
    v["stim"] = [classify(c, year >= 2022, "primary")[1] for c in v.code]
    v["meth"] = v.code.isin(METH)
    v["amph"] = v.code.isin(AMPH)
    g = v.groupby(KEY)[["stim", "meth", "amph"]].any()
    g["amph_no_meth"] = g.amph & ~g.meth
    return g.reset_index()


def summary(group: str, year: int, people: pd.DataFrame, f: pd.DataFrame) -> dict:
    m = people.merge(f, on=KEY, how="left")
    tested = m.stim.notna()
    t = m[tested]
    return dict(group=group, year=year, n=len(m), tested=int(tested.sum()),
                stim=int(t.stim.sum()), meth=int(t.meth.sum()), amph_no_meth=int(t.amph_no_meth.sum()))


def year_rows(y: int) -> list[dict]:
    p = load(y, "person", KEY + ["PER_TYP", "INJ_SEV", "N_MOT_NO", "STR_VEH"])
    peds = p[(p.PER_TYP == 5) & (p.INJ_SEV == 4)].copy()
    drivers = p[p.PER_TYP == 1]
    sv = peds.STR_VEH if "STR_VEH" in peds and peds.STR_VEH.notna().any() else peds.N_MOT_NO
    strike = pd.DataFrame({"ST_CASE": peds.ST_CASE.values, "VEH_NO": sv.values})
    # one row per pedestrian death; deaths with no matching driver (e.g. hit-and-run
    # with no driver record) drop out and are counted
    sd = strike.merge(drivers[KEY], on=["ST_CASE", "VEH_NO"], how="left")
    no_driver = int(sd.PER_NO.isna().sum())
    sd = sd.dropna(subset=["PER_NO"]).astype({"PER_NO": int})
    ped_cases = set(p.loc[p.PER_TYP == 5, "ST_CASE"])
    ctl = drivers[~drivers.ST_CASE.isin(ped_cases)][KEY]
    allp = pd.concat([peds[KEY], sd[KEY], ctl], ignore_index=True)
    f = flags(y, results(y, allp))
    rows = [summary("pedestrian", y, peds[KEY], f), summary("striking_driver", y, sd[KEY], f),
            summary("control_driver", y, ctl, f)]
    rows[1]["no_driver_record"] = no_driver
    print(y, rows, flush=True)
    return rows


def main() -> None:
    t = pd.DataFrame([r for y in YEARS for r in year_rows(y)])
    for tag, ys in (("2009-11", [2009, 2010, 2011]), ("2020-22", [2020, 2021, 2022])):
        g = t[t.year.isin(ys)].groupby("group")[["n", "tested", "stim", "meth", "amph_no_meth", "no_driver_record"]].sum()
        t = pd.concat([t, g.reset_index().assign(year=tag)], ignore_index=True)
    t["year"] = t.year.astype(str)
    t["testing_rate"] = t.tested / t.n
    for c in ("stim", "meth", "amph_no_meth"):
        t[f"share_{c}"] = t[c] / t.tested
    t.round(4).to_csv(FINAL / "test_comments.csv", index=False)
    s = t.set_index(["group", "year"])

    pp = lambda g, y, c: s.loc[(g, y), f"share_{c}"] * 100
    print("\nP18 pedestrians, stimulant share:", {y: round(pp("pedestrian", y, "stim"), 1) for y in ("2022", "2023", "2024")})
    d18 = pp("pedestrian", "2024", "stim") - pp("pedestrian", "2022", "stim")
    print(f"P18 change 2022->2024 {d18:+.1f} pp => {'PASS' if d18 <= -1 else 'FAIL'}")

    ds = pp("pedestrian", "2020-22", "stim") - pp("pedestrian", "2009-11", "stim")
    dm = pp("pedestrian", "2020-22", "meth") - pp("pedestrian", "2009-11", "meth")
    da = pp("pedestrian", "2020-22", "amph_no_meth") - pp("pedestrian", "2009-11", "amph_no_meth")
    print(f"P19 stimulant {ds:+.1f} pp, meth {dm:+.1f} pp, amphetamine without meth {da:+.1f} pp; "
          f"meth/stim = {dm / ds:.0%} => {'PASS' if dm >= ds / 2 else 'FAIL'}")

    dd = pp("striking_driver", "2020-22", "stim") - pp("striking_driver", "2009-11", "stim")
    dc = pp("control_driver", "2020-22", "stim") - pp("control_driver", "2009-11", "stim")
    print(f"P20 striking drivers {dd:+.1f} pp vs control drivers {dc:+.1f} pp; gap {dd - dc:+.1f} => "
          f"{'SUPPORTED' if dd - dc >= 3 else 'NOT SUPPORTED'}")
    show = ["n", "tested", "testing_rate", "share_stim", "share_meth", "share_amph_no_meth"]
    print(s[show].round(3).to_string())


if __name__ == "__main__":
    main()
