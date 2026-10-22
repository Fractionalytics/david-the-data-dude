"""Federal juror funnel for one fiscal year (12 months ending Sept 30), from AO Judicial Business tables.

Reads the national "Total" rows of J-2, J-10, T-1 and T-2 in data/raw/ and prints each stage.
Run from the repo root: python projects/jury-duty/scripts/federal_funnel.py [2023|2025]
"""
import sys
from pathlib import Path

import pdfplumber

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
FY = sys.argv[1] if len(sys.argv) > 1 else "2025"  # 2023 or 2025 (PDFs for both are in data/raw/)


def lines(name):
    with pdfplumber.open(RAW / name) as pdf:
        return [l for p in pdf.pages for l in (p.extract_text() or "").splitlines()]


def nums(line):
    return [float(x.replace(",", "")) for x in line.split() if x.replace(",", "").replace(".", "").isdigit()]


def row(name, prefix):
    # first matching line that has numbers (skips header lines like "Total Juries")
    return next(n for l in lines(name) if l.startswith(prefix) and (n := nums(l)))


# J-2 Total: present, %selected, %challenged, %not sel overall, %voir dire not sel, %non-voir-dire, juries
present, sel, chal, _, vd_not, non_vd, juries = row(f"jb_j2_0930.{FY}.pdf", "Total ")
# J-10: jury trial days for the last five years -> last value is FY
trial_days = row(f"jb_j10_0930.{FY}.pdf", "Jury Trial Days")[-1]
# T-1 Total: all, civil total, civil nonjury, civil jury, crim total, crim nonjury, crim jury
t1 = row(f"jb_t1_0930.{FY}.pdf", "Total ")
jury_trials = t1[3] + t1[6]
# T-2 Total: all, civil total, 1d, 2d, 3d, 4-9, 10-19, 20+, crim total, 1d, 2d, 3d, 4-9, 10-19, 20+
t2 = row(f"jb_t2_0930.{FY}.pdf", "Total ")
one_day_all = t2[2] + t2[9]

seated = present * sel / 100
print(f"Jurors present on selection days:      {present:,.0f}")
print(f"  never called into a courtroom:        {non_vd:.1f}%")
print(f"  went to voir dire:                    {100 - non_vd:.1f}%")
print(f"  selected (sworn, incl. alternates):   {sel:.1f}%  (~{seated:,.0f} people)")
print(f"  selected, given voir dire:            {sel / (100 - non_vd) * 100:.1f}%")
print(f"Juries selected:                        {juries:,.0f}  (~{seated / juries:.1f} jurors each)")
print(f"Jury trials completed (T-1):            {jury_trials:,.0f}  (gap vs juries: {juries - jury_trials:,.0f})")
print(f"Jury trial days / juries selected:      {trial_days / juries:.2f} days per jury (mean)")
print(f"All trials (bench + jury), T-2:         {t2[0]:,.0f}; 1-day: {one_day_all:,.0f}; nonjury: {t1[2] + t1[5]:,.0f}")
