"""Did 2026's shorter book-ahead times come from replacing cancelled classes?

David's hypothesis (2026-10-25): his median lead time dipped in 2026 because he
cancelled more classes and rebooked replacements at short notice. If that is
right, 2026 should show a higher cancellation rate AND a distribution that has
grown a short-lead tail, rather than one that slid down as a whole.

Run: python scripts/replacement_bookings.py
"""

import csv
import datetime
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load():
    out = []
    with open(ROOT / "data" / "processed" / "reservations.csv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if not row["created_at"]:
                continue
            made = datetime.datetime.strptime(row["created_at"][:10], "%Y-%m-%d").date()
            if made < datetime.date(2022, 1, 1):
                continue
            lead = None
            if row["booked_days_ahead"]:
                try:
                    lead = float(row["booked_days_ahead"])
                except ValueError:
                    pass
            cancelled = None
            if row["cancel_date"]:
                try:
                    cancelled = datetime.datetime.strptime(row["cancel_date"][:10], "%Y-%m-%d").date()
                except ValueError:
                    pass
            out.append({
                "made": made,
                "lead": lead,
                "status": row["status"].lower(),
                "cancelled": cancelled,
            })
    out.sort(key=lambda r: r["made"])
    return out


def main():
    rows = load()
    years = sorted({r["made"].year for r in rows})

    print("=" * 74)
    print("1. Cancellation rate by year of booking")
    print("=" * 74)
    print(f"{'year':<6}{'bookings':>10}{'cancelled':>11}{'rate':>8}")
    for y in years:
        block = [r for r in rows if r["made"].year == y]
        cancels = [r for r in block if "cancel" in r["status"]]
        print(f"{y:<6}{len(block):>10}{len(cancels):>11}{len(cancels)/len(block)*100:>7.0f}%")

    print("\n" + "=" * 74)
    print("2. Where the lead times sit, by year")
    print("=" * 74)
    bands = [("<7d", 0, 7), ("7-20d", 7, 21), ("21-27d", 21, 28), ("28d+", 28, 999)]
    print(f"{'year':<6}{'n':>5}" + "".join(f"{name:>9}" for name, _, _ in bands) + f"{'median':>9}")
    for y in years:
        v = [r["lead"] for r in rows if r["made"].year == y and r["lead"] is not None]
        if not v:
            continue
        cells = "".join(
            f"{sum(1 for x in v if lo <= x < hi) / len(v) * 100:>8.0f}%" for _, lo, hi in bands
        )
        print(f"{y:<6}{len(v):>5}{cells}{statistics.median(v):>9.1f}")

    print("\n" + "=" * 74)
    print("3. Bookings made soon after a cancellation ('replacements')")
    print("=" * 74)
    cancel_days = sorted({r["cancelled"] for r in rows if r["cancelled"]})

    def after_cancel(made, window=3):
        return any(0 <= (made - c).days <= window for c in cancel_days)

    print(f"{'year':<6}{'replacement n':>15}{'median':>9}{'  |':>4}{'other n':>9}{'median':>9}")
    for y in years:
        block = [r for r in rows if r["made"].year == y and r["lead"] is not None]
        rep = [r["lead"] for r in block if after_cancel(r["made"])]
        oth = [r["lead"] for r in block if not after_cancel(r["made"])]
        if not rep or not oth:
            continue
        print(f"{y:<6}{len(rep):>15}{statistics.median(rep):>9.1f}{'  |':>4}"
              f"{len(oth):>9}{statistics.median(oth):>9.1f}")

    allrep = [r["lead"] for r in rows if r["lead"] is not None and after_cancel(r["made"])]
    alloth = [r["lead"] for r in rows if r["lead"] is not None and not after_cancel(r["made"])]
    print(f"\nall years: replacement median {statistics.median(allrep):.1f} (n={len(allrep)}), "
          f"other median {statistics.median(alloth):.1f} (n={len(alloth)})")


if __name__ == "__main__":
    main()
