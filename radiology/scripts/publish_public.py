"""Sync everything visitors should see into the public repo (david-the-data-dude/radiology).

    python -I -X utf8 projects/radiology/scripts/publish_public.py

Copied: the processed tables (aggregate counts from CMS, Census, FDA, NRMP, and pay figures as
published by Doximity and Medscape), the dated claims log, our scripts, the data-challenges doc,
the spot-checks (trimmed, below), the exploratory chart, the Remotion source, the rendered videos
and stills for the Reel's charts, and the Reel cover.

Deliberately NOT copied:
- data/raw (1.4 GB of CMS, Census, FDA and NRMP downloads; the scripts say where to get them);
- spot-checks rows 1-4, which name individual radiologists by NPI with their Medicare volumes:
  public records, but a public repo shouldn't single out people;
- docs/research and docs/beat-skeleton.md (working notes, including unverified pasted research);
- the superseded "Sheet1" compositions' renders, and the .env file.
The public README.md is maintained by hand.

The public repo is found next to the main checkout (via git's common dir). Writing files here
publishes nothing; committing and pushing the public repo does.
"""
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
COMMON = Path(subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip())
PUBLIC = COMMON.parent.parent / "david-the-data-dude" / "radiology"

DOCS = ["data-challenges.md"]
VIDEO_FILES = ["package.json", "package-lock.json", "tsconfig.json", "remotion.config.ts",
               "render-all.mjs", "render-stills.mjs", "README.md"]
# The Reel's charts, in "Revised Script" card order (README composition table).
VIDEOS = ["rev03-headline-square", "rev06-07-capability", "rev08-amara", "rev09-10-prescription",
          "rev11-13-reasons", "rev14-pay-premium", "rev16-takeaway-square"]


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def trim_spot_checks(text: str) -> str:
    """Drop the check rows that name an individual radiologist (Item starts with 'NPI ') and the two
    private notes about them, and add a note."""
    private = (r"\|\s*\d+\s*\|\s*NPI \d{10}", r"Individual NPIs are public", r"\*\*Rows 1–4 have two kinds of link")
    out = [line for line in text.splitlines() if not any(re.match(p, line) for p in private)]
    note = ("> **Public version.** The private copy also has checks 1-4, which look up four individual "
            "radiologists by NPI. They passed; they're left out so this repo doesn't single out people.")
    out.insert(2, note + "\n")
    return "\n".join(out) + "\n"


def main() -> None:
    for sub in ("data", "scripts", "docs", "charts", "videos", "video/src"):
        shutil.rmtree(PUBLIC / sub, ignore_errors=True)
    for folder in ("processed", "claims"):
        for f in (ROOT / "data" / folder).glob("*.*"):
            copy(f, PUBLIC / "data" / folder / f.name)
    for f in sorted((ROOT / "scripts").glob("*")):
        if f.suffix in (".py", ".sh"):
            copy(f, PUBLIC / "scripts" / f.name)
    copy(REPO / "requirements.txt", PUBLIC / "scripts" / "requirements.txt")
    for name in DOCS:
        copy(ROOT / "docs" / name, PUBLIC / "docs" / name)
    spot = trim_spot_checks((ROOT / "docs" / "spot-checks.md").read_text(encoding="utf-8"))
    (PUBLIC / "docs" / "spot-checks.md").write_text(spot, encoding="utf-8")
    for png in (ROOT / "charts" / "exploratory").glob("*.png"):
        copy(png, PUBLIC / "charts" / "exploratory" / png.name)

    for f in (ROOT / "video" / "src").rglob("*"):
        if f.is_file():
            copy(f, PUBLIC / "video" / "src" / f.relative_to(ROOT / "video" / "src"))
    for name in VIDEO_FILES:
        copy(ROOT / "video" / name, PUBLIC / "video" / name)
    out = ROOT / "video" / "out"
    for name in VIDEOS:
        copy(out / f"{name}.mp4", PUBLIC / "videos" / f"{name}.mp4")
        copy(out / "stills" / f"{name}.png", PUBLIC / "videos" / "stills" / f"{name}.png")
    copy(ROOT / "cover.jpg", PUBLIC / "cover.jpg")
    print(f"published to {PUBLIC}: {len(VIDEOS)} videos")


if __name__ == "__main__":
    main()
