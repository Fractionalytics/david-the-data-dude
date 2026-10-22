"""Sync everything visitors should see into the public repo (../david-the-data-dude/jury-duty).

    python projects/jury-duty/scripts/publish_public.py      (from the main checkout, after merging)
    python projects/jury-duty/scripts/publish_public.py --dry-run   (list what would be copied)

Copies only what is ours to share:
- README.md (from docs/public-README.md, written and fact-checked here) and the Reel cover.
- data/: Racine's CCAP-35 counts 2015-2025, the Wisconsin spine per 1,000 summoned, every source's stage
  rates, the Oregon and Florida county tables with NCHS urban-rural codes, Massachusetts' FY2012-2015 counts,
  and the federal civil jury-trial length distribution.
- scripts/ (the pipeline) with requirements.txt, docs/data-challenges.md, the Remotion source in video/, and
  the rendered animation on black (videos/jury-duty-animation.mp4).

Deliberately NOT copied: data/raw (the courts' PDFs, the FJC Integrated Database download, the NCHS file;
they're public records, linked from the README), idb_civil_trials.csv (rebuilt by the script), the
exploratory side-by-side chart and its data, docs/sources.md and docs/funnel-ranges.md (working notes),
docs/reference/ (John Johnson's Sankey image, which is his), the per-card ProRes clips (too big for GitHub)
and the preview (it shows a still of David's frame), mock_frame.py, CLAUDE.md, NEXT_SESSION.md and .env.

Writing files here publishes nothing; committing and pushing the public repo does.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PUBLIC = ROOT.parents[2] / "david-the-data-dude" / "jury-duty"

DATA = ["racine_ccap35_2015_2025.csv", "wi_spine_per_1000.csv", "funnel_rates.csv", "oregon_counties_2025.csv",
        "florida_counties_2024.csv", "ma_ojc_annual.csv", "federal_civil_jury_trial_lengths.csv"]
SCRIPTS = ["federal_funnel.py", "ma_funnel.py", "idb_civil_trials.py", "idb_jury_lengths.py", "extract_counties.py",
           "build_ranges.py", "wi_spine.py", "publish_public.py"]
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
        copy(ROOT / "data" / name, PUBLIC / "data" / name)
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
    copy(ROOT / "video" / "out" / "jury-duty-animation.mp4", PUBLIC / "videos" / "jury-duty-animation.mp4")

    print(("would copy" if DRY else "published") + f" {len(copied)} files to {PUBLIC}:")
    for c in copied:
        print("  " + c)


if __name__ == "__main__":
    main()
