"""The 620-week grid: one cell per calendar week, filled if David took a class.

Answers "how do we show that a missed week almost never follows a missed week"
by making adjacency visible — no two empty cells touch, except where they do,
and those are coloured. Serves cards 10 and 25.

Run: python scripts/week_grid.py   ->  charts/week_grid.png
"""

import csv
import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W = 1080
MARGIN = 120
CELL, GAP = 15, 2
ROW_H = 30

INK = (247, 240, 228)
GROUND = (14, 10, 12)
MISSED = (70, 58, 62)
SHUTDOWN = (150, 44, 52)
VARIANT = (196, 120, 60)
BREAK = (255, 196, 92)

COVID_OUT = datetime.date(2020, 3, 5)
COVID_BACK = datetime.date(2021, 6, 5)


def monday(d):
    return d - datetime.timedelta(days=d.weekday())


def font(size, bold=False):
    try:
        return ImageFont.truetype(f"C:/Windows/Fonts/{'arialbd' if bold else 'arial'}.ttf", size)
    except OSError:
        return ImageFont.load_default()


def load():
    days = []
    with open(ROOT / "data" / "processed" / "reservations.csv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["attended"] == "True":
                days.append(datetime.datetime.strptime(row["start_datetime"][:10], "%Y-%m-%d").date())
    days.sort()
    attended = {monday(d) for d in days}
    weeks, cur, last = [], monday(days[0]), monday(days[-1])
    while cur <= last:
        weeks.append((cur, cur in attended))
        cur += datetime.timedelta(days=7)
    return weeks


def classify(weeks):
    """Tag each missed week by the length of the run it belongs to."""
    tags, i = {}, 0
    while i < len(weeks):
        if weeks[i][1]:
            i += 1
            continue
        j = i
        while j < len(weeks) and not weeks[j][1]:
            j += 1
        length = j - i
        for k in range(i, j):
            week = weeks[k][0]
            if length >= 20:
                tags[week] = ("shutdown", length)
            elif length >= 3:
                tags[week] = ("variant", length)
            elif length == 2:
                tags[week] = ("break", length)
            else:
                tags[week] = ("single", length)
        i = j
    return tags


def main():
    weeks = load()
    tags = classify(weeks)
    years = sorted({w.isocalendar()[0] for w, _ in weeks})

    height = 150 + len(years) * ROW_H + 170
    im = Image.new("RGB", (W, height), GROUND)
    d = ImageDraw.Draw(im)

    d.text((MARGIN, 44), "EVERY WEEK, 2014-2026", font=font(30, True), fill=INK)
    d.text((MARGIN, 84), "one square per calendar week  -  filled if he took a class",
           font=font(21), fill=INK + ())

    top = 150
    for r, year in enumerate(years):
        y = top + r * ROW_H
        d.text((MARGIN - 62, y + 1), str(year), font=font(19, True), fill=(180, 172, 162))
        for week, went in weeks:
            iso = week.isocalendar()
            if iso[0] != year:
                continue
            x = MARGIN + (iso[1] - 1) * (CELL + GAP)
            box = (x, y, x + CELL, y + CELL)
            if went:
                d.rectangle(box, fill=INK)
            else:
                kind, _ = tags[week]
                colour = {"shutdown": SHUTDOWN, "variant": VARIANT,
                          "break": BREAK, "single": MISSED}[kind]
                if kind == "single":
                    d.rectangle(box, outline=colour, width=2)
                else:
                    d.rectangle(box, fill=colour)

    legend_y = top + len(years) * ROW_H + 30
    items = [
        (INK, "a week with a class", True),
        (MISSED, "one week missed, on its own  (29 times)", False),
        (BREAK, "two weeks missed in a row  (once: Sep 2024)", True),
        (VARIANT, "the COVID-variant gaps, 2021  (12 weeks, then 3)", True),
        (SHUTDOWN, "the shutdown  (64 weeks)", True),
    ]
    for i, (colour, label, filled) in enumerate(items):
        y = legend_y + i * 27
        box = (MARGIN, y, MARGIN + CELL, y + CELL)
        if filled:
            d.rectangle(box, fill=colour)
        else:
            d.rectangle(box, outline=colour, width=2)
        d.text((MARGIN + CELL + 14, y - 2), label, font=font(19), fill=(214, 206, 196))

    out = ROOT / "charts" / "week_grid.png"
    out.parent.mkdir(exist_ok=True)
    im.save(out)

    pre = sum(1 for w, g in weeks if w < monday(COVID_OUT) and not g)
    post = sum(1 for w, g in weeks if w >= monday(COVID_BACK) and not g)
    print(f"620 weeks; missed: {pre} pre-COVID, {post} post-COVID")
    print("wrote", out)


if __name__ == "__main__":
    main()
