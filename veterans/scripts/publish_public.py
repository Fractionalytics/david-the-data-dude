"""Sync everything visitors should see into the public repo (../david-the-data-dude/veterans).

    python projects/veterans/scripts/publish_public.py      (from the main checkout, after merging)
    python projects/veterans/scripts/publish_public.py --dry-run   (list what would be copied)

Copies only what is ours to share:
- README.md (from docs/public-README.md, written and fact-checked here) and the Reel cover.
- data/: the VetPop2023 FY2026 tables, the Census 2024 shares and metro counts, the VA-vs-Census comparison,
  and DoD retirees by rank.
- scripts/ (the pipeline) with requirements.txt, docs/data-challenges.md, and the Remotion source in video/.

Deliberately NOT copied: data/raw (VA, Census, BLS, DoD and Pew files, plus the CVN and DoD PDFs; all public,
linked from the README or fetched by fetch_sources.py), docs/findings.md, sources.md, script-check.md and
caption-and-first-comment.md (working notes), visual-options.html, the per-card ProRes clips (too big for GitHub),
the preview and public/mock-bg.png (they show a still of David's frame), CLAUDE.md, NEXT_SESSION.md and .env.

Writing files here publishes nothing; committing and pushing the public repo does.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PUBLIC = ROOT.parents[2] / "david-the-data-dude" / "veterans"

SCRIPTS = ["fetch_sources.py", "vetpop_tables.py", "acs_geo.py", "metro_rates.py", "pums_veterans.py",
           "pums_shares.py", "va_vs_census.py", "pdf_grep.py", "pdf_page.py", "publish_public.py"]
VIDEO_FILES = ["package.json", "package-lock.json", "tsconfig.json", "remotion.config.ts", "README.md", "render-cards.mjs"]

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
    copy(ROOT / "cover.jpg", PUBLIC / "cover.jpg")
    for f in sorted((ROOT / "data").glob("*.csv")):
        copy(f, PUBLIC / "data" / f.name)
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
