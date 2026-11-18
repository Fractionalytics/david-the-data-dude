"""Pre-registered test P14 (docs/hypothesis-test.md, round 7): did large US cities
that ran automated speed cameras by 2016 see pedestrian death rates rise less
than matched cities in states that bar speed cameras?

    python scripts/test_cameras.py cities   # sample, covariates, groups (no outcomes)
    python scripts/test_cameras.py run      # place deaths, compute P14
      reads  data/raw/census_places/*        (scripts/fetch_h11.py)
             data/raw/tiger/tl_2010_<SS>_place10.zip
             data/raw/fars/FARS<YEAR>NationalCSV.zip, 2005-2022
      writes data/final/test_cameras_cities.csv   one row per sample city
             data/final/test_cameras_years.csv    deaths, population, rate by city x year
             data/final/test_cameras.csv          P14 summary and placebo distribution

Sample: incorporated places with 2010 Census population >= 250,000, on fixed
2010 boundaries. Deaths are placed by FARS crash coordinates (pedestrians
killed, PER_TYP 5, INJ_SEV 4). Population: Census place estimates (intercensal
2000-2010 for 2005-2009, Vintage 2020 for 2010-2019, Vintage 2024 for 2020-2022);
these follow current boundaries, so annexation can inflate later populations a
little (noted in the results).
Groups (fixed before outcomes; see TREATED and BAN_STATES):
  treated     speed cameras on city streets by end of 2016, >= 20 locations,
              still running through 2020-22
  comparison  cities in states that barred speed cameras for the whole window
  other       everyone else (used only for placebo draws)
Matching: z-scores across the sample of (2009-11 pedestrian rate, ACS 2008-12
poverty rate, log 2010 density). Each treated city's comparison = ban-state
cities in its Census region (all ban-state cities if fewer than 2), weighted by
1 / (distance + 0.25).
"""

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fars_pedestrians import FINAL, load  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PLACES = ROOT / "data" / "raw" / "census_places"
TIGER = ROOT / "data" / "raw" / "tiger"
PRE0, PRE, POST = [2005, 2006, 2007], [2009, 2010, 2011], [2020, 2021, 2022]
YEARS = list(range(2005, 2023))

# Filled from docs/h11-policy-dates.md and the camera research, committed with the
# pre-registration before any outcome was computed. Keys: "SS-PLACE" (2010 FIPS).
TREATED: dict[str, str] = {
    "11-50000": "Washington DC: photo radar from 2001, about 87 cameras in 2016",
    "36-51000": "New York: from Jan 2014, 140 zones in 2014, 750 by 2020",
    "17-14000": "Chicago: from Oct 2013, about 150 cameras in 63 zones by 2016",
}
SENSITIVITY = {"53-63000": "Seattle: 28 cameras in 14 school zones by 2015 (borderline on the 20-location rule)"}
BAN_STATES: dict[str, str] = {
    "48": "Texas: cities barred from speed cameras from June 2007 (Transp. Code 542.2035)",
    "34": "New Jersey: never authorized",
    "55": "Wisconsin: photo radar banned (349.02(3), 1990s)",
    "32": "Nevada: only officer-operated cameras (NRS 484A.600, 1999)",
}

