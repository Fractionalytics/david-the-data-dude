"""Reel 3 (2026-11-16): split the FARS stimulant signal in dead pedestrians into meth/amphetamine vs. cocaine,
by year, to check Brumbelow's "meth rise began around 2010" against our combined "stimulants from 2015".

    python scripts/ped_meth_vs_cocaine.py
      reads  FARS via test_ped_drugs.results (same tested definition as test_ped_drugs.py)
      writes data/final/ped_meth_vs_cocaine.csv

Meth/amphetamine: 3-digit 400, 401, 408, 417; 4-digit 3019, 3053. Cocaine: 3-digit 402, 407, 410, 430;
4-digit 3022, 3032, 3033, 3039, 3080-3082. A pedestrian can be positive for both.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ped_drugs import FINAL, INVALID, KEY, results  # noqa: E402

METH3, METH4 = {400, 401, 408, 417}, {3019, 3053}
COKE3, COKE4 = {402, 407, 410, 430}, {3022, 3032, 3033, 3039, 3080, 3081, 3082}


def main() -> None:
    rows = []
    for y in range(2000, 2025):
        peds, r, _ = results(y)
        r = r.assign(code=r.code.astype(int))
        v = r[~r.code.isin(INVALID)]
        new = y >= 2022
        v = v.assign(meth=v.code.isin(METH4 if new else METH3), coke=v.code.isin(COKE4 if new else COKE3))
        per = v.groupby(KEY)[["meth", "coke"]].any()
        rows.append((y, len(peds), len(per), int(per.meth.sum()), int(per.coke.sum())))
    t = pd.DataFrame(rows, columns=["year", "killed", "tested", "meth_amph", "cocaine"])
    t["meth_share"] = (t.meth_amph / t.tested * 100).round(1)
    t["coke_share"] = (t.cocaine / t.tested * 100).round(1)
    t.to_csv(FINAL / "ped_meth_vs_cocaine.csv", index=False)
    print(t.to_string(index=False))


if __name__ == "__main__":
    main()
