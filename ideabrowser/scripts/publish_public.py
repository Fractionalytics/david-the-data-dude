"""Sync everything visitors should see into the public repo (david-the-data-dude/ideabrowser).

    python projects/ideabrowser/scripts/publish_public.py

The brief's rule: Ideabrowser's emails are its content in David's private inbox, so only
aggregate results and derived charts are published. Copied: our scripts, the method docs,
per-day labels (date and Jev's answers, no idea titles or text), aggregate tables, the chart
data, the exploratory charts, the Remotion source and the rendered videos and stills.

Deliberately NOT copied: data/raw (the emails), data/processed (email bodies, idea titles and
links, Jev's inputs), docs/spot-checks.md (links into David's Gmail), docs/pilot-review.csv and
docs/themes.md (lists of idea titles), the Claude and TypeSafe logo files and the conveyor
render that shows them, and the .env file. The public README.md is maintained by hand.

The public repo is found next to the main checkout (via git's common dir), so this also runs
from a worktree. Writing files here publishes nothing; committing and pushing the public repo does.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pandas as pd

from classify import ANSWERS, load_ideas

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
COMMON = Path(subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip())
PUBLIC = COMMON.parent.parent / "david-the-data-dude" / "ideabrowser"

SCRIPTS = ["fetch_emails.py", "build_table.py", "definitions.py", "classify.py", "classify_greg13.py",
           "classify_agent_customer.py", "cluster_ideas.py", "make_chart_data.py", "exploratory_charts.py",
           "publish_public.py"]
DOCS = ["categories.md", "data-challenges.md", "greg-13.md"]
VIDEO_FILES = ["package.json", "package-lock.json", "tsconfig.json", "remotion.config.ts",
               "render-all.mjs", "render-stills.mjs", "README.md", ".gitignore"]
VIDEOS = ["services-by-era", "daily-strip", "seesaw"]  # conveyor shows third-party logos


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def export_data(out: Path) -> None:
    """Per-day labels and aggregate counts: our labels on dates, nothing of Ideabrowser's text."""
    a = pd.DataFrame(map(json.loads, ANSWERS.open(encoding="utf-8")))
    main = a[(a.definitions_version == "v3") & (a["mode"] == "main")].drop_duplicates("key", keep="last")
    d = load_ideas().merge(main, on="key")
    d = d[d.role == "featured"].copy()
    d["date"] = d.date_utc.str[:10]
    d["era"] = d.era.map({1: "1 (Jul 2025-Jan 2026)", 2: "2 (Jan-Jul 2026)", 3: "newsletter (Jul 28 2026 on)"})
    cols = ["date", "era"]
    for q in ("business_type", "who_pays", "industry", "ai_central"):
        d[q + "_confidence"] = d[q + "_confidence"].round(2)
        cols += [q, q + "_confidence"]
    out.mkdir(parents=True, exist_ok=True)
    d.sort_values("date")[cols].to_csv(out / "daily_featured_labels.csv", index=False)
    pd.crosstab(d.era, d.business_type, margins=True, margins_name="all").to_csv(out / "business_type_by_era.csv")
    d["month"] = d.date.str[:7]
    pd.crosstab(d.month, d.business_type, margins=True, margins_name="all").to_csv(out / "business_type_by_month.csv")


def main() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC / "data", ignore_errors=True)
    export_data(PUBLIC / "data")
    copy(ROOT / "video" / "src" / "data" / "ideabrowser.json", PUBLIC / "data" / "chart-data" / "ideabrowser.json")

    for name in SCRIPTS:
        copy(ROOT / "scripts" / name, PUBLIC / "scripts" / name)
    copy(REPO / "requirements.txt", PUBLIC / "scripts" / "requirements.txt")
    for name in DOCS:
        copy(ROOT / "docs" / name, PUBLIC / "docs" / name)
    for png in (ROOT / "charts" / "exploratory").glob("*.png"):
        copy(png, PUBLIC / "charts" / "exploratory" / png.name)

    shutil.rmtree(PUBLIC / "video" / "src", ignore_errors=True)
    for f in (ROOT / "video" / "src").rglob("*"):
        if f.is_file():
            copy(f, PUBLIC / "video" / "src" / f.relative_to(ROOT / "video" / "src"))
    for name in VIDEO_FILES:
        copy(ROOT / "video" / name, PUBLIC / "video" / name)
    out = ROOT / "video" / "out"
    for name in VIDEOS:
        copy(out / f"{name}.mp4", PUBLIC / "videos" / f"{name}.mp4")
        copy(out / "stills" / f"{name}.png", PUBLIC / "videos" / "stills" / f"{name}.png")
    print(f"published to {PUBLIC}: {len(SCRIPTS)} scripts, {len(DOCS)} docs, {len(VIDEOS)} videos")


if __name__ == "__main__":
    main()