REGION = {  # Census regions by state FIPS
    **{s: "Northeast" for s in ["09", "23", "25", "33", "34", "36", "42", "44", "50"]},
    **{s: "Midwest" for s in ["17", "18", "19", "20", "26", "27", "29", "31", "38", "39", "46", "55"]},
    **{s: "South" for s in ["01", "05", "10", "11", "12", "13", "21", "22", "24", "28", "37", "40", "45",
                            "47", "48", "51", "54"]},
    **{s: "West" for s in ["02", "04", "06", "08", "15", "16", "30", "32", "35", "41", "49", "53", "56"]},
}


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def cities() -> pd.DataFrame:
    v20 = pd.read_csv(PLACES / "SUB-EST2020_ALL.csv", encoding="latin-1", dtype={"STATE": str, "PLACE": str})
    v20 = v20[v20.SUMLEV == 162].copy()
    v20["pop2010"] = num(v20.CENSUS2010POP)
    c = v20[v20.pop2010 >= 250_000].copy()
    c["id"] = c.STATE + "-" + c.PLACE
    c = c.set_index("id")
    out = c[["STATE", "PLACE", "NAME", "STNAME", "pop2010"]].copy()
    for y in range(2010, 2020):
        out[f"pop{y}"] = num(c[f"POPESTIMATE{y}"])
    ic = pd.read_csv(PLACES / "sub-est00int.csv", encoding="latin-1", dtype={"STATE": str, "PLACE": str})
    ic = ic[ic.SUMLEV == 162].assign(id=lambda x: x.STATE + "-" + x.PLACE).drop_duplicates("id").set_index("id")
    for y in range(2005, 2010):
        out[f"pop{y}"] = num(ic[f"POPESTIMATE{y}"].reindex(out.index))
    v24 = pd.read_csv(PLACES / "sub-est2024.csv", encoding="latin-1", dtype={"STATE": str, "PLACE": str})
    v24 = v24[v24.SUMLEV == 162].assign(id=lambda x: x.STATE + "-" + x.PLACE).drop_duplicates("id").set_index("id")
    for y in (2020, 2021, 2022):
        out[f"pop{y}"] = num(v24[f"POPESTIMATE{y}"].reindex(out.index))
    gaps = out[[f"pop{y}" for y in YEARS]].isna().any(axis=1)
    if gaps.any():  # Urban Honolulu is a CDP with no place estimate before 2010
        print("dropped (population estimates missing):", out.NAME[gaps].tolist())
        out = out[~gaps]
    # covariates
    acs = []
    for s in out.STATE.unique():
        j = pd.read_json(PLACES / f"acs5_2012_place_{s}.json")
        j.columns = j.iloc[0]
        acs.append(j.iloc[1:])
    acs = pd.concat(acs).assign(id=lambda x: x.state + "-" + x.place).set_index("id")
    out["poverty"] = num(acs.B17001_002E).reindex(out.index) / num(acs.B17001_001E).reindex(out.index)
    geo = places_geo(out)
    out["aland_km2"] = geo.set_index("id").ALAND10.reindex(out.index) / 1e6
    out["density"] = out.pop2010 / out.aland_km2
    out["region"] = out.STATE.map(REGION)
    out["group"] = np.where(out.index.isin(TREATED), "treated",
                            np.where(out.STATE.isin(BAN_STATES), "comparison", "other"))
    return out


def places_geo(c: pd.DataFrame) -> gpd.GeoDataFrame:
    parts = []
    for s in c.STATE.unique():
        g = gpd.read_file(f"zip://{TIGER / f'tl_2010_{s}_place10.zip'}")[["STATEFP10", "PLACEFP10", "ALAND10", "geometry"]]
        parts.append(g)
    g = pd.concat(parts, ignore_index=True)
    g["id"] = g.STATEFP10 + "-" + g.PLACEFP10
    g = g[g.id.isin(c.index)]
    missing = set(c.index) - set(g.id)
    assert not missing, f"no 2010 boundary for {missing}"
    return gpd.GeoDataFrame(g, geometry="geometry", crs=parts[0].crs)


def place_deaths(c: pd.DataFrame) -> pd.DataFrame:
    geo = places_geo(c).to_crs("EPSG:4269")
    rows, cover = [], []
    for y in YEARS:
        p = load(y, "person", ["ST_CASE", "PER_TYP", "INJ_SEV"])
        a = load(y, "accident", ["ST_CASE", "LATITUDE", "LONGITUD"])
        d = p[(p.PER_TYP == 5) & (p.INJ_SEV == 4)].merge(a, on="ST_CASE", how="left", validate="m:1")
        ok = d.LATITUDE.between(17, 72) & d.LONGITUD.between(-180, -60)
        pts = gpd.GeoDataFrame(d[ok], geometry=gpd.points_from_xy(d[ok].LONGITUD, d[ok].LATITUDE), crs="EPSG:4269")
        j = gpd.sjoin(pts, geo[["id", "geometry"]], how="inner", predicate="within")
        j = j[~j.index.duplicated(keep="first")]
        n = j.groupby("id").size()
        rows.append(pd.DataFrame({"id": c.index, "year": y, "deaths": n.reindex(c.index).fillna(0).astype(int).values}))
        cover.append(dict(year=y, killed=len(d), bad_xy=int((~ok).sum()), in_sample_cities=len(j)))
        print(cover[-1], flush=True)
    print(pd.DataFrame(cover).to_string(index=False))
    return pd.concat(rows, ignore_index=True)


