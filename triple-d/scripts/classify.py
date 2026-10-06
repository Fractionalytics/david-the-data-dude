"""Classify restaurants with Jev. Answers are cached per (slug, definitions version).

    python scripts/classify.py --sample 40    # pilot on a random sample
    python scripts/classify.py                # everything with a description

Reads data/interim/restaurants.csv, appends to data/interim/jev_answers.jsonl.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient

from webdata import load_web
from definitions import DEFINITIONS_VERSION, MODEL, QUESTIONS, name_rule

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
ANSWERS = INTERIM / "jev_answers.jsonl"
load_dotenv(ROOT.parents[1] / ".env")


def state_for(r) -> dict:
    """Only the fields the questions read. Dishes are truncated to keep state small."""
    s = {"name": r.restaurant, "location": r.location}
    for field, col, limit in (("yelp_categories", "yelp_categories", 200), ("description", "notes", 600),
                              ("signature_dishes", "dishes", 600), ("format_tags", "format_tags", 200)):
        val = getattr(r, col, None)
        if isinstance(val, str) and val.strip():
            s[field] = val.strip()[:limit]
    return s


def state_hash(state: dict) -> str:
    return hashlib.sha1(json.dumps(state, sort_keys=True).encode()).hexdigest()[:12]


def done_keys() -> set:
    """Cache key includes the state hash, so new evidence (e.g. a late detail page) re-runs that restaurant."""
    if not ANSWERS.exists():
        return set()
    with ANSWERS.open(encoding="utf-8") as f:
        return {(a["id"], a["definitions_version"], state_hash(a["state"])) for a in map(json.loads, f)}


def load_inputs() -> pd.DataFrame:
    """restaurants.csv plus web-researched descriptions for restaurants foodiepie doesn't have."""
    df = pd.read_csv(INTERIM / "restaurants.csv")
    df["id"] = df.slug.fillna(df.restaurant + "|" + df.location)
    df = df.drop_duplicates("id")
    web = load_web()
    unmatched = df.slug.isna() & df.id.isin(web.index)
    found = unmatched & df.id.map(web.found).fillna(False).astype(bool)
    df.loc[found, "notes"] = df.loc[found, "id"].map(web.description)
    df.loc[found, "format_tags"] = df.loc[found, "id"].map(lambda i: ", ".join(web.format_tags[i] or []))
    df["description_source"] = "none"
    df.loc[df.slug.notna(), "description_source"] = "foodiepie"
    df.loc[found, "description_source"] = "web"
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int)
    args = ap.parse_args()

    df = load_inputs()
    if args.sample:
        df = df.sample(args.sample, random_state=7)
    seen = done_keys()
    todo = [r for r in df.itertuples() if (r.id, DEFINITIONS_VERSION, state_hash(state_for(r))) not in seen]
    print(f"{len(todo)} to classify ({len(df) - len(todo)} cached) with {MODEL}, definitions {DEFINITIONS_VERSION}")

    with TypeSafeClient(model=MODEL, api_key=os.environ["TYPESAFE_API_KEY"]) as client, \
            ANSWERS.open("a", encoding="utf-8") as out:
        for i, r in enumerate(todo, 1):
            state = state_for(r)
            resp = client.system_one(state=state, questions=QUESTIONS)
            a = resp.answers
            out.write(json.dumps({
                "id": r.id,
                "definitions_version": DEFINITIONS_VERSION,
                "model": resp.model,
                "name_rule": name_rule(r.restaurant),
                "choice": a["category"].choice,
                "confidence": a["category"].confidence,
                "probabilities": a["category"].probabilities,
                "noul_diner": a["is_diner"].noul,
                "noul_drive_in": a["is_drive_in"].noul,
                "noul_dive": a["is_dive"].noul,
                "input_tokens": resp.usage.input_tokens,
                "description_source": r.description_source,
                "state": state,
            }) + "\n")
            out.flush()
            if i % 50 == 0:
                print(f"  {i}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
