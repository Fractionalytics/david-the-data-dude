"""Is the customer an AI agent? One Jev yes/no question across all 1,433 ideas.

Approved by David 2026-10-08 after the bottom-up themes (docs/themes.md) found "tools for AI
agents themselves" as the most stable, fastest-rising theme. Featured ideas get title + pitch,
"more ideas" the title only. --mode title_only reruns the featured ideas from their titles to
measure how much certainty is lost without a pitch.
Appends to data/processed/agent_customer_answers.jsonl, cached by idea, version, mode and input.

Usage:
  python projects/ideabrowser/scripts/classify_agent_customer.py
  python projects/ideabrowser/scripts/classify_agent_customer.py --mode title_only
"""
import argparse
import json
import os

from dotenv import load_dotenv
from typesafe_sdk import Noul, TypeSafeClient

from classify import DATA, ROOT, load_ideas, state_for, state_hash
from definitions import MODEL

VERSION = "a1"
ANSWERS = DATA / "agent_customer_answers.jsonl"

QUESTIONS = {
    "agent_customer": Noul(instructions=(
        "Is this business idea built for AI agents as its customers or users? "
        "Yes if the product exists to serve, protect, monitor, test, supply, rate or sell to AI agents "
        "(software agents acting on their own), for example trust scores, sandboxes or data feeds for agents. "
        "No if it uses AI agents to serve people or businesses, such as an AI receptionist or an AI agent "
        "that does a job for a company."
    )),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["main", "title_only"], default="main")
    args = ap.parse_args()
    load_dotenv(ROOT / ".env")

    ideas = load_ideas()
    if args.mode == "title_only":
        ideas = ideas[ideas.role == "featured"]
    seen = set()
    if ANSWERS.exists():
        seen = {(a["key"], a["version"], a["mode"], a["state_hash"]) for a in map(json.loads, ANSWERS.open(encoding="utf-8"))}
    todo = [r for r in ideas.itertuples()
            if (r.key, VERSION, args.mode, state_hash(state_for(r, args.mode))) not in seen]
    print(f"{len(todo)} to score ({len(ideas) - len(todo)} cached), mode {args.mode}, {MODEL}, version {VERSION}")

    with TypeSafeClient(model=MODEL, api_key=os.environ["TYPESAFE_API_KEY"]) as client, \
            ANSWERS.open("a", encoding="utf-8") as out:
        for i, r in enumerate(todo, 1):
            state = state_for(r, args.mode)
            resp = client.system_one(state=state, questions=QUESTIONS)
            out.write(json.dumps({"key": r.key, "version": VERSION, "mode": args.mode, "model": resp.model,
                                  "state_hash": state_hash(state),
                                  "agent_customer": resp.answers["agent_customer"].noul}) + "\n")
            out.flush()
            if i % 100 == 0:
                print(f"  {i}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
