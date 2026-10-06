"""Fetch and cache raw HTML for the triple-d project.

Every page is cached under data/raw/cache/ and skipped on rerun, so an
interrupted run resumes where it stopped.

    python scripts/fetch.py lists      # foodiepie list pages: show=all and hide-closed
    python scripts/fetch.py wiki       # Wikipedia episode list
    python scripts/fetch.py details    # one foodiepie detail page per restaurant (needs lists)
"""

import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "cache"
BASE = "https://www.foodiepie.com"
SHOW = "Diners-Drive-Ins-and-Dives"
WIKI_URL = "https://en.wikipedia.org/wiki/List_of_Diners,_Drive-Ins_and_Dives_episodes"
DELAY_S = 1.0
HEADERS = {"User-Agent": "Mozilla/5.0 (content-engine research script)"}

session = requests.Session()
session.headers.update(HEADERS)


def get_cached(url: str, path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(resp.text, encoding="utf-8")
    time.sleep(DELAY_S)
    return resp.text


def page_count(html: str) -> int:
    return max(int(n) for n in re.findall(r"Go to page \d+ of (\d+)", html) or ["1"])


def fetch_lists() -> None:
    # show=all includes closed restaurants; the default view hides them.
    for mode, extra in (("all", "&show=all"), ("open", "")):
        first = get_cached(f"{BASE}/list.php?s={SHOW}{extra}&p=1", CACHE / "list" / mode / "p001.html")
        n = page_count(first)
        for p in range(2, n + 1):
            get_cached(f"{BASE}/list.php?s={SHOW}{extra}&p={p}", CACHE / "list" / mode / f"p{p:03d}.html")
        print(f"list/{mode}: {n} pages cached")


def fetch_wiki() -> None:
    get_cached(WIKI_URL, CACHE / "wiki" / "episodes.html")
    print("wiki: cached")


def fetch_details() -> None:
    slugs = sorted({
        m for f in (CACHE / "list" / "all").glob("p*.html")
        for m in re.findall(r'restaurant\.php\?rst=([^"&]+)"', f.read_text(encoding="utf-8"))
    })
    todo = [s for s in slugs if not (CACHE / "detail" / f"{s}.html").exists()]
    print(f"details: {len(slugs)} restaurants, {len(todo)} to fetch")
    for i, slug in enumerate(todo, 1):
        try:
            get_cached(f"{BASE}/restaurant.php?rst={slug}", CACHE / "detail" / f"{slug}.html")
        except requests.RequestException as e:
            print(f"  FAILED {slug}: {e}")
        if i % 100 == 0:
            print(f"  {i}/{len(todo)}", flush=True)
    print("details: done")


if __name__ == "__main__":
    {"lists": fetch_lists, "wiki": fetch_wiki, "details": fetch_details}[sys.argv[1]]()
