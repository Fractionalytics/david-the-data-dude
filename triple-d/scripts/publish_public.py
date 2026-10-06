"""Sync everything visitors should see into the public repo (../david-the-data-dude/triple-d).

    python scripts/publish_public.py

Copies only what is ours to share: our scripts, our docs, the final table (facts plus our
labels), the Wikipedia-derived episode list (CC BY-SA), Jev's answers without the evidence it
read, the chart data, the Remotion source, and the rendered videos and stills.

Deliberately NOT copied: anything containing foodiepie's descriptions or Yelp's categories
(data/raw, foodiepie_*.csv, restaurants.csv, jev_answers.jsonl, jev_buckets.jsonl), the
agents' web-research notes, and the .env file. The public README.md is maintained by hand.

Writing files here publishes nothing; committing and pushing the public repo does.
"""

import shutil
from pathlib import Path

import export_public

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PUBLIC = ROOT.parents[2] / "david-the-data-dude" / "triple-d"

SCRIPTS = ["fetch.py", "parse.py", "match.py", "webdata.py", "definitions.py", "classify.py",
           "classify_buckets.py", "build_final.py", "make_chart_data.py", "export_public.py",
           "publish_public.py"]
VIDEO_FILES = ["package.json", "package-lock.json", "tsconfig.json", "remotion.config.ts",
               "render-all.mjs", "render-stills.mjs", "README.md", ".gitignore"]


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
    export_public.main()  # data/definitions.json + data/jev_output.csv (no evidence text)

    data = PUBLIC / "data"
    copy(ROOT / "data" / "final" / "triple_d_restaurants.csv", data / "triple_d_restaurants.csv")
    copy(ROOT / "data" / "interim" / "wiki_appearances.csv", data / "wiki_appearances.csv")
    for name in ("triple-d.json", "triple-d-all.json"):
        copy(ROOT / "video" / "src" / "data" / name, data / "chart-data" / name)

    for name in SCRIPTS:
        copy(ROOT / "scripts" / name, PUBLIC / "scripts" / name)
    copy(REPO / "requirements.txt", PUBLIC / "scripts" / "requirements.txt")

    n_docs = sync_dir(ROOT / "docs", PUBLIC / "docs", "*.md")
    copy(REPO / "docs" / "difficulty-rubric.md", PUBLIC / "docs" / "difficulty-rubric.md")

    n_src = sync_dir(ROOT / "video" / "src", PUBLIC / "video" / "src")
    for name in VIDEO_FILES:
        copy(ROOT / "video" / name, PUBLIC / "video" / name)

    out = ROOT / "video" / "out"
    n_mp4 = sync_dir(out, PUBLIC / "videos", "*.mp4")
    n_png = sync_dir(out / "stills", PUBLIC / "videos" / "stills", "*.png")
    print(f"published to {PUBLIC}: {len(SCRIPTS)} scripts, {n_docs + 1} docs, {n_src} video source files, "
          f"{n_mp4} videos, {n_png} stills")


if __name__ == "__main__":
    main()
