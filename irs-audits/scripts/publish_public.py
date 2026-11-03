"""Sync everything visitors should see into the public repo (../david-the-data-dude/irs-audits).

    python projects/irs-audits/scripts/publish_public.py      (from the main checkout, after merging)
    python projects/irs-audits/scripts/publish_public.py --dry-run   (list what would be copied)

Copies only what is ours to share:
- README.md (from docs/public-README.md, written and fact-checked here) and the Reel cover.
- data/: the Reel's seven bands, Table 3-1 in long form, mail vs. in-person audits by bracket, TRAC's
  examiner split, and data/raw's Data Book spreadsheets (U.S. government works the scripts read).
- scripts/ (the pipeline) with requirements.txt, the exploratory scatterplots in charts/,
  docs/data-challenges.md, the Remotion source and pencil font in video/, and the rendered animation on
  black (videos/irs-audits-animation.mp4).

Deliberately NOT copied: data/raw/older (old Data Books and scans used only for research notes),
data/releases (frozen copies of the same tables), charts/final_frames and mock_final_frames.py (pre-recording
mockups), docs/research-notes.md, docs/beats.md and docs/first-comment.txt (working notes and drafts), the
per-card ProRes clips (too big for GitHub) and the preview (it shows a still of David's frame), CLAUDE.md,
NEXT_SESSION.md and .env.

Writing files here publishes nothing; committing and pushing the public repo does.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PUBLIC = ROOT.parents[2] / "david-the-data-dude" / "irs-audits"

DATA = ["reel_bands.csv", "table_3_1_long.csv", "odds_by_income.csv", "audit_types_by_bracket.csv",
        "audit_types_trac_fy2022.csv"]
SCRIPTS = ["parse_table_3_1.py", "audit_type_odds.py", "audit_types_by_income.py", "chart_odds_vs_field_share.py",
           "reel_bands.py", "publish_public.py"]
CHARTS = ["odds_vs_field_share.png", "odds_vs_field_share_fy23_25.png"]
VIDEO_FILES = ["package.json", "package-lock.json", "tsconfig.json", "remotion.config.ts", "README.md", "render-cards.mjs",
               "fonts/Caveat-600.woff2"]

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
    for f in sorted((ROOT / "data" / "raw").glob("*.xlsx")):
        copy(f, PUBLIC / "data" / "raw" / f.name)
    for name in SCRIPTS:
        copy(ROOT / "scripts" / name, PUBLIC / "scripts" / name)
    copy(REPO / "requirements.txt", PUBLIC / "scripts" / "requirements.txt")
    for name in CHARTS:
        copy(ROOT / "charts" / name, PUBLIC / "charts" / name)
    copy(ROOT / "docs" / "data-challenges.md", PUBLIC / "docs" / "data-challenges.md")
    if not DRY and (PUBLIC / "video" / "src").exists():
        shutil.rmtree(PUBLIC / "video" / "src")
    for f in sorted((ROOT / "video" / "src").rglob("*")):
        if f.is_file():
            copy(f, PUBLIC / "video" / "src" / f.relative_to(ROOT / "video" / "src"))
    for name in VIDEO_FILES:
        copy(ROOT / "video" / name, PUBLIC / "video" / name)
    copy(ROOT / "video" / "out" / "irs-audits-animation.mp4", PUBLIC / "videos" / "irs-audits-animation.mp4")

    print(("would copy" if DRY else "published") + f" {len(copied)} files to {PUBLIC}:")
    for c in copied:
        print("  " + c)


if __name__ == "__main__":
    main()
