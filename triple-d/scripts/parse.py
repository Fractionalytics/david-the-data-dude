"""Parse cached HTML into tidy CSVs under data/interim/.

    python scripts/parse.py

Outputs:
    wiki_appearances.csv      one row per (episode, restaurant) from Wikipedia
    foodiepie_restaurants.csv one row per foodiepie restaurant, with open/closed and detail-page fields
    foodiepie_episodes.csv    one row per (restaurant, episode title) from foodiepie
"""

import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "cache"
OUT = ROOT / "data" / "interim"


def clean(text: str) -> str:
    text = re.sub(r"\[\s*[\w\s]+\s*\]", "", text)  # footnote markers like [ 26 ]
    return re.sub(r"\s+", " ", text).strip()


def parse_date(text: str):
    for fmt in ("%B %d, %Y", "%b %d, %Y"):  # Wikipedia mixes "February 16" and "Feb 16"
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def expand_rowspans(table) -> list[list]:
    """Return the table body as a full grid, copying rowspan cells down."""
    grid, carry = [], {}  # carry: col index -> [remaining rows, cell]
    for tr in table.find_all("tr")[1:]:
        cells, row, col = tr.find_all(["td", "th"]), [], 0
        it = iter(cells)
        while True:
            if col in carry:
                left, cell = carry[col]
                row.append(cell)
                carry[col][0] -= 1
                if carry[col][0] == 0:
                    del carry[col]
                col += 1
                continue
            cell = next(it, None)
            if cell is None:
                break
            span = int(cell.get("rowspan", 1))
            if span > 1:
                carry[col] = [span - 1, cell]
            row.append(cell)
            col += 1
        grid.append(row)
    return grid


def parse_wiki() -> pd.DataFrame:
    soup = BeautifulSoup((CACHE / "wiki" / "episodes.html").read_text(encoding="utf-8"), "html.parser")
    rows = []
    for table in soup.select("table.wikitable")[1:]:  # [0] is the series overview
        heading = table.find_previous(["h2", "h3"]).get_text(strip=True)
        season = int(re.match(r"Season (\d+)", heading).group(1))
        for cells in expand_rowspans(table):
            if len(cells) < 6:
                continue
            total, ep, title, rest, loc, date = (clean(c.get_text(" ", strip=True)) for c in cells[:6])
            if not rest:
                continue
            closed = bool(re.search(r"\(closed\)", rest, re.I))
            air = parse_date(re.sub(r"\(.*?\)", "", date).strip())
            rows.append({
                "season": season,
                "episode_overall": total,
                "episode_in_season": ep,
                "episode_title": title.strip('"'),
                "restaurant": re.sub(r"\s*\(closed\)\s*", " ", rest, flags=re.I).strip(),
                "location": loc,
                "air_date": air,
                "wiki_closed": closed,
            })
    return pd.DataFrame(rows)


def parse_list_pages(mode: str) -> list[dict]:
    rows = []
    for f in sorted((CACHE / "list" / mode).glob("p*.html")):
        soup = BeautifulSoup(f.read_text(encoding="utf-8"), "html.parser")
        for tr in soup.select("tr[id^=check_]"):
            link = tr.select_one('.media-body a[href*="restaurant.php"]')
            tds = tr.find_all("td", recursive=False)
            episodes = list(dict.fromkeys(
                clean(a.get_text()).strip('"') for a in tr.select('a[href*="list.php?e="]')
            ))
            rows.append({
                "slug": link["href"].split("rst=")[1],
                "name": clean(link.get_text()),
                "city": clean(tr.select_one('a[href*="list.php?c="]').get_text()) if tr.select_one('a[href*="list.php?c="]') else None,
                "state": clean(tr.select_one('a[href*="list.php?state="]').get_text()) if tr.select_one('a[href*="list.php?state="]') else None,
                "dishes": clean(tds[1].get_text(" | ", strip=True)) if len(tds) > 1 else None,
                "notes": clean(tds[-1].get_text(" ", strip=True)),
                "episodes": episodes,
            })
    return rows


def parse_detail(slug: str) -> dict:
    f = CACHE / "detail" / f"{slug}.html"
    if not f.exists():
        return {"yelp_categories": None, "price": None}
    soup = BeautifulSoup(f.read_text(encoding="utf-8"), "html.parser")
    text = soup.get_text("\n", strip=True)
    # Line like "$ - Food Trucks, Polish" or "$$ - Diners, Burgers"
    m = re.search(r"^(\${1,4}) - (.+)$", text, re.M)
    return {"price": m.group(1) if m else None, "yelp_categories": m.group(2).strip() if m else None}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    wiki = parse_wiki()
    wiki.to_csv(OUT / "wiki_appearances.csv", index=False)
    print(f"wiki: {len(wiki)} appearances, seasons {wiki.season.min()}-{wiki.season.max()}")

    all_rows = parse_list_pages("all")
    open_slugs = {r["slug"] for r in parse_list_pages("open")}
    fp = pd.DataFrame(all_rows).drop_duplicates("slug")
    fp["open_on_foodiepie"] = fp.slug.isin(open_slugs)
    details = pd.DataFrame([{"slug": s, **parse_detail(s)} for s in fp.slug])
    fp = fp.merge(details, on="slug", how="left")

    eps = fp[["slug", "episodes"]].explode("episodes").rename(columns={"episodes": "episode_title"})
    eps.to_csv(OUT / "foodiepie_episodes.csv", index=False)
    fp.drop(columns="episodes").to_csv(OUT / "foodiepie_restaurants.csv", index=False)
    print(f"foodiepie: {len(fp)} restaurants ({fp.open_on_foodiepie.sum()} open), "
          f"{fp.yelp_categories.notna().sum()} with categories, {len(eps)} restaurant-episode rows")


if __name__ == "__main__":
    main()
