"""Who, when and where: decompose the rise in US pedestrian deaths (FARS),
2009 (4,109) to 2022 (7,593, +3,484) and 2024 (7,080, +2,971).

    python scripts/fetch_fars.py 2000 2024      (FARS zips, cached)
    python scripts/fetch_file.py <census url> census/<file>   (three files below)
    python scripts/fetch_fred.py ALPOP AKPOP ... WYPOP        (51 state series)
    python scripts/fars_decompose.py
      reads  data/raw/fars/FARS<YEAR>NationalCSV.zip (in place, via fars_pedestrians.load)
             data/raw/census/us-est00int-alldata.csv   (July 2000-2009, single year of age)
             data/raw/census/nc-est2020-agesex-res.csv (July 2010-2019)
             data/raw/census/nc-est2024-agesex-res.csv (July 2020-2024)
             data/raw/fred/<ST>POP.csv                 (state resident population, thousands)
      writes data/final/fars_decompose_<topic>.csv, one long table per topic
             (year, category, deaths, dark_deaths [, extras]):
               age, sex, hour, month, dayofweek, alcohol, hit_run, urban_rural,
               region, state (2009-11 vs 2021-23 averages), speeding, speed_limit,
               location (PERSON.LOCATION), pbtype_group, pbtype_position (2014 on),
               vehicle_age, vehicle_dark
             data/final/fars_decompose_share_of_increase.csv: for every dimension
               and category, deaths in 2009 / 2022 / 2024, the change, and the share
               of the national change (+3,484 to 2022, +2,971 to 2024) it accounts for.
               Dimensions that start later use their own first year (base_year column).

Pedestrian death and striking vehicle as in fars_pedestrians.py (PER_TYP 5,
INJ_SEV 4; striking vehicle via N_MOT_NO / STR_VEH). "Dark" = LGT_COND 2, 3, 6.

Code mappings (checked against the *NAME label columns, which the files carry
from 2015, and against code distributions and year-to-year continuity before):

  Age (PERSON.AGE): unknown = 99 through 2008; 998 / 999 from 2009 (when ages
    of 97+ became literal). Groups 0-15, 16-24, 25-44, 45-64, 65+.
  Sex (PERSON.SEX): 1 male, 2 female, 8 / 9 unknown.
  Hour (ACCIDENT.HOUR, crash hour): daytime 6-17, evening 18-20 (6-9pm),
    late_evening 21-23 (9pm-midnight), overnight 0-5, unknown 99.
  Day of week (ACCIDENT.DAY_WEEK 1 Sunday .. 7 Saturday): weekend is NHTSA's
    Friday 6pm to Monday 5:59am; crossed with dark.
  Alcohol, pedestrian (PERSON.ALC_RES): the unit changed in 2015. Through 2014
    0-94 = BAC in hundredths, 95-99 = refused / not given / unknown; from 2015
    0-940 = thousandths, 995-999 = not reported / not given / unknown. Only
    those values count as "tested". Imputed BAC (MIPER.P1-P10, ten
    multiple-imputation draws, hundredths in every year) gives an expected
    count with BAC >= .08 = sum over pedestrians of the share of the ten draws
    >= 8. Driver = PER_TYP 1 in the striking vehicle, same MIPER method.
    VEHICLE.DR_DRINK (police-reported drinking) is also kept.
  Hit-and-run (VEHICLE.HIT_RUN, striking vehicle): from 2009 0 no, 1 yes,
    9 unknown. Through 2008 the field had several "yes" variants (codes 1, 2,
    3, 5, with 2 the common one); any nonzero code is counted as yes, but
    those labels were not checked against the manual (no NAME columns), and
    the series steps from 20.2% (2008) to 16.6% (2009). Use 2009 on.
  Urban / rural: ACCIDENT.RUR_URB from 2015 (1 rural, 2 urban, else unknown);
    before, ROAD_FNC 1-9 rural, 11-19 urban, 99 unknown.
  Region: Census regions by STATE FIPS (PERSON.STATE; ACCIDENT.STATE is the
    first column and in the 2021-22 files its byte-order mark survives the
    loader's header cleaning, so it is not used).
  Speeding (VEHICLE.SPEEDREL, from 2009): 2009-12 0 no, 1 yes, 9 unknown;
    from 2013 2 racing, 3 over the limit, 4 too fast for conditions,
    5 specifics unknown (all "yes"), 8 no driver present, 9 unknown.
  Speed limit: ACCIDENT.SP_LIMIT (crash level) through 2009, VEHICLE.VSPD_LIM
    of the striking vehicle from 2010. 0 = no statutory limit, 98 / 99 unknown.
  Location (PERSON.LOCATION, all years) was recoded in 2010. Codes 1-9 are at an
    intersection and 10-13 not at an intersection on the roadway in both
    schemes; 14 and up are off the travel lanes (shoulder, sidewalk, parking
    lane, median, driveway, non-trafficway). We use only those three coarse
    groups across the break (they are continuous 2009 -> 2010); the detail
    (marked crosswalk etc.) is from 2010 on.
  PBTYPE (from 2014 only): PEDCGP crash-type group and PEDPOS position, codes
    stable 2014-2024 (labels from the NAME columns). Its share of the
    increase is measured 2014 -> 2022 / 2024.
  Vehicle age = crash year - VEHICLE.MOD_YEAR of the striking vehicle;
    9998 / 9999 unknown. Body class as in fars_pedestrians.body_class.

Caveats: 2024 is the latest NHTSA file and may still be revised. Pedestrian
BAC was "not reported" for 2,372 of 7,080 (33%) in 2024 against 947 (12%) in
2022, so tested-only alcohol shares are unreliable for 2024. The Census
urban-area boundaries behind RUR_URB were redrawn after the 2020 census.
FRED state populations are Census vintage estimates (2009 from the
intercensal series), not the same vintage across all years.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fars_pedestrians import FINAL, ROOT, YEARS, load, year_peds  # noqa: E402

CENSUS = ROOT / "data" / "raw" / "census"
FRED = ROOT / "data" / "raw" / "fred"
BASE, PEAK, LAST = 2009, 2022, 2024
AGE_GROUPS = ["0-15", "16-24", "25-44", "45-64", "65+"]
FIPS = {1: "AL", 2: "AK", 4: "AZ", 5: "AR", 6: "CA", 8: "CO", 9: "CT", 10: "DE", 11: "DC", 12: "FL",
        13: "GA", 15: "HI", 16: "ID", 17: "IL", 18: "IN", 19: "IA", 20: "KS", 21: "KY", 22: "LA",
        23: "ME", 24: "MD", 25: "MA", 26: "MI", 27: "MN", 28: "MS", 29: "MO", 30: "MT", 31: "NE",
        32: "NV", 33: "NH", 34: "NJ", 35: "NM", 36: "NY", 37: "NC", 38: "ND", 39: "OH", 40: "OK",
        41: "OR", 42: "PA", 44: "RI", 45: "SC", 46: "SD", 47: "TN", 48: "TX", 49: "UT", 50: "VT",
        51: "VA", 53: "WA", 54: "WV", 55: "WI", 56: "WY"}
REGION = {**{s: "Northeast" for s in "CT ME MA NH RI VT NJ NY PA".split()},
          **{s: "Midwest" for s in "IL IN MI OH WI IA KS MN MO NE ND SD".split()},
          **{s: "South" for s in "DE DC FL GA MD NC SC VA WV AL KY MS TN AR LA OK TX".split()},
          **{s: "West" for s in "AZ CO ID MT NV NM UT WY AK CA HI OR WA".split()}}
PEDCGP = {100: "unusual_circumstances", 200: "backing_vehicle", 310: "working_playing_in_road",
          340: "bus_related", 350: "unique_midblock", 400: "walking_along_roadway",
          460: "driveway_access", 500: "waiting_to_cross", 600: "in_roadway_circumstances_unknown",
          720: "multiple_threat_trapped", 740: "dash_dart_out", 750: "crossing_vehicle_not_turning",
          790: "crossing_vehicle_turning", 800: "non_trafficway", 910: "crossing_expressway",
          990: "other_unknown"}
PEDPOS = {1: "intersection_area", 2: "crosswalk_area", 3: "travel_lane", 4: "shoulder_bike_parking_lane",
          5: "sidewalk_path_driveway", 6: "unpaved_right_of_way", 7: "non_trafficway", 8: "non_trafficway",
          9: "other_unknown"}
LOC_DETAIL = {1: "intersection_marked_crosswalk", 2: "intersection_unmarked_or_unknown_crosswalk",
              3: "intersection_not_in_crosswalk", 9: "intersection_unknown", 10: "midblock_marked_crosswalk",
              11: "midblock_roadway_not_in_crosswalk", 13: "midblock_roadway_crosswalk_unknown"}


def age_group(a: pd.Series, year: int) -> pd.Series:
    unknown = a.isin([99]) if year < 2009 else a.isin([998, 999])
    g = pd.cut(a, [-1, 15, 24, 44, 64, 200], labels=AGE_GROUPS).astype(str)
    return g.where(~unknown & a.notna(), "unknown")


def hour_group(h: pd.Series) -> pd.Series:
    return pd.Series(np.select([h.between(6, 17), h.between(18, 20), h.between(21, 23), h.between(0, 5)],
                               ["daytime_6am_6pm", "evening_6_9pm", "late_evening_9pm_midnight", "overnight_midnight_6am"],
                               "unknown"), index=h.index)


def weekend(dow: pd.Series, h: pd.Series) -> pd.Series:
    wk = ((dow == 6) & (h.between(18, 23))) | dow.isin([7, 1]) | ((dow == 2) & h.between(0, 5))
    return wk.where(dow.between(1, 7) & h.between(0, 23))


def tested_bac(r: pd.Series, year: int) -> pd.Series:
    if year < 2015:
        return (r / 100).where(r.between(0, 94))
    return (r / 1000).where(r.between(0, 940))


def year_frame(year: int) -> pd.DataFrame:
    d, _ = year_peds(year)
    key = ["ST_CASE", "VEH_NO", "PER_NO"]
    p = load(year, "person", key + ["PER_TYP", "STATE", "AGE", "SEX", "LOCATION", "ALC_RES"])
    d = d.merge(p.drop(columns="PER_TYP"), on=key, how="left", validate="1:1")
    a = load(year, "accident", ["ST_CASE", "MONTH", "HOUR", "DAY_WEEK", "SP_LIMIT", "RUR_URB"])
    d = d.merge(a, on="ST_CASE", how="left", validate="m:1")
    v = load(year, "vehicle", ["ST_CASE", "VEH_NO", "HIT_RUN", "SPEEDREL", "VSPD_LIM", "DR_DRINK", "MOD_YEAR"])
    d = d.merge(v.rename(columns={"VEH_NO": "str_veh"}), on=["ST_CASE", "str_veh"], how="left", validate="m:1")
    pb = load(year, "pbtype", key + ["PEDCGP", "PEDPOS"])
    if len(pb):
        d = d.merge(pb, on=key, how="left", validate="1:1")

    mi = load(year, "miper", key + [f"P{i}" for i in range(1, 11)])
    pcols = [f"P{i}" for i in range(1, 11)]
    mi["mi_bac08"] = (mi[pcols] >= 8).mean(axis=1)
    mi["mi_p1"] = mi.P1
    d = d.merge(mi[key + ["mi_bac08", "mi_p1"]], on=key, how="left", validate="1:1")
    drv = p[p.PER_TYP == 1][["ST_CASE", "VEH_NO", "PER_NO"]].merge(mi[key + ["mi_bac08"]], on=key, how="left")
    drv = drv.sort_values("PER_NO").drop_duplicates(["ST_CASE", "VEH_NO"])
    d = d.merge(drv.rename(columns={"VEH_NO": "str_veh", "mi_bac08": "drv_mi_bac08"})[["ST_CASE", "str_veh", "drv_mi_bac08"]],
                on=["ST_CASE", "str_veh"], how="left", validate="m:1")

    d["age_group"] = age_group(d.AGE, year)
    d["sex"] = d.SEX.map({1: "male", 2: "female"}).fillna("unknown")
    d["hour_group"] = hour_group(d.HOUR)
    d["month"] = d.MONTH.astype(int)
    wk = weekend(d.DAY_WEEK, d.HOUR)
    d["week_part"] = np.where(wk.isna(), "unknown", np.where(wk == True, "weekend", "weekday"))  # noqa: E712
    d["week_part_dark"] = d.week_part + np.where(d.dark, "_dark", "_not_dark")
    d["bac"] = tested_bac(d.ALC_RES, year)
    d["state"] = d.STATE.map(FIPS)
    d["region"] = d.state.map(REGION).fillna("unknown")
    if year >= 2015:
        d["urban_rural"] = d.RUR_URB.map({1: "rural", 2: "urban"}).fillna("unknown")
    else:
        rf = d.ROAD_FNC
        d["urban_rural"] = np.where(rf.between(1, 9), "rural", np.where(rf.between(11, 19), "urban", "unknown"))
    hr = d.HIT_RUN
    d["hit_run"] = np.where(hr == 0, "no", np.where(hr.between(1, 8), "yes", "unknown"))
    if year >= 2009:
        s = d.SPEEDREL
        d["speeding"] = np.where(s == 0, "no", np.where(s.between(1, 5), "yes", "unknown"))
    else:
        d["speeding"] = pd.NA
    lim = d.SP_LIMIT if year <= 2009 else d.VSPD_LIM
    d["speed_limit_var"] = "ACCIDENT.SP_LIMIT" if year <= 2009 else "VEHICLE.VSPD_LIM"
    d["speed_limit"] = np.select([lim.between(1, 30), lim == 35, lim.between(40, 45), lim.between(50, 55), lim.between(60, 90)],
                                 ["30_or_less", "35", "40-45", "50-55", "60_plus"], "unknown_or_none")
    loc = d.LOCATION
    d["location"] = np.select([loc.between(1, 9), loc.between(10, 13), loc.between(14, 97)],
                              ["at_intersection", "midblock_on_roadway", "off_travel_lanes"], "unknown")
    d["location_detail"] = loc.map(LOC_DETAIL).fillna(d.location) if year >= 2010 else pd.NA
    if "PEDCGP" in d:
        d["pbtype_group"] = d.PEDCGP.map(PEDCGP).fillna("other_unknown")
        d["pbtype_position"] = d.PEDPOS.map(PEDPOS).fillna("other_unknown")
    my = d.MOD_YEAR.where(d.MOD_YEAR.between(1900, year + 1))
    d["vehicle_age_years"] = year - my
    d["vehicle_age"] = pd.cut(d.vehicle_age_years, [-2, 4, 9, 14, 19, 200],
                              labels=["0-4", "5-9", "10-14", "15-19", "20_plus"]).astype(str).replace("nan", "unknown")
    d["vehicle_class"] = d.vehicle.replace({"suv": "light_truck", "van": "light_truck", "pickup": "light_truck",
                                            "other_light": "light_truck"})
    return d


def long(d: pd.DataFrame, col: str) -> pd.DataFrame:
    x = d[d[col].notna()]
    return x.groupby(["year", col]).agg(deaths=("dark", "size"), dark_deaths=("dark", "sum")).reset_index().rename(
        columns={col: "category"})


def share(t: pd.DataFrame, dim: str, base: int = BASE) -> pd.DataFrame:
    w = t.pivot_table(index="category", columns="year", values="deaths", aggfunc="sum", fill_value=0)
    out = pd.DataFrame({"dimension": dim, "category": w.index, "base_year": base,
                        "deaths_base": w[base], "deaths_2022": w[PEAK], "deaths_2024": w[LAST]})
    for y in (PEAK, LAST):
        out[f"change_to_{y}"] = out[f"deaths_{y}"] - out.deaths_base
        out[f"share_of_increase_to_{y}"] = (out[f"change_to_{y}"] / out[f"change_to_{y}"].sum()).round(4)
    out["share_of_deaths_base"] = (out.deaths_base / out.deaths_base.sum()).round(4)
    out["share_of_deaths_2022"] = (out.deaths_2022 / out.deaths_2022.sum()).round(4)
    return out.sort_values("change_to_2022", ascending=False).reset_index(drop=True)


def census_age() -> pd.DataFrame:
    a = pd.read_csv(CENSUS / "us-est00int-alldata.csv")
    a = a[(a.MONTH == 7) & (a.AGE != 999) & a.YEAR.between(2000, 2009)][["YEAR", "AGE", "TOT_POP"]]
    a.columns = ["year", "age", "pop"]
    frames = [a]
    for f, yrs in [("nc-est2020-agesex-res.csv", range(2010, 2020)), ("nc-est2024-agesex-res.csv", range(2020, 2025))]:
        b = pd.read_csv(CENSUS / f)
        b = b[(b.SEX == 0) & (b.AGE != 999)]
        for y in yrs:
            frames.append(pd.DataFrame({"year": y, "age": b.AGE.values, "pop": b[f"POPESTIMATE{y}"].values}))
    p = pd.concat(frames)
    p["category"] = pd.cut(p.age, [-1, 15, 24, 44, 64, 200], labels=AGE_GROUPS).astype(str)
    return p.groupby(["year", "category"])["pop"].sum().reset_index().rename(columns={"pop": "population"})


def state_pop() -> pd.DataFrame:
    rows = []
    for st in FIPS.values():
        s = pd.read_csv(FRED / f"{st}POP.csv")
        s["year"] = pd.to_datetime(s.iloc[:, 0]).dt.year
        for y, v in zip(s.year, pd.to_numeric(s.iloc[:, 1], errors="coerce")):
            rows.append({"state": st, "year": y, "population": v * 1000})
    return pd.DataFrame(rows)


def main() -> None:
    frames = []
    for y in YEARS:
        d = year_frame(y)
        frames.append(d)
        tested = d.bac.notna()
        agree = (d.mi_p1[tested] == np.floor(d.bac[tested] * 100 + 1e-9)).mean()
        print(y, len(d), "tested", round(tested.mean(), 3), "MIPER.P1 = tested BAC (hundredths) for", round(agree, 3),
              "driver matched", round(d.drv_mi_bac08.notna().mean(), 3), "states", d.state.nunique(), flush=True)
    d = pd.concat(frames, ignore_index=True)
    shares = []

    def save(t: pd.DataFrame, topic: str, base: int = BASE) -> None:
        t.to_csv(FINAL / f"fars_decompose_{topic}.csv", index=False)
        shares.append(share(t, topic, base))

    # 1 age, with Census rates and a population-only counterfactual
    age = long(d, "age_group").merge(census_age(), on=["year", "category"], how="left")
    age["rate_per_100k"] = (age.deaths / age.population * 1e5).round(3)
    r09 = age[age.year == BASE].set_index("category").rate_per_100k
    age["deaths_at_2009_rates"] = (age.population * age.category.map(r09) / 1e5).round(0)
    save(age, "age")
    for c in ["sex", "hour_group", "month", "week_part_dark", "hit_run", "urban_rural", "region", "speed_limit",
              "location", "vehicle_age", "vehicle_class"]:
        topic = {"hour_group": "hour", "week_part_dark": "dayofweek", "vehicle_class": "vehicle_dark"}.get(c, c)
        t = long(d, c)
        if c == "speed_limit":
            t = t.merge(d.groupby("year").speed_limit_var.first().reset_index(), on="year")
        save(t, topic)
    save(long(d[d.year >= 2009], "speeding"), "speeding")
    loc_d = long(d[d.year >= 2010], "location_detail")
    loc_d.to_csv(FINAL / "fars_decompose_location_detail.csv", index=False)
    shares.append(share(loc_d, "location_detail", 2010))
    save(long(d[d.year >= 2014], "pbtype_group"), "pbtype_group", 2014)
    save(long(d[d.year >= 2014], "pbtype_position"), "pbtype_position", 2014)

    # alcohol: tested-only shares and multiple-imputation expected counts
    g = d.groupby("year")
    alc = pd.DataFrame({
        "deaths": g.size(),
        "ped_tested": g.bac.count(),
        "ped_tested_bac08": g.bac.apply(lambda s: (s >= 0.08).sum()),
        "ped_mi_bac08_expected": g.mi_bac08.sum().round(1),
        "driver_mi_bac08_expected": g.drv_mi_bac08.sum().round(1),
        "driver_matched": g.drv_mi_bac08.count(),
        "driver_reported_drinking": g.DR_DRINK.apply(lambda s: (s == 1).sum()),
    })
    alc["ped_tested_share"] = (alc.ped_tested / alc.deaths).round(4)
    alc["ped_bac08_share_of_tested"] = (alc.ped_tested_bac08 / alc.ped_tested).round(4)
    alc["ped_mi_bac08_share"] = (alc.ped_mi_bac08_expected / alc.deaths).round(4)
    alc["driver_mi_bac08_share"] = (alc.driver_mi_bac08_expected / alc.deaths).round(4)
    alc["dark_ped_mi_bac08_expected"] = d[d.dark].groupby("year").mi_bac08.sum().round(1)
    alc["dark_deaths"] = d[d.dark].groupby("year").size()
    alc.reset_index().to_csv(FINAL / "fars_decompose_alcohol.csv", index=False)
    for who, lab in [("ped", "ped"), ("driver", "driver")]:
        e = alc[f"{who}_mi_bac08_expected"]
        mi = pd.concat([pd.DataFrame({"year": alc.index.values, "category": f"{lab}_bac_08_plus", "deaths": e.values}),
                        pd.DataFrame({"year": alc.index.values, "category": f"{lab}_under_08" + ("_or_no_driver_record" if who == "driver" else ""),
                                      "deaths": (alc.deaths - e).values})])
        shares.append(share(mi, f"alcohol_{'pedestrian' if who == 'ped' else 'driver'}_imputed"))

    # cross-tabs the night question needs
    dk = d.assign(dark_label=np.where(d.dark, "dark", "not_dark"))
    for col in ["age_group", "urban_rural", "speed_limit", "location", "region", "sex"]:
        x = dk.assign(cat=dk[col] + "|" + dk.dark_label)
        shares.append(share(long(x, "cat"), f"{col}_x_dark"))
    season = pd.Series(np.where(dk.month.isin([10, 11, 12, 1, 2]), "oct_feb", "mar_sep"), index=dk.index)
    shares.append(share(long(dk.assign(cat=season + "|" + dk.dark_label), "cat"), "season_x_dark"))
    shares.append(share(long(dk.assign(cat=season + "|" + dk.hour_group), "cat"), "season_x_hour"))
    x = dk[dk.year >= 2014]
    shares.append(share(long(x.assign(cat=x.pbtype_group + "|" + x.dark_label), "cat"), "pbtype_group_x_dark", 2014))

    # state: 2009-11 vs 2021-23 averages
    sp = state_pop()
    st = d.groupby(["year", "state"]).size().rename("deaths").reset_index().merge(sp, on=["state", "year"], how="left")
    early, late = st[st.year.between(2009, 2011)], st[st.year.between(2021, 2023)]
    s = pd.DataFrame({"deaths_2009_11": early.groupby("state").deaths.mean(), "pop_2009_11": early.groupby("state").population.mean(),
                      "deaths_2021_23": late.groupby("state").deaths.mean(), "pop_2021_23": late.groupby("state").population.mean()})
    s["rate_2009_11"] = (s.deaths_2009_11 / s.pop_2009_11 * 1e5).round(2)
    s["rate_2021_23"] = (s.deaths_2021_23 / s.pop_2021_23 * 1e5).round(2)
    s["change_deaths"] = (s.deaths_2021_23 - s.deaths_2009_11).round(1)
    s["share_of_national_increase"] = (s.change_deaths / s.change_deaths.sum()).round(4)
    s["share_of_population_2021_23"] = (s.pop_2021_23 / s.pop_2021_23.sum()).round(4)
    s["deaths_if_2009_11_rate"] = (s.rate_2009_11 * s.pop_2021_23 / 1e5).round(1)
    s["region"] = s.index.map(REGION)
    s = s.sort_values("change_deaths", ascending=False)
    s.round(1).reset_index().to_csv(FINAL / "fars_decompose_state.csv", index=False)
    rg = s.groupby("region")[["deaths_2009_11", "deaths_2021_23", "pop_2009_11", "pop_2021_23", "change_deaths", "deaths_if_2009_11_rate"]].sum()
    rg["rate_2009_11"] = (rg.deaths_2009_11 / rg.pop_2009_11 * 1e5).round(2)
    rg["rate_2021_23"] = (rg.deaths_2021_23 / rg.pop_2021_23 * 1e5).round(2)
    rg["share_of_national_increase"] = (rg.change_deaths / rg.change_deaths.sum()).round(4)
    rg["share_of_population_2021_23"] = (rg.pop_2021_23 / rg.pop_2021_23.sum()).round(4)
    rg.round(1).reset_index().to_csv(FINAL / "fars_decompose_state_regions_avg.csv", index=False)

    sh = pd.concat(shares, ignore_index=True)
    sh.to_csv(FINAL / "fars_decompose_share_of_increase.csv", index=False)

    pd.set_option("display.width", 250)
    pd.set_option("display.max_rows", 400)
    cols = ["dimension", "category", "base_year", "deaths_base", "deaths_2022", "deaths_2024", "change_to_2022",
            "share_of_increase_to_2022", "share_of_increase_to_2024"]
    print(sh[sh.dimension.str.startswith("season")][cols].to_string(index=False))
    print(age[age.year.isin([2009, 2022, 2024])].to_string(index=False))
    print(age.groupby("year")[["deaths", "deaths_at_2009_rates"]].sum().loc[[2009, 2022, 2024]])
    print(alc.loc[[2000, 2005, 2009, 2014, 2015, 2019, 2022, 2023, 2024]].to_string())
    print(s.head(15).to_string())
    print(rg.to_string())


if __name__ == "__main__":
    main()
