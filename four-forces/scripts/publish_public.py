"""Sync everything visitors should see into the public repo (david-the-data-dude/four-forces).

    python -I -X utf8 projects/amara/scripts/publish_public.py      (from the main checkout)

Copied: the raw public-data files (BLS OEWS national zips, BLS AI exposure categories, BLS CES call
centers, NY Fed recent-graduate file; about 2 MB, all published by U.S. government agencies or the
NY Fed), the processed tables, our scripts, the data-challenges, corrections, numbers-by-period and
rubric docs, the exploratory charts, the Remotion source, the rendered videos and stills for the
Reel's charts, the carousel slides and PDF, and the Reel cover.

Deliberately NOT copied:
- docs/research (working notes: agent research reports, secondary-source leads, and David's private
  conversation notes about a named friend, which need that person's OK before going public);
- docs/beat-skeleton.md and docs/number-picks.md (script drafting notes) and carousel/slides.md;
- the .env file.
The public README.md is maintained by hand.

Renders live in video/out/, which is gitignored and exists only in the checkout that rendered them
(the project worktree). The public repo is found next to the main checkout via git's common dir, so
running this from the worktree after the merge publishes the merged content with its renders. Writing files here
publishes nothing; committing and pushing the public repo does.
"""
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
COMMON = Path(subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip())
PUBLIC = COMMON.parent.parent / "david-the-data-dude" / "four-forces"

DOCS = ["data-challenges.md", "corrections.md", "numbers-by-period.md", "rubric-table.md"]
VIDEO_FILES = ["package.json", "package-lock.json", "tsconfig.json", "remotion.config.ts",
               "render-all.mjs", "render-stills.mjs", "render-checks.mjs", "render-carousel.mjs", "zones.env", "README.md"]
# The Reel's charts, in storyboard card order (video/README.md composition table).
VIDEOS = ["c07-waterfall-ceiling", "c08-waterfall-pretrend", "c09-waterfall-loans", "c10-waterfall-remaining",
          "c11-top-declines", "c13-forces-title", "c14-forces-list", "c15-forces-table", "c16a-office-vs-rest",
          "c16b-forces-fast", "c17a-radiology-grid", "c17b-paralegals", "c17c-forces-slow", "c19-call-centers-square"]


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> None:
    for sub in ("data", "scripts", "docs", "charts", "videos", "video/src", "carousel"):
        shutil.rmtree(PUBLIC / sub, ignore_errors=True)
    for folder in ("raw", "processed"):
        for f in (ROOT / "data" / folder).rglob("*"):
            if f.is_file() and f.name != ".gitkeep":
                copy(f, PUBLIC / "data" / folder / f.relative_to(ROOT / "data" / folder))
    for f in sorted((ROOT / "scripts").glob("*.py")):
        copy(f, PUBLIC / "scripts" / f.name)
    copy(REPO / "requirements.txt", PUBLIC / "scripts" / "requirements.txt")
    for name in DOCS:
        copy(ROOT / "docs" / name, PUBLIC / "docs" / name)
    for png in (ROOT / "charts").glob("*.png"):
        copy(png, PUBLIC / "charts" / png.name)

    for f in (ROOT / "video" / "src").rglob("*"):
        if f.is_file():
            copy(f, PUBLIC / "video" / "src" / f.relative_to(ROOT / "video" / "src"))
    for name in VIDEO_FILES:
        copy(ROOT / "video" / name, PUBLIC / "video" / name)
    out = ROOT / "video" / "out"
    for name in VIDEOS:
        copy(out / f"{name}.mp4", PUBLIC / "videos" / f"{name}.mp4")
    for name in VIDEOS:
        copy(out / "stills" / f"{name}.png", PUBLIC / "videos" / "stills" / f"{name}.png")
    for png in sorted((out / "carousel").glob("0[1-6].png")):
        copy(png, PUBLIC / "carousel" / png.name)
    copy(ROOT / "carousel" / "four-forces-carousel.pdf", PUBLIC / "carousel" / "four-forces-carousel.pdf")
    copy(ROOT / "cover.jpg", PUBLIC / "cover.jpg")
    print(f"published to {PUBLIC}: {len(VIDEOS)} videos")


if __name__ == "__main__":
    main()
