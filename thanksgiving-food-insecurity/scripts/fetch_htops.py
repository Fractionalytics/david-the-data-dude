"""Download the Census HTOPS (2026) and HPS (2022 week 49) tables used in
docs/research/federal-surveys.md into data/raw/htops/.

Run: python -I scripts/fetch_htops.py
"""
import pathlib
import time
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent.parent
OUT = HERE / "data" / "raw" / "htops"
UA = "content-engine-research-bot/1.0 (research bot; data journalism; low-volume downloads)"
B = "https://www2.census.gov/programs-surveys/demo/tables/hhp"

FILES = {}
for c in ("2609", "2607", "2603"):
    for t in ("spending1", "food1"):
        FILES[f"{c}_{t}.xlsx"] = f"{B}/2026/{c}/{t}.xlsx"
for t in ("spending1", "food1", "food2"):
    FILES[f"2022wk49_{t}.xlsx"] = f"{B}/2022/wk49/{t}_week49.xlsx"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, url in FILES.items():
        dest = OUT / name
        if dest.exists():
            print("have", name)
            continue
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            dest.write_bytes(r.read())
            print(r.status, name, url)
        time.sleep(2)


if __name__ == "__main__":
    main()
