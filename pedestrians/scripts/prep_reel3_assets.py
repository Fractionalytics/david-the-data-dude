"""Assets for Reel 3's Remotion charts (video/src/reel3/).

Writes:
- video/public/reel3/pages/p<N>.png: pages of Brumbelow's report (data/raw/papers/pedestrian_impairment_2026.pdf),
  rendered at 2x, and the highlight rectangles for each passage the Reel points at.
- video/src/reel3/assets.json: those rectangles, the Europe map as SVG paths (Natural Earth 1:50m countries,
  public domain, data/raw/naturalearth/), and the numbers for every new chart, so the video never
  recomputes them.

Run from the project folder: python scripts/prep_reel3_assets.py
"""
import json
from math import cos, radians
from pathlib import Path

import fitz
import pandas as pd
from shapely.geometry import box, mapping, shape

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / "video" / "public" / "reel3" / "pages"
PUB.mkdir(parents=True, exist_ok=True)
OUT = ROOT / "video" / "src" / "reel3" / "assets.json"
OUT.parent.mkdir(parents=True, exist_ok=True)
ZOOM = 2

# --- Brumbelow's report: pages and passages (page numbers are 1-based) ---
PASSAGES = {
    "title": (1, "Pedestrian fatalities and methamphetamine impairment"),
    "factors": (1, "I looked at many possibilities:"),
    "noShift": (2, "almost none show a shift beginning around 2010 for nighttime crashes"),
    "twoExceptions": (2, "I've only been able to find two exceptions."),
    "urbanNight": (1, "the increase is concentrated in urban nighttime crashes"),
    "arterials": (2, "it has come on collectors and arterials"),
    "drugRise": (4, "a sharp increase among nighttime pedestrian fatalities began around 2010"),
    "notDrivers": (4, "it is more commonly reported at night for pedestrians than for drivers of striking vehicles"),
}
doc = fitz.open(ROOT / "data" / "raw" / "papers" / "pedestrian_impairment_2026.pdf")
pages = sorted({p for p, _ in PASSAGES.values()})
for p in pages:
    doc[p - 1].get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM)).save(PUB / f"p{p}.png")
page_w, page_h = doc[0].rect.width * ZOOM, doc[0].rect.height * ZOOM
hl = {}
for k, (p, q) in PASSAGES.items():
    rects = doc[p - 1].search_for(q)
    assert rects, f"passage not found: {k}"
    # merge word rects into one rect per line
    lines = {}
    for r in rects:
        key = round(r.y0)
        a = lines.get(key)
        lines[key] = r if a is None else a | r
    hl[k] = {"page": p, "rects": [[round(v * ZOOM, 1) for v in (r.x0, r.y0, r.x1, r.y1)] for r in lines.values()]}

# --- Europe map ---
gj = json.loads((ROOT / "data" / "raw" / "naturalearth" / "ne_50m_admin_0_countries.geojson").read_text(encoding="utf-8"))
LON0, LON1, LAT0, LAT1 = -11, 34, 35, 70
K = cos(radians(52))
clip = box(LON0, LAT0, LON1, LAT1)
MAP_W, MAP_H = 760, 560  # drawing box inside the plate
sx = MAP_W / ((LON1 - LON0) * K)
sy = MAP_H / (LAT1 - LAT0)
s = min(sx, sy)


def proj(lon, lat):
    return ((lon - LON0) * K * s, (LAT1 - lat) * s)


def path_of(geom):
    out = []
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    for poly in polys:
        if poly.geom_type != "Polygon" or poly.area < 0.02:
            continue
        for ring in [poly.exterior]:
            pts = [proj(x, y) for x, y in ring.simplify(0.04).coords]
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    return "".join(out)


countries = []
for f in gj["features"]:
    pr = f["properties"]
    if pr["CONTINENT"] not in ("Europe", "Asia", "Africa"):
        continue
    g = shape(f["geometry"]).intersection(clip)
    if g.is_empty:
        continue
    d = path_of(g)
    if d:
        countries.append({"iso": pr["ISO_A3"] if pr["ISO_A3"] != "-99" else pr["ADM0_A3"], "name": pr["NAME"],
                          "europe": pr["CONTINENT"] == "Europe", "d": d})
cz = next(c for c in countries if c["iso"] == "CZE")

# --- Card 10: meth in wastewater, 2025 campaign (EUDA explorer download, saved by David 2026-11-17) ---
# Daily mean, mg of methamphetamine per 1,000 people a day. The file also has cities outside Europe
# (US, Canada, Australia, New Zealand, Chile, South Korea); the map keeps those inside its frame.
ww = pd.read_csv(ROOT / "data" / "raw" / "euda" / "euda_wastewater_meth.tsv", sep="\t").iloc[:, :17]
ww = ww[(ww.Year == 2025) & (ww.Metabolite == "methamphetamine")]
ww = ww[ww.Longitude.between(LON0, LON1) & ww.Latitude.between(LAT0, LAT1) & ~ww.Country.isin(["US", "CA", "AU", "NZ", "CL", "KR"])]
cities = [{"x": round(proj(r.Longitude, r.Latitude)[0], 1), "y": round(proj(r.Longitude, r.Latitude)[1], 1),
           "v": float(r["Daily mean"]), "cz": r.Country == "CZ"} for _, r in ww.iterrows()]
