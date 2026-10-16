"""National OEWS employment for the occupations in the Amara's Law research, May 2019 and 2022-2025.

Input: data/raw/oews/oesm{YY}nat.zip (BLS national files, downloaded by David 2026-10-15).
Outputs: data/processed/oews_occupations_long.csv (one row per occupation-year, with RSE)
         data/processed/oews_occupations_wide.csv (employment by year, plus % changes)

Caveat: BLS "does not encourage" OEWS time-series comparisons (each estimate pools three years of panels).

Run from projects/amara/:  python scripts/oews_occupations.py
"""
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/oews"
OUT = ROOT / "data/processed"
YEARS = [2019, 2022, 2023, 2024, 2025]

OCCUPATIONS = {
    "43-4051": "Customer service representatives",
    "41-9041": "Telemarketers",
    "43-2011": "Switchboard operators",
    "27-3091": "Interpreters and translators",
    "27-3043": "Writers and authors",
    "27-3042": "Technical writers",
    "27-3041": "Editors",
    "15-1251": "Computer programmers",
    "15-1252": "Software developers",
    "15-1253": "Software QA analysts and testers",
    "15-1256": "Software developers and QA (2019 hybrid code)",
    "27-1024": "Graphic designers",
    "23-1011": "Lawyers",
    "23-2011": "Paralegals and legal assistants",
    "43-6012": "Legal secretaries and administrative assistants",
    "43-3031": "Bookkeeping, accounting and auditing clerks",
    "31-9094": "Medical transcriptionists",
    "43-9021": "Data entry keyers",
    "29-1224": "Radiologists",
}


def load(year: int) -> pd.DataFrame:
    yy = str(year)[2:]
    with zipfile.ZipFile(RAW / f"oesm{yy}nat.zip") as z:
        name = next(n for n in z.namelist() if n.endswith(".xlsx"))
        with z.open(name) as f:
            df = pd.read_excel(f, dtype=str)
    df.columns = [c.upper() for c in df.columns]
    df = df[df["OCC_CODE"].isin(OCCUPATIONS)]
    return pd.DataFrame({
        "year": year,
        "soc": df["OCC_CODE"],
        "title_bls": df["OCC_TITLE"],
        "employment": pd.to_numeric(df["TOT_EMP"], errors="coerce"),
        "emp_rse_pct": pd.to_numeric(df["EMP_PRSE"], errors="coerce"),
    })


long = pd.concat([load(y) for y in YEARS], ignore_index=True)
OUT.mkdir(parents=True, exist_ok=True)
long.to_csv(OUT / "oews_occupations_long.csv", index=False)

wide = long.pivot(index="soc", columns="year", values="employment").reindex(columns=YEARS)
wide.insert(0, "occupation", wide.index.map(OCCUPATIONS))
wide["chg_2019_22_pct"] = ((wide[2022] / wide[2019] - 1) * 100).round(1)
wide["chg_2022_25_pct"] = ((wide[2025] / wide[2022] - 1) * 100).round(1)
wide = wide.reindex([s for s in OCCUPATIONS if s in wide.index])
wide.to_csv(OUT / "oews_occupations_wide.csv")

pd.set_option("display.width", 200)
print(wide.to_string())
rse = long.pivot(index="soc", columns="year", values="emp_rse_pct")
print("\nRelative standard error of employment (%):")
print(rse.to_string())
