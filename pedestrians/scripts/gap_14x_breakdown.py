"""Break the 14x US-vs-Europe drug death gap (cards 1-2) into four non-overlapping slices of the US bar (2026-11-13).

    python scripts/gap_14x_breakdown.py
      writes data/final/gap_14x_breakdown.csv

US 2024 slices (deaths), each counted once:
  fentanyl + stimulant          28,063  CDC WONDER export (wonder_fent_and_stim_2018_2024.csv; stimulant = T43.6 or T40.5)
  fentanyl, no stimulant        47,735 (all T40.4, wonder_fent_all_2018_2024.csv) minus the pair
  stimulant, no fentanyl        18,907  Friedman, Palamar, Ciccarone et al. 2026 preprint, PDF p. 6 (provisional 2024)
  everything else               remainder of all 79,384 drug deaths (heroin, pills, methadone, benzodiazepines... without
                                fentanyl or a stimulant). Mixing the preprint's count with WONDER makes this slice approximate.
Europe: 16.7 deaths per million (EDR 2025, the bar in cards 1-2). US population 340,110,988 (WONDER 2024).
Each slice is expressed as a multiple of Europe's whole bar, so the four multiples add up to the 14x.
"""
from pathlib import Path

import pandas as pd

FINAL = Path(__file__).resolve().parents[1] / "data" / "final"
POP, EU_RATE, TOTAL = 340_110_988, 16.7, 79_384
pair, fent_all, stim_no_fent = 28_063, 47_735, 18_907
slices = {
    "fentanyl + stimulant": pair,
    "fentanyl, no stimulant": fent_all - pair,
    "stimulant, no fentanyl": stim_no_fent,
    "everything else": TOTAL - fent_all - stim_no_fent,
}
t = pd.DataFrame({"slice": list(slices), "deaths": list(slices.values())})
t["per_million"] = t.deaths / POP * 1e6
t["x_europe_bar"] = t.per_million / EU_RATE
t["share_of_us_bar"] = t.deaths / TOTAL
t.round(3).to_csv(FINAL / "gap_14x_breakdown.csv", index=False)
print(t.round(2).to_string(index=False))
print(f"total: {t.per_million.sum():.1f} per million = {t.x_europe_bar.sum():.1f}x Europe's {EU_RATE}")
