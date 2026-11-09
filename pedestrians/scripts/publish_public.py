"""Sync everything visitors should see into the public repo (../david-the-data-dude/pedestrians).

    python projects/sedans-to-suvs/scripts/publish_public.py      (from the main checkout, after merging)
    python projects/sedans-to-suvs/scripts/publish_public.py --dry-run   (list what would be copied)

Copies only what is ours to share:
- README.md (from docs/public-README.md, written and fact-checked here) and the Reel cover.
- data/: the frozen release behind the Reel (data/releases/2026-11-09-reel/).
- scripts/ (the pipeline) with requirements.txt; docs/hypothesis-test.md, bradford-hill.md and data-challenges.md;
  the Remotion source in video/.

Deliberately NOT copied: data/raw (FARS, Eurostat, Census, CDC, HUD and other source files: public, re-fetchable
or downloaded by hand from their sites), the other data/final tables, research notes, script reviews, spot checks,
caption-and-first-comment.md, the H11 draft, the per-card ProRes clips (too big for GitHub), video/public/ (stills
of David's frames), CLAUDE.md, NEXT_SESSION.md and .env.

Writing files here publishes nothing; committing and pushing the public repo does.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PUBLIC = ROOT.parents[2] / "david-the-data-dude" / "pedestrians"
RELEASE = ROOT / "data" / "releases" / "2026-11-09-reel"
DOCS = ["hypothesis-test.md", "bradford-hill.md", "data-challenges.md"]
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
    for f in sorted(RELEASE.iterdir()):
        copy(f, PUBLIC / "data" / f.name)
    for f in sorted((ROOT / "scripts").glob("*.py")):
        copy(f, PUBLIC / "scripts" / f.name)
    copy(REPO / "requirements.txt", PUBLIC / "scripts" / "requirements.txt")
    for name in DOCS:
        copy(ROOT / "docs" / name, PUBLIC / "docs" / name)
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
