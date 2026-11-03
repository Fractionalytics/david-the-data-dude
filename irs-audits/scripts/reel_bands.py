"""The seven income bands the Reel uses, computed from raw IRS tables.

The script treats $1-$50K and $50K-$200K as single bands and leaves out "no total
positive income" and international returns. Merged rates are recomputed from
counts, not averaged.

- Odds: TY2021 returns ever examined / returns filed (Table 3-1).
- Field share: Field audits / all audits closed, pooled FY2023-FY2025 (Table 18 and
  3-2), the years most TY2021 audits would have closed. FY2025 alone is kept for
  comparison.

Output: data/reel_bands.csv
"""
import csv
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent.parent
COVERAGE = HERE / "data" / "table_3_1_long.csv"
RAW = HERE / "data" / "raw"
OUT = HERE / "data" / "reel_bands.csv"
TAX_YEAR = 2021
POOLED = {2023: RAW / "23dbs03t18ex.xlsx", 2024: RAW / "24dbs03t18ex.xlsx", 2025: RAW / "25db-3-02-ex.xlsx"}

BANDS = {
    "<$50K": ["$1 under $25,000", "$25,000 under $50,000"],
    "$50K–$200K": ["$50,000 under $75,000", "$75,000 under $100,000", "$100,000 under $200,000"],
    "$200K–$500K": ["$200,000 under $500,000"],
    "$500K–$1M": ["$500,000 under $1,000,000"],
    "$1M–$5M": ["$1,000,000 under $5,000,000"],
    "$5M–$10M": ["$5,000,000 under $10,000,000"],
    "$10M+": ["$10,000,000 or more"],
}


def closed_by_band(path):
    """{band label: (total, field)} for one fiscal year, individual rows only."""
    out = {}
    for r in openpyxl.load_workbook(path, data_only=True).active.iter_rows(values_only=True):
        label = str(r[0] or "").strip()
        if label.startswith("Corporation"):
            break
        if label and label not in out and all(isinstance(v, (int, float)) for v in r[1:4]):
            out[label] = (int(r[1]), int(r[2]))
    return out


def lookup(table, name):
    return next(v for k, v in table.items() if k.startswith(name))


def main():
    coverage = {}
    with COVERAGE.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if int(r["tax_year"]) == TAX_YEAR and r["section"].startswith("Size of total positive income"):
                coverage.setdefault(r["category"].strip(), r)
    tables = {fy: closed_by_band(path) for fy, path in POOLED.items()}

    out = []
    for band, parts in BANDS.items():
        rows = [next(v for k, v in coverage.items() if k.startswith(p)) for p in parts]
        filed = sum(int(float(r["returns_filed"])) for r in rows)
        examined = sum(int(float(r["examined_total"])) for r in rows)
        closed = {fy: [lookup(t, p) for p in parts] for fy, t in tables.items()}
        pooled_total = sum(v[0] for rows_ in closed.values() for v in rows_)
        pooled_field = sum(v[1] for rows_ in closed.values() for v in rows_)
        fy25_total = sum(v[0] for v in closed[2025])
        fy25_field = sum(v[1] for v in closed[2025])
        out.append({
            "band": band,
            "ty2021_returns_filed": filed,
            "ty2021_examined": examined,
            "audit_rate_pct": round(100 * examined / filed, 4),
            "one_in": round(filed / examined),
            "field_share_fy2023_25_pct": round(100 * pooled_field / pooled_total, 1),
            "field_share_fy2025_pct": round(100 * fy25_field / fy25_total, 1),
            "est_field_one_in_at_most": round(filed / examined / (pooled_field / pooled_total)),
        })

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    for r in out:
        print(r)
    print("<$50K vs. $50K-$200K rate ratio:", round(out[0]["audit_rate_pct"] / out[1]["audit_rate_pct"], 2))


if __name__ == "__main__":
    main()
