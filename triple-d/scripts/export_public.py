"""Export the classifier definitions and Jev's raw answers to the public repo.

    python scripts/export_public.py   # -> ../david-the-data-dude/triple-d/

Only facts, our definitions, and Jev's outputs are published. The evidence Jev
read (foodiepie's descriptions and dishes, Yelp categories) is deliberately left
out: it is foodiepie's writing and Yelp's data, used for analysis but not ours
to republish. Writing here does not publish anything; committing and pushing the
public repo does, and needs the user's go-ahead.
"""

import json
from pathlib import Path

import pandas as pd

from definitions import BUCKET_QUESTIONS, BUCKETS, BUCKETS_VERSION, DEFINITIONS, DEFINITIONS_VERSION, MODEL, NAME_RULES, QUESTIONS

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT.parents[2] / "david-the-data-dude" / "triple-d" / "data"
CATS = ["Diner", "Drive-In", "Dive", "Other"]


def question_spec(q) -> dict:
    d = q.model_dump() if hasattr(q, "model_dump") else dict(q)
    return {k: v for k, v in d.items() if v is not None}


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)

    (PUBLIC / "definitions.json").write_text(json.dumps({
        "definitions_version": DEFINITIONS_VERSION,
        "model": MODEL,
        "categories": DEFINITIONS,
        "name_rules": [{"category": c, "regex": p.pattern, "case_insensitive": True} for c, p in NAME_RULES],
        "questions": {k: question_spec(q) for k, q in QUESTIONS.items()},
        "other_buckets": {
            "buckets_version": BUCKETS_VERSION,
            "asked_of": "restaurants whose strict classification is Other",
            "buckets": BUCKETS,
            "questions": {k: question_spec(q) for k, q in BUCKET_QUESTIONS.items()},
        },
        "policies": {
            "strict": "Name rule if one matches, else the Choice question's most likely of the four categories.",
            "forced": "Name rule if one matches, else the most likely of Diner / Drive-In / Dive with Other "
                      "excluded; if there is no unique best (all three 0.00), the restaurant stays Other.",
        },
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    final = pd.read_csv(ROOT / "data" / "final" / "triple_d_restaurants.csv")
    final["id"] = final.slug.fillna(final.restaurant + "|" + final.location)
    with (ROOT / "data" / "interim" / "jev_answers.jsonl").open(encoding="utf-8") as f:
        answers = {a["id"]: a for a in map(json.loads, f) if a["definitions_version"] == DEFINITIONS_VERSION}
    with (ROOT / "data" / "interim" / "jev_buckets.jsonl").open(encoding="utf-8") as f:
        buckets = {a["id"]: a for a in map(json.loads, f) if a["buckets_version"] == BUCKETS_VERSION}

    rows = []
    for r in final.itertuples():
        a = answers[r.id]
        b = buckets.get(r.id) if r.classification == "Other" else None
        rows.append({
            "restaurant": r.restaurant, "location": r.location, "first_air_date": r.first_air_date,
            "model": a["model"], "definitions_version": a["definitions_version"],
            "name_rule": a["name_rule"], "jev_choice": a["choice"], "jev_confidence": a["confidence"],
            **{f"p_{c.lower().replace('-', '_')}": a["probabilities"][c] for c in CATS},
            "is_diner": a["noul_diner"], "is_drive_in": a["noul_drive_in"], "is_dive": a["noul_dive"],
            "jev_bucket": b["bucket"] if b else None, "jev_bucket_confidence": b["confidence"] if b else None,
            "evidence_source": a["description_source"], "input_tokens": a["input_tokens"],
        })
    pd.DataFrame(rows).to_csv(PUBLIC / "jev_output.csv", index=False)
    print(f"{len(rows)} rows -> {PUBLIC / 'jev_output.csv'}; definitions -> {PUBLIC / 'definitions.json'}")


if __name__ == "__main__":
    main()
