"""Score the 424 featured ideas against Greg Isenberg's 13 "businesses left to build".

Exploratory, approved by David 2026-10-07 (docs/greg-13.md). One yes/no (Noul) question
per type, because the types overlap; code combines them. Featured ideas only, title + pitch.
Appends to data/processed/greg13_answers.jsonl, cached by idea, version and input.

Usage: python projects/ideabrowser/scripts/classify_greg13.py
"""
import json
import os

from dotenv import load_dotenv
from typesafe_sdk import Noul, TypeSafeClient

from classify import DATA, ROOT, load_ideas, state_for, state_hash
from definitions import MODEL

VERSION = "g1"
ANSWERS = DATA / "greg13_answers.jsonl"

TYPES = {
    "ai_service_firm": ("an AI native service firm",
                        "The customer buys a finished result (bookkeeping done, calls answered) delivered by a firm "
                        "using AI, not software the customer runs themselves. A SaaS tool the customer operates is no."),
    "offline": ("an offline business",
                "The business mainly operates in the physical world: in person, local, on site. "
                "An app for an offline industry is no."),
    "distribution": ("a distribution business (media, community, audience)",
                     "The business is itself an audience: a newsletter, media brand, community or creator channel. "
                     "Merely using social media for marketing is no."),
    "proprietary_data": ("a proprietary dataset business",
                         "The core asset is data others can't easily get, collected or built by the business. "
                         "Using public data or an API is no."),
    "domain_harness": ("a domain-specific harness",
                       "Software or an AI agent that runs one industry's whole workflow end to end. "
                       "Handling a single task within the workflow is no."),
    "robotics": ("a robotics or physical AI business",
                 "Robots, drones, sensors or AI acting in the physical world."),
    "fan_product": ("a physical product with a fan following",
                    "A physical product sold to an enthusiast or fan community. Commodity goods are no."),
    "compute_energy": ("a compute or energy business",
                       "Selling compute, chips, power, energy, or energy savings."),
    "health_care": ("a health, longevity or care business",
                    "Health, medical care, longevity, caregiving, or elder or child care. "
                    "A general fitness app is yes only if health is its core claim."),
    "marketplace_social": ("a marketplace or social network",
                           "Connects two sides (buyers and sellers, people, or AI agents), or is a social network."),
    "real_assets": ("a real assets business",
                    "Owns, finances or trades property, equipment, land or infrastructure. "
                    "Software for real estate agents is no."),
    "vertical_agent": ("a vertical agent",
                       "An AI agent that does one specific job for one industry. A general-purpose AI tool is no."),
    "security": ("a security business",
                 "Cybersecurity, fraud prevention, physical security, or identity."),
}

QUESTIONS = {k: Noul(instructions=f"Is this business idea {name}? Yes if: {rule}") for k, (name, rule) in TYPES.items()}


def main():
    load_dotenv(ROOT / ".env")
    ideas = load_ideas()
    ideas = ideas[ideas.role == "featured"]
    seen = set()
    if ANSWERS.exists():
        seen = {(a["key"], a["version"], a["state_hash"]) for a in map(json.loads, ANSWERS.open(encoding="utf-8"))}
    todo = [r for r in ideas.itertuples() if (r.key, VERSION, state_hash(state_for(r, "main"))) not in seen]
    print(f"{len(todo)} to score ({len(ideas) - len(todo)} cached), {MODEL}, version {VERSION}")

    with TypeSafeClient(model=MODEL, api_key=os.environ["TYPESAFE_API_KEY"]) as client, \
            ANSWERS.open("a", encoding="utf-8") as out:
        for i, r in enumerate(todo, 1):
            state = state_for(r, "main")
            resp = client.system_one(state=state, questions=QUESTIONS)
            row = {"key": r.key, "version": VERSION, "model": resp.model, "state_hash": state_hash(state)}
            row.update({k: resp.answers[k].noul for k in QUESTIONS})
            out.write(json.dumps(row) + "\n")
            out.flush()
            if i % 50 == 0:
                print(f"  {i}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
