"""Build one row per player who appeared in the 2026 MLB regular season.

Sources (fetched once into data/raw/cache/, re-fetched only with --refresh):
- Baseball-Reference bulk WAR files (bWAR), /data/war_daily_bat.txt and
  /data/war_daily_pitch.txt. Not disallowed by robots.txt; two requests total.
- MLB Stats API /api/v1/sports/1/players?season=2026: name parts, birth
  country, primary position. One request.

Joined on MLB's player ID (bbref's mlb_ID column).

WAR rules:
- war_bat: sum of 2026 batting WAR across stints (includes fielding/position).
- war_pitch: sum of 2026 pitching WAR across stints.
- war_total = war_bat + war_pitch (only two-way players have both meaningfully).

Position: MLB's primaryPosition, with LF/CF/RF/OF -> OF. TWP (two-way) is kept
as-is and resolved when rosters are built.

Output: data/processed/players_2026.csv
"""
import argparse
import json
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "cache"  # gitignored; re-fetchable
OUT = ROOT / "data" / "processed" / "players_2026.csv"
SEASON = 2026
UA = {"User-Agent": "Mozilla/5.0 (content-engine research; one-off download)"}
SOURCES = {
    "war_daily_bat.txt": "https://www.baseball-reference.com/data/war_daily_bat.txt",
    "war_daily_pitch.txt": "https://www.baseball-reference.com/data/war_daily_pitch.txt",
    "mlb_players_2026.json": f"https://statsapi.mlb.com/api/v1/sports/1/players?season={SEASON}",
}
POS_MAP = {"LF": "OF", "CF": "OF", "RF": "OF"}


def fetch(refresh: bool) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        path = RAW / name
        if path.exists() and not refresh:
            continue
        r = requests.get(url, headers=UA, timeout=120)
        r.raise_for_status()
        path.write_bytes(r.content)


def war_by_player(fname: str, col: str) -> pd.DataFrame:
    df = pd.read_csv(RAW / fname, low_memory=False)
    df = df[df.year_ID == SEASON]
    g = df.groupby("mlb_ID").agg(
        bbref_id=("player_ID", "first"),
        **{col: ("WAR", "sum")},
        **{f"g_{col.split('_')[1]}": ("G", "sum")},
        teams=("team_ID", lambda s: "/".join(dict.fromkeys(s))),
    )
    return g


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    fetch(args.refresh)

    bat = war_by_player("war_daily_bat.txt", "war_bat")
    pit = war_by_player("war_daily_pitch.txt", "war_pitch")
    war = bat.join(pit, how="outer", lsuffix="_b", rsuffix="_p")
    war["bbref_id"] = war.bbref_id_b.fillna(war.bbref_id_p)
    war["teams"] = war.teams_b.fillna(war.teams_p)
    war = war.drop(columns=["bbref_id_b", "bbref_id_p", "teams_b", "teams_p"])
    war[["war_bat", "war_pitch"]] = war[["war_bat", "war_pitch"]].fillna(0.0)
    war[["g_bat", "g_pitch"]] = war[["g_bat", "g_pitch"]].fillna(0).astype(int)
    war["war_total"] = (war.war_bat + war.war_pitch).round(2)
    war.index = war.index.astype(int)

    people = json.loads((RAW / "mlb_players_2026.json").read_text(encoding="utf-8"))["people"]
    mlb = pd.DataFrame([{
        "mlb_id": p["id"],
        "full_name": p.get("fullName"),
        "first_name": p.get("useName") or p.get("firstName"),
        "last_name": p.get("lastName"),
        "use_last_name": p.get("useLastName"),
        "name_suffix": p.get("nameSuffix"),
        "birth_country": p.get("birthCountry"),
        "birth_city": p.get("birthCity"),
        "pos_mlb": p["primaryPosition"]["abbreviation"],
    } for p in people]).set_index("mlb_id")
    mlb["position"] = mlb.pos_mlb.replace(POS_MAP)

    df = mlb.join(war, how="outer")
    df.index.name = "mlb_id"
    df["in_mlb_list"] = df.full_name.notna()
    df["has_war"] = df.war_total.notna()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.reset_index().to_csv(OUT, index=False, encoding="utf-8")

    print(f"MLB API players: {mlb.shape[0]}, bbref 2026 players: {war.shape[0]}, joined: {df.shape[0]}")
    print(f"  in MLB list only (no 2026 bWAR row): {(~df.has_war).sum()}")
    print(f"  bWAR only (not in MLB list): {(~df.in_mlb_list).sum()}")


if __name__ == "__main__":
    main()
