"""Parse IRS Data Book Table 3-1 (all available years) into a long CSV.

Source: https://www.irs.gov/pub/irs-soi/25db-3-01-ex-allyears.xlsx (FY2025 Data Book,
tax years 2010-2023), saved in data/raw/. Each tax year is a block of six columns:
returns filed, examined closed, examined in process, percentage covered, no-change
count, recommended additional tax (thousands of dollars).

Tax years 2015-2023 are as of September 30, 2025; 2010-2014 are frozen at the date in
their header. The published percentage is rounded to 0.1 and shows "[8]" for under
0.05%, so pct_computed = (closed + in_process) / returns_filed is the one to use.
Disclosure-suppressed cells ("d") and other footnote markers become blank.

Output: data/table_3_1_long.csv
"""
import csv
import re
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent.parent
SRC = HERE / "data" / "raw" / "25db-3-01-ex-allyears.xlsx"
OUT = HERE / "data" / "table_3_1_long.csv"
FIRST_DATA_ROW = 7


def num(v):
    return v if isinstance(v, (int, float)) else None


def main():
    ws = openpyxl.load_workbook(SRC, data_only=True).active
    header = [c.value for c in ws[3]]
    blocks = []
    for col, label in enumerate(header):
        m = re.match(r"Tax Year (\d{4})(.*)", str(label or ""))
        if m:
            as_of = re.search(r"as of ([A-Za-z]+ \d+, \d{4})", m.group(2))
            blocks.append((col, int(m.group(1)), as_of.group(1) if as_of else "September 30, 2025",
                           "†" in m.group(2)))

    rows = []
    section = ""
    for r in ws.iter_rows(min_row=FIRST_DATA_ROW, values_only=True):
        label = (r[0] or "").strip()
        if not label or label.startswith(("†", "d—", "*—", "N/A", "[", "NOTES", "SOURCE")):
            continue
        if all(v is None for v in r[1:]):
            section = label.rstrip(":")
            continue
        if not label.startswith(("No ", "$")):
            section = ""
        for col, ty, as_of, in_statute in blocks:
            filed, closed, in_proc, pct, no_change, add_tax = r[col:col + 6]
            examined = (num(closed) or 0) + (num(in_proc) or 0) if num(closed) is not None or num(in_proc) is not None else None
            suppressed = closed == "d" or in_proc == "d"
            rows.append({
                "tax_year": ty,
                "as_of": as_of,
                "within_3yr_statute": in_statute,
                "section": section,
                "category": label,
                "returns_filed": num(filed),
                "examined_closed": num(closed),
                "examined_in_process": num(in_proc),
                "examined_total": None if suppressed else examined,
                "pct_published": pct if num(pct) is not None else ("<0.05" if pct == "[8]" else None),
                "pct_computed": round(100 * examined / filed, 4) if examined is not None and not suppressed and num(filed) else None,
                "no_change": num(no_change),
                "recommended_additional_tax_thousands": num(add_tax),
            })

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows, tax years {min(b[1] for b in blocks)}-{max(b[1] for b in blocks)} -> {OUT.name}")


if __name__ == "__main__":
    main()
