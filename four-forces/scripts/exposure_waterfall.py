"""Waterfall: how big is the job gap in the most AI-exposed occupations, once other suspects are removed?

Most AI-exposed = BLS "Very high" relative AI exposure (186 occupations in the balanced panel).
Gap = jobs those occupations would have had in May 2025 at the rest of the economy's 2022-25 growth rate, minus actual.
Steps (each a difference-in-differences variant; not causal):
  1. Raw gap vs. all other rated occupations.
  2. Adjust for the very-high group's slower growth BEFORE ChatGPT (2019-22 gap vs. the rest).
  3. Drop loan and insurance processing occupations (interest rates).
  4. Also drop health care occupations (SOC 29, 31) from both sides (a hiring boom that flatters the comparison).

Input: data/processed/exposure_ledger_occupations.csv (from exposure_ledger.py)
Outputs: data/processed/exposure_waterfall.csv, charts/exposure_waterfall.png (exploratory)
Run from projects/amara/:  python scripts/exposure_waterfall.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
p = pd.read_csv(ROOT / "data/processed/exposure_ledger_occupations.csv", dtype={"soc": str})
LOANS = ["13-2072", "43-4131", "43-9041", "13-2053"]  # loan officers, loan clerks, insurance claims clerks, underwriters
HEALTH = p["soc"].str.startswith(("29-", "31-"))


def gap(df: pd.DataFrame, adjust_pretrend: bool) -> float:
    vh, rest = df[df["exposure"] == "Very high"], df[df["exposure"] != "Very high"]
    g = lambda d, a, b: d[str(b)].sum() / d[str(a)].sum() - 1
    excess = g(vh, 2022, 2025) - g(rest, 2022, 2025)
    if adjust_pretrend:
        excess -= g(vh, 2019, 2022) - g(rest, 2019, 2022)
    return -excess * vh["2022"].sum()


steps = [
    ("Raw gap vs. rest of economy", gap(p, False)),
    ("Adjusted for pre-ChatGPT trend", gap(p, True)),
    ("Minus loan processing (interest rates)", gap(p[~p["soc"].isin(LOANS)], True)),
    ("Minus health care hiring boom", gap(p[~p["soc"].isin(LOANS) & ~HEALTH], True)),
]
non_office = p[~p["soc"].str.startswith("43-")]
df = pd.DataFrame(steps, columns=["step", "gap_jobs"])
df.to_csv(ROOT / "data/processed/exposure_waterfall.csv", index=False)
for s, v in steps:
    print(f"{s:42s} {v / 1e6:5.2f}M")
print(f"{'Check: very-high non-office jobs only':42s} {gap(non_office, True) / 1e6:5.2f}M  (the gap is office work)")

fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150)
labels = [s for s, _ in steps]
vals = [v / 1e6 for _, v in steps]
ax.bar(range(len(vals)), vals, color=["#c8312b", "#d9776f", "#e3a39c", "#c8312b"], width=0.6)
for i, v in enumerate(vals):
    ax.text(i, v + 0.03, f"{v:.2f}M", ha="center", fontsize=9)
ax.set_xticks(range(len(vals)), [l.replace(" (", "\n(").replace("vs. ", "vs.\n") for l in labels], fontsize=7)
ax.set_ylabel("Jobs short of the rest of the economy's pace (millions)", fontsize=8)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.set_title("Most AI-exposed jobs (BLS 'very high'), May 2022 - May 2025: exploratory", loc="left", fontsize=10)
fig.text(0.01, 0.01, "Source: BLS OEWS (May 2019, 2022, 2025) and BLS AI exposure categories. Balanced panel of 757 occupations. Not causal.",
         fontsize=6, color="#777777")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(ROOT / "charts/exposure_waterfall.png")
