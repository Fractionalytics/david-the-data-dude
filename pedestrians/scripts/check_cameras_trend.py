"""Not pre-registered: how much of P14's gap could the pre-existing trend explain?

    python scripts/check_cameras_trend.py   (reads data/final/test_cameras_cities.csv)

Uses P14's matched weights. Compares the treated-minus-comparison change in
rate (per 100,000) before (2005-07 -> 2009-11, 4 years between midpoints)
and after (2009-11 -> 2020-22, 11 years), and what the after gap would be if
the before gap had simply continued at the same yearly pace.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_cameras as tc  # noqa: E402

c = pd.read_csv(tc.FINAL / "test_cameras_cities.csv", index_col=0, dtype={"STATE": str})
c.index = c.index.astype(str)
c["abs_post"] = c.rate_post - c.rate_pre
treated = [i for i in c.index if c.at[i, "group"] == "treated"]
w = tc.matched(c, treated)
pre = c.loc[treated, "pretrend"].mean() - np.mean([(v * c.loc[v.index, "pretrend"]).sum() for v in w.values()])
post = c.loc[treated, "abs_post"].mean() - np.mean([(v * c.loc[v.index, "abs_post"]).sum() for v in w.values()])
print(f"pre gap (4 yrs): {pre:+.3f} per 100k; post gap (11 yrs): {post:+.3f}")
print(f"pre gap carried forward 11 years at the same pace: {pre / 4 * 11:+.3f}")
print(f"share of the post gap that a continued pre-trend would account for: {pre / 4 * 11 / post:.0%}")
