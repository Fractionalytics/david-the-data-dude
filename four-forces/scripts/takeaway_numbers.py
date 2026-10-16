"""Candidate takeaway numbers against ONE benchmark: all US jobs outside office & administrative support (SOC 43).

Uses BLS's official OEWS totals (00-0000 all occupations, 43-0000 office & admin), so nothing is dropped.
Customer service reps (43-4051) and data entry keyers (43-9021) sit inside SOC 43, so the same benchmark fits all rows.

Output: data/processed/takeaway_numbers.csv
Run from projects/amara/:  python scripts/takeaway_numbers.py
"""
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
YEARS = [2019, 2022, 2023, 2024, 2025]
CODES = {"00-0000": "All occupations", "43-0000": "Office & administrative support",
         "43-4051": "Customer service representatives", "43-9021": "Data entry keyers"}


def load(year: int) -> pd.Series:
    with zipfile.ZipFile(ROOT / f"data/raw/oews/oesm{str(year)[2:]}nat.zip") as z:
        name = next(n for n in z.namelist() if n.endswith(".xlsx"))
        with z.open(name) as f:
            df = pd.read_excel(f, dtype=str)
    df.columns = [c.upper() for c in df.columns]
    df = df[df["OCC_CODE"].isin(CODES)].drop_duplicates("OCC_CODE")
    return pd.to_numeric(df.set_index("OCC_CODE")["TOT_EMP"]).rename(year)


t = pd.concat([load(y) for y in YEARS], axis=1)
t.loc["benchmark"] = t.loc["00-0000"] - t.loc["43-0000"]
t.insert(0, "series", [CODES.get(c, "All jobs outside office & admin (benchmark)") for c in t.index])
t["chg_2019_22"] = t[2022] - t[2019]
t["pct_2019_22"] = ((t[2022] / t[2019] - 1) * 100).round(1)
t["chg_2022_25"] = t[2025] - t[2022]
t["pct_2022_25"] = ((t[2025] / t[2022] - 1) * 100).round(1)
t.to_csv(ROOT / "data/processed/takeaway_numbers.csv", index_label="soc")

pd.set_option("display.width", 200)
print(t[["series", 2019, 2022, 2025, "chg_2019_22", "pct_2019_22", "chg_2022_25", "pct_2022_25"]].to_string())
