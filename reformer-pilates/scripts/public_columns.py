"""Show every column in the Tremble export, so David can rule on what ships.

Nothing is written. This prints the raw columns with samples, then the proposed
public schema, so the cut is reviewed before it is made rather than after.

Run: python scripts/public_columns.py
"""

import csv
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = next((ROOT / "data" / "raw").glob("*Reservation_History*.csv"))

# Columns that must not ship, and why.
DROP = {
    "full_name": "David's name, on every row",
    "user_id": "account identifier",
    "reserved_for_guest": "guest's name where present",
    "instrutor": "instructors' FULL names (sic: misspelled in the export)",
    "reservation_id": "identifier",
    "class_id": "identifier",
    "updated_at": "no analytical use; a bare timestamp",
    "reservation_type": "constant 'standard' in every row",
}

KEEP = {
    "status": "check in / cancel / penalty cancel / pending",
    "start_datetime": "when the class ran",
    "created_at": "when it was booked - the whole booking-ahead story",
    "cancel_date": "when it was cancelled, where it was",
    "class_type": "the product name as Tremble labelled it over the years",
    "custom_name": "the class name variant",
    "spot": "machine number",
    "location": "which studio",
}

ADD = {
    "instructor": "FIRST NAME ONLY, derived from the dropped full name",
}


def main():
    rows = list(csv.DictReader(open(RAW, encoding="utf-8-sig")))
    cols = list(rows[0].keys())
    print(f"{RAW.name}: {len(rows)} rows, {len(cols)} columns\n")

    print("=" * 78)
    print("EVERY COLUMN IN THE RAW EXPORT")
    print("=" * 78)
    for c in cols:
        vals = [r[c] for r in rows if r[c] not in ("", None)]
        distinct = len(set(vals))
        sample = list(dict.fromkeys(vals))[:3]
        verdict = "DROP" if c in DROP else "keep"
        why = DROP.get(c, KEEP.get(c, ""))
        print(f"\n  {c}   [{verdict}]  {len(vals)} filled, {distinct} distinct")
        if why:
            print(f"    {why}")
        for s in sample:
            print(f"    e.g. {s[:70]}")

    print("\n" + "=" * 78)
    print("PROPOSED PUBLIC SCHEMA")
    print("=" * 78)
    for c, why in {**KEEP, **ADD}.items():
        print(f"  {c:<16} {why}")

    print("\n" + "=" * 78)
    print("THE FIRST-NAME COLLISION")
    print("=" * 78)
    first = collections.defaultdict(set)
    for r in rows:
        full = (r.get("instrutor") or "").strip()
        if not full:
            continue
        for name in full.split(","):
            name = name.strip()
            if name:
                first[name.split()[0]].add(name)
    clashes = {k: v for k, v in first.items() if len(v) > 1}
    print(f"{len(first)} distinct first names across the instructors.")
    if clashes:
        print(f"{len(clashes)} of them belong to more than one person:\n")
        for k, v in sorted(clashes.items()):
            counts = []
            for full in sorted(v):
                n = sum(1 for r in rows if full in (r.get("instrutor") or ""))
                counts.append(f"{n} classes")
            print(f"  {k}: {len(v)} people ({', '.join(counts)})")
        print("\nFirst-names-only merges each of these into one person in the public data.")
    else:
        print("No collisions.")


if __name__ == "__main__":
    main()
