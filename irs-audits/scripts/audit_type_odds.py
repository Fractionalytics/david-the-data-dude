"""Split the odds of an audit into mail and in-person, by income.

Combines two IRS Data Book tables that measure different things:
- Table 3-1 (data/table_3_1_long.csv): share of a tax year's returns ever examined.
  We use Tax Year 2021, the newest year mostly past the 3-year statute.
- Table 3-2 (data/raw/25db-3-02-ex.xlsx): examinations closed in fiscal 2025, split
  into field (in person: field and office audits) and correspondence (mail).

Applying FY2025's field share to TY2021's coverage assumes the mix of audit types
for TY2021 returns matched the mix of audits closed in FY2025. That's an
approximation (see docs/data-challenges.md).

Output: data/odds_by_income.csv
"""
import csv
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent.parent
COVERAGE = HERE / "data" / "table_3_1_long.csv"
TYPES = HERE / "data" / "raw" / "25db-3-02-ex.xlsx"
OUT = HERE / "data" / "odds_by_income.csv"
TAX_YEAR = 2021

ROWS = [
    "Individual income tax returns, total",
    "No total positive income",
    "$1 under $25,000",
    "$25,000 under $50,000",
    "$50,000 under $75,000",
    "$75,000 under $100,000",
    "$100,000 under $200,000",
    "$200,000 under $500,000",
    "$500,000 under $1,000,000",
    "$1,000,000 under $5,000,000",
    "$5,000,000 under $10,000,000",
    "$10,000,000 or more",
    "International returns",
    "Returns with earned income tax credit",
]


def main():
    coverage = {}
    with COVERAGE.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            # Corporate rows reuse some dollar labels, so keep individual rows only.
            if int(r["tax_year"]) == TAX_YEAR and (r["section"].startswith("Size of total positive income")
                                                  or not r["section"]):
                coverage.setdefault(r["category"].strip(), r)

    types = {}
    for r in openpyxl.load_workbook(TYPES, data_only=True).active.iter_rows(values_only=True):
        label = str(r[0] or "").strip()
        if label and label not in types and all(str(v).isdigit() for v in r[1:4]):
            types[label] = (int(r[1]), int(r[2]), int(r[3]))

    out = []
    for name in ROWS:
        cov = next(v for k, v in coverage.items() if k.startswith(name))
        total, field, mail = next(v for k, v in types.items() if k.startswith(name))
        filed, examined = float(cov["returns_filed"]), float(cov["examined_total"])
        rate = examined / filed
        field_share = field / total
        out.append({
            "category": name,
            f"ty{TAX_YEAR}_returns_filed": int(filed),
            f"ty{TAX_YEAR}_examined": int(examined),
            "audit_rate_pct": round(100 * rate, 3),
            "one_in": round(1 / rate),
            "fy2025_exams_closed": total,
            "fy2025_field": field,
            "fy2025_mail": mail,
            "mail_share_pct": round(100 * mail / total, 1),
            "in_person_rate_pct": round(100 * rate * field_share, 4),
            "in_person_one_in": round(1 / (rate * field_share)),
            "mail_rate_pct": round(100 * rate * (1 - field_share), 4),
        })

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    for r in out:
        print(f"{r['category'][:38]:38} 1 in {r['one_in']:>5,}  mail {r['mail_share_pct']:>5}%  in person 1 in {r['in_person_one_in']:>7,}")


if __name__ == "__main__":
    main()
