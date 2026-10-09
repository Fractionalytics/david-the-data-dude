"""Classify every Ideabrowser idea with Jev (questions in definitions.py).

Reads data/processed/ideas.csv and emails.csv. Appends answers to
data/processed/jev_answers.jsonl (cached by idea, definitions version, mode and input).

One row per idea: eras 1-2 are keyed by their /idea/ slug (first mention wins), the
newsletter era by email id. Featured ideas get their title plus the first 150 words of
the pitch; "more ideas" get the title, or the slug as words when there is no title.

Modes:
  main        the classification used in the analysis
  title_only  featured ideas from the title alone (how far to trust title-only answers)
  reordered   every option list reversed, "Not clear"/"Other" kept last (order-bias check)

Usage:
  python projects/ideabrowser/scripts/classify.py --pilot           # 50 stratified ideas
  python projects/ideabrowser/scripts/classify.py                   # all ideas
  python projects/ideabrowser/scripts/classify.py --mode title_only
  python projects/ideabrowser/scripts/classify.py --mode reordered --sample 100
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

from definitions import DEFINITIONS_VERSION, MODEL, QUESTIONS

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "projects" / "ideabrowser" / "data" / "processed"
ANSWERS = DATA / "jev_answers.jsonl"
PITCH_WORDS = 150
LAST = ("Other", "Not clear", "Not stated")

STOP = re.compile(
    r"Tomorrow's hint|More ideas released today|Also released today|Browse this idea|View this idea|"
    r"View [Ff]ull|Read the full analysis|See the full opportunity|TACTIC OF THE DAY|HIDDEN NICHE|"
    r"━{5,}|-{10,}|🕒"
)


def squash(s):
    return re.sub(r"\s+", " ", s).strip()


def pitch(body, title):
    """Text after the featured title (or the 'Idea of the Day' heading), up to the next section."""
    i = squash(body).lower().find(squash(title).lower()[:40])
    if i >= 0:
        flat = squash(body)
        rest = flat[i + len(squash(title)):]
    else:
        m = re.search(r"^(📌\s*)?(IDEA OF THE DAY|Idea of the Day)\s*$", body, re.M)
        if not m:
            return ""
        rest = squash(body[m.end():])
    stop = STOP.search(rest)
    rest = rest[: stop.start()] if stop else rest
    rest = re.sub(r"^\(\$[^)]*\)\s*", "", rest)  # money tag right after the title
    rest = re.sub(r"\b\w+ \d{1,2}, 20\d\d\b", "", rest, count=1)  # date line
    return " ".join(rest.split()[:PITCH_WORDS])


def load_ideas():
    ideas = pd.read_csv(DATA / "ideas.csv")
    bodies = pd.read_csv(DATA / "emails.csv").set_index("id").body_text
    ideas["key"] = ideas.slug.fillna("email:" + ideas.email_id)
    ideas = ideas.drop_duplicates("key")
    ideas["title"] = ideas.title.fillna(ideas.slug.str.replace("-", " "))
    ideas["pitch"] = [
        pitch(bodies[r.email_id], r.title) if r.role == "featured" else ""
        for r in ideas.itertuples()
    ]
    return ideas


def questions_for(mode):
    if mode != "reordered":
        return QUESTIONS
    out = {}
    for qid, q in QUESTIONS.items():
        named = [k for k in q.criteria if k not in LAST][::-1]
        last = [k for k in q.criteria if k in LAST]
        out[qid] = Choice(instructions=q.instructions, criteria={k: q.criteria[k] for k in named + last})
    return out


def state_for(r, mode):
    if r.role == "featured" and mode != "title_only":
        return {"idea_title": r.title, "idea_pitch": r.pitch}
    return {"idea_title": r.title}


def state_hash(state):
    return hashlib.sha1(json.dumps(state, sort_keys=True).encode()).hexdigest()[:12]


def done_keys():
    if not ANSWERS.exists():
        return set()
    with ANSWERS.open(encoding="utf-8") as f:
        return {(a["key"], a["definitions_version"], a["mode"], a["state_hash"]) for a in map(json.loads, f)}


def pilot_sample(ideas):
    """50 ideas: 10 from each era x role cell."""
    cells = ideas.groupby(["era", "role"], group_keys=False)
    return cells.apply(lambda g: g.sample(min(10, len(g)), random_state=7))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["main", "title_only", "reordered"], default="main")
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--sample", type=int)
    args = ap.parse_args()
    load_dotenv(ROOT / ".env")

    ideas = load_ideas()
    if args.mode == "title_only":
        ideas = ideas[ideas.role == "featured"]
    if args.pilot:
        ideas = pilot_sample(ideas)
    elif args.sample:
        ideas = ideas.sample(args.sample, random_state=11)

    seen = done_keys()
    todo = [r for r in ideas.itertuples()
            if (r.key, DEFINITIONS_VERSION, args.mode, state_hash(state_for(r, args.mode))) not in seen]
    print(f"{len(todo)} to classify ({len(ideas) - len(todo)} cached), mode {args.mode}, "
          f"{MODEL}, definitions {DEFINITIONS_VERSION}")

    questions = questions_for(args.mode)
    with TypeSafeClient(model=MODEL, api_key=os.environ["TYPESAFE_API_KEY"]) as client, \
            ANSWERS.open("a", encoding="utf-8") as out:
        for i, r in enumerate(todo, 1):
            state = state_for(r, args.mode)
            resp = client.system_one(state=state, questions=questions)
            row = {"key": r.key, "definitions_version": DEFINITIONS_VERSION, "mode": args.mode,
                   "model": resp.model, "state_hash": state_hash(state), "state": state,
                   "input_tokens": resp.usage.input_tokens}
            for qid in questions:
                a = resp.answers[qid]
                row[qid] = a.choice
                row[qid + "_confidence"] = a.confidence
                row[qid + "_probabilities"] = a.probabilities
            out.write(json.dumps(row) + "\n")
            out.flush()
            if i % 50 == 0:
                print(f"  {i}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
