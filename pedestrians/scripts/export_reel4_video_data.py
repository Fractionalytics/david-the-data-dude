"""Reel 4: write the chart data the Remotion clips read.

    python scripts/export_reel4_video_data.py
      reads  data/final/reel4_four_waves.csv   (scripts/reel4_four_waves.py)
      writes video/src/reel4/data.json         (deaths by year, 2000-2025; 2025 provisional)

OxyContin sales for the card 4-6 slopegraph come from Van Zee 2009 (AJPH, PMC2622774): "Sales grew from
$48 million in 1996 to almost $1.1 billion in 2000."
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "final" / "reel4_four_waves.csv", index_col="year").loc[2000:2025]
cols = {"w1": "wave1_rx_no_fent", "w2": "wave2_heroin_no_fent", "w3": "wave3_fent_no_stim",
        "w4": "wave4_fent_and_stim", "stim": "stim_no_fent"}
out = {
    "years": [int(y) for y in df.index],
    "series": {k: [int(v) for v in df[c]] for k, c in cols.items()},
    "oxycontin": [{"year": 1996, "sales": 48e6}, {"year": 2000, "sales": 1.1e9}],
}
assert out["series"]["w4"][out["years"].index(2023)] == 41583
assert out["series"]["w3"][out["years"].index(2021)] == 36172
dest = ROOT / "video" / "src" / "reel4" / "data.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(out, indent=1))
print("wrote", dest, {k: max(v) for k, v in out["series"].items()})
