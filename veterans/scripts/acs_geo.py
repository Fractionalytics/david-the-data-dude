"""Veterans by metro and county from ACS 2024 1-year table B21002, plus the Lake County IL check against VetPop."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "raw", ROOT / "data"

d = pd.read_csv(RAW / "acs2024_b21002.dat", sep="|", dtype={"GEO_ID": str})
print(d.GEO_ID.str[:5].value_counts().head(12))
print("E001 US:", d.loc[d.GEO_ID.str.startswith("0100000"), ["GEO_ID", "B21002_E001", "B21002_M001"]].to_string())

metro = d[d.GEO_ID.str.startswith("310M")][["GEO_ID", "B21002_E001", "B21002_M001"]].copy()
metro.columns = ["geo_id", "veterans", "moe"]
metro["cbsa"] = metro.geo_id.str[-5:]
metro = metro.sort_values("veterans", ascending=False)
metro.to_csv(OUT / "metro_veterans_acs2024.csv", index=False)
print(metro.head(15).to_string())

county = d[d.GEO_ID.str.startswith("0500000")][["GEO_ID", "B21002_E001", "B21002_M001"]].copy()
county.columns = ["geo_id", "acs_veterans", "moe"]
county["FIPS"] = county.geo_id.str[-5:].astype(int)
vp = pd.read_csv(OUT / "county_fy2026.csv")
vp23 = pd.read_csv(RAW / "cache" / "vetpop_county_9L.csv")
vp23 = vp23[vp23.Date.str.startswith("09/30/2024")]
vp23["Veterans"] = pd.to_numeric(vp23["Veterans"].astype(str).str.replace(",", ""))
vp24 = vp23.groupby(["FIPS", "County, State"])["Veterans"].sum().reset_index()
m = county.merge(vp24, on="FIPS")
m["ratio"] = (m.Veterans / m.acs_veterans).round(2)
print("Counties compared:", len(m), "median VetPop/ACS ratio:", m.ratio.median())
print(m.sort_values("Veterans", ascending=False).head(12)[["County, State", "Veterans", "acs_veterans", "moe", "ratio"]].to_string())
print(m[m.Veterans > 30000].sort_values("ratio", ascending=False).head(10)[["County, State", "Veterans", "acs_veterans", "ratio"]].to_string())
