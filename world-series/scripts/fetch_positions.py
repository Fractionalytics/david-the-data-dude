"""Each 2026 player's primary position, from games played at each position in 2026.

MLB Stats API /api/v1/people?personIds=...&hydrate=stats(group=[fielding],type=[season],season=2026),
100 players per request (about 15 requests). Raw responses cached in data/raw/cache/fielding_2026/.

Rule: the position group with the most 2026 games (LF/CF/RF/OF pooled as OF; DH counts as a
position). Ties go to more games started, then more innings. Players with no 2026 fielding or DH games
(pinch-hit only) fall back to MLB's career primaryPosition. Two-way Shohei Ohtani is
marked TWP and resolved when rosters are built (his WAR is pitching + batting combined).

Output: data/processed/positions_2026.csv (mlb_id, primary_pos, games by position).
"""
import json
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "cache" / "fielding_2026"
PLAYERS = ROOT / "data" / "processed" / "players_2026.csv"
OUT = ROOT / "data" / "processed" / "positions_2026.csv"
URL = "https://statsapi.mlb.com/api/v1/people"
GROUP = {"LF": "OF", "CF": "OF", "RF": "OF", "OF": "OF"}
POSITIONS = ["P", "C", "1B", "2B", "3B", "SS", "OF", "DH"]
TWO_WAY = {660271}  # Shohei Ohtani


def fetch(ids):
    CACHE.mkdir(parents=True, exist_ok=True)
    people = []
    for i in range(0, len(ids), 100):
        path = CACHE / f"batch_{i // 100:02d}.json"
        if not path.exists():
            r = requests.get(URL, params={
                "personIds": ",".join(map(str, ids[i:i + 100])),
                "hydrate": "stats(group=[fielding],type=[season],season=2026)",
            }, timeout=120)
            r.raise_for_status()
            path.write_text(r.text, encoding="utf-8")
        people += json.loads(path.read_text(encoding="utf-8"))["people"]
    return people


def splits_by_position(person):
    """Per-position (games, starts, innings). Uses team-less total splits when present."""
    splits = [sp for s in person.get("stats", []) for sp in s["splits"]]
    totals = [sp for sp in splits if "team" not in sp]
    rows = totals if totals else splits
    out = {}
    for sp in rows:
        pos = GROUP.get(sp["position"]["abbreviation"], sp["position"]["abbreviation"])
        st = sp["stat"]
        g, gs, inn = out.get(pos, (0, 0, 0.0))
        out[pos] = (g + st.get("gamesPlayed", 0), gs + st.get("gamesStarted", 0),
                    inn + float(st.get("innings", 0) or 0))
    return out


def main():
    p = pd.read_csv(PLAYERS)
    ids = sorted(p[p.has_war].mlb_id.astype(int))
    rows = []
    for person in fetch(ids):
        pos = splits_by_position(person)
        row = {"mlb_id": person["id"]}
        row.update({f"g_{k}": pos.get(k, (0,))[0] for k in POSITIONS})
        if person["id"] in TWO_WAY:
            row["primary_pos"] = "TWP"
        elif pos:
            row["primary_pos"] = max(pos, key=lambda k: pos[k])
        else:
            row["primary_pos"] = None
        rows.append(row)
    df = pd.DataFrame(rows)
    # No 2026 fielding or DH games (pinch-hit only): fall back to MLB's career label.
    df["primary_pos"] = df.primary_pos.fillna(df.mlb_id.map(p.set_index("mlb_id").position))
    df.to_csv(OUT, index=False)
    print(f"{len(df)} players; no 2026 fielding/DH games: {df.primary_pos.isna().sum()}")
    print(df.primary_pos.value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()