def period_rate(t: pd.DataFrame, years: list[int]) -> pd.Series:
    s = t[t.year.isin(years)].groupby("id")[["deaths", "pop"]].sum()
    return s.deaths / s["pop"] * 1e5


def matched(c: pd.DataFrame, treated: list[str]) -> dict[str, pd.Series]:
    z = c[["rate_pre", "poverty", "logdens"]].apply(lambda s: (s - s.mean()) / s.std())
    comp = c[c.group == "comparison"]
    out = {}
    for t in treated:
        pool = comp[comp.region == c.at[t, "region"]]
        if len(pool) < 2:
            pool = comp
        dist = np.sqrt(((z.loc[pool.index] - z.loc[t]) ** 2).sum(axis=1))
        w = 1 / (dist + 0.25)
        out[t] = w / w.sum()
    return out


def gap(c: pd.DataFrame, treated: list[str]) -> dict:
    m = matched(c, treated)
    rt = c.loc[treated, "rel"].mean()
    rc = np.mean([(w * c.loc[w.index, "rel"]).sum() for w in m.values()])
    pre_t = c.loc[treated, "pretrend"].mean()
    pre_c = np.mean([(w * c.loc[w.index, "pretrend"]).sum() for w in m.values()])
    return dict(treated_rel=rt, comparison_rel=rc, gap=rt - rc, pretrend_diff=pre_t - pre_c)


def run() -> None:
    c = cities()
    t = place_deaths(c)
    t["pop"] = [c.at[i, f"pop{y}"] for i, y in zip(t.id, t.year)]
    t["rate"] = t.deaths / t["pop"] * 1e5
    t.to_csv(FINAL / "test_cameras_years.csv", index=False)
    c["rate_pre0"], c["rate_pre"], c["rate_post"] = period_rate(t, PRE0), period_rate(t, PRE), period_rate(t, POST)
    c["rel"] = c.rate_post / c.rate_pre - 1
    c["pretrend"] = c.rate_pre - c.rate_pre0
    c["logdens"] = np.log(c.density)
    c.to_csv(FINAL / "test_cameras_cities.csv")
    treated = [i for i in c.index if c.at[i, "group"] == "treated"]
    real = gap(c, treated)
    rng = np.random.default_rng(20261110)
    others = c.index[c.group == "other"].tolist()
    plac = [gap(c, list(rng.choice(others, size=len(treated), replace=False)))["gap"] for _ in range(1000)]
    rank = float(np.mean(np.array(plac) <= real["gap"]))
    pass_size = real["comparison_rel"] > 0 and real["treated_rel"] <= 0.75 * real["comparison_rel"]
    interpretable = abs(real["pretrend_diff"]) <= 0.3
    verdict = "NOT INTERPRETABLE" if not interpretable else ("PASS" if pass_size and rank <= 0.10 else "FAIL")
    summ = pd.DataFrame([{**real, "placebo_share_at_or_below": rank, "n_treated": len(treated),
                          "n_comparison": int((c.group == "comparison").sum()), "verdict": verdict}])
    summ.to_csv(FINAL / "test_cameras.csv", index=False)
    print(summ.T.to_string())
    show = ["NAME", "group", "region", "rate_pre0", "rate_pre", "rate_post", "rel", "poverty", "density"]
    print(c.sort_values(["group", "rel"])[show].round(3).to_string())
    for i, w in matched(c, treated).items():
        print(c.at[i, "NAME"], "<-", ", ".join(f"{c.at[k, 'NAME']} {v:.2f}" for k, v in w.sort_values(ascending=False).items()))
    print("placebo gap percentiles 5/10/50/90:", np.percentile(plac, [5, 10, 50, 90]).round(3))
    s = gap(c, treated + list(SENSITIVITY))
    print("not scored, with Seattle added:", {k: round(v, 3) for k, v in s.items()})
    for i in treated + list(SENSITIVITY):
        g1 = gap(c, [i])
        print("not scored, one city:", c.at[i, "NAME"], {k: round(v, 3) for k, v in g1.items()})


if __name__ == "__main__":
    if sys.argv[1:] == ["cities"]:
        c = cities()
        print(c[["NAME", "STNAME", "pop2010", "pop2005", "pop2022", "poverty", "density", "region", "group"]]
              .sort_values("pop2010", ascending=False).round(3).to_string())
    else:
        run()
