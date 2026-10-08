"""Parse the archived Silver Alert monthly-report PDFs (2011-2020) into two tables.

Input:  data/raw/silver_monthly_pdfs/*.pdf (fetched by wayback_download.py)
Output: data/interim/silver_monthly_totals.csv  one row per report: month, alerts that month, year-to-date,
                                                 since-2008 total, cumulative direct recoveries
        data/interim/silver_monthly_cases.csv   one row per alert: date, age, sex, agency, last known, recovered
                                                 (no names; the reports carry none)

The per-month direct-recovery count is derived later as the difference of the cumulative totals, so a report
that is missing or lists no per-row marker doesn't break the series.
"""
from pathlib import Path
import re

import fitz  # PyMuPDF
import pandas as pd

ROOT = Path(__file__).resolve().parents[1] / "data"
SRC = ROOT / "raw" / "silver_monthly_pdfs"
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december"]


def num(pattern, text):
    m = re.search(pattern, text, re.I | re.S)
    return int(m.group(1).replace(",", "")) if m else None


totals, cases = [], []
for pdf in sorted(SRC.glob("*.pdf")):
    year = int(pdf.name[:4])
    stem = pdf.stem.lower()
    month = next((i + 1 for i, m in enumerate(MONTHS) if m in stem[4:] or m[:3] + "_" in stem[4:]), None)
    text = "\n".join(page.get_text() for page in fitz.open(pdf))
    flat = re.sub(r"\s+", " ", text)
    totals.append({
        "file": pdf.name,
        "year": year,
        "month": month,
        "alerts_month": num(r"Total for [A-Za-z]+\s*:?\s*(\d+)", flat),
        "alerts_ytd": num(r"Total for the Year of \d{4}\s*:?\s*(\d+)", flat),
        "alerts_since_2008": num(r"(?:implementation date[^)]*\)|inception of Florida Silver Alert Plan)\s*:?\s*([\d,]+)", flat),
        "direct_recoveries_to_date": num(r"(?<!In)Direct Recover(?:y|ies)[^\d]*?(?:to date)?\s*=?\s*([\d,]+)", flat),
        "indirect_recoveries_to_date": num(r"Indirect Recover(?:y|ies)[^\d]*?(?:to date)?\s*=?\s*([\d,]+)", flat),
        "pages": len(fitz.open(pdf)),
    })
    # Case rows: a row number ("8." or, in some reports, a bare "8") followed by a date line. A row's fields are
    # the lines up to the next row or the totals. Known layout quirks, handled below: age and sex reversed
    # ("Male/ 88"); a place or agency name wrapped onto two lines ("Chadds Ford Township," / "PA"); agency and last-known
    # place merged into one line ("Jupiter PD Jupiter, FL"); and an empty recovery cell.
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    starts = [i for i, l in enumerate(lines[:-1])
              if re.fullmatch(r"\d{1,2}\.?", l) and re.fullmatch(r"\d{1,2}/\d{1,2}(/\d{2,4})?", lines[i + 1])]
    for k, i in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else len(lines)
        fields = []
        for l in lines[i + 1: end]:
            # Stop at the totals, the header, or the empty numbered template rows some reports end with ("12.", ".").
            if re.match(r"Total for|\*|Recoveries|Date$|Age/Sex$|Agency$|Info \(last|Recovered$|\d{0,2}\.?$", l):
                break
            # Join a wrapped place name: "Chadds Ford Township," + "PA", or "Unincorporated Dade" + "County, FL".
            # Not "Bal Harbour FL," + "Pompano Beach, FL", where the comma is a typo after a complete place.
            wrapped = fields and ((fields[-1].endswith(",") and not re.search(r"\b[A-Z]{2},$", fields[-1]))
                                  or re.match(r"(County|Airport)\b", l))
            if wrapped:
                fields[-1] += " " + l
            else:
                fields.append(l)
        date, who, rest = fields[0], fields[1] if len(fields) > 1 else "", fields[2:]
        m = re.fullmatch(r"(\d{2,3})\s*/\s*(Male|Female|M|F)", who, re.I)
        r_ = re.fullmatch(r"(Male|Female|M|F)\s*/\s*(\d{2,3})", who, re.I)
        age, sex = (m[1], m[2]) if m else (r_[2], r_[1]) if r_ else (None, None)
        # An agency name wrapped onto two lines ("Naples Police and Emergency" / "Services Department"):
        # the second line has no comma, so it isn't a place.
        while len(rest) > 3 and "," not in rest[1]:
            rest = [rest[0] + " " + rest[1]] + rest[2:]
        if len(rest) == 2:
            merged = re.fullmatch(r"(.*?\b(?:PD|SO|CSO|Office|Department|Patrol|Police))\s+(.+,\s*[A-Za-z]{2,})", rest[0])
            rest = [merged[1], merged[2], rest[1]] if merged else rest + [None]
        cases.append({
            "file": pdf.name,
            "year": year,
            "month": month,
            "row": int(lines[i].rstrip(".")),
            "date": date,
            "age": int(age) if age else None,
            "sex": sex[0].upper() if sex else None,
            "agency": rest[0] if len(rest) > 0 else None,
            "last_known": rest[1] if len(rest) > 1 else None,
            "recovered": rest[2] if len(rest) > 2 else None,
            "extra_fields": " | ".join(rest[3:]) or None,
        })

