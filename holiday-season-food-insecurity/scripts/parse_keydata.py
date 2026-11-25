"""Monthly national SNAP and WIC participation from USDA FNS's Program
Information Report (Keydata), downloaded by David on 2026-11-23 to
data/raw/fns/keydata-August-2026.xlsx (FY2025-FY2026, generated 2026-11-13;
recent months are preliminary).

Writes data/snap_wic_monthly.csv and prints the changes.
Run from the repo root: python -I projects/thanksgiving-food-insecurity/scripts/parse_keydata.py
"""
import csv
import datetime as dt
import pathlib

import openpyxl

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "fns" / "keydata-August-2026.xlsx"
OUT = ROOT / "data" / "snap_wic_monthly.csv"


def months(ws, cols):
    """Rows whose first cell is a month like 'Oct 2025' with numeric data."""
    out = {}
    for r in ws.iter_rows(values_only=True):
        label = r[0]
        try:
            m = dt.datetime.strptime(str(label).strip(), "%b %Y").date()
        except ValueError:
            continue
        vals = [r[c] for c in cols]
        if all(isinstance(v, (int, float)) for v in vals):
            out[m] = vals
    return out


def main():
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    snap = months(wb["SNAP-$"], [1, 2, 3])  # households, persons, benefit per person
    wic = months(wb["WIC"], [4])  # total participants
    rows = []
    for m in sorted(snap):
        rows.append([m.isoformat(), *snap[m], wic.get(m, [None])[0]])
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month", "snap_households", "snap_persons", "snap_benefit_per_person", "wic_participants"])
        w.writerows(rows)

    first, last = dt.date(2025, 7, 1), max(snap)
    p0, p1 = snap[first][1], snap[last][1]
    print(f"SNAP persons  {first:%b %Y} {p0:,.0f} -> {last:%b %Y} {p1:,.0f}  {p1 - p0:+,.0f} ({100 * (p1 / p0 - 1):+.1f}%)")
    peak = max(snap, key=lambda k: snap[k][1])
    print(f"SNAP persons peak in file: {peak:%b %Y} {snap[peak][1]:,.0f}")
    print(f"SNAP benefit per person {first:%b %Y} ${snap[first][2]:.2f} -> {last:%b %Y} ${snap[last][2]:.2f}")
    w0, w1 = wic[dt.date(2025, 8, 1)][0], wic[last][0]
    print(f"WIC participants Aug 2025 {w0:,.0f} -> {last:%b %Y} {w1:,.0f}  {w1 - w0:+,.0f} ({100 * (w1 / w0 - 1):+.1f}%)")


if __name__ == "__main__":
    main()
