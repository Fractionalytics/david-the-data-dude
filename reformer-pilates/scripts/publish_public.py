"""Sync what visitors should see into the public repo (../david-the-data-dude/reformer-pilates).

    python projects/reformer-pilates/scripts/publish_public.py             (from the MAIN checkout, after merging)
    python projects/reformer-pilates/scripts/publish_public.py --dry-run   (list what would be copied)

Run it from the main checkout. The public repo is found relative to this one, and
that path is wrong inside a worktree.

Copies only what is ours to share:
- README.md (from docs/public-README.md) and the Reel cover.
- data/tremble_attendance.csv: the de-identified booking history, built by
  build_public_data.py after David reviewed every column on 2026-10-26.
- charts/: the four exploratory charts built from the Tremble data alone.
- scripts/: the Tremble-only pipeline, with requirements.txt.
- docs/data-challenges.md (from docs/public-data-challenges.md).

Deliberately NOT copied:
- Anything Apple Health. The export, data/raw/cache/, classes_with_health.csv,
  workouts.csv, workout_heart_rate.csv, instructors_watch.csv, the scripts that
  read them (parse_apple_health, join_classes_workouts, instructors, szabi_test,
  szabi_chart, scriptv2_numbers) and charts/card18_szabi_bpm.png. David's call,
  2026-10-26: none of it goes public, and no figure in the Reel needs it.
- data/raw/: the export carries his name, his account id and instructors' full
  names. data/public/tremble_attendance.csv is the publishable cut of it.
- data/processed/: intermediate files, several joined to Apple Health.
- charts/counter_mock*.png: they composite a frame of class footage, including
  other people in the room.
- video/: the compositions sit over footage that is not ours to publish.
- The working docs (arc-options, book-claims, visual-plan, shortlist,
  pre-record-audit, script-v2-numbers, caption-skeleton, caption-draft,
  sources, the full data-challenges), CLAUDE.md, NEXT_SESSION.md and .env.

Writing files here publishes nothing; committing and pushing the public repo does.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT.parents[2] / "david-the-data-dude" / "reformer-pilates"

CHARTS = [
    "week_grid.png",
    "sundays_by_quarter.png",
    "weekends_by_quarter.png",
    "time_of_day.png",
]
SCRIPTS = [
    "clean_tremble.py",
    "habit.py",
    "missed_weeks.py",
    "book_ahead.py",
    "replacement_bookings.py",
    "week_grid.py",
    "chart_sundays.py",
    "chart_weekends.py",
    "chart_time_of_day.py",
    "public_columns.py",
    "build_public_data.py",
    "publish_public.py",
]

DRY = "--dry-run" in sys.argv
copied: list[str] = []


def copy(src: Path, dst: Path) -> None:
    if not src.is_file():
        raise FileNotFoundError(src)
    copied.append(str(dst.relative_to(PUBLIC)).replace("\\", "/"))
    if DRY:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> None:
    if not PUBLIC.parent.is_dir():
        raise SystemExit(
            f"Public repo not found at {PUBLIC.parent}. Run this from the main checkout, not a worktree."
        )

    copy(ROOT / "docs" / "public-README.md", PUBLIC / "README.md")
    copy(ROOT / "docs" / "public-data-challenges.md", PUBLIC / "docs" / "data-challenges.md")
    copy(ROOT / "cover.jpg", PUBLIC / "cover.jpg")
    copy(ROOT / "data" / "public" / "tremble_attendance.csv", PUBLIC / "data" / "tremble_attendance.csv")

    for name in CHARTS:
        copy(ROOT / "charts" / name, PUBLIC / "charts" / name)
    for name in SCRIPTS:
        copy(ROOT / "scripts" / name, PUBLIC / "scripts" / name)

    reqs = PUBLIC / "scripts" / "requirements.txt"
    if not DRY:
        reqs.parent.mkdir(parents=True, exist_ok=True)
        reqs.write_text("pandas\nnumpy\nscipy\nmatplotlib\nPillow\n", encoding="utf-8")
    copied.append("scripts/requirements.txt")

    # Nothing identifying may reach the public repo. Check, don't assume.
    #
    # The needles come from the private export, never from a literal here: this
    # script is itself published, so hardcoding the name and account id would
    # have been the leak it is meant to prevent. (It was, on the first pass.)
    if not DRY:
        import csv

        raw = next((ROOT / "data" / "raw").glob("*Reservation_History*.csv"))
        rows = list(csv.DictReader(open(raw, encoding="utf-8-sig")))
        BOOLEAN = {"true", "false", "0", "1"}
        needles = set()
        for col in ("full_name", "user_id", "reserved_for_guest",
                    "reservation_id", "class_id"):
            needles |= {
                r[col] for r in rows
                if r[col] and len(r[col]) > 3 and r[col].lower() not in BOOLEAN
            }
        needles |= {
            p.strip()
            for r in rows
            for p in (r["instrutor"] or "").split(",")
            if len(p.split()) > 1
        }

        leaks = []
        for path in PUBLIC.rglob("*"):
            if not path.is_file() or path.suffix.lower() in {".jpg", ".png"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for needle in needles:
                if needle in text:
                    leaks.append(f"{path.relative_to(PUBLIC)}: {needle!r}")
        print(f"leak check ({len(needles)} names and ids): {'CLEAN' if not leaks else 'FAILED'}")
        for leak in leaks:
            print(f"  {leak}")
        if leaks:
            raise SystemExit("refusing to finish with identifying data in the public folder")

    print(f"{'Would copy' if DRY else 'Copied'} {len(copied)} files to {PUBLIC}:")
    for name in sorted(copied):
        print(f"  {name}")
    if not DRY:
        print("\nNothing is published until the public repo is committed and pushed.")


if __name__ == "__main__":
    main()
