"""Pick spot-check candidates from the CMS by-provider files (2016, 2024).

Prints, for David to verify by hand (docs/spot-checks.md):
- a diagnostic radiologist billing in both years (identity across years),
- a clinician whose provider type changed between radiology types (2016 DR -> 2024 IR),
- the highest-volume diagnostic radiologist in 2024 (outlier check),
- a median-volume diagnostic radiologist in 2024,
- credentials found under types we dropped or kept as physicians (Maxillofacial Surgery,
  Undefined Physician type) to test the physician / non-physician split.

Individual NPIs are public CMS data but stay in this private repo; never publish them.

Run from the repo worktree root:
    python -I -X utf8 projects/radiology/scripts/spot_check_candidates.py
"""
import csv
import statistics
from collections import Counter
from pathlib import Path

CACHE = Path("projects/radiology/data/raw/cache/cms_by_provider")
RAD = {"Diagnostic Radiology", "Interventional Radiology"}
CHECK_TYPES = {"Maxillofacial Surgery", "Undefined Physician type"}


def load(year):
    rad, creds = {}, {t: Counter() for t in CHECK_TYPES}
    with open(CACHE / f"{year}.csv", encoding="latin-1", newline="") as f:
        for r in csv.DictReader(f):
            if r["Rndrng_Prvdr_Ent_Cd"] != "I":
                continue
            t = r["Rndrng_Prvdr_Type"].strip()
            if t in RAD:
                rad[r["Rndrng_NPI"]] = (t, float(r["Tot_Srvcs"] or 0), r["Rndrng_Prvdr_State_Abrvtn"],
                                        r["Rndrng_Prvdr_Crdntls"])
            if t in CHECK_TYPES:
                creds[t][r["Rndrng_Prvdr_Crdntls"].upper().replace(".", "").strip()] += 1
    return rad, creds


def main():
    r16, c16 = load(2016)
    r24, c24 = load(2024)
    both = sorted(n for n in r16 if n in r24 and r16[n][0] == r24[n][0] == "Diagnostic Radiology")
    switched = sorted(n for n in r16 if n in r24 and r16[n][0] == "Diagnostic Radiology"
                      and r24[n][0] == "Interventional Radiology")
    dr24 = sorted(((v[1], n) for n, v in r24.items() if v[0] == "Diagnostic Radiology"))
    med = dr24[len(dr24) // 2]
    print("DR in both years:", len(both), "example", both[len(both) // 3], r16[both[len(both) // 3]], r24[both[len(both) // 3]])
    print("DR (2016) -> IR (2024):", len(switched), "example", switched[0] if switched else None,
          r16.get(switched[0]) if switched else None, r24.get(switched[0]) if switched else None)
    print("Top-volume DR 2024:", dr24[-1][1], r24[dr24[-1][1]])
    print("Median-volume DR 2024:", med[1], r24[med[1]], "median services", statistics.median(v for v, _ in dr24))
    print("Radiology NPIs only in 2016:", sum(1 for n in r16 if n not in r24), "only in 2024:", sum(1 for n in r24 if n not in r16))
    for t in CHECK_TYPES:
        print(t, "credentials 2024:", c24[t].most_common(6))


if __name__ == "__main__":
    main()
