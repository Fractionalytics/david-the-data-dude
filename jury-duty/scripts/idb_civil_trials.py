"""Federal civil trials in the FJC Integrated Database: how often are trial dates filled in, and how long are jury trials?

Input: data/raw/idb/cv88on.zip (FJC IDB civil cumulative file, 330 MB, not committed;
https://www.fjc.gov/sites/default/files/idb/textfiles/cv88on.zip). Codebook: data/raw/idb/civil_codebook_1988_forward.pdf.
Keeps terminated cases that reached trial (PROCPROG 6-9) and writes them to data/idb_civil_trials.csv.

Run from the repo root: python projects/jury-duty/scripts/idb_civil_trials.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COLS = ["DISTRICT", "NOS", "PROCPROG", "DISP", "TERMDATE", "TRIBEGAN", "TRIALEND", "TAPEYEAR"]
# PROCPROG: 6 during court trial, 7 during jury trial, 8 after court trial, 9 after jury trial
TRIAL_PROG = {"6", "7", "8", "9"}

chunks = []
for c in pd.read_csv(ROOT / "data/raw/idb/cv88on.zip", sep="\t", usecols=COLS, dtype=str,
                     chunksize=500_000, encoding="latin-1"):
    chunks.append(c[c.PROCPROG.isin(TRIAL_PROG)])
t = pd.concat(chunks)
t["jury"] = t.PROCPROG.isin({"7", "9"})
for col in ["TERMDATE", "TRIBEGAN", "TRIALEND"]:
    t[col] = pd.to_datetime(t[col], format="%m/%d/%Y", errors="coerce")
t["term_fy"] = t.TERMDATE.dt.year + (t.TERMDATE.dt.month >= 10)
t["days"] = (t.TRIALEND - t.TRIBEGAN).dt.days + 1  # inclusive count of calendar days
t.to_csv(ROOT / "data/idb_civil_trials.csv", index=False)

cov = t.groupby(["term_fy", "jury"]).agg(trials=("jury", "size"), with_dates=("days", "count")).unstack("jury")
print("Trials by termination FY (jury = PROCPROG 7/9), and how many have both trial dates:")
print(cov.tail(15).to_string())
