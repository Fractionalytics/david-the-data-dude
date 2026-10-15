"""Classify each 2026 MLB surname by origin with Jev (question in definitions.py).

Reads data/processed/players_2026.csv (players who appeared: has_war) and
data/processed/etymology.json (fetch_etymology.py). One Jev call per unique
(surname, birth country) pair, so "Lee" from Korea and "Lee" from the USA are asked
separately. Each half of a compound surname (Crow, Armstrong) is also asked, as a
"part" row; the player's primary type is Compound (decided in code, names.is_compound).

State: surname, birth_country, and the Wiktionary etymology (up to 3 language sections,
the language likeliest for the birth country first), or "No dictionary entry found."
Roster contenders with uncertain types were researched on the web (data/interim/contenders.csv,
web_etymology_*.json); their summary goes first, with any Wiktionary text after it.

Answers append to data/processed/jev_answers.jsonl, cached by key, definitions version,
mode and etymology text (a changed etymology is re-asked; the latest answer wins).

Modes:
  main        the classification used in the analysis
  reordered   option list reversed, "Other" kept last (order-bias check)

Usage:
  python projects/world-series/scripts/classify.py --pilot      # ~50 names, stratified by country
  python projects/world-series/scripts/classify.py              # all
  python projects/world-series/scripts/classify.py --mode reordered --sample 100
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
from fetch_etymology import order_for, strip_accents
from names import compound_parts, is_compound, surname

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "projects" / "world-series" / "data" / "processed"
ANSWERS = DATA / "jev_answers.jsonl"
NO_ENTRY = "No dictionary entry found."
NATIVE_ONLY = {"Republic of Korea": ["Korean"], "Taiwan": ["Chinese"]}
LATAM = ["Dominican Republic", "Venezuela", "Cuba", "Puerto Rico", "Mexico"]
# Surnames always in the pilot (David's example and boundary cases).
PILOT_MUST = ["Ohtani", "Burke", "Warren", "Paez", "Kim", "Smith", "King", "De Paula", "De Jesus", "Lee",
              "Kiner-Falefa", "Crow-Armstrong"]


def informative(text):
    """True when an entry says more than 'surname'."""
    rest = re.sub(r"(Etymology:|Definitions:|surname|countable|male|female|[.\s,])", "", text, flags=re.I)
    return len(rest) >= 4  # "Velasco -ez" is enough


def etymology_text(entries, country):
    secs = [(e["language"], e["text"]) for e in entries if informative(e["text"])]
    if country in NATIVE_ONLY:  # English "Lee" (meadow) is the wrong word for a Korean or Taiwanese Lee
        secs = [s for s in secs if s[0] in NATIVE_ONLY[country]]
    secs = order_for(secs, country)[:3]
    return " | ".join(f"{lang}: {txt}" for lang, txt in secs) if secs else NO_ENTRY


def load_names():
    p = pd.read_csv(DATA / "players_2026.csv")
    p = p[p.has_war].copy()
    p["surname"] = p.use_last_name.map(surname)
    rows = p.drop_duplicates(["surname", "birth_country"])[["surname", "birth_country"]].assign(part_of="")
    parts = [{"surname": w, "birth_country": r.birth_country, "part_of": r.surname}
             for r in rows.itertuples() if is_compound(r.surname) for w in compound_parts(r.surname)]
    names = pd.concat([rows, pd.DataFrame(parts)], ignore_index=True)
    names["key"] = (names.part_of.where(names.part_of == "", "part:" + names.part_of + ":")
                    + names.surname + "|" + names.birth_country)
    ety = json.loads((DATA / "etymology.json").read_text(encoding="utf-8"))
    names["etymology"] = [etymology_text(ety.get(r.surname) or ety.get(strip_accents(r.surname)) or [],
                                         r.birth_country) for r in names.itertuples()]
    names["ety_source"] = (names.etymology != NO_ENTRY).map({True: "wiktionary", False: "none"})
    web = web_etymology()
    for i, r in names.iterrows():
        if r.surname in web:
            wikt = "" if r.etymology == NO_ENTRY else f" | Wiktionary: {r.etymology}"
            names.at[i, "etymology"] = f"Surname dictionaries: {web[r.surname]}{wikt}"
            names.at[i, "ety_source"] = "web" if not wikt else "web+wiktionary"
    return names


def web_etymology():
    """Web-researched origins for roster contenders (data/interim/web_etymology_*.json)."""
    out = {}
    for f in sorted((ROOT / "projects" / "world-series" / "data" / "interim").glob("web_etymology_*.json")):
        for e in json.loads(f.read_text(encoding="utf-8")):
            if e.get("evidence_strength") != "none":
                out[e["surname"]] = e["origin_summary"]
    return out


def ety_hash(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def questions_for(mode):
    if mode != "reordered":
        return QUESTIONS
    out = {}
    for qid, q in QUESTIONS.items():
        named = [k for k in q.criteria if k != "Other"][::-1]
        out[qid] = Choice(instructions=q.instructions, criteria={k: q.criteria[k] for k in named + ["Other"]})
    return out


def done_keys():
    if not ANSWERS.exists():
        return set()
    with ANSWERS.open(encoding="utf-8") as f:
        return {(a["key"], a["definitions_version"], a["mode"], ety_hash(a.get("etymology", ""))) for a in map(json.loads, f)}


def pilot_sample(names):
    must = names[names.surname.isin(PILOT_MUST) | names.part_of.isin(PILOT_MUST)]
    rest = names.drop(must.index)
    rest = rest[rest.part_of == ""]
    usa = rest[rest.birth_country == "USA"].sample(20, random_state=7)
    latam = rest[rest.birth_country.isin(LATAM)].sample(12, random_state=7)
    other = rest[~rest.birth_country.isin(["USA"] + LATAM)].sample(9, random_state=7)
    return pd.concat([must, usa, latam, other])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["main", "reordered"], default="main")
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--sample", type=int)
    args = ap.parse_args()
    load_dotenv(ROOT / ".env")

    names = load_names()
    if args.pilot:
        names = pilot_sample(names)
    elif args.sample:
        names = names[names.part_of == ""].sample(args.sample, random_state=11)

    seen = done_keys()
    todo = [r for r in names.itertuples() if (r.key, DEFINITIONS_VERSION, args.mode, ety_hash(r.etymology)) not in seen]
    print(f"{len(todo)} to classify ({len(names) - len(todo)} cached), mode {args.mode}, "
          f"{MODEL}, definitions {DEFINITIONS_VERSION}; "
          f"with etymology: {(names.etymology != NO_ENTRY).sum()}/{len(names)}")

    questions = questions_for(args.mode)
    with TypeSafeClient(model=MODEL, api_key=os.environ["TYPESAFE_API_KEY"]) as client, \
            ANSWERS.open("a", encoding="utf-8") as out:
        for i, r in enumerate(todo, 1):
            state = {"surname": r.surname, "birth_country": r.birth_country, "etymology": r.etymology}
            resp = client.system_one(state=state, questions=questions)
            row = {"key": r.key, "surname": r.surname, "birth_country": r.birth_country,
                   "part_of": r.part_of, "compound": is_compound(r.surname),
                   "has_etymology": r.etymology != NO_ENTRY, "ety_source": r.ety_source, "etymology": r.etymology,
                   "definitions_version": DEFINITIONS_VERSION, "mode": args.mode, "model": resp.model,
                   "input_tokens": resp.usage.input_tokens}
            for qid in questions:
                a = resp.answers[qid]
                row[qid] = a.choice
                row[qid + "_confidence"] = a.confidence
                row[qid + "_probabilities"] = a.probabilities
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            if i % 50 == 0:
                print(f"  {i}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
