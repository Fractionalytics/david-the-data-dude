"""Print the NY Fed HHDC flow-into-serious-delinquency rates used in
docs/research/federal-surveys.md (Q3 2022, Q3 2025, Q3 2026, latest quarter).

Run: python -I scripts/parse_nyfed.py
"""
import pathlib

import openpyxl

F = (pathlib.Path(__file__).resolve().parent.parent / "data" / "raw" / "nyfed"
     / "HHD_C_Report_2026Q3.xlsx")
WANT = ("22:Q3", "25:Q3", "26:Q2", "26:Q3")


def show(ws):
    rows = [r for r in ws.iter_rows(values_only=True)]
    hdr = None
    for r in rows:
        cells = [c for c in r if c is not None]
        if not cells:
            continue
        first = str(r[0]).strip() if r[0] is not None else ""
        if hdr is None and any(isinstance(c, str) and c.strip() in
                               ("Credit Card", "Auto Loan", "18-29") for c in r):
            hdr = r
            print("   header:", [c for c in r])
            continue
        if hdr is not None and first in WANT:
            print("  ", [c for c in r])
    # notes
    for r in rows:
        for c in r:
            if isinstance(c, str) and ("note" in c.lower() or "annual" in c.lower()):
                print("   NOTE:", c)


def main():
    wb = openpyxl.load_workbook(F, read_only=True, data_only=True)
    for name in ("Page 14 Data", "Page 26 Data", "Page 27 Data"):
        print("==", name)
        show(wb[name])


if __name__ == "__main__":
    main()