STATES = {"Alabama": "AL", "Arizona": "AZ", "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Illinois": "IL",
          "Indiana": "IN", "Iowa": "IA", "Kentucky": "KY", "Louisiana": "LA", "Maryland": "MD", "Michigan": "MI",
          "Minnesota": "MN", "Mississippi": "MS", "New Jersey": "NJ", "New York": "NY", "North Carolina": "NC",
          "Ohio": "OH", "Pennsylvania": "PA", "South Carolina": "SC", "Tennessee": "TN", "Texas": "TX",
          "Virginia": "VA", "Washington": "WA"}


def recovery_state(place):
    """Two-letter state for a recovery location; 'not found' for still-active alerts; None if unreadable.

    Reads ", GA"-style codes and full state names ("Morris, Illinois", "Georgia"). A place with no state but a
    Florida county or Florida-only town word is FL. "Washington" alone stays WA but is flagged in spot checks
    (state or D.C.?).
    """
    if not isinstance(place, str) or not place.strip():
        return None
    p = place.replace("*", "").strip().rstrip(",")
    if re.search(r"active|remains missing|unknown", p, re.I):
        return "not found"
    m = re.search(r",\s*([A-Z]{2})\b", p)
    if m:
        return m[1].upper()
    for name, code in STATES.items():
        if re.search(rf"\b{name}\b", p, re.I) and not re.search(r"West Virginia", p, re.I):
            return code
    if re.search(r"County|Dade|Beach|Port|Point|Gardens|Tampa|Ft\.|Punta|Lauderdale|Lucie|Daytona", p):
        return "FL"
    return None


t = pd.DataFrame(totals).sort_values(["year", "month"])
c = pd.DataFrame(cases)
c["recovered_state"] = c.recovered.map(recovery_state)
c["mark"] = c.recovered.fillna("").map(lambda s: "indirect" if "**" in s else "direct" if "*" in s else "")
(ROOT / "interim").mkdir(exist_ok=True)
t.to_csv(ROOT / "interim" / "silver_monthly_totals.csv", index=False)
c.to_csv(ROOT / "interim" / "silver_monthly_cases.csv", index=False)
print(f"{len(t)} reports, {len(c)} case rows")
print(t.drop(columns="file").to_string(index=False))
t["case_rows"] = t.file.map(c.groupby("file").size()).fillna(0).astype(int)
bad = t[t.case_rows != t.alerts_month]
print(f"\nReports where case rows != 'Total for month' ({len(bad)}):")
print(bad[["file", "alerts_month", "case_rows"]].to_string(index=False))
