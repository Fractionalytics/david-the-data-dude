"""Pre-registered test P9 (docs/hypothesis-test.md, Round 2): among pedestrians
killed who were tested for drugs, did the share positive for a stimulant
(methamphetamine, amphetamine, cocaine) or an opioid (including fentanyl) rise
from 2009-11 to 2020-22?

    python scripts/test_ped_drugs.py
      reads  data/raw/fars/FARS<YEAR>NationalCSV.zip, 2000-2024 (PERSON; DRUGS from 2018)
      writes data/final/test_ped_drugs.csv   one row per year x definition, plus
                                             pooled rows for 2009-11 and 2020-22

Pedestrians killed: PERSON.PER_TYP 5 and INJ_SEV 4 (as in fars_pedestrians.py).

Where the drug results are
  2000-2017  PERSON.DRUGRES1-3: at most three results per person.
  2018-2024  separate DRUGS file, one row per test result (any number), with the
             specimen (DRUGSPEC); joined on ST_CASE, VEH_NO, PER_NO. A pedestrian
             with no DRUGS row counts as not tested (the count is printed).

The coding change. The 2018 overhaul in these files is structural (the DRUGS
file, unlimited results, specimen type); the drug codes themselves stay the
same 3-digit scheme through 2021 (checked against the DRUGRESNAME labels in
2017, 2018 and 2021). The drug codes change in the 2022 file, to a 4-digit
scheme with far more named substances (e.g. fentanyl 151 -> 1059; caffeine,
nicotine and many prescription drugs get their own codes inside the classes).
Pre-2015 files carry no label columns; their codes are the same numbers as
2015-17. Checked against the 2015-2021 labels: among pedestrians killed in
2009-11, the only unlabeled codes are 606 (281 results, inside the 600s
cannabinoid class) and seven single results (135, 145, 185, 213 in the
narcotics range, counted as opioids by range; 314, 531, 921 in other classes).
The printed "not in 2017 labels" list uses all persons and only the 2017 file.

Result codes                        3-digit (to 2021)   4-digit (2022 on)
  not tested                        0                   0
  negative                          1                   1
  not reported                      95                  9995
  tested, results unknown           997                 9997
  positive, type unknown            998                 9998
  unknown if tested                 999                 9999

"Tested" = at least one valid result: negative, or any drug code, or
"positive, type unknown" (998/9998). Not tested / not reported / results
unknown / unknown if tested are not valid results.

Drug mappings (from the label columns)
  PRIMARY (pre-registered intent: the named drugs)
    opioid      3-digit: 100-295, the "narcotics" class; every labeled code in it
                is an opioid (incl. 151 fentanyl, 125 carfentanil, 154 heroin,
                295 narcotics type unknown).
                4-digit: 1000-1997, "narcotic analgesics", minus 1097 papaverine
                (not an opioid) and 1133 mitragynine (kratom, not a scheduled
                opioid); includes fentanyl analogs, norfentanyl (1136), 4-ANPP
                (1123), 6-MAM (1079), EDDP (1137), tramadol, 1997 type unknown.
    stimulant   amphetamine, methamphetamine, cocaine and cocaine metabolites:
                3-digit: 400 amphetamine sulfate, 401 amphetamine, 402
                benzoylecgonine, 407 cocaine, 408 dextroamphetamine, 410 ecgonine,
                417 methamphetamine, 430 coca leaves.
                4-digit: 3019 amphetamine, 3022 benzoylecgonine, 3032
                cocaethylene, 3033 cocaine, 3039 ecgonine, 3053 methamphetamine,
                3080 ecgonine methyl ester, 3081 norcocaine, 3082 methylecgonine.
  BROAD (uncertainty check: whole classes)
    opioid      3-digit 100-295; 4-digit 1000-1997 (all).
    stimulant   3-digit 400-495; 4-digit 3000-3997 except 3026 caffeine,
                3034 cotinine, 3066 nicotine (new in 2022; counting them would
                make the class jump for a reason unrelated to the hypothesis).
  Also reported: first3 = PRIMARY but using only each pedestrian's first three
  result rows (file order) from 2018 on, to mimic the pre-2018 three-result cap.

Steps
  1. Per year 2000-2024: killed, tested, testing rate, positive (stimulant or
     opioid), share positive among tested; also stimulant-only and opioid-only.
  2. Pooled 2009-11 and 2020-22 (sums over the three years).
  3. Pre-registered: PASS if the PRIMARY 2020-22 share is >= 5 percentage points
     above the 2009-11 share.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fars_pedestrians import FINAL, load  # noqa: E402

YEARS = range(2000, 2025)
EARLY, LATE = [2009, 2010, 2011], [2020, 2021, 2022]
KEY = ["ST_CASE", "VEH_NO", "PER_NO"]
INVALID = {0, 95, 997, 999, 9995, 9997, 9999}

STIM3 = {400, 401, 402, 407, 408, 410, 417, 430}
STIM4 = {3019, 3022, 3032, 3033, 3039, 3053, 3080, 3081, 3082}
NONOPIOID4 = {1097, 1133}
STIM4_EXCL = {3026, 3034, 3066}


def classify(code: int, new: bool, how: str) -> tuple[bool, bool]:
    """(opioid, stimulant) for one result code."""
    if new:
        opi = 1000 <= code <= 1997 and (how == "broad" or code not in NONOPIOID4)
        stim = (3000 <= code <= 3997 and code not in STIM4_EXCL) if how == "broad" else code in STIM4
    else:
        opi = 100 <= code <= 295
        stim = 400 <= code <= 495 if how == "broad" else code in STIM3
    return opi, stim


def results(year: int) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """Pedestrians killed, and their result rows (KEY, code, order)."""
    if year <= 2017:
        cols = [f"DRUGRES{i}" for i in (1, 2, 3)]
        p = load(year, "person", KEY + ["PER_TYP", "INJ_SEV"] + cols)
        peds = p[(p.PER_TYP == 5) & (p.INJ_SEV == 4)][KEY].copy()
        r = p.loc[peds.index, KEY + cols].melt(id_vars=KEY, value_name="code")
        r["order"] = r.variable.str[-1].astype(int)
        return peds, r.drop(columns="variable").dropna(subset=["code"]), 0
    p = load(year, "person", KEY + ["PER_TYP", "INJ_SEV"])
    peds = p[(p.PER_TYP == 5) & (p.INJ_SEV == 4)][KEY].copy()
    d = load(year, "drugs", KEY + ["DRUGRES"]).rename(columns={"DRUGRES": "code"})
    d["order"] = d.groupby(KEY).cumcount() + 1
    r = d.merge(peds, on=KEY)
    missing = len(peds.merge(r[KEY].drop_duplicates(), on=KEY, how="left", indicator=True)
                  .query("_merge == 'left_only'"))
    return peds, r, missing


def summarize(year, peds, r, how, cap3=False) -> dict:
    r = r[r.order <= 3] if cap3 else r
    r = r.assign(code=r.code.astype(int))
    valid = r[~r.code.isin(INVALID)]
    new = year >= 2022
    drug = valid.code[valid.code > 1]
    wrong = drug[(drug < 1000) & (drug != 998)] if new else drug[drug >= 1000]
    assert wrong.empty, f"{year}: codes from the other scheme: {sorted(wrong.unique())[:10]}"
    flags = valid.code.apply(lambda c: classify(c, new, how))
    valid = valid.assign(opi=[f[0] for f in flags], stim=[f[1] for f in flags])
    per = valid.groupby(KEY)[["opi", "stim"]].any()
    n_test = len(per)
    pos = int((per.opi | per.stim).sum())
    return {"year": year, "definition": how + ("_first3" if cap3 else ""), "killed": len(peds),
            "tested": n_test, "positive": pos, "stimulant": int(per.stim.sum()), "opioid": int(per.opi.sum()),
            "max_results_per_ped": int(r.groupby(KEY).size().max()) if len(r) else 0}


def main() -> None:
    rows = []
    for y in YEARS:
        peds, r, missing = results(y)
        if missing:
            print(f"{y}: {missing} pedestrians killed with no DRUGS row (counted as not tested)")
        for how in ("primary", "broad"):
            rows.append(summarize(y, peds, r, how))
        if y >= 2018:
            rows.append(summarize(y, peds, r, "primary", cap3=True))
            over3 = int((r.groupby(KEY).order.max() > 3).sum())
            rows[-1]["peds_over3_results"] = over3
        print(next(x for x in rows if x["year"] == y and x["definition"] == "primary"), flush=True)
    t = pd.DataFrame(rows)

    # code check: every 2009-11 code must be labeled in the 2017 file
    lab = load(2017, "person", [f"DRUGRES{i}" for i in (1, 2, 3)])
    known = set(pd.unique(lab.values.ravel()))
    seen = set()
    for y in EARLY:
        _, r, _ = results(y)
        seen |= set(r.code.astype(int))
    print("2009-11 codes not in 2017 labels:", sorted(seen - known) or "none")

    pooled = []
    for tag, ys in (("2009-11", EARLY), ("2020-22", LATE)):
        g = t[t.year.isin(ys)].groupby("definition")[["killed", "tested", "positive", "stimulant", "opioid"]].sum()
        g["year"] = tag
        pooled.append(g.reset_index())
    t = pd.concat([t.astype({"year": str}), *pooled], ignore_index=True)
    t["testing_rate"] = t.tested / t.killed
    for c in ("positive", "stimulant", "opioid"):
        t[f"share_{c}"] = t[c] / t.tested
    t.round(4).to_csv(FINAL / "test_ped_drugs.csv", index=False)

    show = ["year", "killed", "tested", "testing_rate", "positive", "share_positive", "share_stimulant", "share_opioid"]
    print(t[t.definition == "primary"][show].round(3).to_string(index=False))
    for d in ("primary", "broad", "primary_first3"):
        p = t[(t.definition == d) & t.year.isin(["2009-11", "2020-22"])].set_index("year")
        if "2009-11" not in p.index:  # first3 only exists from 2018; early period is capped at 3 anyway
            p = pd.concat([t[(t.definition == "primary") & (t.year == "2009-11")].set_index("year"), p])
        diff = (p.share_positive["2020-22"] - p.share_positive["2009-11"]) * 100
        print(f"\n{d}: 2009-11 {p.share_positive['2009-11']:.1%} of {p.tested['2009-11']} tested "
              f"(testing rate {p.testing_rate['2009-11']:.1%}); 2020-22 {p.share_positive['2020-22']:.1%} "
              f"of {p.tested['2020-22']} (testing rate {p.testing_rate['2020-22']:.1%}); "
              f"change {diff:+.1f} pp => {'PASS' if diff >= 5 else 'FAIL'}"
              + ("  [pre-registered]" if d == "primary" else "  [not pre-registered]"))


if __name__ == "__main__":
    main()
