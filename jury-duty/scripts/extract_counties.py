"""Extract county-level jury data for Oregon (2025) and Florida (calendar 2024), tagged by NCHS 2023 urban-rural code.

Oregon: "2025 Summons Response Rates by County", pages 9-11 of the OJD Jury Data Overview deck (data/raw/or/).
Florida: OSCA Jury Management Indices Report, quarter ending Dec 31, 2024 (data/raw/fl/), one page per county,
  four quarterly values (Jan-Mar ... Oct-Dec 2024) per index.
Urbanicity: NCHS 2023 codes (data/raw/nchs/): 1 large central metro = urban, 2 large fringe metro = suburban,
  3-4 medium/small metro = small metro, 5-6 micropolitan/noncore = rural.

Run from the repo root: python projects/jury-duty/scripts/extract_counties.py
"""
import re
from pathlib import Path

import pandas as pd
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
GROUP = {"1": "urban", "2": "suburban", "3": "small metro", "4": "small metro", "5": "rural", "6": "rural"}

nchs = pd.read_csv(RAW / "nchs" / "NCHSUR2023_3156.csv", dtype=str, encoding="latin-1")
nchs["county"] = nchs.CTYNAME.str.replace(" County", "", regex=False).str.replace("St. ", "St. ", regex=False)
nchs["urbanicity"] = nchs.CODE2023.map(GROUP)


def tag(df, st):
    n = nchs[nchs.ST_ABBREV == st][["county", "CODE2023", "urbanicity", "CTYPOP"]].assign(key=lambda d: d.county.str.lower())
    out = df.assign(key=df.county.str.lower()).merge(n.drop(columns="county"), on="key", how="left").drop(columns="key")
    missing = out[out.CODE2023.isna()].county.tolist()
    assert not missing, f"{st} counties without an NCHS code: {missing}"
    return out


# --- Oregon ---
with pdfplumber.open(RAW / "or" / "oregon_jury_data_overview_2026-04.pdf") as pdf:
    text = "\n".join(pdf.pages[i].extract_text() for i in (8, 9, 10))
num = r"(\d+) \(\d+%\)"
rows = []
for m in re.finditer(rf"^([A-Z][a-z]+(?: [A-Z][a-z]+)?) (\d+) \(100%\) {num} {num} {num} {num}$", text, re.M):
    rows.append(m.groups())
# Multnomah's row wraps across lines in the PDF: the total sits on its own line above the name
m = re.search(rf"^(\d+)\nMultnomah {num} {num} {num} {num}", text, re.M)
rows.append(("Multnomah", m.group(1), *m.groups()[1:]))
oregon = pd.DataFrame(rows, columns=["county", "summoned", "responded_qualified", "disq_deferred_excused",
                                     "no_response", "undeliverable"])
oregon[oregon.columns[1:]] = oregon[oregon.columns[1:]].astype(int)
assert len(oregon) == 36, len(oregon)
assert (oregon.iloc[:, 2:].sum(axis=1) == oregon.summoned).all(), "Oregon parts don't add to total"
oregon = tag(oregon, "OR")
oregon.to_csv(ROOT / "data" / "oregon_counties_2025.csv", index=False)
print(f"Oregon: {len(oregon)} counties, {oregon.summoned.sum():,} summoned (deck says 829,744)")

# --- Florida ---
# Each county page prints its indices in pairs, one line per pair: "<County> 4 values <County> 4 values".
# In page order the pairs are (Summoning Yield, JDPT), (PBI, Percent to Voir Dire), (Average Panel Size, Trials).
PAIRS = [("summoning_yield_pct", "jdpt"), ("pbi", "pct_to_voir_dire"), ("avg_panel", "trials")]
V = r"([\d.]+)%? ([\d.]+)%? ([\d.]+)%? ([\d.]+)%?"
rows = []
with pdfplumber.open(RAW / "fl" / "fl_jury_mgmt_indices_fy2024-25_q2.pdf") as pdf:
    for page in pdf.pages:
        t = page.extract_text() or ""
        head = re.search(r"^Jury Management Indices Report (.+?) County$", t, re.M)  # Madison's page starts with chart debris
        if not head:
            continue  # circuit summary pages
        county = head.group(1).strip()
        c = re.escape(county)
        lines = re.findall(rf"^{c} {V} {c} {V}$", t, re.M)
        assert len(lines) == 3, (county, len(lines))
        rec = {"county": county}
        for (left, right), vals in zip(PAIRS, lines):
            nums = [float(v) for v in vals]
            rec[left], rec[right] = nums[:4], nums[4:]
        rows.append(rec)
fl = pd.DataFrame(rows)
florida = pd.DataFrame({"county": fl.county})
for col in ["summoning_yield_pct", "pct_to_voir_dire", "jdpt", "avg_panel"]:
    # mean of the 2024 quarters that had activity (small counties report 0.0 for quarters with no trials)
    florida[col] = fl[col].map(lambda v: round(sum(x for x in v if x) / max(1, sum(1 for x in v if x)), 1))
florida["trials_2024"] = fl["trials"].map(sum).astype(int)
florida = tag(florida, "FL")
florida.to_csv(ROOT / "data" / "florida_counties_2024.csv", index=False)
print(f"Florida: {len(florida)} counties; missing values per column:\n{florida.isna().sum().to_string()}")
