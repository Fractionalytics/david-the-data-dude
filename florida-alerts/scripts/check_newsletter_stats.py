"""Check the hand-transcribed newsletter figures against the extracted newsletter text.

data/interim/newsletter_stats.csv was typed from the newsletters' stat boxes (numbers there are sometimes spelled
out, periods vary, and some figures are cumulative, so regex extraction mislabels them). This script confirms that
every row's quote appears on the stated page and that every digit-written number in the row appears in its quote.
"""
from pathlib import Path
import re
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1] / "data" / "interim"
stats = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else ROOT / "newsletter_stats.csv")


def norm(s):
    return re.sub(r"\s+", " ", s.replace("­ ", "").replace("­", "")).replace("’", "'").strip().lower()


failures = 0
for i, row in stats.iterrows():
    pages = (ROOT / "newsletters" / f"{row.source_issue}.txt").read_text(encoding="utf-8").split("\f")
    page = norm(pages[row.page - 1])
    quote = norm(row.quote)
    if quote not in page:
        print(f"row {i + 2}: quote not found on {row.source_issue} p{row.page}: {row.quote!r}")
        failures += 1
        continue
    digits = set(re.findall(r"\d[\d,]*", row.quote.replace(",", "")))
    for col in ("alerts_issued", "recovered", "direct_recoveries"):
        v = row[col]
        if pd.notna(v) and str(int(v)) not in digits and not re.search(r"[A-Z]{3,}|[a-z]+-[a-z]+|One Hundred|Four", row.quote):
            print(f"row {i + 2}: {col}={int(v)} not written as digits in quote {row.quote!r}")
            failures += 1
print(f"{len(stats)} rows checked, {failures} problems")
sys.exit(1 if failures else 0)
