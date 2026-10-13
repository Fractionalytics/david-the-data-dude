"""Control the radiologist counts for an aging population and for Medicare demand.

Inputs (all saved in data/raw/ or data/processed/):
- Census national population by single year of age (SEX=0 rows; AGE 85 = 85+, AGE 999 = total):
  census/nc-est2020-agesex-res.csv (2010-2020) and census/nc-est2024-agesex-res.csv (2020-2024),
  from https://www2.census.gov/programs-surveys/popest/datasets/{2010-2020,2020-2024}/national/asrh/
- CMS Medicare Monthly Enrollment, national annual rows (ORGNL_MDCR_BENES = traditional
  fee-for-service enrollees): cms_enrollment/national_annual.json, from
  https://data.cms.gov/data-api/v1/dataset/d7fabe1e-d19b-4333-9eff-e80e0643f2fd/data
- data/processed/cms_provider_type_counts.csv and the physician split in cms_physician_index.py.

Output: data/processed/demand_controls.csv

Run from the repo worktree root:
    python -I -X utf8 projects/radiology/scripts/demand_controls.py
"""
import csv
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path("projects/radiology")
RAW = ROOT / "data/raw"
OUT = ROOT / "data/processed/demand_controls.csv"
YEARS = (2016, 2021, 2024)

spec = importlib.util.spec_from_file_location("idx", ROOT / "scripts/cms_physician_index.py")
idx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(idx)


def census_65plus():
    pop65, total = {}, {}
    for fname in ("nc-est2020-agesex-res.csv", "nc-est2024-agesex-res.csv"):
        for r in csv.DictReader(open(RAW / "census" / fname, encoding="utf-8")):
            if r["SEX"] != "0":
                continue
            age = int(r["AGE"])
            for y in YEARS:
                col = f"POPESTIMATE{y}"
                if col in r:
                    if age == 999:
                        total[y] = int(r[col])
                    elif age >= 65:
                        pop65[y] = pop65.get(y, 0) + int(r[col])
    return pop65, total


def main():
    pop65, total = census_65plus()
    enroll = {int(r["YEAR"]): int(r["ORGNL_MDCR_BENES"])
              for r in json.load(open(RAW / "cms_enrollment/national_annual.json", encoding="utf-8"))}
    n, srv = defaultdict(lambda: defaultdict(int)), defaultdict(lambda: defaultdict(float))
    for r in csv.DictReader(open(ROOT / "data/processed/cms_provider_type_counts.csv", encoding="utf-8")):
        t = idx.RENAMES.get(r["provider_type"], r["provider_type"])
        if t in idx.NON_PHYSICIAN:
            continue
        n[t][int(r["year"])] += int(r["individual_npis"])
        srv[t][int(r["year"])] += float(r["tot_srvcs"])
    phys = {y: sum(v[y] for v in n.values()) for y in YEARS}
    rad = {y: n["Diagnostic Radiology"][y] + n["Interventional Radiology"][y] for y in YEARS}
    phys_srv = {y: sum(v[y] for v in srv.values()) for y in YEARS}
    dr_srv = {y: srv["Diagnostic Radiology"][y] for y in YEARS}

    series = {
        "US population (Census)": total,
        "US population 65+ (Census)": pop65,
        "traditional Medicare enrollees (CMS)": enroll,
        "radiologists (DR+IR) per 100k people 65+": {y: rad[y] / pop65[y] * 1e5 for y in YEARS},
        "physicians per 100k people 65+": {y: phys[y] / pop65[y] * 1e5 for y in YEARS},
        "radiologists (DR+IR) per 100k people": {y: rad[y] / total[y] * 1e5 for y in YEARS},
        "physicians per 100k people": {y: phys[y] / total[y] * 1e5 for y in YEARS},
        "diagnostic radiology services per traditional Medicare enrollee": {y: dr_srv[y] / enroll[y] for y in YEARS},
        "all physician services per traditional Medicare enrollee": {y: phys_srv[y] / enroll[y] for y in YEARS},
    }
    rows = []
    for name, d in series.items():
        rows.append({"series": name, **{str(y): round(d[y], 2) for y in YEARS},
                     "pct_2016_2024": round(100 * (d[2024] - d[2016]) / d[2016], 1)})
        print(rows[-1])
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
