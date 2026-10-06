"""Assemble the final one-row-per-restaurant table.

    python scripts/build_final.py   # -> data/final/triple_d_restaurants.csv

Joins the Wikipedia roster, foodiepie and web-research status, and the latest
Jev answers for the current DEFINITIONS_VERSION. Revisits under variant names
(two Wikipedia names matched to one foodiepie restaurant) collapse to one row.
"""

import ast
import json
from pathlib import Path

import pandas as pd

from webdata import load_web
from definitions import BUCKETS_VERSION, DEFINITIONS_VERSION

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
FINAL = ROOT / "data" / "final"
SCORES = {"Diner": "noul_diner", "Drive-In": "noul_drive_in", "Dive": "noul_dive"}

# Country from the parsed state code; restaurants abroad have no state, so use the last part of
# the location. in_us (states, DC, Puerto Rico, USVI) scopes the "American tastes" charts.
CANADA = {"AB", "BC", "ON", "QC", "MB", "NS"}
MEXICO = {"BCS", "COAH", "QR"}
US_TERRITORIES = {"PR": "Puerto Rico", "VI": "U.S. Virgin Islands"}


def country_of(state, location: str) -> str:
    if isinstance(state, str):
        if state in CANADA:
            return "Canada"
        if state in MEXICO:
            return "Mexico"
        return US_TERRITORIES.get(state, "USA")
    return location.split(",")[-1].strip()

# Hand corrections from the user's spot-checks (docs/spot-checks.md). They win over every
# automated signal. classification -> basis "human"; status -> status_source "spot-check".
HUMAN_OVERRIDES = {
    "La-Santisima-Phoenix-AZ": {"status": "Closed", "classification_forced": "Dive",
                                "note": "Burned down in 2025 (spot-check #1)"},
    "Jakes-Good-Eats-Charlotte-NC": {"classification": "Dive", "classification_forced": "Dive",
                                     "note": "Restaurant in a converted gas station; user's call (spot-check #7)"},
}


def as_list(v) -> list:
    return ast.literal_eval(v) if isinstance(v, str) else []


def load_answers() -> pd.DataFrame:
    """Latest answer per restaurant for the current definitions version."""
    with (INTERIM / "jev_answers.jsonl").open(encoding="utf-8") as f:
        rows = [a for a in map(json.loads, f) if a["definitions_version"] == DEFINITIONS_VERSION]
    return pd.DataFrame(rows).drop_duplicates("id", keep="last").set_index("id")


def load_buckets() -> pd.DataFrame:
    """Latest bucket answer per "Other" restaurant (classify_buckets.py), if any."""
    path = INTERIM / "jev_buckets.jsonl"
    if not path.exists():
        return pd.DataFrame(columns=["bucket", "confidence"])
    with path.open(encoding="utf-8") as f:
        rows = [a for a in map(json.loads, f) if a["buckets_version"] == BUCKETS_VERSION]
    return pd.DataFrame(rows).drop_duplicates("id", keep="last").set_index("id")


