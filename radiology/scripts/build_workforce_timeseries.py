"""Build data/processed/workforce_timeseries.csv, the tidy long table for the Radiology project.

Columns: year, source, series, value, unit, notes, source_url, verification.

verification values:
  - "parsed"      : computed by a script from a raw file saved in data/raw/
  - "read_pdf"    : read by hand/code from a saved PDF; page given in notes
  - "api"         : returned by an official API; response saved in data/raw/
  - "fetched_page": read from an official web page via WebFetch (not saved)
  - "search_snippet_unverified": seen only in a web-search summary; the primary page
                    was blocked or not fetched. Lead only; do not publish as-is.

Inputs:
  data/processed/nrmp_radiology_match.csv           (scripts/parse_nrmp.py)
  data/raw/imaging/cms_mupphy_provider_type_counts.csv (scripts/cms_radiologist_counts.sh)
  data/raw/bls/bls_api_oews_2025.json               (BLS public API v1)
  ACGME Data Resource Books in data/raw/acgme/      (values hand-entered below with pages)

Run from the repo worktree root:
    python -I -X utf8 projects/radiology/scripts/build_workforce_timeseries.py
"""
import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path("projects/radiology")
OUT = ROOT / "data/processed/workforce_timeseries.csv"
rows = []


def add(year, source, series, value, unit, notes, url, verification):
    rows.append(dict(year=year, source=source, series=series, value=value, unit=unit,
                     notes=notes, source_url=url, verification=verification))


# --- NRMP Main Residency Match (Table 7/7A, all sections summed) -----------------
nrmp = pd.read_csv(ROOT / "data/processed/nrmp_radiology_match.csv")
tot = nrmp[nrmp.section.str.startswith("Total")]
for (yr, sp), g in tot.groupby(["year", "specialty"]):
    if sp == "Radiology-Nuclear Medicine":
        continue
    v = g.set_index("measure").value
    url = g.source_url.iloc[0]
    if v.positions_offered == 0:
        continue
    pages = ",".join(str(int(p)) for p in sorted(nrmp[(nrmp.year == yr) & (nrmp.specialty == sp)
                                                     & ~nrmp.section.str.startswith("Total")].page.unique()))
    note = (f"PGY-1 + PGY-2 + Physician(R) positions; Table 7/7A of {g.source_file.iloc[0]} p.{pages}")
    if yr <= 2011:
        note += "; 2011 edition has no separate Physician (R) section"
    add(yr, "NRMP Main Residency Match", f"{sp}: positions offered", int(v.positions_offered), "positions", note, url, "parsed")
    add(yr, "NRMP Main Residency Match", f"{sp}: positions filled (all applicants)", int(v.filled_all_applicants), "positions", note, url, "parsed")
    add(yr, "NRMP Main Residency Match", f"{sp}: positions filled by U.S. MD seniors", int(v.filled_us_md_seniors), "positions", note, url, "parsed")
    add(yr, "NRMP Main Residency Match", f"{sp}: % filled by U.S. MD seniors",
        round(100 * v.filled_us_md_seniors / v.positions_offered, 1), "percent", note, url, "parsed")
    add(yr, "NRMP Main Residency Match", f"{sp}: % filled (all applicants)",
        round(100 * v.filled_all_applicants / v.positions_offered, 1), "percent", note, url, "parsed")
# DR + IR combined offered (IR integrated split out of DR from 2016)
comb = tot[(tot.measure == "positions_offered") & tot.specialty.isin(
    ["Diagnostic Radiology", "Interventional Radiology (Integrated)"])].groupby("year").value.sum()
for yr, v in comb.items():
    add(yr, "NRMP Main Residency Match", "DR + IR (Integrated): positions offered", int(v), "positions",
        "Sum of Diagnostic Radiology and Interventional Radiology (Integrated); IR integrated first offered 2016",
        "https://www.nrmp.org/match-data/", "parsed")

# 2026 applicants per position (Table 11A, p.78, 2026 edition only)
u26 = "https://www.nrmp.org/wp-content/uploads/2026/05/Main_Match_Results_and_Data-2026.pdf"
add(2026, "NRMP Main Residency Match", "Diagnostic Radiology: positions per U.S. MD senior applicant (top choice)", 1.5,
    "ratio", "Table 11A p.78; 1,268 total positions", u26, "read_pdf")
