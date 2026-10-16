"""Monthly employment in the telephone call center industry (NAICS 56142), BLS CES, not seasonally adjusted.

Series CEU6056142001 (all employees, thousands) from the BLS public API v2 (unregistered).
This is an INDUSTRY count (everyone employed by call-center firms), not the customer service occupation.
Compare the same month across years, since the series is not seasonally adjusted.

Outputs: data/raw/bls_ces_call_centers.json, data/processed/call_centers_ces.csv
Run from projects/amara/:  python scripts/call_centers_ces.py
"""
import json
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/CEU6056142001?startyear=2019&endyear=2026"

raw = json.load(urllib.request.urlopen(URL, timeout=60))
(ROOT / "data/raw/bls_ces_call_centers.json").write_text(json.dumps(raw, indent=1), encoding="utf-8")

rows = [{"date": pd.Timestamp(int(d["year"]), int(d["period"][1:]), 1), "employment_k": float(d["value"]),
         "preliminary": any(f.get("code") == "P" for f in d.get("footnotes", []) if f)}
        for d in raw["Results"]["series"][0]["data"] if d["period"].startswith("M") and d["period"] != "M13"]
df = pd.DataFrame(rows).sort_values("date")
df.to_csv(ROOT / "data/processed/call_centers_ces.csv", index=False)

s = df.set_index("date")["employment_k"]
s.index = s.index.strftime("%Y-%m")
pts = {"May 2019": "2019-05", "May 2022": "2022-05", "Nov 2022 (ChatGPT)": "2022-11", "May 2023": "2023-05",
       "May 2024": "2024-05", "May 2025": "2025-05", "Aug 2025": "2025-08", "Aug 2026 (latest, P)": "2026-08"}
for k, d in pts.items():
    print(f"{k:22s} {s[d]:7.1f}k")
pct = lambda a, b: (s[b] / s[a] - 1) * 100
print(f"May 2019 -> May 2022: {pct('2019-05', '2022-05'):+.1f}%")
print(f"May 2022 -> May 2025: {pct('2022-05', '2025-05'):+.1f}%")
print(f"May 2022 -> May 2023: {pct('2022-05', '2023-05'):+.1f}%")
print(f"Nov 2021 -> Nov 2022 (year before ChatGPT, same month): {pct('2021-11', '2022-11'):+.1f}%")
print(f"Aug 2019 -> Aug 2022 (same month, pre-ChatGPT): {pct('2019-08', '2022-08'):+.1f}%")
print(f"Aug 2022 -> Aug 2026 (same month, spans ChatGPT): {pct('2022-08', '2026-08'):+.1f}% ({s['2026-08'] - s['2022-08']:+.1f}k)")
# Benchmark, CES total nonfarm NSA (CEU0000000001): Aug 2022 153,209k -> Aug 2026 158,905k (P) = +3.7%
print(f"Aug 2025 -> Aug 2026: {pct('2025-08', '2026-08'):+.1f}%")
