"""Sync everything visitors should see into the public repo (../david-the-data-dude/voting).

    python projects/voting/scripts/publish_public.py             (from the main checkout, after merging)
    python projects/voting/scripts/publish_public.py --dry-run   (list what would be copied)

Copies only what is ours to share:
- README.md (from docs/public-README.md, written and fact-checked here) and the Reel cover.
- data/: turnout by age (Census CPS, a U.S. government work), the 65+ per 18-24 voter ratio, national turnout
  (UF Election Lab figures, CC BY 4.0, credited in the README) and the age of Congress (from CC0 data).
- charts/: the exploratory charts built only from those sources.
- scripts/ (the pipeline) with requirements.txt, docs/data-challenges.md, the Remotion source in video/, and
  the rendered animation on black (videos/voting-animation.mp4).

Deliberately NOT copied: data/raw (Census, UF and congress-legislators files are public and linked from the
README; Gallup's topline PDF and Pew's page are theirs), data/processed/trust.csv and the gallup/pew charts
(Gallup's and Pew's series, used only in early research), the 9:16 hook mockups and the cut "voter boxes"
mockup, working notes (research-notes, arc-options, close-races, why-2018, gerontocracy-test, sources,
pinned-comment), the per-card ProRes clips (too big for GitHub) and the preview (it plays over a stand-in of
David's frame), video/public/mock-bg.png, CLAUDE.md, NEXT_SESSION.md and .env.

Writing files here publishes nothing; committing and pushing the public repo does.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PUBLIC = ROOT.parents[2] / "david-the-data-dude" / "voting"

DATA = ["turnout_by_age.csv", "senior_to_young_ratio.csv", "turnout.csv", "congress_age.csv"]
CHARTS = ["senior_to_young_voter_ratio.png", "adults_by_age.png", "age_gap.png", "turnout_by_age.png",
          "senior_share_of_voters.png", "vep_turnout.png", "eligible_vs_voted.png", "congress_age.png"]
SCRIPTS = ["build_series.py", "build_congress_age.py", "explore_charts.py", "publish_public.py"]
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
    for name in DATA:
        copy(ROOT / "data" / "processed" / name, PUBLIC / "data" / name)
    for name in CHARTS:
        copy(ROOT / "charts" / name, PUBLIC / "charts" / name)
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
    copy(ROOT / "videos" / "voting-animation.mp4", PUBLIC / "videos" / "voting-animation.mp4")

    print(("would copy" if DRY else "published") + f" {len(copied)} files to {PUBLIC}:")
    for c in copied:
        print("  " + c)


if __name__ == "__main__":
    main()
