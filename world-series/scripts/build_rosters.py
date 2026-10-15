"""Build each surname type's best 13-man roster by 2026 bWAR and crown the World Series of Last Names.

Inputs (data/processed/): players_2026.csv, positions_2026.csv, jev_answers.jsonl (definitions
version and mode "main" only), and data/compound_parts_research.csv.

Surname type:
- Compound (names.is_compound) when the surname joins two surnames; its two halves get types
  from the hand research in compound_parts_research.csv. When both halves share a type
  (Crow-Armstrong: Cognominal + Cognominal), the player plays for that type instead.
- Otherwise Jev's Choice. A tie for the top probability is "Other" (no column-order argmax).
- Matronymic answers are merged into Patronymic (David, 2026-10-11): "Patronymic" means
  named after a parent, and includes a few matronymics (raw answer kept in jev_type).
- Hand decisions in data/overrides.csv (who decided, when, source) win over everything above.

Roster: P x4, C, 1B, 2B, 3B, SS, OF x3, DH, each the highest-WAR player whose 2026 primary
position matches. A team short at a position fills the empty slot with its best remaining
player of any position (David: short teams "make do"); with nobody left the slot stays empty.
Shohei Ohtani (TWP) counts with his combined pitching + batting WAR and is placed as P or DH,
whichever gives the Toponymic team the higher total.

Scenario "free agents": each compound player may instead play for either half's team.
Every combination is evaluated.

Outputs: data/processed/players_final.csv, rosters.csv, standings.csv, free_agents.csv
"""
import itertools
import json
from pathlib import Path

import pandas as pd

from definitions import DEFINITIONS_VERSION
from names import is_compound, surname

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
MERGE = {"Matronymic": "Patronymic"}
SLOTS = [("P", 4), ("C", 1), ("1B", 1), ("2B", 1), ("3B", 1), ("SS", 1), ("OF", 3), ("DH", 1)]


def jev_types():
    rows = [a for a in map(json.loads, (DATA / "jev_answers.jsonl").open(encoding="utf-8"))
            if a["definitions_version"] == DEFINITIONS_VERSION and a["mode"] == "main" and not a["part_of"]]
    out = {}
    for a in rows:
        probs = a["surname_type_probabilities"]
        top = max(probs.values())
        tied = sum(v == top for v in probs.values()) > 1
        out[a["key"]] = {"jev_type": "Other" if tied else a["surname_type"], "jev_tie": tied,
                         "jev_confidence": a["surname_type_confidence"], "has_etymology": a["has_etymology"],
                         "ety_source": a.get("ety_source", "wiktionary" if a["has_etymology"] else "none")}
    return out


def load_players():
    p = pd.read_csv(DATA / "players_2026.csv")
    p = p[p.has_war].copy()
    pos = pd.read_csv(DATA / "positions_2026.csv")[["mlb_id", "primary_pos"]]
    p = p.merge(pos, on="mlb_id", how="left")
    p["surname"] = p.use_last_name.map(surname)
    p["compound"] = p.surname.map(is_compound)
    jt = pd.DataFrame.from_dict(jev_types(), orient="index")
    p = p.join(jt, on=p.surname + "|" + p.birth_country)
    missing = p.jev_type.isna() & ~p.compound
    assert not missing.any(), f"{missing.sum()} players without a Jev answer"
    # Matronymic is merged into Patronymic (David, 2026-10-11); jev_type keeps the raw answer.
    p["surname_type"] = p.jev_type.replace(MERGE).where(~p.compound, "Compound")
    # A compound whose two halves share a type plays for that type (David, 2026-10-11: Crow-Armstrong).
    halves = pd.read_csv(ROOT / "data" / "compound_parts_research.csv").groupby("compound").hand_type.agg(set)
    same = {c: next(iter(t)) for c, t in halves.items() if len(t) == 1}
    p.loc[p.surname.isin(same), "surname_type"] = p.surname.map(same)
    over = pd.read_csv(ROOT / "data" / "overrides.csv").set_index("surname").surname_type
    p["overridden"] = p.surname.isin(over.index)
    p.loc[p.overridden, "surname_type"] = p.surname.map(over)
    # How the type is known: a source (dictionary or web research), a hand decision, or Jev alone.
    p["evidence"] = p.ety_source.map({"wiktionary": "source", "web": "source", "web+wiktionary": "source"}).fillna("jev_only")
    p.loc[p.compound, "evidence"] = "hand"
    p.loc[p.overridden, "evidence"] = "hand"
    return p


def roster(team):
    """Best roster for one team: list of dicts (slot, player, pos, war)."""
    options = [team]
    twp = team[team.primary_pos == "TWP"]
    if len(twp):
        options = [team.assign(primary_pos=team.primary_pos.replace("TWP", as_pos)) for as_pos in ("P", "DH")]
    best = None
    for t in options:
        t = t.sort_values("war_total", ascending=False)
        picked, empty = [], []
        for pos, n in SLOTS:
            pool = t[t.primary_pos == pos].head(n)
            picked += [{"slot": pos, **r} for r in pool.to_dict("records")]
            empty += [pos] * (n - len(pool))
        used = {r["mlb_id"] for r in picked}
        rest = t[~t.mlb_id.isin(used)]
        for slot, r in zip(empty, rest.to_dict("records")):
            picked.append({"slot": f"{slot} (flex)", **r})
        total = sum(r["war_total"] for r in picked)
        if best is None or total > best[0]:
            best = (total, picked)
    return best[1]


def standings(players):
    rows, rosters = [], []
    for team, g in players.groupby("surname_type"):
        r = roster(g)
        rosters += [{"team": team, **x} for x in r]
        rows.append({"team": team, "players": len(g), "roster_war": round(sum(x["war_total"] for x in r), 2),
                     "flex_slots": sum("flex" in x["slot"] for x in r), "roster_size": len(r)})
    return pd.DataFrame(rows).sort_values("roster_war", ascending=False), pd.DataFrame(rosters)


def main():
    p = load_players()
    p.to_csv(DATA / "players_final.csv", index=False, encoding="utf-8")
    table, rosters = standings(p)
    table.to_csv(DATA / "standings.csv", index=False)
    rosters.to_csv(DATA / "rosters.csv", index=False, encoding="utf-8")
    print(f"ties sent to Other: {int(p.jev_tie.fillna(False).sum())}")
    print(table.to_string(index=False))

    # Free agents: each compound player picks Compound or either half's team.
    research = pd.read_csv(ROOT / "data" / "compound_parts_research.csv")
    halves = research.groupby("compound").hand_type.apply(list).to_dict()
    comp = p[p.surname_type == "Compound"]
    choices = [sorted({"Compound", *halves[s]}) for s in comp.surname]
    results = []
    for combo in itertools.product(*choices):
        q = p.copy()
        q.loc[comp.index, "surname_type"] = combo
        t, _ = standings(q)
        results.append({**{n: c for n, c in zip(comp.full_name, combo)},
                        "champion": t.iloc[0].team, "champion_war": t.iloc[0].roster_war,
                        **{f"war_{r.team}": r.roster_war for r in t.itertuples()}})
    fa = pd.DataFrame(results)
    fa.to_csv(DATA / "free_agents.csv", index=False, encoding="utf-8")
    print(f"\nfree-agent combinations: {len(fa)}; champions: {fa.champion.value_counts().to_dict()}")
    war_cols = [c for c in fa.columns if c.startswith("war_")]
    print("best possible total per team:", fa[war_cols].max().sort_values(ascending=False).round(2).to_dict())


if __name__ == "__main__":
    main()