wastewater = {"cities": sorted(cities, key=lambda c: c["v"]), "n": len(cities),
              "czMedian": float(ww[ww.Country == "CZ"]["Daily mean"].median()),
              "restMedian": float(ww[ww.Country != "CZ"]["Daily mean"].median())}

# --- Numbers for the charts ---
b = pd.read_csv(ROOT / "data" / "final" / "three_buckets.csv").set_index(["country", "period"])
us_e, us_l = b.loc[("US", "cz_early_years")], b.loc[("US", "cz_late_years")]
cz_e, cz_l = b.loc[("Czechia", "early")], b.loc[("Czechia", "late")]
r = pd.read_csv(ROOT / "data" / "final" / "eu_pedestrian_rates.csv")
pop = r[r.geo == "US"].assign(pop=lambda d: d.deaths / d.rate_per_100k * 1e5).set_index("year")["pop"]
floor = us_l.stim_floor_per_million / cz_l.stim_floor_per_million
cz_pp = 31600 / 10.55e6  # Czechia's high-risk meth users, 2016 (NMC table 3-7) per person
users = {k: (v / pop[2016]) / cz_pp for k, v in (("lo", 1.3e6), ("best", 3.2e6), ("hi", 5.3e6))}  # RAND RR3140 Table 2.6
rand = {2009: 1.7, 2012: 2.1, 2013: 2.5, 2014: 2.8, 2015: 3.4, 2016: 3.2}  # RAND chronic meth users, millions
m = pd.read_csv(ROOT / "data" / "final" / "ped_meth_vs_cocaine.csv").set_index("year")
yrs = list(range(2009, 2017))
meth_pm = m.loc[yrs, "meth_amph"] / pop[yrs]
users_pp = pd.Series({y: v * 1e6 / pop[y] for y, v in rand.items()})
def meth_only():
    """Overdose deaths (UCD X40-44, X60-64, X85, Y10-14) listing T43.6 and no opioid (T40.0-T40.4, T40.6)."""
    W = ROOT / "data" / "raw" / "cdc_wonder"

    def read(f):
        d = pd.read_csv(W / f)
        d = d[d["Year Code"].notna()]
        return d.set_index(d["Year Code"].astype(int))[["Deaths", "Population"]].astype(float)

    allm = pd.concat([read("wonder_meth_od_all_2009_2017.csv"), read("wonder_meth_all_2018_2024.csv")])
    opi = pd.concat([read("wonder_meth_od_opioids_2009_2017.csv"), read("wonder_meth_with_opioids_2018_2024.csv")])
    rate = (allm.Deaths - opi.Deaths) / allm.Population * 1e5
    return [{"year": int(y), "v": float(v), "deaths": int(allm.Deaths[y] - opi.Deaths[y])} for y, v in rate.items()]


numbers = {
    "chartE": {"users": users, "floor": floor,
               "risk": {"best": floor / users["best"], "lo": floor / users["hi"], "hi": floor / users["lo"]}},
    "buckets": {
        "stim": {"us": us_l.stim_floor_per_million, "cz": cz_l.stim_floor_per_million},
        "noStim": {"us": us_l.tested_neg_per_million, "cz": cz_l.tested_neg_per_million},
        "slope": {"usNo": [us_e.tested_neg_per_million, us_l.tested_neg_per_million],
                  "czNo": [cz_e.tested_neg_per_million, cz_l.tested_neg_per_million],
                  "usStim": [us_e.stim_floor_per_million, us_l.stim_floor_per_million],
                  "czStim": [cz_e.stim_floor_per_million, cz_l.stim_floor_per_million]},
        "total": {"us": [us_e.total_per_million, us_l.total_per_million],
                  "cz": [cz_e.total_per_million, cz_l.total_per_million]},
    },
    # Card 44: P25's four state groups, 2018-24 (scripts/test_ped_tandem_states.py).
    "stateGrid": pd.read_csv(ROOT / "data" / "final" / "test_ped_tandem_groups.csv")[["hiM", "hiR", "n", "Y"]]
                   .to_dict("records"),
    # Card 32: meth overdose deaths with no opioid listed, per 100,000, 2009-2024 (CDC WONDER; see SOURCE.md).
    "methOnly": meth_only(),
    # Earlier card 32: RAND's chronic meth users per 1,000 US residents (best estimates; RAND has no 2010-11 figures).
    "rand": [{"year": y, "v": float(users_pp[y] * 1000)} for y in rand],
    "tandem": {"meth": [{"year": y, "v": float(meth_pm[y] / meth_pm[2009])} for y in yrs],
               "users": [{"year": y, "v": float(users_pp[y] / users_pp[2009])} for y in rand]},
}
OUT.write_text(json.dumps({"page": {"w": page_w, "h": page_h}, "highlights": hl,
                           "map": {"w": (LON1 - LON0) * K * s, "h": (LAT1 - LAT0) * s, "countries": countries}, "wastewater": wastewater, "numbers": numbers},
                          default=float), encoding="utf-8")
print(f"{len(countries)} map shapes, Czechia {len(cz['d'])} chars; highlights {list(hl)}")
print(json.dumps(numbers["chartE"], default=float))
