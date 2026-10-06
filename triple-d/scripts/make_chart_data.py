"""Aggregate the final table into the chart data the Remotion videos read.

    python scripts/make_chart_data.py   # -> video/src/data/triple-d.json      (US only: what the videos use)
                                        # -> video/src/data/triple-d-all.json  (every country, for reference)

The videos are about American tastes, so they use restaurants in the US and its territories
(in_us: states, DC, Puerto Rico). Per-season numbers count a restaurant in every season it
appeared (revisits included). `episodes` is every episode that season, in any country.
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "video" / "src" / "data"
CATS = ["Diner", "Drive-In", "Dive", "Other"]
# Four season groups for the stacked "Then vs. now" chart.
ERAS = (("S1-10", 1, 10), ("S11-20", 11, 20), ("S21-30", 21, 30), ("S31-43", 31, 43))
# First and last ten seasons for the slope charts.
SLOPE_ERAS = (("First 10", 1, 10), ("Last 10", 34, 43))


def counts(series: pd.Series) -> dict:
    vc = series.value_counts()
    return {c: int(vc.get(c, 0)) for c in CATS}


def season_groups(by_season: pd.DataFrame, groups) -> list[dict]:
    out = []
    for label, lo, hi in groups:
        g = by_season[by_season.season.between(lo, hi)]
        out.append({
            "label": label,
            "seasons": [lo, hi],
            "restaurants": len(g),
            "detailed": {c: int(n) for c, n in g.detailed_category.value_counts().items()},
        })
    return out


def build(f: pd.DataFrame, episodes: pd.Series, scope: str) -> dict:
    by_season = f.assign(season=f.seasons.astype(str).str.split("; ")).explode("season")
    by_season["season"] = by_season.season.astype(int)

    seasons = []
    for s, g in by_season.groupby("season"):
        strict = counts(g.classification)
        seasons.append({
            "season": int(s),
            "episodes": int(episodes[s]),
            "restaurants": len(g),
            "strict": strict,
            "forced": counts(g.classification_forced),
            "detailed": {c: int(n) for c, n in g.detailed_category.value_counts().items()},
            "pctDDD": round(100 * (len(g) - strict["Other"]) / len(g), 1),
        })

    return {
        "scope": scope,
        "uniqueRestaurants": len(f),
        "appearances": {str(k): int(v) for k, v in f.appearances.value_counts().sort_index().items()},
        "totals": {
            "strict": counts(f.classification),
            "forced": counts(f.classification_forced),
            # Diner / Drive-In / Dive plus the 12 "Other" buckets, largest first.
            "detailed": [{"category": c, "count": int(n)} for c, n in f.detailed_category.value_counts().items()],
        },
        "seasons": seasons,
        "eras": season_groups(by_season, ERAS),
        "slopeEras": season_groups(by_season, SLOPE_ERAS),
    }


def main() -> None:
    f = pd.read_csv(ROOT / "data" / "final" / "triple_d_restaurants.csv")
    if f.detailed_category.isna().any():
        raise SystemExit("detailed_category is incomplete; run classify_buckets.py and build_final.py first")
    wiki = pd.read_csv(ROOT / "data" / "interim" / "wiki_appearances.csv")
    episodes = wiki.groupby("season").episode_overall.nunique()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, subset, scope in (("triple-d.json", f[f.in_us], "us"), ("triple-d-all.json", f, "all")):
        data = build(subset, episodes, scope)
        (DATA_DIR / name).write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
        print(f"{scope}: {data['uniqueRestaurants']} restaurants, {len(data['seasons'])} seasons -> {DATA_DIR / name}")


if __name__ == "__main__":
    main()
