"""Sync everything visitors should see into the public repo (../david-the-data-dude/florida-alerts).

    python scripts/publish_public.py      (run from the main checkout, after merging)

Copies only what is ours to share, or FDLE's / DOJ's own public figures:
- data/: the processed tables, the hand-typed newsletter and press-release figures with their source quotes,
  FDLE's 197 success stories (FDLE's public text, no names), the chart data, and the case-level alerts
  COARSENED to year, month, age, sex, agency, recovery state and FDLE's direct/indirect mark.
- scripts/, docs/ (data challenges, back in my day, spot checks, the difficulty rubric), the Remotion source, the five
  chart MP4s, and the Reel cover.

Deliberately NOT copied:
- data/raw (FDLE, FMCDF and Wayback PDFs and HTML) and the extracted PDF text in data/interim.
- The exact alert dates and the last-seen and recovery towns. The brief's privacy rule allows month, county,
  age, sex and how found; a day plus a town plus an age can point to one person.
- docs/data-plan.md (a plan pasted in from another AI tool), the .env file, node_modules and check stills.
- The spot checks' "Our data says" and "Look up" columns, which hold exact dates, towns and links to FDLE's full
  reports. The public spot-checks.md keeps each check's purpose and verdict.

The public README.md is maintained by hand. Writing files here publishes nothing; committing and pushing the
public repo does.
"""

import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PUBLIC = ROOT.parents[2] / "david-the-data-dude" / "florida-alerts"

DATA = {
    "processed": ["silver_alerts_yearly.csv", "silver_cumulative.csv", "silver_recovery_states.csv",
                  "alerts_yearly_by_type.csv", "alerts_yearly_direct.csv", "amber_national_yearly.csv"],
    "interim": ["newsletter_stats.csv", "silver_anniversary_releases.csv", "silver_success_stories.csv",
                "silver_monthly_totals.csv"],
}
CASE_COLUMNS = ["year", "month", "row", "age", "sex", "agency", "recovered_state", "mark"]
DOCS = ["data-challenges.md", "back-in-my-day.md"]
VIDEO_FILES = ["package.json", "package-lock.json", "tsconfig.json", "remotion.config.ts", "render-all.mjs",
               "render-stills.mjs", "render-checks.mjs", "README.md", "zones.env"]


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def sync_dir(src: Path, dst: Path, pattern: str = "*") -> int:
    if dst.exists():
        shutil.rmtree(dst)
    n = 0
    for f in src.rglob(pattern):
        if f.is_file():
            copy(f, dst / f.relative_to(src))
            n += 1
    return n


def trim_spot_checks(text: str) -> str:
    """Drop the 'Our data says' and 'Look up' columns from every 6-column check table, and add a note."""
    out, in_check_table = [], False
    for line in text.splitlines():
        parts = [c.strip() for c in line.strip().strip('|').split('|')] if line.startswith('|') else []
        if parts[:4] == ["#", "Item", "Tests", "Our data says"]:
            in_check_table = True  # only check tables; the Results tally also has six columns
        elif not parts:
            in_check_table = False
        if in_check_table and len(parts) == 6:
            line = '| ' + ' | '.join(parts[:3] + parts[5:]) + ' |'
        out.append(line)
    note = ("> **Public version.** The private copy also lists each check's exact values and a link to the archived "
            "FDLE report. Those columns hold exact dates and towns, which this repo leaves out (see the README).")
    out.insert(2, note + chr(10))
    return chr(10).join(out) + chr(10)



def main() -> None:
    if (PUBLIC / "data").exists():
        shutil.rmtree(PUBLIC / "data")
    for folder, names in DATA.items():
        for name in names:
            copy(ROOT / "data" / folder / name, PUBLIC / "data" / name)
    cases = pd.read_csv(ROOT / "data" / "interim" / "silver_monthly_cases.csv")
    (PUBLIC / "data").mkdir(parents=True, exist_ok=True)
    cases[CASE_COLUMNS].to_csv(PUBLIC / "data" / "silver_alert_cases_2011_2020.csv", index=False)
    copy(ROOT / "video" / "src" / "data" / "silver.json", PUBLIC / "data" / "chart-data" / "silver.json")

    n_scripts = sync_dir(ROOT / "scripts", PUBLIC / "scripts", "*.py")
    copy(REPO / "requirements.txt", PUBLIC / "scripts" / "requirements.txt")

    if (PUBLIC / "docs").exists():
        shutil.rmtree(PUBLIC / "docs")
    for name in DOCS:
        copy(ROOT / "docs" / name, PUBLIC / "docs" / name)
    copy(REPO / "docs" / "difficulty-rubric.md", PUBLIC / "docs" / "difficulty-rubric.md")
    spot = trim_spot_checks((ROOT / "docs" / "spot-checks.md").read_text(encoding="utf-8"))
    (PUBLIC / "docs" / "spot-checks.md").write_text(spot, encoding="utf-8")

    n_src = sync_dir(ROOT / "video" / "src", PUBLIC / "video" / "src")
    for name in VIDEO_FILES:
        copy(ROOT / "video" / name, PUBLIC / "video" / name)
    n_mp4 = sync_dir(ROOT / "video" / "out", PUBLIC / "videos", "*.mp4")
    for f in (PUBLIC / "videos").rglob("checks"):
        shutil.rmtree(f)
    copy(ROOT / "cover.jpg", PUBLIC / "cover.jpg")

    print(f"published to {PUBLIC}: {len(cases)} coarsened case rows, {n_scripts} scripts, {len(DOCS) + 2} docs, "
          f"{n_src} video source files, {n_mp4} videos, cover")


if __name__ == "__main__":
    main()
