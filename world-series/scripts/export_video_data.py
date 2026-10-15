"""Export what the Remotion video needs to video/src/data/video.json.

- teams: the four named teams (David's names, design/make_logos.py colors), each with its player
  count, ball count (1 ball = BALL players, rounded), roster by position and roster WAR.
- other: everyone else (Other, Patronage, Acquired/assigned, Compound, Ornamental), one gray-ish bin.
- logos: each team's logo as inline SVG markup (viewBox 0 0 600 600) from make_logos.py.
- ranking: the four teams by roster WAR, best first.

Inputs: data/processed/players_final.csv and rosters.csv (build_rosters.py).
"""
import json
import sys
from pathlib import Path

import pandas as pd

PROJ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJ / "design"))
import make_logos  # noqa: E402

DATA = PROJ / "data" / "processed"
OUT = PROJ / "video" / "src" / "data" / "video.json"
BALL = 5
TEAMS = [  # order of the bins, left to right: the order the script introduces them
    ("Occupational", "jobs", "The Jobs"),
    ("Patronymic", "sons", "The Sons of Somebody"),
    ("Cognominal", "nicknames", "The Nicknames"),
    ("Toponymic", "places", "The Places"),
]
POSITIONS = ["P", "C", "1B", "2B", "3B", "SS", "OF", "DH"]
# One distinct ball color per team, readable on the cream background (Jobs' black and Sons' navy
# would clash, so Jobs uses its gold).
BALL_COLOR = {"jobs": "#F2B705", "sons": "#13294B", "nicknames": "#B3272D", "places": "#1F4D3A"}


def main():
    p = pd.read_csv(DATA / "players_final.csv")
    r = pd.read_csv(DATA / "rosters.csv")
    r["pos"] = r.slot.str.replace(" (flex)", "", regex=False)
    teams = []
    for tech, key, name in TEAMS:
        g = r[r.team == tech]
        roster = {pos: [{"name": x.full_name, "war": round(x.war_total, 2)}
                        for x in g[g.pos == pos].sort_values("war_total", ascending=False).itertuples()]
                  for pos in POSITIONS}
        n = int((p.surname_type == tech).sum())
        teams.append({"key": key, "type": tech, "name": name, "players": n, "balls": round(n / BALL),
                      "color": BALL_COLOR[key],
                      "rosterWar": round(g.war_total.sum(), 2), "roster": roster})
    other_n = int((~p.surname_type.isin([t[0] for t in TEAMS])).sum())
    logos = {key: make_logos.DRAW[key](make_logos.TEAMS[key]) for _, key, _ in TEAMS}
    ranking = [t["key"] for t in sorted(teams, key=lambda t: -t["rosterWar"])]
    data = {"ballPlayers": BALL, "totalPlayers": int(len(p)), "teams": teams,
            "other": {"players": other_n, "balls": round(other_n / BALL)}, "logos": logos, "ranking": ranking}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    for t in teams:
        print(f"{t['name']:<22}{t['players']:>5} players {t['balls']:>4} balls  roster WAR {t['rosterWar']}")
    print(f"{'Other':<22}{other_n:>5} players {data['other']['balls']:>4} balls")
    print("ranking:", ranking)


if __name__ == "__main__":
    main()
