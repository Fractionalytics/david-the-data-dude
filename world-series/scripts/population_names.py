"""The most common surnames in the US population for each team, by language of origin.

Population: US Census Bureau, 2010 Census surname file (public domain), downloaded to
data/raw/cache/census/Names_2010Census.csv from
https://www2.census.gov/topics/genealogy/2010surnames/names.zip

Method (same as the player classification):
- Take the TOP_N most common surnames.
- Fetch each name's Wiktionary etymology (fetch_etymology.py), language sections ordered
  Spanish first when most US bearers are Hispanic, English first otherwise.
- Ask Jev two Choice questions: the surname type (the v5 criteria from definitions.py, with
  Matronymic merged into Patronymic) and the language the surname comes from.
- "Spanish-origin" needs both Jev's language answer = Spanish and a Hispanic majority among US
  bearers (Census pcthispanic >= 50). "English-origin" is Jev's British Isles answer
  (English, Scottish, Welsh or Irish).

Answers cache in data/processed/population_jev.jsonl. Output: data/processed/population_top_names.csv
"""
import hashlib
import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

from classify import etymology_text, NO_ENTRY
from definitions import MODEL, SURNAME_TYPE
from fetch_etymology import extract, fetch

ROOT = Path(__file__).resolve().parents[3]
PROJ = ROOT / "projects" / "world-series"
CENSUS = PROJ / "data" / "raw" / "cache" / "census" / "Names_2010Census.csv"
ANSWERS = PROJ / "data" / "processed" / "population_jev.jsonl"
OUT = PROJ / "data" / "processed" / "population_top_names.csv"
TOP_N = 500
VERSION = "p1"
TEAM = {"Toponymic": "The Places", "Cognominal": "The Nicknames", "Patronymic": "The Sons of Somebody",
        "Occupational": "The Jobs"}

QUESTIONS = {
    "surname_type": Choice(
        instructions=(
            "Classify the surname in `surname` by how the surname originally arose (its etymology). "
            "`etymology` is what surname dictionaries say about the surname, possibly for several "
            "languages or origins, the most likely first; base the answer on its best-supported "
            "origin when it explains one, otherwise on your own knowledge. `us_bearers` describes who "
            "carries the name in the United States; use it only as a hint to the language."),
        criteria=SURNAME_TYPE,
    ),
    "language": Choice(
        instructions=(
            "Which language or region does the surname in `surname` come from, for most of the people "
            "who carry it in the United States? Use `etymology` and `us_bearers`."),
        criteria={
            "British Isles": "English, Scottish, Welsh or Irish, including anglicized Gaelic names (Smith, Jones, Kelly, Campbell).",
            "Spanish or Portuguese": "Spanish or Portuguese, including names common across Latin America (Garcia, Rodriguez, Silva).",
            "German or Dutch": "German, Dutch or Scandinavian (Schmidt, Mueller, Peterson spelled Petersen, Van Dyke).",
            "Other": "Any other language, such as Italian, French, Polish, Chinese, Vietnamese, Korean or Arabic.",
        },
    ),
}


def us_bearers(pct_hispanic):
    return ("Most US bearers are Hispanic." if pct_hispanic >= 50
            else "Most US bearers are not Hispanic.")


def main():
    load_dotenv(ROOT / ".env")
    c = pd.read_csv(CENSUS, na_values=["(S)"]).head(TOP_N)
    c["surname"] = c.name.str.title()
    c["pcthispanic"] = c.pcthispanic.fillna(0)

    pages = fetch(sorted(c.surname))
    rows = []
    for r in c.itertuples():
        entries = [{"language": l, "text": x} for l, x in extract(pages.get(r.surname) or "")]
        country = "Mexico" if r.pcthispanic >= 50 else "USA"  # orders Spanish or English sections first
        rows.append(etymology_text(entries, country))
    c["etymology"] = rows

    done = {}
    if ANSWERS.exists():
        for a in map(json.loads, ANSWERS.open(encoding="utf-8")):
            done[(a["surname"], a["version"], a["state_hash"])] = a
    with TypeSafeClient(model=MODEL, api_key=os.environ["TYPESAFE_API_KEY"]) as client, \
            ANSWERS.open("a", encoding="utf-8") as out:
        answers = []
        for r in c.itertuples():
            state = {"surname": r.surname, "etymology": r.etymology, "us_bearers": us_bearers(r.pcthispanic)}
            h = hashlib.sha1(json.dumps(state, sort_keys=True).encode()).hexdigest()[:12]
            a = done.get((r.surname, VERSION, h))
            if a is None:
                resp = client.system_one(state=state, questions=QUESTIONS)
                a = {"surname": r.surname, "version": VERSION, "state_hash": h, "model": resp.model}
                for q in QUESTIONS:
                    a[q] = resp.answers[q].choice
                    a[q + "_confidence"] = resp.answers[q].confidence
                out.write(json.dumps(a, ensure_ascii=False) + "\n")
                out.flush()
            answers.append(a)

    a = pd.DataFrame(answers)
    c = c.join(a[["surname_type", "surname_type_confidence", "language", "language_confidence"]])
    c["surname_type"] = c.surname_type.replace({"Matronymic": "Patronymic"})
    c["origin"] = None
    c.loc[c.language == "British Isles", "origin"] = "English"
    c.loc[(c.language == "Spanish or Portuguese") & (c.pcthispanic >= 50), "origin"] = "Spanish"
    c["has_etymology"] = c.etymology != NO_ENTRY
    c["team"] = c.surname_type.map(TEAM)
    c[["rank", "surname", "count", "pcthispanic", "origin", "language", "language_confidence", "surname_type",
       "surname_type_confidence", "team", "has_etymology", "etymology"]].to_csv(OUT, index=False, encoding="utf-8")

    top = c[c.team.notna() & c.origin.notna()]
    for (team, origin), g in top.groupby(["team", "origin"]):
        names = ", ".join(f"{r.surname} (#{r.rank}, {r.count:,})" for r in g.head(5).itertuples())
        print(f"{team:<22}{origin:<9}{names}")


if __name__ == "__main__":
    main()
