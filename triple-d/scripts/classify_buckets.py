"""Put each "Other" restaurant into one of the 12 buckets in definitions.BUCKETS.

    python scripts/classify_buckets.py   # needs data/final from build_final.py

Uses the same evidence (state) as classify.py. Answers are appended to
data/interim/jev_buckets.jsonl, cached by (restaurant id, BUCKETS_VERSION, state).
Run build_final.py afterwards to fill the detailed_category column.
"""

import json
import os

import pandas as pd
from typesafe_sdk import TypeSafeClient

from classify import INTERIM, load_inputs, state_for, state_hash
from definitions import BUCKET_QUESTIONS, BUCKETS_VERSION, MODEL

ROOT = INTERIM.parent.parent
ANSWERS = INTERIM / "jev_buckets.jsonl"


def done_keys() -> set:
    if not ANSWERS.exists():
        return set()
    with ANSWERS.open(encoding="utf-8") as f:
        return {(a["id"], a["buckets_version"], state_hash(a["state"])) for a in map(json.loads, f)}


def main() -> None:
    final = pd.read_csv(ROOT / "data" / "final" / "triple_d_restaurants.csv")
    final["id"] = final.slug.fillna(final.restaurant + "|" + final.location)
    other_ids = set(final.loc[final.classification == "Other", "id"])
    df = load_inputs()
    df = df[df.id.isin(other_ids)]
    seen = done_keys()
    todo = [r for r in df.itertuples() if (r.id, BUCKETS_VERSION, state_hash(state_for(r))) not in seen]
    print(f"{len(todo)} to bucket ({len(df) - len(todo)} cached) with {MODEL}, buckets {BUCKETS_VERSION}")

    with TypeSafeClient(model=MODEL, api_key=os.environ["TYPESAFE_API_KEY"]) as client, \
            ANSWERS.open("a", encoding="utf-8") as out:
        for i, r in enumerate(todo, 1):
            state = state_for(r)
            resp = client.system_one(state=state, questions=BUCKET_QUESTIONS)
            a = resp.answers["bucket"]
            out.write(json.dumps({
                "id": r.id,
                "buckets_version": BUCKETS_VERSION,
                "model": resp.model,
                "bucket": a.choice,
                "confidence": a.confidence,
                "probabilities": a.probabilities,
                "input_tokens": resp.usage.input_tokens,
                "state": state,
            }) + "\n")
            out.flush()
            if i % 100 == 0:
                print(f"  {i}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
