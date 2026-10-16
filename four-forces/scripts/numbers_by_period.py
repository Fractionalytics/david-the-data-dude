"""Every OEWS number used in the script, with both periods: May 2019 -> May 2022 and May 2022 -> May 2025.

Inputs: data/raw/oews/oesm{YY}nat.zip, data/raw/bls_ai_exposure_categories.xlsx (via exposure_ledger outputs).
Output: data/processed/numbers_by_period.csv, plus a markdown table printed for docs/numbers-by-period.md

Run from projects/amara/ after exposure_ledger.py:  PYTHONIOENCODING=utf-8 python scripts/numbers_by_period.py
"""
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
YEARS = [2019, 2022, 2025]

ROWS = [  # (group, code, label)
    ("Benchmark", "BENCH", "All jobs outside office & admin support"),
    ("Benchmark", "00-0000", "All US jobs (all occupations)"),
    ("Fast lane", "43-0000", "Office & administrative support (all)"),
    ("Fast lane", "43-4051", "Customer service representatives"),
    ("Fast lane", "43-9021", "Data entry keyers"),
    ("Fast lane", "43-3031", "Bookkeeping, accounting & auditing clerks"),
    ("Fast lane", "43-4171", "Receptionists & information clerks"),
    ("Fast lane", "41-9041", "Telemarketers"),
    ("Other suspects", "43-4131", "Loan interviewers & clerks"),
    ("Other suspects", "13-2072", "Loan officers"),
    ("Other suspects", "15-1251", "Computer programmers"),
    ("Slow lane", "23-2011", "Paralegals & legal assistants"),
    ("Slow lane", "23-1011", "Lawyers (employees only)"),
    ("Slow lane", "43-6012", "Legal secretaries & admin assistants"),
    ("Third lane", "LOW", "All low-AI-exposure occupations (BLS rating; 203 occupations)"),
    ("Third lane", "31-1131", "Nursing assistants"),
    ("Third lane", "37-2012", "Maids & housekeeping cleaners"),
    ("Third lane", "37-2011", "Janitors & cleaners"),
    ("Third lane", "53-7064", "Hand packers & packagers"),
    ("Exposure groups", "VH", "All very-high-AI-exposure occupations (186)"),
    ("Exposure groups", "NOTVH", "All other rated occupations (571)"),
    ("Jobs added", "15-2051", "Data scientists"),
    ("Jobs added", "15-1252", "Software developers"),
    ("Jobs added", "41-9031", "Sales engineers"),
    ("Jobs added", "47-2111", "Electricians"),
    ("Jobs added", "47-2061", "Construction laborers"),
    ("Jobs added", "49-9051", "Electrical power-line installers"),
]


def load(year: int) -> pd.Series:
    with zipfile.ZipFile(ROOT / f"data/raw/oews/oesm{str(year)[2:]}nat.zip") as z:
        name = next(n for n in z.namelist() if n.endswith(".xlsx"))
        with z.open(name) as f:
            df = pd.read_excel(f, dtype=str)
    df.columns = [c.upper() for c in df.columns]
    df = df.drop_duplicates("OCC_CODE")
    return pd.to_numeric(df.set_index("OCC_CODE")["TOT_EMP"], errors="coerce").rename(year)


emp = pd.concat([load(y) for y in YEARS], axis=1)
emp.loc["BENCH"] = emp.loc["00-0000"] - emp.loc["43-0000"]
panel = pd.read_csv(ROOT / "data/processed/exposure_ledger_occupations.csv", dtype={"soc": str})
for code, mask in {"LOW": panel["exposure"] == "Low", "VH": panel["exposure"] == "Very high",
                   "NOTVH": panel["exposure"] != "Very high"}.items():
    emp.loc[code] = [panel.loc[mask, str(y)].sum() for y in YEARS]

out = []
for group, code, label in ROWS:
    v = emp.loc[code]
    row = {"group": group, "code": code, "category": label, "may_2019": v[2019], "may_2022": v[2022], "may_2025": v[2025]}
    for a, b in [(2019, 2022), (2022, 2025)]:
        ok = pd.notna(v[a]) and pd.notna(v[b])
        row[f"chg_{a}_{b}"] = v[b] - v[a] if ok else None
        row[f"pct_{a}_{b}"] = (v[b] / v[a] - 1) * 100 if ok else None
    out.append(row)
df = pd.DataFrame(out)
df.to_csv(ROOT / "data/processed/numbers_by_period.csv", index=False)


def n(x):
    return "n/a" if pd.isna(x) else f"{x:,.0f}"


def s(x, pct=False):
    if pd.isna(x):
        return "n/a"
    return f"{x:+.1f}%" if pct else f"{x:+,.0f}"


lines = ["| Lane | Category | May 2019 | May 2022 | May 2025 | 2019→22 change | 2019→22 % | 2022→25 change | 2022→25 % |",
         "|---|---|---|---|---|---|---|---|---|"]
for r in out:
    lines.append(f"| {r['group']} | {r['category']} | {n(r['may_2019'])} | {n(r['may_2022'])} | {n(r['may_2025'])} | "
                 f"{s(r['chg_2019_2022'])} | {s(r['pct_2019_2022'], True)} | {s(r['chg_2022_2025'])} | {s(r['pct_2022_2025'], True)} |")
print("\n".join(lines))  # pasted into docs/numbers-by-period.md
