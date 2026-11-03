"""Audit types by income: what's published, bracket by bracket.

Two outputs, because the sources use different brackets and years:
- data/audit_types_by_bracket.csv: all 11 Data Book brackets. TY2021 audit rate
  (Table 3-1) and audits closed in FY2025 by mail and "Field" (Table 3-2), from
  data/odds_by_income.csv, plus the Field share for FY2020-2025 and pooled
  FY2023-2025 (Table 18 / 3-2). Run audit_type_odds.py first.
- data/audit_types_trac_fy2022.csv: the only split of Field into revenue agents
  and tax auditors that we found, TRAC's FY2022 Table 1, in TRAC's five income
  classes. Typed in from https://tracreports.org/reports/706/.

Underreporter (CP2000) cases and math-error notices have no income split in the
Data Book (Tables 3-8 and 3-9), so they aren't here.
"""
import csv
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent.parent
ODDS = HERE / "data" / "odds_by_income.csv"
RAW = HERE / "data" / "raw"
FY_TABLES = {
    2020: RAW / "20dbs03t18ex.xlsx",
    2021: RAW / "21dbs03t18ex.xlsx",
    2022: RAW / "22dbs03t18ex.xlsx",
    2023: RAW / "23dbs03t18ex.xlsx",
    2024: RAW / "24dbs03t18ex.xlsx",
    2025: RAW / "25db-3-02-ex.xlsx",
}
OUT_BRACKET = HERE / "data" / "audit_types_by_bracket.csv"
OUT_TRAC = HERE / "data" / "audit_types_trac_fy2022.csv"

# TRAC Table 1, FY2022: returns, revenue agents, tax auditors, correspondence.
TRAC = [
    ("Under $25,000 gross receipts, with EITC", 23526357, 3131, 5725, 289629),
    ("Under $200,000 TPI, excluding the row above", 130852772, 31981, 30921, 187489),
    ("$200,000 under $1 million TPI, no Schedule C or F", 6869124, 4509, 1144, 28111),
    ("$200,000 under $1 million TPI, with Schedule C or F", 2593338, 5442, 2045, 19311),
    ("$1 million or more TPI", 703576, 7710, 987, 8069),
]
TRAC_TOTALS = (52773, 40822, 532609)


def closed_by_band(path):
    """Table 18 / 3-2: {band label: (total, field)} for one fiscal year, individual rows only."""
    out = {}
    for r in openpyxl.load_workbook(path, data_only=True).active.iter_rows(values_only=True):
        label = str(r[0] or "").strip()
        if label.startswith("Corporation"):
            break
        if label and label not in out and all(isinstance(v, (int, float)) for v in r[1:4]):
            out[label] = (int(r[1]), int(r[2]))
    return out


def field_share(tables, name):
    """Field share of audits closed across the given fiscal years, in percent."""
    rows = [next(v for k, v in t.items() if k.startswith(name)) for t in tables]
    return round(100 * sum(r[1] for r in rows) / sum(r[0] for r in rows), 1)


def write(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    with ODDS.open(encoding="utf-8") as f:
        odds = list(csv.DictReader(f))
    all_closed = int(odds[0]["fy2025_exams_closed"])
    brackets = [r for r in odds[1:] if not r["category"].startswith("Returns with")]
    for col in ("fy2025_exams_closed", "fy2025_field", "fy2025_mail", "ty2021_examined", "ty2021_returns_filed"):
        total = sum(int(r[col]) for r in brackets)
        assert total == int(odds[0][col]), (col, total, odds[0][col])

    tables = {fy: closed_by_band(path) for fy, path in FY_TABLES.items()}

    out = []
    for r in odds:
        closed = int(r["fy2025_exams_closed"])
        shares = {f"field_share_fy{fy}_pct": field_share([tables[fy]], r["category"]) for fy in FY_TABLES}
        out.append({
            "category": r["category"],
            "ty2021_returns_filed": r["ty2021_returns_filed"],
            "ty2021_examined": r["ty2021_examined"],
            "ty2021_audit_one_in": r["one_in"],
            "fy2025_all_audits": closed,
            "fy2025_mail": r["fy2025_mail"],
            "fy2025_field": r["fy2025_field"],
            "mail_share_pct": r["mail_share_pct"],
            "share_of_all_audits_pct": round(100 * closed / all_closed, 1),
            "est_mail_one_in": round(100 / float(r["mail_rate_pct"])),
            "est_field_one_in_at_most": r["in_person_one_in"],
            **shares,
            "field_share_fy2023_25_pct": field_share([tables[fy] for fy in (2023, 2024, 2025)], r["category"]),
        })
    write(OUT_BRACKET, out)

    assert tuple(sum(row[i] for row in TRAC) for i in (2, 3, 4)) == TRAC_TOTALS
    trac = []
    for name, returns, agents, auditors, mail in TRAC:
        total = agents + auditors + mail
        trac.append({
            "income_class": name,
            "returns": returns,
            "revenue_agents": agents,
            "tax_auditors": auditors,
            "correspondence": mail,
            "total": total,
            "revenue_agent_one_in": round(returns / agents),
            "tax_auditor_one_in": round(returns / auditors),
            "correspondence_one_in": round(returns / mail),
            "all_one_in": round(returns / total),
            "tax_auditor_share_of_non_mail_pct": round(100 * auditors / (agents + auditors), 1),
        })
    write(OUT_TRAC, trac)

    for r in out:
        print(f"{r['category'][:38]:38} 1 in {r['ty2021_audit_one_in']:>5}  mail {r['fy2025_mail']:>7} field {r['fy2025_field']:>6}"
              f"  {r['share_of_all_audits_pct']:>5}%  mail 1 in {r['est_mail_one_in']:>5}  field 1 in {r['est_field_one_in_at_most']:>6}")
    for r in trac:
        print(r)


if __name__ == "__main__":
    main()
