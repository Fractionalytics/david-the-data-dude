"""Sync everything visitors should see into the public repo (../david-the-data-dude/world-series).

    python projects/world-series/scripts/publish_public.py      (from the main checkout, after merging)

Copies only what is ours to share:
- data/: the surname classification for all 1,472 players (name, birth country, 2026 primary
  position, surname type, how it is known, Jev's answer and confidence; no WAR), the team rosters
  with WAR, the standings, scenarios, counts, distribution, free-agent combinations, David's
  overrides with sources, the compound-name research, and the Census top-500 names (type and
  origin only).
- scripts/, docs/ (data challenges, name meanings), design/ (logo script, logos, Reel cover),
  the Remotion source, the rendered animation, and the carousel slides and PDF.

Deliberately NOT copied: data/raw (Baseball-Reference and MLB API downloads, Census file,
Wiktionary pages), full-season WAR for every player (only rostered players' WAR is published),
etymology text (Wiktionary, CC BY-SA, and the research agents' summaries of surname
dictionaries: etymology.json, jev_answers.jsonl, population_jev.jsonl, data/interim/), and .env.
The public README.md is maintained by hand.

Writing files here publishes nothing; committing and pushing the public repo does.
"""
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PUBLIC = ROOT.parents[2] / "david-the-data-dude" / "world-series"
PROC = ROOT / "data" / "processed"

SCRIPTS = ["names.py", "build_players.py", "fetch_positions.py", "fetch_etymology.py", "definitions.py",
           "classify.py", "build_rosters.py", "distribution.py", "scenarios.py", "population_names.py",
           "export_video_data.py", "publish_public.py"]
VIDEO_FILES = ["package.json", "package-lock.json", "tsconfig.json", "remotion.config.ts", "README.md"]


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


def main() -> None:
    data = PUBLIC / "data"
    data.mkdir(parents=True, exist_ok=True)
    p = pd.read_csv(PROC / "players_final.csv")
    p[["mlb_id", "full_name", "surname", "birth_country", "primary_pos", "surname_type", "jev_type",
       "jev_confidence", "evidence", "compound", "overridden"]].to_csv(data / "players_surname_types.csv", index=False)
    r = pd.read_csv(PROC / "rosters.csv")
    r[["team", "slot", "full_name", "surname_type", "birth_country", "primary_pos", "war_total"]].to_csv(
        data / "rosters.csv", index=False)
    pop = pd.read_csv(PROC / "population_top_names.csv")
    pop.drop(columns=["etymology"]).to_csv(data / "census_top500_surnames.csv", index=False)
    for name in ("standings.csv", "scenarios.csv", "counts.csv", "distribution.csv", "free_agents.csv"):
        copy(PROC / name, data / name)
    for name in ("overrides.csv", "compound_parts_research.csv"):
        copy(ROOT / "data" / name, data / name)

    for name in SCRIPTS:
        copy(ROOT / "scripts" / name, PUBLIC / "scripts" / name)
    copy(REPO / "requirements.txt", PUBLIC / "scripts" / "requirements.txt")

    for name in ("data-challenges.md", "name-meanings.md"):
        copy(ROOT / "docs" / name, PUBLIC / "docs" / name)

    copy(ROOT / "design" / "make_logos.py", PUBLIC / "design" / "make_logos.py")
    n_logos = sync_dir(ROOT / "design" / "png", PUBLIC / "design" / "logos", "*.png")
    copy(ROOT / "design" / "cover.jpg", PUBLIC / "cover.jpg")

    n_src = sync_dir(ROOT / "video" / "src", PUBLIC / "video" / "src")
    for name in VIDEO_FILES:
        copy(ROOT / "video" / name, PUBLIC / "video" / name)
    copy(ROOT / "video" / "out" / "world-series.mp4", PUBLIC / "videos" / "world-series-animation.mp4")
    n_slides = sync_dir(ROOT / "video" / "out" / "carousel", PUBLIC / "carousel", "*.png")
    copy(ROOT / "carousel" / "world-series-carousel.pdf", PUBLIC / "carousel" / "world-series-carousel.pdf")

    print(f"published to {PUBLIC}: {len(SCRIPTS)} scripts, {n_logos} logo images, {n_src} video source files, "
          f"{n_slides} carousel slides + PDF, animation, cover")


if __name__ == "__main__":
    main()
