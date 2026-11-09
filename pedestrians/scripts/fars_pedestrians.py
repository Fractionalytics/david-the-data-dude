"""Annual US pedestrian deaths from NHTSA's crash census (FARS), broken down
by light, road type, sidewalk and the vehicle that struck them.

    python scripts/fetch_fars.py 2000 2024      (downloads, cached)
    python scripts/fars_pedestrians.py
      reads  data/raw/fars/FARS<YEAR>NationalCSV.zip (read in place, never extracted)
      writes data/final/fars_ped_by_light.csv
             data/final/fars_ped_by_road.csv
             data/final/fars_ped_by_sidewalk.csv      (2014 on)
             data/final/fars_ped_dark_arterial.csv
             data/final/fars_ped_by_vehicle.csv
             data/final/fars_ped_totals_check.csv     (vs. IIHS published counts)

A pedestrian death is a PERSON record with PER_TYP = 5 (pedestrian) and
INJ_SEV = 4 (fatal). Other non-motorists (cyclists, people on personal
conveyances) are excluded, as in NHTSA's and IIHS's pedestrian counts.

Code mappings (checked against the NAME columns the files carry from 2015 on,
and against code distributions in the earlier years):

  Light (ACCIDENT.LGT_COND, crash level)
    daylight 1 | dawn_dusk 4, 5 | dark 2 not lighted, 3 lighted, 6 unknown
    lighting (code 6 exists from 2009) | other_unknown 7, 8, 9

  Road (ACCIDENT.ROAD_FNC through 2014, FUNC_SYS from 2015)
                       ROAD_FNC (rural / urban)      FUNC_SYS
    interstate_freeway 1, 11 interstate; 12 urban    1 interstate, 2 other
                       other freeway/expressway      freeway/expressway
    arterial           2 rural other principal,      3 other principal,
                       3 rural minor; 13 urban other 4 minor arterial
                       principal, 14 urban minor
    collector          4, 5 rural major/minor; 15    5 major, 6 minor collector
    local              6, 16                         7
    unknown            9, 19, 99                     96 not in state
                                                     inventory, 98, 99
  Caveat: ROAD_FNC has no rural freeway code, so rural freeways that are not
  interstates sit in "arterial" through 2014 and in "interstate_freeway" from
  2015. The 2015 switch also came with states re-classifying roads (FHWA's
  HPMS codes), so expect a step in 2014-15.

  Sidewalk (PBTYPE.PBSWALK, first published for 2014)
    yes 1 | none_noted 0 | unknown 8, 9. "None noted" means the crash report
    did not note one, not proof there was none.

  Striking vehicle (VEHICLE.BODY_TYP of the vehicle that struck the pedestrian)
    Identified by the pedestrian's PERSON.N_MOT_NO ("striking vehicle number")
    for 2000-2010 and PERSON.STR_VEH (its new name) from 2011. If neither gives
    a vehicle, fall back to the only vehicle in a single-vehicle crash
    (ACCIDENT.VE_FORMS = 1); otherwise "unmatched". In the 2000-2024 files every
    pedestrian death carries a valid striking-vehicle number that joins to a
    VEHICLE row, so the fallback is never used.
    Station wagons (code 6) count as cars; FARS codes most crossovers as
    compact utility (14), so they count as SUVs.
    car          1-13, 17 (sedans, coupes, hatchbacks, wagons, auto-based pickups)
    light truck  suv 14-16, 19 | van 20-29 | pickup 30-39 | other_light 40-48
    large_truck  60-64, 66, 67, 71, 72, 78, 79 (NHTSA's large-truck codes)
    other        buses 50-59, motorcycles 80-89, motor homes 65, 73, other 90-97
    unknown      49 (unknown light vehicle), 98, 99, and unmatched
"""

import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "fars"
FINAL = ROOT / "data" / "final"
YEARS = range(2000, 2025)
IIHS = {2000: 4763, 2005: 4892, 2009: 4109, 2015: 5495, 2019: 6272, 2022: 7593, 2023: 7367}

