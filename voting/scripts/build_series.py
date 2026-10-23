"""Build the turnout and trust series from the raw downloads in data/raw/.

Outputs (data/processed/):
- turnout.csv: one row per federal general election, 1890-2024.
    vep_turnout         UF Election Lab (Michael McDonald), voting-eligible population. CC BY 4.0.
    vep_count, ballots  UF Election Lab state files' "United States" rows, 1980-2024 (people, not %).
                        ballots = total ballots counted, or vote for highest office where that's missing (1980-1996).
    cps_citizen_turnout Census CPS Table A-1, % of voting-age citizens who SAY they voted (1978+).
    cps_registered      Census CPS Table A-1, % of voting-age citizens who say they are registered.
    cps_turnout_of_registered  cps_citizen_turnout / cps_registered: the "% of registered voters" rate.
- turnout_by_age.csv: Census CPS Table A-1, % who say they voted, by age group.
    cps_citizen_turnout  % of citizens (by age, only from 2002)
    cps_total_turnout    % of everyone that age, noncitizens included (1964+); lower, especially for the young
    population_k         everyone that age, in thousands (CPS)
    voters_k             population_k x cps_total_turnout: self-reported voters, in thousands
    share_of_voters      that age group's % of all self-reported voters that year
    share_of_adults      that age group's % of the voting-age population that year
- trust.csv: long format, one row per reading.
    gallup_congress     Gallup "great deal" + "quite a lot" confidence in Congress (June topline, 1998-2026).
    pew_trust           Pew compilation: trust the government in Washington "always" or "most of the time"
                        (individual polls from NES/ANES, Gallup, CBS/NYT, ABC/Post, CNN, Pew).

CPS turnout is self-reported and runs above official counts; nonresponse is counted as "did not vote".
"""
import re
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed"
OUT.mkdir(exist_ok=True)


def vep():
    df = pd.read_csv(RAW / "US_VEP_Turnout_Rates_v1.4.csv").dropna(how="all")
    df["type"] = df["TURNOUT_RATE_PRES"].notna().map({True: "presidential", False: "midterm"})
    df["vep_turnout"] = df["TURNOUT_RATE_PRES"].fillna(df["TURNOUT_RATE_MIDTERM"]) * 100
    return df.rename(columns={"YEAR": "year"})[["year", "type", "vep_turnout"]]


def cps():
    x = pd.read_excel(RAW / "census_cps_hst_vote01.xlsx", header=None)
    # Each block starts with a label row in column 0, then year rows; column 2 is % of the total
    # population, column 3 is % of the citizen population.
    def block(label, col=3):
        start = x.index[x[0].astype(str).str.strip() == label][0] + 1
        rows = []
        for _, r in x.iloc[start:].iterrows():
            if not re.fullmatch(r"\d{4}", str(r[0]).strip()):
                break
            rows.append((int(r[0]), pd.to_numeric(r[col], errors="coerce")))
        return pd.DataFrame(rows, columns=["year", label])

    ages = []
    for a in ["18 to 24 Years", "25 to 44 Years", "45 to 64 Years", "65 Years and Over"]:
        lab = f"{a}, Percent Voted"
        c = block(lab).rename(columns={lab: "cps_citizen_turnout"})
        t = block(lab, col=2).rename(columns={lab: "cps_total_turnout"})
        n = block(lab, col=1).rename(columns={lab: "population_k"})
        ages.append(c.merge(t, on="year").merge(n, on="year").assign(age=a.replace(" Years", "")))
    by_age = pd.concat(ages)
    by_age["type"] = (by_age["year"] % 4 == 0).map({True: "presidential", False: "midterm"})
    by_age["voters_k"] = (by_age["population_k"] * by_age["cps_total_turnout"] / 100).round()
    by_age["share_of_voters"] = (by_age["voters_k"] / by_age.groupby("year")["voters_k"].transform("sum") * 100).round(1)
    by_age["share_of_adults"] = (by_age["population_k"] / by_age.groupby("year")["population_k"].transform("sum") * 100).round(1)
    by_age[["year", "type", "age", "cps_citizen_turnout", "cps_total_turnout", "population_k", "voters_k",
            "share_of_voters", "share_of_adults"]].to_csv(OUT / "turnout_by_age.csv", index=False)

    v = block("Total, Percent Voted").rename(columns={"Total, Percent Voted": "cps_citizen_turnout"})
    g = block("Total, Percent Registered").rename(columns={"Total, Percent Registered": "cps_registered"})
    df = v.merge(g, on="year")
    df["cps_turnout_of_registered"] = (df["cps_citizen_turnout"] / df["cps_registered"] * 100).round(1)
    return df


def gallup():
    text = "\n".join(p.extract_text() for p in PdfReader(RAW / "gallup_confidence_topline_2026-06.pdf").pages)
    # Recent-trend table: "2026 Jun 33 61 27 ..." with 17 columns A-Q; G (index 6) is Congress.
    rows = []
    for m in re.finditer(r"^(\d{4}) (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) ((?:\S+ ?){17})", text, re.M):
        vals = [None if v == "--" else int(v) for v in m.group(2).split()[:17]]
        rows.append({"year": int(m.group(1)), "gallup_congress": vals[6]})
    df = pd.DataFrame(rows).drop_duplicates("year")
    return df.melt("year", var_name="series", value_name="value")


def pew():
    lines = (RAW / "pew_trust_1958-2025.md").read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("| Date |  | Individual polls"))
    rows = []
    for l in lines[start + 2:]:
        if not l.startswith("|"):
            break
        cells = [c.strip() for c in l.strip("|").split("|")]
        if cells[2]:
            rows.append({"date": pd.to_datetime(cells[0]), "source": cells[1], "value": float(cells[2])})
    df = pd.DataFrame(rows)
    df["year"], df["series"] = df["date"].dt.year, "pew_trust"
    return df


def vep_counts():
    """National VEP and ballots (people, not rates): 1980-2022 file plus the 2024 file."""
    num = lambda s: pd.to_numeric(s.astype(str).str.replace(",", ""), errors="coerce")
    a = pd.read_csv(RAW / "Turnout_1980_2022_v1.2.csv")
    a = a[a["STATE"] == "United States"]
    # 1980-1996 have no total-ballots count; vote for highest office stands in.
    a = pd.DataFrame({"year": a["YEAR"], "vep_count": num(a["VEP"]),
                      "ballots": num(a["TOTAL_BALLOTS_COUNTED"]).fillna(num(a["VOTE_FOR_HIGHEST_OFFICE"]))})
    b = pd.read_csv(RAW / "Turnout_2024G_v0.4.csv")
    b = b[b["STATE"] == "United States"]
    b = pd.DataFrame({"year": [2024], "vep_count": num(b["VEP"]).values, "ballots": num(b["TOTAL_BALLOTS_COUNTED"]).values})
    return pd.concat([a, b], ignore_index=True)


turnout = vep().merge(vep_counts(), on="year", how="left").merge(cps(), on="year", how="left")
turnout.to_csv(OUT / "turnout.csv", index=False)
trust = pd.concat([gallup(), pew()], ignore_index=True)[["series", "year", "date", "source", "value"]]
trust.to_csv(OUT / "trust.csv", index=False)
print(f"turnout.csv: {len(turnout)} rows, {turnout.year.min()}-{turnout.year.max()}")
print(trust.groupby("series").agg(n=("value", "size"), first=("year", "min"), last=("year", "max")))
