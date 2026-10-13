"""Index radiology's Match growth against every other specialty, 2016 vs 2026.

Reads Table 7 / 7A from the saved 2016 and 2026 NRMP "Results and Data" PDFs and
sums positions offered (PGY-1 + PGY-2 + Physician (R)) per specialty for the
edition's first year column (2016, 2021, 2026). 2021-2026 is the cleaner window:
it starts after the osteopathic programs finished joining the Match. Also reads the GRAND TOTAL rows.

Caveat: the whole Match grew partly because osteopathic (AOA) programs moved into
the NRMP under single GME accreditation (2015-2020), so "all of the Match" is an
inflated benchmark. PGY-1 preliminary/transitional seats are counted as listed.

Output: data/processed/nrmp_specialty_growth.csv

Run from the repo worktree root:
    python -I -X utf8 projects/radiology/scripts/nrmp_specialty_growth.py
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

import pdfplumber

ROOT = Path("projects/radiology")
RAW = ROOT / "data/raw/nrmp"
OUT = ROOT / "data/processed/nrmp_specialty_growth.csv"
EDITIONS = {2016: ("Main-Match-Results-and-Data-2016.pdf", [30, 31]),
            2021: ("MRM-Results_and-Data_2021_revised.pdf", [28, 29]),
            2026: ("Main_Match_Results_and_Data-2026.pdf", [44, 45])}
# One number group per year: offered, filled US seniors, filled all (15 numbers, 5 years).
# Some PDF cells run together (e.g. "21,52841,482"), so parse the first number only.
NUM = r"\d{1,3}(?:,\d{3})*"
# Specialty names that changed between editions -> one name.
ALIASES = {"Orthopaedic Surgery": "Orthopedic Surgery", "Psychiatry": "Psychiatry (Categorical)",
           "Thoracic Surgery": "Thoracic Surgery (Integrated)",
           "Vascular Surgery": "Vascular Surgery (Integrated)"}
ROW = re.compile(rf"^\s*(?P<name>[A-Za-z][A-Za-z&/().\- ]*?)\s*(?P<first>{NUM})\s")


def first_year_offered(year):
    fname, pages = EDITIONS[year]
    totals, grand = defaultdict(int), None
    with pdfplumber.open(RAW / fname) as pdf:
        for pg in pages:
            for line in pdf.pages[pg - 1].extract_text().splitlines():
                # Up/down arrow glyphs (private-use chars) prefix rows with >10% changes.
                m = ROW.match(re.sub(r"[-]", "", line))
                if not m:
                    continue
                name = re.sub(r"\s+", " ", m["name"]).strip()
                name = ALIASES.get(name, name)
                value = int(m["first"].replace(",", ""))
                if name == "GRAND TOTAL":
                    grand = value
                elif not name.startswith("TOTAL") and "Table" not in name:
                    totals[name] += value
    return totals, grand


def main():
    t16, g16 = first_year_offered(2016)
    t21, g21 = first_year_offered(2021)
    t26, g26 = first_year_offered(2026)
    t16["GRAND TOTAL"], t21["GRAND TOTAL"], t26["GRAND TOTAL"] = g16, g21, g26
    pct = lambda a, b: round(100 * (b - a) / a, 1) if a else ""
    rows = []
    for name in sorted(set(t16) | set(t26)):
        a, m, b = t16.get(name, 0), t21.get(name, 0), t26.get(name, 0)
        rows.append({"specialty": name, "positions_2016": a, "positions_2021": m, "positions_2026": b,
                     "pct_change": pct(a, b), "pct_change_2021_2026": pct(m, b)})
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    big = sorted((r for r in rows if r["positions_2016"] >= 100 and r["specialty"] != "GRAND TOTAL"),
                 key=lambda r: -r["pct_change"])
    print("only in one edition (name changes):",
          [r["specialty"] for r in rows if not (r["positions_2016"] and r["positions_2026"])])
    for i, r in enumerate(big, 1):
        print(f"{i:>2}. {r['specialty']:<35}{r['positions_2016']:>7}{r['positions_2021']:>7}{r['positions_2026']:>7}"
              f"{r['pct_change']:>8}%{r['pct_change_2021_2026']:>8}%")
    g = next(r for r in rows if r["specialty"] == "GRAND TOTAL")
    print("GRAND TOTAL", g16, g21, g26, g["pct_change"], g["pct_change_2021_2026"])


if __name__ == "__main__":
    main()