add(2026, "NRMP Main Residency Match", "Interventional Radiology: positions per U.S. MD senior applicant (top choice)", 1.4,
    "ratio", "Table 11A p.78; 245 total positions", u26, "read_pdf")

# --- ACGME active residents (Data Resource Books) --------------------------------
acg = "https://www.acgme.org/about/publications-and-resources/graduate-medical-education-data-resource-book/"
dr_res = {  # academic year start -> (value, book, page)
    2007: (4427, "2007-2008 DRB", 77), 2008: (4490, "2008-2009 DRB", 78), 2009: (4556, "2009-2010 DRB", 53),
    2010: (4584, "2010-2011 DRB", 64), 2011: (4650, "2015-2016 DRB", 57), 2012: (4652, "2015-2016 DRB", 57),
    2013: (4652, "2015-2016 DRB", 57), 2014: (4676, "2015-2016 DRB", 57), 2015: (4740, "2015-2016 DRB", 57),
    2016: (4769, "2020-2021 DRB", 57), 2017: (4760, "2020-2021 DRB", 57), 2018: (4671, "2020-2021 DRB", 57),
    2019: (4551, "2020-2021 DRB", 57), 2020: (4557, "2024-2025 DRB", 57), 2021: (4567, "2024-2025 DRB", 57),
    2022: (4614, "2024-2025 DRB", 57), 2023: (4698, "2024-2025 DRB", 57), 2024: (4770, "2024-2025 DRB", 57),
}
ir_res = {2016: (13, "2020-2021 DRB", 57), 2017: (60, "2020-2021 DRB", 57), 2018: (246, "2020-2021 DRB", 57),
          2019: (424, "2020-2021 DRB", 57), 2020: (591, "2024-2025 DRB", 57), 2021: (678, "2024-2025 DRB", 57),
          2022: (750, "2024-2025 DRB", 57), 2023: (782, "2024-2025 DRB", 57), 2024: (811, "2024-2025 DRB", 57)}
for yr, (v, book, pg) in dr_res.items():
    add(yr, "ACGME Data Resource Book", "Radiology-diagnostic: active residents", v, "residents",
        f"Academic year {yr}-{yr + 1}; {book} p.{pg}", acg, "read_pdf")
for yr, (v, book, pg) in ir_res.items():
    add(yr, "ACGME Data Resource Book", "Interventional radiology - integrated: active residents", v, "residents",
        f"Academic year {yr}-{yr + 1}; {book} p.{pg}", acg, "read_pdf")
    add(yr, "ACGME Data Resource Book", "DR + IR integrated: active residents", v + dr_res[yr][0], "residents",
        f"Academic year {yr}-{yr + 1}; sum of two rows, {book} p.{pg}", acg, "parsed")

# --- CMS Medicare Physician & Other Practitioners: NPIs by provider type -----------
cms = pd.read_csv(ROOT / "data/raw/imaging/cms_mupphy_provider_type_counts.csv")
for r in cms.itertuples():
    add(r.data_year, "CMS Medicare Physician & Other Practitioners - by Provider",
        f"{r.provider_type}: clinicians billing Medicare Part B", r.found_rows, "NPIs",
        "Rows with Rndrng_Prvdr_Type equal to this value; PUF excludes NPIs with <11 beneficiaries; "
        "Medicare fee-for-service only", r.dataset_api.replace("/stats", ""), "api")
dr_ir = cms[cms.provider_type.isin(["Diagnostic Radiology", "Interventional Radiology"])].groupby("data_year").found_rows.sum()
for yr, v in dr_ir.items():
    add(yr, "CMS Medicare Physician & Other Practitioners - by Provider",
        "Diagnostic + Interventional Radiology: clinicians billing Medicare Part B", int(v), "NPIs",
        "Sum of the two provider types", "https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners", "api")

# --- BLS OEWS 29-1224 Radiologists ----------------------------------------------
api = json.load(open(ROOT / "data/raw/bls/bls_api_oews_2025.json", encoding="utf-8"))
dt = {"01": ("employment", "jobs"), "02": ("employment RSE", "percent"), "04": ("mean annual wage", "USD"),
      "13": ("median annual wage", "USD")}