LIGHT = {1: "daylight", 4: "dawn_dusk", 5: "dawn_dusk", 2: "dark_not_lighted", 3: "dark_lighted", 6: "dark_unknown_lighting"}
ROAD_FNC = {1: "interstate_freeway", 11: "interstate_freeway", 12: "interstate_freeway",
            2: "arterial", 3: "arterial", 13: "arterial", 14: "arterial",
            4: "collector", 5: "collector", 15: "collector", 6: "local", 16: "local"}
FUNC_SYS = {1: "interstate_freeway", 2: "interstate_freeway", 3: "arterial", 4: "arterial",
            5: "collector", 6: "collector", 7: "local"}
SIDEWALK = {1: "yes", 0: "none_noted"}


def body_class(b: float) -> str:
    if pd.isna(b):
        return "unknown"
    b = int(b)
    if 1 <= b <= 13 or b == 17:
        return "car"
    if 14 <= b <= 16 or b == 19:
        return "suv"
    if 20 <= b <= 29:
        return "van"
    if 30 <= b <= 39:
        return "pickup"
    if 40 <= b <= 48:
        return "other_light"
    if b in (60, 61, 62, 63, 64, 66, 67, 71, 72, 78, 79):
        return "large_truck"
    if 50 <= b <= 97:
        return "other"
    return "unknown"


def load(year: int, table: str, cols: list[str]) -> pd.DataFrame:
    z = zipfile.ZipFile(RAW / f"FARS{year}NationalCSV.zip")
    m = [i for i in z.infolist() if i.filename.rsplit("/", 1)[-1].lower() == f"{table}.csv"]
    if not m:
        return pd.DataFrame(columns=cols)
    clean = lambda c: c.upper().replace("ï»¿", "").replace("﻿", "").strip()
    with z.open(m[0]) as f:
        d = pd.read_csv(f, encoding="latin-1", low_memory=False, usecols=lambda c: clean(c) in cols)
    return d.rename(columns=clean)


def year_peds(year: int) -> tuple[pd.DataFrame, str]:
    p = load(year, "person", ["ST_CASE", "VEH_NO", "PER_NO", "PER_TYP", "INJ_SEV", "N_MOT_NO", "STR_VEH"])
    peds = p[(p.PER_TYP == 5) & (p.INJ_SEV == 4)].copy()
    a = load(year, "accident", ["ST_CASE", "LGT_COND", "ROAD_FNC", "FUNC_SYS", "VE_FORMS"])
    peds = peds.merge(a, on="ST_CASE", how="left", validate="m:1")
    peds["year"] = year
    peds["light"] = peds.LGT_COND.map(LIGHT).fillna("other_unknown")
    peds["dark"] = peds.light.str.startswith("dark")
    road_var = "FUNC_SYS" if "FUNC_SYS" in peds and peds.FUNC_SYS.notna().any() else "ROAD_FNC"
    peds["road"] = peds[road_var].map(FUNC_SYS if road_var == "FUNC_SYS" else ROAD_FNC).fillna("unknown")

    pb = load(year, "pbtype", ["ST_CASE", "VEH_NO", "PER_NO", "PBSWALK"])
    if len(pb):
        peds = peds.merge(pb, on=["ST_CASE", "VEH_NO", "PER_NO"], how="left", validate="1:1")
        peds["sidewalk"] = peds.PBSWALK.map(SIDEWALK).fillna("unknown")
    else:
        peds["sidewalk"] = pd.NA

    sv = "STR_VEH" if "STR_VEH" in peds else "N_MOT_NO"
    v = load(year, "vehicle", ["ST_CASE", "VEH_NO", "BODY_TYP"])
    peds["str_veh"] = pd.to_numeric(peds[sv], errors="coerce").where(lambda s: s.between(1, 900))
    peds["match"] = sv.lower()
    single = peds.str_veh.isna() & (peds.VE_FORMS == 1)
    peds.loc[single, "str_veh"] = 1
    peds.loc[single, "match"] = "single_vehicle"
    peds.loc[peds.str_veh.isna(), "match"] = "unmatched"
    peds = peds.merge(v.rename(columns={"VEH_NO": "str_veh"}), on=["ST_CASE", "str_veh"], how="left", validate="m:1")
    peds["vehicle"] = peds.BODY_TYP.map(body_class)
    return peds, road_var


