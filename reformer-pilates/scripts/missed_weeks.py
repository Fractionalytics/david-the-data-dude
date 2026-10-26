"""Missed-week runs, split by era, for cards 10 and 25.

David's claim is that he never missed a week straight after missing the previous
one, outside COVID. This counts the runs so the claim can be stated per era, and
prints the week grid the visual would be built from.

Run: python scripts/missed_weeks.py
"""

import csv
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# David's last class before the shutdown, and his first on returning.
COVID_OUT = datetime.date(2020, 3, 5)
COVID_BACK = datetime.date(2021, 6, 5)


def monday(d):
    return d - datetime.timedelta(days=d.weekday())


def load_weeks():
    days = []
    with open(ROOT / "data" / "processed" / "reservations.csv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["attended"] == "True":
                days.append(datetime.datetime.strptime(row["start_datetime"][:10], "%Y-%m-%d").date())
    days.sort()
    attended = {monday(d) for d in days}
    first, last = monday(days[0]), monday(days[-1])
    weeks, cur = [], first
    while cur <= last:
        weeks.append((cur, cur in attended))
        cur += datetime.timedelta(days=7)
    return weeks, days


def runs_of_misses(weeks):
    runs, start, length = [], None, 0
    for week, went in weeks:
        if not went:
            if length == 0:
                start = week
            length += 1
        elif length:
            runs.append((start, length))
            start, length = None, 0
    if length:
        runs.append((start, length))
    return runs


def era(week):
    if week < monday(COVID_OUT):
        return "pre-COVID"
    if week < monday(COVID_BACK):
        return "the shutdown"
    return "post-COVID"


def main():
    weeks, days = load_weeks()
    print(f"{len(weeks)} calendar weeks, {sum(1 for _, w in weeks if w)} with a class, "
          f"{sum(1 for _, w in weeks if not w)} missed\n")

    for name in ("pre-COVID", "the shutdown", "post-COVID"):
        block = [(w, went) for w, went in weeks if era(w) == name]
        if not block:
            continue
        went = sum(1 for _, g in block if g)
        print(f"{name:<14} {block[0][0]} to {block[-1][0]}: "
              f"{len(block):>3} weeks, {went:>3} with a class ({went/len(block)*100:.0f}%)")

    print()
    all_runs = runs_of_misses(weeks)
    print(f"{len(all_runs)} runs of missed weeks in all\n")

    for name in ("pre-COVID", "the shutdown", "post-COVID"):
        block = [r for r in all_runs if era(r[0]) == name]
        if not block:
            continue
        singles = sum(1 for _, n in block if n == 1)
        multi = [(s, n) for s, n in block if n >= 2]
        print(f"--- {name} ---")
        print(f"  runs of missed weeks: {len(block)}  (single weeks: {singles}, two or more: {len(multi)})")
        for s, n in multi:
            print(f"    {s} : {n} weeks in a row")
        print()

    print("=== the answer to card 25, per era ===")
    for name in ("pre-COVID", "post-COVID"):
        multi = [(s, n) for s, n in all_runs if era(s) == name and n >= 2]
        print(f"  {name}: {len(multi)} time(s) a missed week followed a missed week")

    print("\n=== milestones ===")
    for n in (100, 250, 500, 700, 750, 779):
        if n <= len(days):
            print(f"  class #{n}: {days[n-1]}")

    print("\n=== week grid, one row per year (# = class, . = missed) ===")
    year = None
    line = ""
    for week, went in weeks:
        if week.isocalendar()[0] != year:
            if line:
                print(f"  {year}  {line}")
            year, line = week.isocalendar()[0], ""
        line += "#" if went else "."
    print(f"  {year}  {line}")


if __name__ == "__main__":
    main()
