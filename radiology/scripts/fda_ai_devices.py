"""Count FDA AI-enabled medical device authorizations by year, radiology vs. all.

Input: data/raw/fda/aiml-devices.csv, the FDA "Artificial Intelligence-Enabled
Medical Devices" list (downloaded 2026-10-11 from
https://www.fda.gov/media/178541/download?attachment; page last updated
2026-09-04, latest decision date in file 2026-06-29). Columns: Date of Final
Decision, Submission Number, Device, Company, Panel (Lead), Primary Product Code.

"Radiology" = Panel (Lead) == "Radiology" (the FDA review panel that led the
review, not a clinical-use classification; a device can touch imaging and still
sit under Cardiovascular or Neurology).

Output: data/processed/fda_ai_devices_by_year.csv with, per decision year:
all devices, radiology-panel devices, radiology share, and cumulative counts.
The final year is partial (through the latest decision date in the file).

Run from the repo worktree root:
    python -I -X utf8 projects/radiology/scripts/fda_ai_devices.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path("projects/radiology")
SRC = ROOT / "data/raw/fda/aiml-devices.csv"
OUT = ROOT / "data/processed/fda_ai_devices_by_year.csv"


def main():
    df = pd.read_csv(SRC, dtype=str)
    df["date"] = pd.to_datetime(df["Date of Final Decision"], format="%m/%d/%Y")
    df["year"] = df["date"].dt.year
    df["is_radiology"] = df["Panel (Lead)"].str.strip().eq("Radiology")
    assert df["Submission Number"].is_unique, "duplicate submission numbers"
    g = df.groupby("year").agg(all_devices=("is_radiology", "size"),
                               radiology_devices=("is_radiology", "sum"))
    g = g.reindex(range(g.index.min(), g.index.max() + 1), fill_value=0)
    g["radiology_share"] = (g.radiology_devices / g.all_devices).round(3)
    g["cumulative_all"] = g.all_devices.cumsum()
    g["cumulative_radiology"] = g.radiology_devices.cumsum()
    g["cumulative_radiology_share"] = (g.cumulative_radiology / g.cumulative_all).round(3)
    last = df["date"].max()
    g["notes"] = ""
    g.loc[last.year, "notes"] = f"partial year through {last:%Y-%m-%d}"
    g.to_csv(OUT)
    print(g.to_string())
    print("panels:", df["Panel (Lead)"].value_counts().head(8).to_dict())


if __name__ == "__main__":
    main()
