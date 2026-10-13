"""Index radiologists against all physicians billing Medicare, 2016 / 2021 / 2024.

Reads data/processed/cms_provider_type_counts.csv (from cms_provider_type_counts.py),
drops non-physician provider types (NON_PHYSICIAN below: nurse practitioners,
physician assistants, therapists, dentists, suppliers, etc.) and compares radiology
(Diagnostic + Interventional Radiology) with the physician total.

"Maxillofacial Surgery" here means its dentist-only surgeons; the ones with an MD or DO
arrive as "Maxillofacial Surgery (MD/DO)" (split in cms_provider_type_counts.py) and count
as physicians.

Renamed types are merged (cardiology and cardiac electrophysiology names changed
after 2016). Types that CMS split out later (e.g. Hospitalist from Internal Medicine)
move people between specialties but not in or out of the physician total.

Output: data/processed/cms_physician_index.csv

Run from the repo worktree root:
    python -I -X utf8 projects/radiology/scripts/cms_physician_index.py
"""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path("projects/radiology")
IN = ROOT / "data/processed/cms_provider_type_counts.csv"
OUT = ROOT / "data/processed/cms_physician_index.csv"
YEARS = (2016, 2021, 2024)
NON_PHYSICIAN = {
    "Nurse Practitioner", "Physician Assistant", "Physical Therapist in Private Practice",
    "Certified Registered Nurse Anesthetist (CRNA)", "Chiropractic", "Optometry",
    "Licensed Clinical Social Worker", "Psychologist, Clinical", "Podiatry",
    "Occupational Therapist in Private Practice", "Audiologist", "Anesthesiology Assistant",
    "Licensed Professional Counselor", "Speech Language Pathologist",
    "Registered Dietitian or Nutrition Professional", "Certified Clinical Nurse Specialist",
    "Certified Nurse Midwife", "Marriage and Family Therapist",
    "Oral Surgery (Dentists only)", "Oral Surgery (Dentist only)", "Maxillofacial Surgery",
    "Dentist", "Prosthodontics", "Oral Medicine", "Periodontics", "Orofacial Pain",
    "Oral and Maxillofacial Pathology", "Oral and Maxillofacial Radiology", "Dental Anesthesiology",
    "Clinical Laboratory", "Clinic or Group Practice", "Mass Immunizer Roster Biller",
    "Ambulance Service Provider", "Independent Diagnostic Testing Facility (IDTF)",
    "Portable X-Ray Supplier", "All Other Suppliers", "Pharmacy", "Slide Preparation Facility",
    "Unknown Supplier/Provider Specialty",
}
RENAMES = {"Cardiovascular Disease (Cardiology)": "Cardiology",
           "Clinical Cardiatric Electrophysiology": "Clinical Cardiac Electrophysiology"}
RADIOLOGY = {"Diagnostic Radiology", "Interventional Radiology"}


def main():
    n = defaultdict(lambda: defaultdict(int))
    srv = defaultdict(lambda: defaultdict(float))
    for r in csv.DictReader(open(IN, encoding="utf-8")):
        t = RENAMES.get(r["provider_type"], r["provider_type"])
        n[t][int(r["year"])] += int(r["individual_npis"])
        srv[t][int(r["year"])] += float(r["tot_srvcs"])
    phys = {t: v for t, v in n.items() if t not in NON_PHYSICIAN}
    phys_srv = {y: sum(srv[t][y] for t in phys) for y in YEARS}
    dr_srv = {y: srv["Diagnostic Radiology"][y] for y in YEARS}
    total = {y: sum(v[y] for v in phys.values()) for y in YEARS}
    allc = {y: sum(v[y] for v in n.values()) for y in YEARS}
    rad = {y: sum(phys[t][y] for t in RADIOLOGY) for y in YEARS}
    dr = {y: phys["Diagnostic Radiology"][y] for y in YEARS}
    pct = lambda d, a, b: round(100 * (d[b] - d[a]) / d[a], 1)
    rows = []
    for label, d in [("all clinicians", allc), ("physicians", total),
                     ("radiology (DR+IR)", rad), ("diagnostic radiology", dr)]:
        rows.append({"group": label, **{str(y): d[y] for y in YEARS},
                     "pct_2016_2024": pct(d, 2016, 2024), "pct_2021_2024": pct(d, 2021, 2024)})
    rows.append({"group": "radiology share of physicians (%)",
                 **{str(y): round(100 * rad[y] / total[y], 2) for y in YEARS},
                 "pct_2016_2024": "", "pct_2021_2024": ""})
    # Workload: Medicare FFS services per billing clinician. FFS volume shrinks as
    # patients move to Medicare Advantage, so compare radiology with physicians, not over time alone.
    per_dr = {y: round(dr_srv[y] / dr[y]) for y in YEARS}
    per_phys = {y: round(phys_srv[y] / total[y]) for y in YEARS}
    for label, d in [("services per diagnostic radiologist", per_dr),
                     ("services per physician", per_phys),
                     ("diagnostic radiology services (total)", {y: round(dr_srv[y]) for y in YEARS})]:
        rows.append({"group": label, **{str(y): d[y] for y in YEARS},
                     "pct_2016_2024": pct(d, 2016, 2024), "pct_2021_2024": pct(d, 2021, 2024)})
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)
    big = sorted(((t, pct(v, 2016, 2024)) for t, v in phys.items() if v[2016] >= 5000),
                 key=lambda x: -x[1])
    for i, (t, p) in enumerate(big, 1):
        print(f"{i:>2}. {t:<45}{phys[t][2016]:>7}{phys[t][2024]:>7}{p:>7}%")


if __name__ == "__main__":
    main()
