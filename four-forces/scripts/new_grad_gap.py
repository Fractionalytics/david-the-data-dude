"""Rebuild Derek Thompson's "New Grad Gap" chart (The Atlantic, 2025) with the NY Fed's latest data.

Gap = all-worker unemployment rate minus recent-graduate unemployment rate (percentage points).
Input: data/raw/nyfed_college_labor.xlsx, sheet "unemployed" (NY Fed, The Labor Market for Recent
College Graduates; CPS via IPUMS). Recent graduates are ages 22-27 with a bachelor's degree or higher.

Outputs: data/processed/new_grad_gap.csv and charts/new_grad_gap.png (exploratory, not a Reel chart).

Run from projects/amara/:  python scripts/new_grad_gap.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/nyfed_college_labor.xlsx"
CSV = ROOT / "data/processed/new_grad_gap.csv"
PNG = ROOT / "charts/new_grad_gap.png"

ws = openpyxl.load_workbook(RAW, data_only=True, read_only=True)["unemployed"]
rows = [r[:5] for r in ws.iter_rows(values_only=True) if r and hasattr(r[0], "year")]
df = pd.DataFrame(rows, columns=["date", "young_workers", "all_workers", "recent_grads", "college_grads"])
df["gap"] = (df["all_workers"] - df["recent_grads"]).round(3)

CSV.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(CSV, index=False)

PNG.parent.mkdir(parents=True, exist_ok=True)
fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150)
ax.plot(df["date"], df["gap"], color="#c8312b", linewidth=1.6)
ax.axhline(0, color="#222222", linewidth=0.8)
ax.axvline(pd.Timestamp("2022-11-30"), color="#888888", linewidth=0.8, linestyle="--")
ax.text(pd.Timestamp("2022-11-30"), ax.get_ylim()[1], " ChatGPT", va="top", fontsize=8, color="#555555")
last = df.iloc[-1]
ax.annotate(f"{last['gap']:+.2f}\n{last['date']:%b %Y}", (last["date"], last["gap"]),
            xytext=(6, 0), textcoords="offset points", fontsize=8, va="center", color="#333333")
ax.set_title("The New Grad Gap, updated", loc="left", fontsize=14)
ax.set_ylabel("All-worker minus recent-grad unemployment (pts)", fontsize=8, color="#555555")
ax.grid(axis="y", color="#e5e5e5", linewidth=0.6)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.tick_params(labelsize=8, colors="#555555")
fig.text(0.01, 0.01, "Source: Federal Reserve Bank of New York, The Labor Market for Recent College Graduates "
         "(CPS via IPUMS),\nupdated Aug 6, 2026. Recent grads: ages 22-27, bachelor's or higher. "
         "Rebuild of Derek Thompson's 2025 chart for The Atlantic.",
         fontsize=6, color="#777777")
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(PNG)

print(df.tail(3).to_string(index=False))
by_year = df.assign(year=df["date"].dt.year).groupby("year")["gap"].mean().round(2)
print(by_year.loc[2019:].to_string())
print("min:", df.loc[df["gap"].idxmin(), ["date", "gap"]].to_dict())
