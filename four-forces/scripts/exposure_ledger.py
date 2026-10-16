"""The unbiased ledger: US employment change since ChatGPT for EVERY occupation, by BLS AI-exposure category.

Inputs:
  data/raw/oews/oesm{YY}nat.zip              BLS OEWS national files, May 2019 and 2022-2025
  data/raw/bls_ai_exposure_categories.xlsx   BLS "Relative AI exposure" (Low/Moderate/High/Very high), 2025-35 projections table
Outputs:
  data/processed/exposure_ledger_occupations.csv   one row per detailed occupation, with exposure and employment by year
  data/processed/exposure_ledger_summary.csv       totals by exposure category

Method: a balanced panel of detailed SOC occupations present in all five OEWS years and in the BLS exposure table.
"Shortfall vs. Low" = what each group would have reached in 2025 had it grown 2022-25 at the Low group's rate,
minus what it actually reached (a difference-in-differences style comparison; not causal).

Caveats: OEWS pools three years of panels and BLS discourages time-series use; it excludes the self-employed.
BLS says exposure "does not imply job loss."

Run from projects/amara/:  python scripts/exposure_ledger.py
"""
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
OUT = ROOT / "data/processed"
YEARS = [2019, 2022, 2023, 2024, 2025]
ORDER = ["Low", "Moderate", "High", "Very high"]


def oews(year: int) -> pd.Series:
    with zipfile.ZipFile(RAW / f"oews/oesm{str(year)[2:]}nat.zip") as z:
        name = next(n for n in z.namelist() if n.endswith(".xlsx"))
        with z.open(name) as f:
            df = pd.read_excel(f, dtype=str)
    df.columns = [c.upper() for c in df.columns]
    group_col = "O_GROUP" if "O_GROUP" in df.columns else "OCC_GROUP"
    df = df[df[group_col].str.lower() == "detailed"]
    return pd.to_numeric(df.set_index("OCC_CODE")["TOT_EMP"], errors="coerce").rename(year)


emp = pd.concat([oews(y) for y in YEARS], axis=1)

exp = pd.read_excel(RAW / "bls_ai_exposure_categories.xlsx", header=1, dtype=str)
exp = exp.rename(columns={exp.columns[0]: "title", exp.columns[1]: "soc", exp.columns[-1]: "exposure"})
exp = exp[exp["exposure"].isin(ORDER)].set_index("soc")[["title", "exposure"]]

all_2025 = emp[2025].sum()
panel = emp.dropna().join(exp, how="inner")
coverage = panel[2025].sum() / all_2025
print(f"Detailed occupations: {emp[2025].notna().sum()} in OEWS 2025; {len(panel)} in balanced panel with exposure")
print(f"Panel covers {coverage:.1%} of May 2025 OEWS employment ({panel[2025].sum():,.0f} of {all_2025:,.0f})")

unmatched = emp[emp[2025].notna() & ~emp.index.isin(panel.index)].sort_values(2025, ascending=False)
print("\nLargest May 2025 occupations left out (missing a year or no exposure code):")
print(unmatched[2025].head(8).to_string())

OUT.mkdir(parents=True, exist_ok=True)
panel["chg_2022_25"] = panel[2025] - panel[2022]
panel["pct_2019_22"] = (panel[2022] / panel[2019] - 1) * 100
panel["pct_2022_25"] = (panel[2025] / panel[2022] - 1) * 100
panel.sort_values("chg_2022_25").to_csv(OUT / "exposure_ledger_occupations.csv", index_label="soc")

g = panel.groupby("exposure")[YEARS].sum().reindex(ORDER)
g["occupations"] = panel.groupby("exposure").size().reindex(ORDER)
g["pct_2019_22"] = (g[2022] / g[2019] - 1) * 100
g["pct_2022_25"] = (g[2025] / g[2022] - 1) * 100
low_rate = g.loc["Low", 2025] / g.loc["Low", 2022]
g["expected_2025_at_low_rate"] = g[2022] * low_rate
g["shortfall_vs_low"] = g["expected_2025_at_low_rate"] - g[2025]
declines = panel[panel["chg_2022_25"] < 0].groupby("exposure")["chg_2022_25"].agg(["count", "sum"]).reindex(ORDER)
g["occupations_declining"] = declines["count"]
g["jobs_lost_in_declining_occs"] = -declines["sum"]
g.to_csv(OUT / "exposure_ledger_summary.csv")

pd.set_option("display.width", 220)
pd.set_option("display.float_format", lambda v: f"{v:,.1f}")
print("\nBy BLS AI exposure (balanced panel):")
print(g.to_string())

hv = panel[panel["exposure"].isin(["High", "Very high"])].sort_values("chg_2022_25")
cols = ["title", "exposure", 2019, 2022, 2025, "chg_2022_25", "pct_2019_22", "pct_2022_25"]
print("\nBiggest declines 2022-25, High/Very high exposure:")
print(hv[cols].head(15).to_string())
print("\nBiggest gains 2022-25, High/Very high exposure:")
print(hv[cols].tail(10).to_string())
