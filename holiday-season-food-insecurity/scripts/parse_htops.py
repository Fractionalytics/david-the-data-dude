"""Parse the Census HTOPS / HPS tables in data/raw/htops/.

Usage:
  python -I scripts/parse_htops.py dump <file.xlsx> [rows]   # print the first rows of the US sheet
  python -I scripts/parse_htops.py                           # print headline shares

Shares are computed from the published weighted counts:
  difficulty = (Somewhat + Very difficult) / (all answer categories, excluding "Did not report")
  food insufficiency = (Sometimes + Often not enough) / (all categories, excluding "Did not report")
"""
import pathlib
import sys

import openpyxl

RAW = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw" / "htops"


def rows_of(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.worksheets[0]  # first sheet = United States
    return ws.title, [list(r) for r in ws.iter_rows(values_only=True)]


def dump(name, n):
    title, rows = rows_of(RAW / name)
    print("SHEET:", title)
    for i, r in enumerate(rows[:n]):
        print(i, [c for c in r])


def num(v):
    if v is None or v == "-" or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return None


def find_header(rows, keyword):
    """Return (index, header) of the row naming the answer categories."""
    for i, r in enumerate(rows):
        cells = [str(c) for c in r if c is not None]
        if any(keyword.lower() in c.lower() for c in cells):
            return i, r
    raise ValueError(keyword)


def shares(name, keyword, numer_words, label_filter):
    _, rows = rows_of(RAW / name)
    hi, hdr = find_header(rows, "did not report")
    hdr = [("" if h is None else str(h).strip()) for h in hdr]
    # answer columns are those after the first column, excluding Total and "Did not report"
    ans_cols = [j for j, h in enumerate(hdr) if j > 0 and h and h.lower() != "total"
                and "did not report" not in h.lower()]
    num_cols = [j for j in ans_cols if any(w.lower() in hdr[j].lower() for w in numer_words)]
    out = []
    section = ""
    for r in rows[hi + 1:]:
        lab = r[0]
        if lab is None:
            continue
        lab = str(lab).strip()
        vals = [num(r[j]) if j < len(r) else None for j in ans_cols]
        if all(v in (0.0, None) for v in vals):
            section = lab
            continue
        if not label_filter(section, lab):
            continue
        den = sum(v for v in vals if v)
        nu = sum(num(r[j]) or 0 for j in num_cols)
        tot = num(r[1])
        out.append((section, lab, tot, nu, den, 100 * nu / den if den else None, 100 * nu / tot if tot else None))
    return [hdr[j] for j in ans_cols], [hdr[j] for j in num_cols], out


def want(section, lab):
    s = section.lower()
    return (lab.lower().startswith("total") or "income" in s or "children" in s
            or "employ" in s or "snap" in s or "food" in s)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "dump":
        dump(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 80)
        return
    jobs = []
    for f in ("2609_spending1.xlsx", "2607_spending1.xlsx", "2603_spending1.xlsx", "2022wk49_spending1.xlsx"):
        jobs.append((f, "difficult", ["somewhat difficult", "very difficult"]))
    for f in ("2609_food1.xlsx", "2607_food1.xlsx", "2603_food1.xlsx", "2022wk49_food1.xlsx", "2022wk49_food2.xlsx"):
        jobs.append((f, "enough", ["sometimes not enough", "often not enough"]))
    for f, kw, words in jobs:
        ans, nums, out = shares(f, kw, words, want)
        # 2603 and 2022 split income below $35,000 into two brackets; combine them so they
        # line up with the single "Less than $35,000" bracket in 2607 and 2609.
        low = [o for o in out if o[0] == "Household income"
               and (o[1].startswith("Less than $25,000") or o[1].startswith("$25,000 - $34,999"))]
        if len(low) == 2:
            nu = sum(o[3] for o in low)
            den = sum(o[4] for o in low)
            tot = sum(o[2] for o in low)
            out.append(("Household income", "COMBINED less than $35,000", tot, nu, den,
                        100 * nu / den, 100 * nu / tot))
        print("\n==", f)
        print("   answer cols:", ans)
        print("   numerator  :", nums)
        for section, lab, tot, nu, den, pct, pct_all in out:
            p = "n/a" if pct is None else f"{pct:5.1f}%"
            print(f"   [{section[:40]}] {lab[:45]:45s} total={tot:,.0f} num={nu:,.0f} den={den:,.0f} -> {p} of respondents | {pct_all:5.1f}% of all")


if __name__ == "__main__":
    main()
