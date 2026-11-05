"""Veterans per 1,000 residents by metro: ACS 2024 B21002 counts over Census Vintage 2024 population estimates."""
from pathlib import Path
import urllib.request
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data"
POP = ROOT / "data" / "raw" / "cbsa-est2024-alldata.csv"
URL = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/metro/totals/cbsa-est2024-alldata.csv"

if not POP.exists():
    req = urllib.request.Request(URL, headers={"User-Agent": "content-engine-research-bot/1.0 (data journalism project)"})
    POP.write_bytes(urllib.request.urlopen(req, timeout=120).read())

pop = pd.read_csv(POP, encoding="latin-1", dtype={"CBSA": str})
pop = pop[pop.LSAD == "Metropolitan Statistical Area"][["CBSA", "NAME", "POPESTIMATE2024"]]
m = pd.read_csv(OUT / "metro_veterans_acs2024.csv", dtype={"cbsa": str}).merge(pop, left_on="cbsa", right_on="CBSA")
m["per_1000"] = (m.veterans / m.POPESTIMATE2024 * 1000).round(1)
m = m[["NAME", "veterans", "moe", "POPESTIMATE2024", "per_1000"]].sort_values("veterans", ascending=False)
m.to_csv(OUT / "metro_veterans_acs2024.csv", index=False)
print(len(m), "metros")
print(m.head(10).to_string())
big = m[m.POPESTIMATE2024 >= 250_000].sort_values("per_1000", ascending=False)
print(big.head(12).to_string())
print(big.tail(6).to_string())
