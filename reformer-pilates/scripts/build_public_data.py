"""Build the de-identified Tremble attendance file.

Writes data/public/tremble_attendance.csv. It does NOT publish: copying to
../david-the-data-dude is a separate, confirmed step.

The cut David approved on 2026-10-26, after reviewing every column:
  - no identifiers at all (reservation_id, class_id, user_id)
  - no names (full_name, reserved_for_guest, and the export's full instructor
    names), instructors reduced to FIRST NAME ONLY, which merges the seven
    pairs who share one
  - no Apple Health anything, ever

Run: python scripts/build_public_data.py
"""

import csv
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Globbed rather than named: the export's filename contains the account holder's
# name, and this script is published.
RAW = next((ROOT / "data" / "raw").glob("*Reservation_History*.csv"))
OUT = ROOT / "data" / "public" / "tremble_attendance.csv"

# The three classes after the export date that David confirmed by hand.
CONFIRMED_AFTER_EXPORT = {"2026-10-11", "2026-10-15", "2026-10-22"}

FIELDS = [
    "start_datetime",
    "status",
    "attended",
    "created_at",
    "cancel_date",
    "class_type",
    "spot",
    "location",
    "instructor",
]


def first_name(full: str) -> str:
    """First name only. A two-instructor class keeps both, comma separated."""
    if not full.strip():
        return ""
    return ", ".join(part.strip().split()[0] for part in full.split(",") if part.strip())


def main():
    rows = list(csv.DictReader(open(RAW, encoding="utf-8-sig")))
    OUT.parent.mkdir(parents=True, exist_ok=True)

    out_rows = []
    for r in rows:
        day = r["start_datetime"][:10]
        status = r["status"]
        attended = status == "check in" or (status == "pending" and day in CONFIRMED_AFTER_EXPORT)
        out_rows.append({
            "start_datetime": r["start_datetime"],
            "status": status,
            "attended": "true" if attended else "false",
            "created_at": r["created_at"],
            "cancel_date": r["cancel_date"],
            "class_type": r["class_type"],
            "spot": r["spot"],
            "location": r["location"],
            "instructor": first_name(r["instrutor"]),
        })

    out_rows.sort(key=lambda r: r["start_datetime"])
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out_rows)

    attended = sum(1 for r in out_rows if r["attended"] == "true")
    print(f"wrote {OUT}")
    print(f"  {len(out_rows)} rows, {attended} attended")
    print(f"  columns: {', '.join(FIELDS)}")

    # Prove the cut: nothing identifying survived. The things to look for are
    # taken from the export itself, so this script carries no name or id of its
    # own — it is published, and a hardcoded needle would be the leak.
    text = OUT.read_text(encoding="utf-8")
    leaks = []
    # 'false' is the only value reserved_for_guest ever takes here, and it also
    # appears as a value of the `attended` column we write, so skip booleans.
    BOOLEAN = {"true", "false", "0", "1"}
    for col, what in [("full_name", "account name"), ("user_id", "account id"),
                      ("reserved_for_guest", "guest field"),
                      ("reservation_id", "reservation id"), ("class_id", "class id")]:
        for value in {r[col] for r in rows if r[col]}:
            if len(value) > 3 and value.lower() not in BOOLEAN and value in text:
                leaks.append(f"{what} {value!r}")
    full_names = {p.strip() for r in rows for p in (r["instrutor"] or "").split(",") if len(p.split()) > 1}
    for full in full_names:
        if full in text:
            leaks.append(f"instructor full name {full!r}")
    print(f"  leak check: {'CLEAN' if not leaks else 'FAILED - ' + '; '.join(leaks)}")
    if leaks:
        raise SystemExit("refusing to leave identifying data in the public file")

    merged = collections.defaultdict(set)
    for full in full_names:
        merged[full.split()[0]].add(full)
    pairs = {k: len(v) for k, v in merged.items() if len(v) > 1}
    print(f"  {len(merged)} first names, {len(pairs)} of them merged from 2 people: {', '.join(sorted(pairs))}")

    print("\n--- first 6 rows ---")
    for r in out_rows[:6]:
        print("  " + " | ".join(f"{r[f]}" for f in FIELDS))


if __name__ == "__main__":
    main()
