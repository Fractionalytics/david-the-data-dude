"""Parse NRMP Main Residency Match "Results and Data" PDFs for radiology rows.

Reads Table 7 / 7A ("Positions Offered and Number Filled by U.S. [MD] Seniors and
All Applicants", five years per edition) from four editions saved in
data/raw/nrmp/: 2011 (covers 2007-2011), 2016 (2012-2016), 2021 (2017-2021) and
2026 (2022-2026). Each row gives, per year: positions offered, filled by U.S. MD
seniors, filled by all applicants.

Sections: PGY-1 (categorical, start in intern year), PGY-2 (advanced, start after
a separate prelim year) and Physician (R) positions (PGY-2 seats reserved for
applicants with prior GME; broken out from 2013 on, absent from the 2011 edition).

Output: data/processed/nrmp_radiology_match.csv (long format, one row per
year x specialty x section x measure) plus a "Total" section summing all three.

Run from the repo worktree root:
    python -I -X utf8 projects/radiology/scripts/parse_nrmp.py
"""
import csv
import re
from pathlib import Path

import pdfplumber

ROOT = Path("projects/radiology")
RAW = ROOT / "data/raw/nrmp"
OUT = ROOT / "data/processed/nrmp_radiology_match.csv"

# edition file -> (1-based pages holding Table 7/7A, years in column order, url)
EDITIONS = {
    "resultsanddata2011.pdf": ([23], [2011, 2010, 2009, 2008, 2007],
        "https://www.nrmp.org/wp-content/uploads/2021/07/resultsanddata2011.pdf"),
    "Main-Match-Results-and-Data-2016.pdf": ([30, 31], [2016, 2015, 2014, 2013, 2012],
        "https://www.nrmp.org/wp-content/uploads/2021/07/Main-Match-Results-and-Data-2016.pdf"),
    "MRM-Results_and-Data_2021_revised.pdf": ([28, 29], [2021, 2020, 2019, 2018, 2017],
        "https://www.nrmp.org/wp-content/uploads/2022/11/MRM-Results_and-Data_2021_revised.pdf"),
    "Main_Match_Results_and_Data-2026.pdf": ([44, 45], [2026, 2025, 2024, 2023, 2022],
        "https://www.nrmp.org/wp-content/uploads/2026/05/Main_Match_Results_and_Data-2026.pdf"),
}
SPECIALTIES = {
    "Radiology-Diagnostic": "Diagnostic Radiology",
    "Interventional Radiology (Integrated)": "Interventional Radiology (Integrated)",
    "Radiology-Nuclear Med": "Radiology-Nuclear Medicine",
}
MEASURES = ["positions_offered", "filled_us_md_seniors", "filled_all_applicants"]


SECTIONS = ["PGY-1", "PGY-2", "Physician (R)"]


def main():
    rows = []
    for fname, (pages, years, url) in EDITIONS.items():
        pdf = pdfplumber.open(RAW / fname)
        for k, pg in enumerate(pages):
            # pdfplumber's text order does not always put a section header before
            # its rows, so assign sections by order: page k starts in section k,
            # and a specialty seen again on the same page means the next section.
            sec_i, seen = k, set()
            for line in pdf.pages[pg - 1].extract_text().split("\n"):
                # some rows start with private-use glyphs (e.g. U+F087), not spaces
                line = re.sub(r"^[\s-]+", "", line)
                for label, name in SPECIALTIES.items():
                    if line.startswith(label):
                        if name in seen:
                            sec_i, seen = sec_i + 1, set()
                        seen.add(name)
                        section = SECTIONS[sec_i]
                        nums = re.findall(r"\d[\d,]*", line.strip()[len(label):])
                        nums = [int(n.replace(",", "")) for n in nums]
                        assert len(nums) == 15, (fname, pg, line)
                        for i, yr in enumerate(years):
                            for j, m in enumerate(MEASURES):
                                rows.append(dict(year=yr, specialty=name, section=section,
                                                 measure=m, value=nums[i * 3 + j],
                                                 source_file=fname, page=pg, source_url=url))
    # Totals across sections
    tot = {}
    for r in rows:
        k = (r["year"], r["specialty"], r["measure"])
        t = tot.setdefault(k, dict(r, section="Total (PGY-1 + PGY-2 + R)", value=0, page=""))
        t["value"] += r["value"]
    rows += list(tot.values())
    rows.sort(key=lambda r: (r["specialty"], r["section"], r["measure"], r["year"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
