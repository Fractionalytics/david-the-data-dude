"""Match Wikipedia restaurant appearances to foodiepie restaurants.

    python scripts/match.py

Wikipedia is the roster (every restaurant, season, air date). foodiepie adds
notes, dishes, Yelp categories and the open/closed signal. Restaurants are
keyed by (normalized name, state).

Outputs data/interim/restaurants.csv (one row per Wikipedia restaurant) and
prints match coverage plus the unmatched names on each side for review.
"""

import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"

STATES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Washington, D.C.": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
    "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Puerto Rico": "PR", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "U.S. Virgin Islands": "VI", "Virgin Islands": "VI",
    "Alberta": "AB", "British Columbia": "BC", "Ontario": "ON", "Quebec": "QC", "Manitoba": "MB",
    "Nova Scotia": "NS", "Baja California Sur": "BCS", "Coahuila": "COAH", "Quintana Roo": "QR",
}
FUZZY_MIN = 0.85
# (Wikipedia name, location) -> foodiepie slug, for cases rules can't catch. Each entry was verified by hand.
MANUAL_MATCHES = {
    ("Artiso's", "Salt Lake City, Utah"): "Aristos-Greek-Cuisine-Salt-Lake-City-UT",  # Wikipedia typo; S24 revisit as Aristo's
}


def norm(name: str) -> str:
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ").replace("'", "").replace("’", "")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\b(the|restaurant|cafe|and)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def name_score(a: str, b: str, same_city: bool) -> float:
    """Similarity of two normalized names, tolerant of added suffixes like 'Restaurant and Delicatessen'."""
    score = SequenceMatcher(None, a, b).ratio()
    ta, tb = set(a.split()), set(b.split())
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    if short and short <= long_ and any(len(t) >= 4 for t in short):
        score = max(score, 0.9)
    elif same_city and a.split()[:1] == b.split()[:1] and len(a.split()[0]) >= 4 and score >= 0.6:
        score = max(score, 0.88)
    return score


def state_of(location: str) -> str | None:
    if "D.C." in location or "District of Columbia" in location:
        return "DC"
    for part in reversed([p.strip() for p in location.split(",")]):
        if part in STATES:
            return STATES[part]
    return None


def main() -> None:
    wiki = pd.read_csv(INTERIM / "wiki_appearances.csv")
    fp = pd.read_csv(INTERIM / "foodiepie_restaurants.csv")
    fp_eps = pd.read_csv(INTERIM / "foodiepie_episodes.csv")

    wiki["state"] = wiki.location.map(state_of)
    wiki["key"] = wiki.restaurant.map(norm)
    fp["key"] = fp.name.map(norm)
    eps_by_slug = fp_eps.groupby("slug").episode_title.apply(lambda s: {norm(t) for t in s.dropna()})

    restaurants = (
        wiki.groupby(["key", "state"], dropna=False)
        .agg(restaurant=("restaurant", "first"), location=("location", "first"),
             seasons=("season", lambda s: sorted(set(s))),
             air_dates=("air_date", lambda s: sorted(set(s.dropna()))),
             episode_titles=("episode_title", lambda s: {norm(t) for t in s}),
             wiki_closed=("wiki_closed", "any"))
        .reset_index()
    )

    fp_by_state = {st: g for st, g in fp.groupby("state")}
    slugs, methods = [], []
    for r in restaurants.itertuples():
        if (r.restaurant, r.location) in MANUAL_MATCHES:
            slugs.append(MANUAL_MATCHES[(r.restaurant, r.location)]); methods.append("manual")
            continue
        cands = fp_by_state.get(r.state, fp.iloc[0:0])
        exact = cands[cands.key == r.key]
        if len(exact) == 1:
            slugs.append(exact.slug.iloc[0]); methods.append("exact")
            continue
        best, best_score = None, 0.0
        wiki_places = {norm(p) for p in r.location.split(",")}
        for c in cands.itertuples():
            score = name_score(r.key, c.key, same_city=norm(c.city) in wiki_places)
            if r.episode_titles & eps_by_slug.get(c.slug, set()):
                score += 0.1  # shared episode title is strong evidence
            if score > best_score:
                best, best_score = c.slug, score
        if best and best_score >= FUZZY_MIN:
            slugs.append(best); methods.append(f"fuzzy:{best_score:.2f}")
        else:
            slugs.append(None); methods.append("unmatched")
    restaurants["slug"] = slugs
    restaurants["match_method"] = methods

    out = restaurants.merge(fp.drop(columns=["key", "name", "state"]), on="slug", how="left")
    out = out.drop(columns=["key", "episode_titles"])
    out.to_csv(INTERIM / "restaurants.csv", index=False)

    matched = out.slug.notna()
    dupes = out[matched].slug.duplicated(keep=False)
    print(f"wiki restaurants: {len(out)}  matched: {matched.sum()}  unmatched: {(~matched).sum()}")
    print(f"  exact: {(out.match_method == 'exact').sum()}  fuzzy: {out.match_method.str.startswith('fuzzy').sum()}")
    print(f"  foodiepie slugs used twice: {dupes.sum()}")
    print(f"  wiki restaurants with no state parsed: {out.state.isna().sum()}")
    unused = fp[~fp.slug.isin(out.slug)]
    print(f"foodiepie restaurants not matched to wiki: {len(unused)}")
    unused[["name", "city", "state"]].to_csv(INTERIM / "unmatched_foodiepie.csv", index=False)
    out[~matched][["restaurant", "location", "seasons"]].to_csv(INTERIM / "unmatched_wiki.csv", index=False)


if __name__ == "__main__":
    main()