def table(d: pd.DataFrame, col: str, order: list[str]) -> pd.DataFrame:
    t = d.groupby(["year", col]).size().unstack(fill_value=0).reindex(columns=order, fill_value=0)
    t.insert(0, "total", t.sum(axis=1))
    return t


def main() -> None:
    FINAL.mkdir(parents=True, exist_ok=True)
    frames, notes = [], []
    for y in YEARS:
        d, road_var = year_peds(y)
        frames.append(d)
        notes.append({"year": y, "road_var": road_var, "striking_field": d.match.mode()[0],
                      "pbswalk_codes": sorted(d.PBSWALK.dropna().astype(int).unique()) if "PBSWALK" in d else [],
                      **d.match.value_counts().to_dict()})
        print(y, len(d), road_var, d.match.value_counts().to_dict(), flush=True)
    d = pd.concat(frames, ignore_index=True)
    print(pd.DataFrame(notes).to_string(index=False))

    chk = d.groupby("year").size().rename("fars_ped_deaths").to_frame()
    chk["iihs_published"] = pd.Series(IIHS)
    chk["pct_diff"] = (chk.fars_ped_deaths / chk.iihs_published - 1).mul(100).round(2)
    chk.to_csv(FINAL / "fars_ped_totals_check.csv")
    print(chk.to_string())

    light = table(d, "light", ["daylight", "dawn_dusk", "dark_lighted", "dark_not_lighted", "dark_unknown_lighting", "other_unknown"])
    light.insert(3, "dark", light[["dark_lighted", "dark_not_lighted", "dark_unknown_lighting"]].sum(axis=1))
    light["dark_share"] = (light.dark / light.total).round(4)
    light.to_csv(FINAL / "fars_ped_by_light.csv")

    road = table(d, "road", ["arterial", "interstate_freeway", "collector", "local", "unknown"])
    road["arterial_share"] = (road.arterial / road.total).round(4)
    road["road_variable"] = pd.Series({n["year"]: n["road_var"] for n in notes})
    road.to_csv(FINAL / "fars_ped_by_road.csv")

    sw = table(d[d.sidewalk.notna()], "sidewalk", ["yes", "none_noted", "unknown"])
    sw["none_noted_share"] = (sw.none_noted / sw.total).round(4)
    sw.to_csv(FINAL / "fars_ped_by_sidewalk.csv")

    da = d.assign(dark_arterial=d.dark & (d.road == "arterial")).groupby("year").agg(
        total=("dark", "size"), dark=("dark", "sum"), arterial=("road", lambda s: (s == "arterial").sum()),
        dark_arterial=("dark_arterial", "sum"))
    da["dark_arterial_share"] = (da.dark_arterial / da.total).round(4)
    da.to_csv(FINAL / "fars_ped_dark_arterial.csv")

    veh = table(d, "vehicle", ["car", "suv", "van", "pickup", "other_light", "large_truck", "other", "unknown"])
    veh.insert(2, "light_truck", veh[["suv", "van", "pickup", "other_light"]].sum(axis=1))
    known = veh.total - veh.unknown
    veh["light_truck_share_of_known"] = (veh.light_truck / known).round(4)
    veh["car_share_of_known"] = (veh.car / known).round(4)
    veh["unknown_share"] = (veh.unknown / veh.total).round(4)
    m = d.groupby(["year", "match"]).size().unstack(fill_value=0)
    veh["matched_by_person_field"] = m.drop(columns=["single_vehicle", "unmatched"], errors="ignore").sum(axis=1)
    veh["matched_by_single_vehicle"] = m.get("single_vehicle", 0)
    veh["unmatched"] = m.get("unmatched", 0)
    veh.to_csv(FINAL / "fars_ped_by_vehicle.csv")

    for name, t in [("light", light), ("road", road), ("sidewalk", sw), ("dark x arterial", da), ("vehicle", veh)]:
        print("\n==", name)
        print(t.to_string())


if __name__ == "__main__":
    main()
