"""What are the FDA's radiology AI devices actually cleared to do?

Groups the 1,230 radiology-panel devices on FDA's AI-enabled device list by their
Primary Product Code. A product code is FDA's own regulatory category for a device
type, with a name and (for newer codes) a legal definition, so the grouping below is
a fixed lookup, not a judgment about each device. Code names and definitions come from
FDA's product classification file (foiclass.txt in
https://www.accessdata.fda.gov/premarket/ftparea/foiclass.zip, downloaded 2026-10-11).

Function groups (CODE_GROUP below):
- scanner: AI inside the imaging hardware or acquisition (CT, MRI, ultrasound, X-ray,
  PET, fluoroscopy, tomosynthesis) - typically reconstruction, denoising, guidance.
- measure: image processing and quantification software (segmentation, measurement).
  LLZ and QIH are broad codes; devices there may also flag findings.
- triage: puts suspected urgent cases higher in the reading queue (QAS, QFM).
- detect: computer-aided detection / diagnosis / referral / risk ("aid" or "assist"
  a clinician in finding or characterizing disease).
- therapy: radiation therapy and ablation planning, positioning.
- other: anything else.

Output: data/processed/fda_device_functions.csv (group, code, code name, devices,
first and latest decision year).

Run from the repo worktree root:
    python -I -X utf8 projects/radiology/scripts/fda_device_functions.py
"""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path("projects/radiology")
DEVICES = ROOT / "data/raw/fda/aiml-devices.csv"
CODES = ROOT / "data/raw/fda/productcode/foiclass.txt"
OUT = ROOT / "data/processed/fda_device_functions.csv"

CODE_GROUP = {
    **dict.fromkeys("IYN JAK LNH KPS OWB IYO KPR NQQ JAA MQB OUO OTE KGI IZL OXO SGH QNK QJU".split(), "scanner"),
    **dict.fromkeys("QIH LLZ QVD PCS QHA".split(), "measure"),
    **dict.fromkeys("QAS QFM".split(), "triage"),
    **dict.fromkeys("MYN QDQ POK OEB QBS QWO SAO SEZ SHE".split(), "detect"),
    **dict.fromkeys("QKB MUJ QTZ IYE LDK".split(), "therapy"),
    **dict.fromkeys("NFJ".split(), "other"),
}


def main():
    names = {r["PRODUCTCODE"]: r["DEVICENAME"]
             for r in csv.DictReader(open(CODES, encoding="latin-1"), delimiter="|")}
    count, years = defaultdict(int), defaultdict(list)
    for r in csv.DictReader(open(DEVICES, encoding="utf-8-sig")):
        if r["Panel (Lead)"] != "Radiology":
            continue
        c = r["Primary Product Code"]
        count[c] += 1
        years[c].append(int(r["Date of Final Decision"][-4:]))
    unmapped = set(count) - set(CODE_GROUP)
    assert not unmapped, f"product codes without a group: {unmapped}"
    rows = sorted(({"group": CODE_GROUP[c], "product_code": c, "code_name": names.get(c, ""),
                    "devices": n, "first_year": min(years[c]), "latest_year": max(years[c])}
                   for c, n in count.items()), key=lambda r: (r["group"], -r["devices"]))
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    total = sum(count.values())
    by_group = defaultdict(int)
    for r in rows:
        by_group[r["group"]] += r["devices"]
    for g, n in sorted(by_group.items(), key=lambda x: -x[1]):
        print(f"{g:<8}{n:>6}{100 * n / total:>7.1f}%")
    print("total", total)


if __name__ == "__main__":
    main()