for s in api["Results"]["series"]:
    code = s["seriesID"][-2:]
    if s["seriesID"][17:23] == "291224" and code in dt and s["data"]:
        d = s["data"][0]
        add(int(d["year"]), "BLS OEWS (national, May)", f"Radiologists (29-1224): {dt[code][0]}", float(d["value"]),
            dt[code][1], f"series {s['seriesID']}; wage-and-salary workers only (excludes self-employed partners)",
            "https://api.bls.gov/publicAPI/v1/timeseries/data/", "api")
for yr, emp, rse, wage in [(2021, 29530, 9.2, 301720), (2022, 29250, 6.3, 329080), (2023, 31960, 5.2, 353960)]:
    u = f"https://www.bls.gov/oes/{yr}/may/oes291224.htm"
    note = "bls.gov returned 403 to our fetch; value from web-search summary of this page. Verify by hand."
    add(yr, "BLS OEWS (national, May)", "Radiologists (29-1224): employment", emp, "jobs", note, u, "search_snippet_unverified")
    add(yr, "BLS OEWS (national, May)", "Radiologists (29-1224): employment RSE", rse, "percent", note, u, "search_snippet_unverified")
    add(yr, "BLS OEWS (national, May)", "Radiologists (29-1224): mean annual wage", wage, "USD", note, u, "search_snippet_unverified")

# --- AAMC Physician Specialty Data Report (secondary, unverified) ------------------
add(2017, "AAMC Physician Specialty Data Report 2018", "Radiology and diagnostic radiology: active physicians", 27719,
    "physicians", "aamc.org downloads sit behind a JavaScript bot challenge; value from web-search summary of the 2018 PSDR. Verify by hand.",
    "https://www.aamc.org/media/35206/download", "search_snippet_unverified")
add(2021, "AAMC Physician Specialty Data Report 2022", "Radiology and diagnostic radiology: active physicians", 27197,
    "physicians", "Reported by Becker's ASC citing the 2022 PSDR; aamc.org blocked. Verify by hand.",
    "https://www.beckersasc.com/asc-news/number-of-active-physicians-by-specialty/", "search_snippet_unverified")

# --- Demand / market context ------------------------------------------------------
add(2023, "Neiman HPI (Christensen et al., JACR Feb 2025)", "Radiologists enrolled to treat Medicare patients", 37482,
    "radiologists", "Baseline of supply projection; reported in press coverage, not read from the paper",
    "https://www.newswise.com/articles/new-studies-shed-light-on-the-future-radiologist-workforce-shortage-by-projecting-future-radiologist-supply-and-demand-for-imaging",
    "search_snippet_unverified")
nw = "https://www.newswise.com/articles/new-studies-shed-light-on-the-future-radiologist-workforce-shortage-by-projecting-future-radiologist-supply-and-demand-for-imaging"
add(2055, "Neiman HPI (Christensen et al., JACR Feb 2025)", "Projected radiologist supply growth 2023-2055 (flat residency)", 25.7,
    "percent", "Press release 2025-02-12", nw, "fetched_page")
add(2055, "Neiman HPI (Christensen et al., JACR Feb 2025)", "Projected imaging utilization growth 2023-2055 (low end)", 16.9,
    "percent", "Press release 2025-02-12; range 16.9-26.9% by modality", nw, "fetched_page")
add(2055, "Neiman HPI (Christensen et al., JACR Feb 2025)", "Projected imaging utilization growth 2023-2055 (high end)", 26.9,
    "percent", "Press release 2025-02-12", nw, "fetched_page")
dox = "https://www.doximity.com/reports/physician-compensation-report/2026"
add(2025, "Doximity Physician Compensation Report 2026", "Radiology: average compensation", 609684, "USD",
    "Self-reported surveys (~23,000 in 2025); 6.6% growth vs 2024, 9th-largest growth", dox, "fetched_page")
add(2025, "Doximity Physician Compensation Report 2026", "Interventional radiology: average compensation", 634658, "USD",
    "10.8% growth, largest of any specialty", dox, "fetched_page")
add(2024, "Doximity Physician Compensation Report 2025", "Radiology: average compensation", 571749, "USD",
    "From AuntMinnie coverage of the 2025 report; 7.5% growth",
    "https://www.auntminnie.com/industry-news/market-analysis/article/15751929/doximity-radiology-makes-top-5-specialties-for-compensation-growth",
    "search_snippet_unverified")

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(sorted(rows, key=lambda r: (r["source"], r["series"], r["year"])))
print(f"wrote {len(rows)} rows to {OUT}")