def main() -> None:
    r = pd.read_csv(INTERIM / "restaurants.csv")
    r["id"] = r.slug.fillna(r.restaurant + "|" + r.location)
    r["seasons"] = r.seasons.map(as_list)
    r["air_dates"] = r.air_dates.map(as_list)

    ent = r.groupby("id").agg(
        restaurant=("restaurant", "first"), location=("location", "first"), state=("state", "first"),
        seasons=("seasons", lambda s: sorted({x for l in s for x in l})),
        air_dates=("air_dates", lambda s: sorted({x for l in s for x in l})),
        wiki_closed=("wiki_closed", "any"), slug=("slug", "first"),
        open_on_foodiepie=("open_on_foodiepie", "first"),
    ).reset_index()

    ans = load_answers()
    missing = ~ent.id.isin(ans.index)
    if missing.any():
        raise SystemExit(f"{missing.sum()} restaurants have no Jev answer for {DEFINITIONS_VERSION}; run classify.py")
    a = ans.loc[ent.id]

    ent["diner_score"] = a.noul_diner.round(3).values
    ent["drive_in_score"] = a.noul_drive_in.round(3).values
    ent["dive_score"] = a.noul_dive.round(3).values
    rule = a.name_rule.values
    strict = a.choice.values
    probs = pd.DataFrame(list(a.probabilities), index=a.index)
    three = probs[list(SCORES)]  # "Other" excluded
    unique_best = three.eq(three.max(axis=1), axis=0).sum(axis=1).eq(1)
    forced = three.idxmax(axis=1).where(unique_best, "Other").values  # no unique best: Guy shrugs
    ent["classification"] = [x or s for x, s in zip(rule, strict)]
    ent["classification_forced"] = [x or f for x, f in zip(rule, forced)]
    ent["classification_basis"] = ["name" if x else "jev" for x in rule]
    ent["jev_confidence"] = a.confidence.round(3).values
    ent["description_source"] = a.description_source.values

    web = load_web()
    web_closed = ent.id.map(web.status).eq("closed") if len(web) else False
    fp_closed = ent.slug.notna() & ~ent.open_on_foodiepie.fillna(True).astype(bool)
    closed = fp_closed | ent.wiki_closed | web_closed
    ent["status"] = closed.map({True: "Closed", False: "Open"})
    ent["status_source"] = [
        ";".join(s for s, flag in (("foodiepie", f), ("wikipedia", w), ("web", x)) if flag)
        for f, w, x in zip(fp_closed, ent.wiki_closed, web_closed)
    ]

    ent["override_note"] = None
    for rid, o in HUMAN_OVERRIDES.items():
        i = ent.index[ent.id == rid]
        if len(i) != 1:
            raise SystemExit(f"override id not found: {rid}")
        for col in ("classification", "classification_forced", "status"):
            if col in o:
                ent.loc[i, col] = o[col]
        if "classification" in o:
            ent.loc[i, "classification_basis"] = "human"
        if "status" in o:
            ent.loc[i, "status_source"] = "spot-check"
        ent.loc[i, "override_note"] = o["note"]

    # detailed_category: Diner / Drive-In / Dive as above, "Other" split into its 12 buckets.
    buckets = load_buckets()
    is_other = ent.classification.eq("Other")
    ent["detailed_category"] = ent.classification.where(~is_other, ent.id.map(buckets.bucket))
    ent["bucket_confidence"] = ent.id.map(buckets.confidence).where(is_other).round(3)
    if ent.detailed_category.isna().any():
        print(f"  note: {ent.detailed_category.isna().sum()} 'Other' restaurants have no bucket yet; run classify_buckets.py")

    ent["country"] = [country_of(st, loc) for st, loc in zip(ent.state, ent.location)]
    ent["in_us"] = ent.country.isin(["USA", *US_TERRITORIES.values()])

    ent["first_air_date"] = ent.air_dates.map(lambda d: d[0] if d else None)
    ent["first_air_year"] = ent.first_air_date.str[:4].astype("Int64")
    ent["appearances"] = ent.air_dates.map(len)
    ent["air_dates"] = ent.air_dates.map("; ".join)
    ent["seasons"] = ent.seasons.map(lambda s: "; ".join(map(str, s)))

    cols = ["restaurant", "location", "state", "country", "in_us", "classification", "classification_forced",
            "detailed_category", "bucket_confidence",
            "diner_score", "drive_in_score", "dive_score", "jev_confidence", "classification_basis",
            "air_dates", "seasons", "first_air_date", "first_air_year", "appearances",
            "status", "status_source", "description_source", "override_note", "slug"]
    out = ent[cols].sort_values(["first_air_date", "restaurant"])
    FINAL.mkdir(parents=True, exist_ok=True)
    out.to_csv(FINAL / "triple_d_restaurants.csv", index=False)

    print(f"{len(out)} restaurants -> {FINAL / 'triple_d_restaurants.csv'}")
    for col in ("classification", "classification_forced", "detailed_category", "status", "description_source"):
        print(f"  {col}: {out[col].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
