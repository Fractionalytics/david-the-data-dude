"""Script check (2026-11-13), not pre-registered: among pedestrians killed in 2022-24 who tested positive for
METHAMPHETAMINE itself (FARS code 3053), what share had no opioid? Companion to P22 (scripts/test_ped_pair.py),
which counts all stimulants (meth, amphetamine, cocaine).

    python scripts/ped_meth_no_opioid.py
Result (2026-11-13): 2,465 meth-positive of 11,894 tested; 614 with an opioid; 75.1% without.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ped_drugs import INVALID, KEY, classify, results  # noqa: E402

tot = dict(tested=0, meth=0, meth_opi=0)
for y in (2022, 2023, 2024):
    peds, r, _ = results(y)
    r = r.assign(code=r.code.astype(int))
    v = r[~r.code.isin(INVALID)].copy()
    v["opi"] = [classify(c, True, "primary")[0] for c in v.code]
    v["meth"] = v.code == 3053
    per = v.groupby(KEY)[["opi", "meth"]].any()
    m = per[per.meth]
    print(y, "tested", len(per), "meth", len(m), "meth+opioid", int(m.opi.sum()))
    tot["tested"] += len(per)
    tot["meth"] += len(m)
    tot["meth_opi"] += int(m.opi.sum())
print(tot, f"meth without opioid: {1 - tot['meth_opi'] / tot['meth']:.1%}")
