"""Count clinicians billing Medicare Part B by provider type, from CMS's bulk files.

Reads the "Medicare Physician & Other Practitioners - by Provider" CSVs for 2016,
2021 and 2024 (one row per NPI; saved in the gitignored data/raw/cache/cms_by_provider/,
download URLs in DOWNLOADS below) and writes per provider type: number of individual
NPIs (Rndrng_Prvdr_Ent_Cd == "I"), their total services and total beneficiaries.

Limits: traditional (fee-for-service) Medicare only; CMS drops NPIs with fewer than
11 beneficiaries; provider type is the specialty on the claims, not board certification.

Output: data/processed/cms_provider_type_counts.csv

Run from the repo worktree root:
    python -I -X utf8 projects/radiology/scripts/cms_provider_type_counts.py
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path("projects/radiology")
CACHE = ROOT / "data/raw/cache/cms_by_provider"
OUT = ROOT / "data/processed/cms_provider_type_counts.csv"
DOWNLOADS = {
    2016: "https://data.cms.gov/sites/default/files/2025-11/e4cd28e1-2d05-4f33-b232-f32b5bebc153/MUP_PHY_R25_P05_V20_D16_Prov.csv",
    2021: "https://data.cms.gov/sites/default/files/2025-11/fc6ea9aa-12f0-4c2f-9909-6c8e06c961cf/MUP_PHY_R25_P07_V20_D21_Prov.csv",
    2024: "https://data.cms.gov/sites/default/files/2026-05/7323ba02-52e7-4a86-b2ce-ad210c25d9aa/MUP_PHY_R26_P05_V10_D24_Prov.csv",
}


MD_DO = re.compile(r"\b(M\.?D|D\.?O)\b")


def num(x):
    try:
        return float(x)
    except ValueError:
        return 0.0


def main():
    rows = []
    for year, url in DOWNLOADS.items():
        npis, srvcs, benes = defaultdict(int), defaultdict(float), defaultdict(float)
        with open(CACHE / f"{year}.csv", encoding="latin-1", newline="") as f:
            for r in csv.DictReader(f):
                if r["Rndrng_Prvdr_Ent_Cd"] != "I":
                    continue
                t = r["Rndrng_Prvdr_Type"].strip()
                # Oral & maxillofacial surgery is a dental specialty; only some of its surgeons
                # also hold a medical degree. Split out the MD/DO ones so cms_physician_index.py
                # can count them as physicians (David's call, 2026-10-12).
                if t == "Maxillofacial Surgery" and MD_DO.search(r["Rndrng_Prvdr_Crdntls"].upper()):
                    t = "Maxillofacial Surgery (MD/DO)"
                npis[t] += 1
                srvcs[t] += num(r["Tot_Srvcs"])
                benes[t] += num(r["Tot_Benes"])
        for t in npis:
            rows.append({"year": year, "provider_type": t, "individual_npis": npis[t],
                         "tot_srvcs": round(srvcs[t]), "tot_benes": round(benes[t]), "source_url": url})
        print(year, len(npis), "types", sum(npis.values()), "individual NPIs")
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
