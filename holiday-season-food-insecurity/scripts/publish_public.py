"""Sync everything visitors should see into the public repo (../david-the-data-dude/holiday-season-food-insecurity).

    python projects/thanksgiving-food-insecurity/scripts/publish_public.py      (from the main checkout, after merging)
    python projects/thanksgiving-food-insecurity/scripts/publish_public.py --dry-run   (list what would be copied)

Copies only what is ours to share:
- README.md (from docs/public-README.md, written and fact-checked here), plus the Reel cover once cover.jpg exists.
- data/: BLS prices and pay (cpi_wages.csv), the AFBF dinner table with inflation adjustment (dinner_real.csv),
  USDA's monthly SNAP and WIC counts (snap_wic_monthly.csv), and the U.S. government source files the scripts read
  (ERS trends.xlsx, the FNS Keydata workbook, Census HTOPS / Household Pulse food tables).
- scripts/ (the pipeline behind the Reel's numbers) with requirements.txt, docs/data-challenges.md, and the
  Remotion source and IBM Plex Mono fonts (SIL Open Font License) in video/.

Deliberately NOT copied: Eviction Lab files and evictions_city_year.csv / parse_evictions.py (not in the Reel, and
Eviction Lab sets its own terms), the NY Fed workbooks (fetch_nyfed.py downloads them), the NEADA, NCCP and
Columbia PDFs (third-party reports, linked from the README), docs/the-case.md, spot-checks.md, research/ and
caption-and-first-comment.md (working notes), the per-card ProRes clips (too big for GitHub), public/speaker-*.png
and render-previews.mjs (they show stills of David's frame), CLAUDE.md, NEXT_SESSION.md and .env.

Writing files here publishes nothing; committing and pushing the public repo does.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PUBLIC = ROOT.parents[2] / "david-the-data-dude" / "holiday-season-food-insecurity"

DATA = ["cpi_wages.csv", "dinner_real.csv", "snap_wic_monthly.csv"]
RAW = ["ers/trends.xlsx", "fns/keydata-August-2026.xlsx"]
SCRIPTS = ["fetch_cpi.py", "fetch_low_end.py", "fetch_essentials.py", "dinner_real.py", "parse_keydata.py",
           "fetch_htops.py", "parse_htops.py", "fetch_nyfed.py", "parse_nyfed.py", "publish_public.py"]
VIDEO_FILES = ["package.json", "package-lock.json", "tsconfig.json", "remotion.config.ts", "README.md", "render-cards.mjs",
               "public/fonts/IBMPlexMono-400.woff2", "public/fonts/IBMPlexMono-600.woff2", "public/fonts/IBMPlexMono-700.woff2"]

DRY = "--dry-run" in sys.argv
copied: list[str] = []


def copy(src: Path, dst: Path) -> None:
    if not src.is_file():
        raise FileNotFoundError(src)
    copied.append(str(dst.relative_to(PUBLIC)))
    if not DRY:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main() -> None:
    if not DRY and not (PUBLIC.parent / ".git").exists():
        raise SystemExit(f"{PUBLIC.parent} isn't the public repo; run this from the main checkout")
    copy(ROOT / "docs" / "public-README.md", PUBLIC / "README.md")
    if (ROOT / "cover.jpg").is_file():
        copy(ROOT / "cover.jpg", PUBLIC / "cover.jpg")
    for name in DATA:
        copy(ROOT / "data" / name, PUBLIC / "data" / name)
    for name in RAW:
        copy(ROOT / "data" / "raw" / name, PUBLIC / "data" / "raw" / name)
    for f in sorted((ROOT / "data" / "raw" / "htops").glob("*.xlsx")):
        copy(f, PUBLIC / "data" / "raw" / "htops" / f.name)
    for name in SCRIPTS:
        copy(ROOT / "scripts" / name, PUBLIC / "scripts" / name)
    copy(REPO / "requirements.txt", PUBLIC / "scripts" / "requirements.txt")
    copy(ROOT / "docs" / "data-challenges.md", PUBLIC / "docs" / "data-challenges.md")
    if not DRY and (PUBLIC / "video" / "src").exists():
        shutil.rmtree(PUBLIC / "video" / "src")
    for f in sorted((ROOT / "video" / "src").rglob("*")):
        if f.is_file():
            copy(f, PUBLIC / "video" / "src" / f.relative_to(ROOT / "video" / "src"))
    for name in VIDEO_FILES:
        copy(ROOT / "video" / name, PUBLIC / "video" / name)

    print(("would copy" if DRY else "published") + f" {len(copied)} files to {PUBLIC}:")
    for c in copied:
        print("  " + c)


if __name__ == "__main__":
    main()
