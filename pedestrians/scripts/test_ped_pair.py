"""Pre-registered test P22 (docs/hypothesis-test.md): among stimulant-positive pedestrians killed, what share were
also opioid-positive? PASS if >= 50% in 2022-24 pooled.

    python scripts/test_ped_pair.py
      reads  data/raw/fars/FARS<YEAR>NationalCSV.zip (via test_ped_drugs.results), 2009-2024
      writes data/final/test_ped_pair.csv

Definitions as P9 "primary" (scripts/test_ped_drugs.py). Fentanyl = codes whose FARS label contains "fentanyl" or
"fentanil" or "ANPP" (fentanyl precursor/metabolite), collected from the 2017 PERSON labels and the 2018-2024 DRUGS
labels; pre-2015 files have no labels and use the 2015-17 code numbers. "Within the first hour" = PERSON.LAG_HRS 0.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fars_pedestrians import FINAL, load  # noqa: E402
from test_ped_drugs import INVALID, KEY, classify, results  # noqa: E402

YEARS = range(2009, 2025)
LATE = [2022, 2023, 2024]
PAT = r"entanyl|entanil|ANPP"


def fentanyl_codes():
    old, new = set(), set()
    d = load(2017, "person", ["DRUGRES1NAME", "DRUGRES1", "DRUGRES2NAME", "DRUGRES2", "DRUGRES3NAME", "DRUGRES3"])
    for i in (1, 2, 3):
        m = d[d[f"DRUGRES{i}NAME"].astype(str).str.contains(PAT, case=False, regex=True)]
        old |= set(m[f"DRUGRES{i}"].astype(int))
    for y in range(2018, 2025):
        d = load(y, "drugs", ["DRUGRES", "DRUGRESNAME"])
        m = d[d.DRUGRESNAME.astype(str).str.contains(PAT, case=False, regex=True)]
        (new if y >= 2022 else old).update(m.DRUGRES.astype(int))
    return old, new


FENT_OLD, FENT_NEW = fentanyl_codes()
print("fentanyl codes, 3-digit:", sorted(FENT_OLD), " 4-digit:", sorted(FENT_NEW))

rows = []
for y in YEARS:
    peds, r, _ = results(y)
    lag = load(y, "person", KEY + ["PER_TYP", "INJ_SEV", "LAG_HRS"])
    lag = lag[(lag.PER_TYP == 5) & (lag.INJ_SEV == 4)][KEY + ["LAG_HRS"]]
    r = r.assign(code=r.code.astype(int))
    valid = r[~r.code.isin(INVALID)].copy()
    new = y >= 2022
    flags = [classify(c, new, "primary") for c in valid.code]
    valid["opi"], valid["stim"] = [f[0] for f in flags], [f[1] for f in flags]
    valid["fent"] = valid.code.isin(FENT_NEW if new else FENT_OLD)
    per = valid.groupby(KEY)[["opi", "stim", "fent"]].any().reset_index().merge(lag, on=KEY, how="left")
    for subset, g in (("all", per), ("first_hour", per[per.LAG_HRS == 0])):
        s = g[g.stim]
        rows.append(dict(year=y, subset=subset, tested=len(g), stim=len(s), stim_opi=int(s.opi.sum()),
                         stim_fent=int(s.fent.sum()), stim_only=int((~s.opi).sum()),
                         opi_only=int((g.opi & ~g.stim).sum())))
t = pd.DataFrame(rows)
for c in ("stim_opi", "stim_fent", "stim_only"):
    t[f"share_of_stim_{c}"] = t[c] / t.stim
t["share_tested_both"] = t.stim_opi / t.tested
t["share_tested_stim_only"] = t.stim_only / t.tested
t.round(4).to_csv(FINAL / "test_ped_pair.csv", index=False)
pd.options.display.float_format = "{:.3f}".format
print(t[t.subset == "all"].drop(columns="subset").to_string(index=False))

for subset in ("all", "first_hour"):
    g = t[(t.subset == subset) & t.year.isin(LATE)][["tested", "stim", "stim_opi", "stim_fent", "stim_only"]].sum()
    share, fshare = g.stim_opi / g.stim, g.stim_fent / g.stim
    tag = "[pre-registered]" if subset == "all" else "[reported, not scored]"
    print(f"\n2022-24 {subset}: {g.stim} stimulant-positive of {g.tested} tested; with an opioid {g.stim_opi} "
          f"({share:.1%}); with fentanyl {g.stim_fent} ({fshare:.1%}); stimulant without opioid {g.stim_only} "
          f"=> P22 {'PASS' if share >= 0.5 else 'FAIL'} {tag}")
