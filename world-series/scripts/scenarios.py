"""What-if standings: move named players to another team and see who wins.

The script's "it comes down to one player" beat. Reads data/processed/players_final.csv
(build_rosters.py) and prints the top three for each scenario below. Edit SCENARIOS to add more.

Output: data/processed/scenarios.csv (scenario, rank, team, roster_war)
"""
from pathlib import Path

import pandas as pd

from build_rosters import standings

DATA = Path(__file__).resolve().parents[1] / "data" / "processed"
SCENARIOS = {
    "as is": {},
    "Messick unknown": {"Parker Messick": "Other"},
    "Skubal Cognominal (Czech nickname 'plucked')": {"Tarik Skubal": "Cognominal"},
    "Duran Patronymic (from the name Durand)": {"Ezequiel Duran": "Patronymic"},
    "Bolte Patronymic (from the name Baldo)": {"Henry Bolte": "Patronymic"},
    "Skubal, Duran, Bolte by their sources": {"Tarik Skubal": "Cognominal", "Ezequiel Duran": "Patronymic",
                                             "Henry Bolte": "Patronymic"},
    "those three + Messick unknown": {"Tarik Skubal": "Cognominal", "Ezequiel Duran": "Patronymic",
                                      "Henry Bolte": "Patronymic", "Parker Messick": "Other"},
}


def main():
    p = pd.read_csv(DATA / "players_final.csv")
    out = []
    for name, moves in SCENARIOS.items():
        q = p.copy()
        for player, team in moves.items():
            assert (q.full_name == player).sum() == 1, player
            q.loc[q.full_name == player, "surname_type"] = team
        table, _ = standings(q)
        top = table.head(3).reset_index(drop=True)
        out += [{"scenario": name, "rank": i + 1, "team": r.team, "roster_war": r.roster_war} for i, r in top.iterrows()]
        print(f"{name:<46}" + " | ".join(f"{r.team} {r.roster_war}" for r in top.itertuples()))
    pd.DataFrame(out).to_csv(DATA / "scenarios.csv", index=False)


if __name__ == "__main__":
    main()
