"""US vs. EU drug use and drug deaths by drug type: the arithmetic behind
docs/research-drugs/by-drug-type.md.

    python scripts/research_by_drug_type.py
      reads  data/raw/nchs_databriefs/db491-tables.pdf values (typed in below, read 2026-11-11)
             data/raw/census/*.csv                     (US population)
             data/raw/eurostat/demo_gind.csv           (EU population)
             data/final/compare_drug_deaths_eu.csv     (EUDA DRD-17..20, from compare_drug_deaths.py)
             data/raw/who_ghe/*.csv                    (WHO GHE 2021 via Our World in Data)
      writes data/final/research_by_drug_type_latest.csv
             data/final/research_by_drug_type_trend_us.csv
             data/final/research_by_drug_type_trend_who.csv

Every hard-coded number below is copied from a primary document; the comment
on each line says which one and which page or table.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from us_eu_decompose import EU27, YEARS, eurostat  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "final"

# ---------------------------------------------------------------- populations
a = pd.read_csv(RAW / "census" / "us-est00int-alldata.csv")
b = pd.read_csv(RAW / "census" / "nc-est2020-agesex-res.csv")
c = pd.read_csv(RAW / "census" / "nc-est2024-agesex-res.csv")
US_POP = {int(y): int(p) for y, p in a[(a.MONTH == 7) & (a.AGE == 999)][["YEAR", "TOT_POP"]].values if y <= 2009}
row = b[(b.SEX == 0) & (b.AGE == 999)].iloc[0]
US_POP.update({y: int(row[f"POPESTIMATE{y}"]) for y in range(2010, 2020)})
row = c[(c.SEX == 0) & (c.AGE == 999)].iloc[0]
US_POP.update({y: int(row[f"POPESTIMATE{y}"]) for y in range(2020, 2025)})
c_all = c[(c.SEX == 0) & (c.AGE != 999)]
US_1564 = {y: int(c_all[(c_all.AGE >= 15) & (c_all.AGE <= 64)][f"POPESTIMATE{y}"].sum()) for y in (2023, 2024)}

_, EPOP = eurostat()
EU_POP = {y: float(EPOP.loc[y, "EU27_2020"]) for y in (2009, 2021, 2022, 2023, 2024)}
DE_POP_2023 = float(EPOP.loc[2023, "DE"])

# ----------------------------------------------------------- US deaths (NCHS)
# NCHS Data Brief 491, data tables for Figures 1, 4 and 5 (deaths, 2002-2022).
DB491 = {  # year: (all, any_opioid, heroin, nat_semi, methadone, synthetic, cocaine, psychostim)
    2009: (37004, 20422, 3278, 9735, 4696, 2946, 4350, 1632),
    2010: (38329, 21089, 3036, 10943, 4577, 3007, 4183, 1854),
    2011: (41340, 22784, 4397, 11693, 4418, 2666, 4681, 2266),
    2012: (41502, 23166, 5925, 11140, 3932, 2628, 4404, 2635),
    2013: (43982, 25052, 8257, 11346, 3591, 3105, 4944, 3627),
    2014: (47055, 28647, 10574, 12159, 3400, 5544, 5415, 4298),
    2015: (52404, 33091, 12989, 12727, 3301, 9580, 6784, 5716),
    2016: (63632, 42249, 15469, 14487, 3373, 19413, 10375, 7542),
    2017: (70237, 47600, 15482, 14495, 3194, 28466, 13942, 10333),
    2018: (67367, 46802, 14996, 12552, 3023, 31335, 14666, 12676),
    2019: (70630, 49860, 14019, 11886, 2740, 36359, 15883, 16167),
    2020: (91799, 68630, 13165, 13471, 3543, 56516, 19447, 23837),
    2021: (106699, 80411, 9173, 13618, 3678, 70601, 24486, 32537),
    2022: (107941, 81806, 5871, 11871, 3334, 73838, 27569, 34022),
    # NCHS Data Brief 549 (2023 and 2024 by drug type).
    2023: (105007, 79358, 3984, 10112, 3355, 72776, 29449, 34855),
    2024: (79384, 54045, 2743, 7989, 3229, 47735, 21945, 28722),
}
COLS = ["all", "any_opioid", "heroin", "rx_opioid_nat_semi", "methadone", "synthetic_fentanyl", "cocaine", "psychostim_meth"]
us = pd.DataFrame.from_dict(DB491, orient="index", columns=COLS)
us.index.name = "year"
us_pm = us.div(pd.Series(US_POP), axis=0).dropna() * 1e6
us_pm.round(1).to_csv(OUT / "research_by_drug_type_trend_us.csv")
US_BENZO_2023 = 10870  # NIDA "Drug Overdose Death Rates" (Aug 2024), from CDC WONDER, T42.4

# US deaths aged 15-64 (NCHS Data Brief 549, age table: 15-24 ... 55-64)
US_DEATHS_1564 = {2023: 5926 + 20770 + 27005 + 21593 + 20606, 2024: 3810 + 14131 + 20116 + 16735 + 16087}

# ---------------------------------------------------------- EU deaths (EUDA)
eu = pd.read_csv(OUT / "compare_drug_deaths_eu.csv")
eu_with, eu_without, eu_rep_pop = eu.with_opioids.sum(), eu.without_opioids.sum(), eu["pop"].sum()
eu_with_pop = eu.loc[eu.with_opioids.notna(), "pop"].sum()
EDR = {  # European Drug Report 2025, PDF page numbers (printed page = PDF page - 1)
    "all_2023": 7500,           # p. 26 / p. 210 ("almost 7500"); p. 218 gives "at least 7459"
    "rate_1564_2023": 24.7,     # p. 26 and p. 217, per million aged 15-64
    "heroin_2023_18ms": 1200,   # p. 211: ~1200 in 2023, 18 EU MS with both years
    "heroin_2023_eu": 1600,     # p. 293: "provisionally estimated ... 1600 deaths in the EU"
    "cocaine_2023_20c": 1051,   # p. 87 and p. 294: 20 countries, 26 %
    "fentanyl_2023_16ms": 153,  # p. 295: 16 EU MS
    "oxycodone_2023_8c": 151,   # p. 296: 8 countries
    "tramadol_2023_13c": 173,   # p. 295: 13 European countries (about 5 %)
    "cathinones_2023_7c": 39,   # p. 296
    "mdma_de_2023": 105,        # p. 122: Germany only
    # p. 295: deaths with non-cocaine stimulants, EU members only (Turkiye 228 and Norway 64 left out)
    "nonco_stim_2023": {"DE": 490, "SE": 75, "DK": 61, "FI": 49, "LV": 41, "EE": 32, "AT": 30},
}
nonco = sum(EDR["nonco_stim_2023"].values())
eu1564_pop = EDR["all_2023"] / EDR["rate_1564_2023"] * 1e6  # implied EU population aged 15-64

def pm_eu(n, y=2023):
    return n / EU_POP[y] * 1e6

us24 = us.loc[2024] / US_POP[2024] * 1e6
us23 = us.loc[2023] / US_POP[2023] * 1e6
rows = [
    # type, US deaths/M (2024), EU deaths/M, EU basis
    ("All drugs", us24["all"], pm_eu(EDR["all_2023"]), "EU ~7,500 (2023, EDR p.26) / EU27 pop"),
    ("Any opioid", us24.any_opioid, eu_with / eu_with_pop * 1e6, "EUDA DRD-18 with opioids, latest year per country / reporting pop"),
    ("Heroin", us24.heroin, pm_eu(EDR["heroin_2023_eu"]), "EU 1,600 provisional (EDR p.293) / EU27 pop"),
    ("Heroin (18-MS count)", us24.heroin, pm_eu(EDR["heroin_2023_18ms"]), "EU 1,200, 18 MS (EDR p.211) / EU27 pop = floor"),
    ("Synthetic opioids / fentanyl", us24.synthetic_fentanyl, pm_eu(EDR["fentanyl_2023_16ms"]), "153 fentanyl deaths, 16 MS (EDR p.295) / EU27 pop = floor"),
    ("Rx opioids (US T40.2; EU oxycodone+tramadol)", us24.rx_opioid_nat_semi, pm_eu(EDR["oxycodone_2023_8c"] + EDR["tramadol_2023_13c"]), "151 oxycodone + 173 tramadol (EDR p.295-296) / EU27 pop = floor, overlap possible"),
    ("Methadone", us24.methadone, float("nan"), "no EU count"),
    ("Psychostimulants / non-cocaine stimulants", us24.psychostim_meth, pm_eu(nonco), f"{nonco} in 7 EU MS (EDR p.295) / EU27 pop = floor"),
    ("Cocaine", us24.cocaine, pm_eu(EDR["cocaine_2023_20c"]), "1,051 in 20 countries (EDR p.87) / EU27 pop = floor"),
    ("Without opioids", (us.loc[2024, "all"] - us.loc[2024, "any_opioid"]) / US_POP[2024] * 1e6, eu_without / eu_with_pop * 1e6, "EUDA DRD-19 / reporting pop"),
    ("Benzodiazepines (US 2023)", US_BENZO_2023 / US_POP[2023] * 1e6, float("nan"), "no EU count"),
]
latest = pd.DataFrame(rows, columns=["type", "us_per_m", "eu_per_m", "eu_basis"])
latest["ratio"] = latest.us_per_m / latest.eu_per_m
latest.round(2).to_csv(OUT / "research_by_drug_type_latest.csv", index=False)

# ------------------------------------------------------------- WHO GHE trend
def who(fn, name):
    w = pd.read_csv(RAW / "who_ghe" / fn)
    w.columns = ["entity", "code", "year", name]
    return w.drop(columns="entity")

ISO3 = {"AT": "AUT", "BE": "BEL", "BG": "BGR", "CY": "CYP", "CZ": "CZE", "DE": "DEU", "DK": "DNK", "EE": "EST",
        "EL": "GRC", "ES": "ESP", "FI": "FIN", "FR": "FRA", "HR": "HRV", "HU": "HUN", "IE": "IRL", "IT": "ITA",
        "LT": "LTU", "LU": "LUX", "LV": "LVA", "MT": "MLT", "NL": "NLD", "PL": "POL", "PT": "PRT", "RO": "ROU",
        "SE": "SWE", "SI": "SVN", "SK": "SVK"}
w = who("death-rates-from-drug-use-disorders-who.csv", "all")
for fn, n in [("death-rate-from-opioid-use-who.csv", "opioid"), ("death-rates-cocaine-who.csv", "cocaine"),
              ("death-rate-amphetamine-who.csv", "amphetamine")]:
    w = w.merge(who(fn, n), on=["code", "year"], how="outer")
w["other"] = w["all"] - w.opioid - w.cocaine - w.amphetamine  # incl. cannabis and other drug use disorders

d, pop = eurostat()
ped = d[(d.pers_cat == "PED") & (d.age == "TOTAL")].pivot_table(index="TIME_PERIOD", columns="geo", values="OBS_VALUE")
tot = d[(d.pers_cat == "TOTAL") & (d.age == "TOTAL")].pivot_table(index="TIME_PERIOD", columns="geo", values="OBS_VALUE")
eu18 = [g for g in EU27 if ped.reindex(YEARS)[g].notna().all() and tot.reindex(YEARS)[g].notna().all()]
out = []
for label, members in (("EU-18 (Reel)", eu18), ("EU-27", EU27)):
    p = pop[members].stack().rename("population").reset_index()
    p.columns = ["year", "geo", "population"]
    m = p.assign(code=p.geo.map(ISO3)).merge(w, on=["code", "year"])
    for y, g in m.groupby("year"):
        r = {"group": label, "year": y}
        for k in ("all", "opioid", "cocaine", "amphetamine", "other"):
            r[k] = (g[k] * g.population).sum() / g.population.sum()
        out.append(r)
for y, g in w[w.code == "USA"].groupby("year"):
    out.append({"group": "US", "year": y, **{k: g[k].iloc[0] for k in ("all", "opioid", "cocaine", "amphetamine", "other")}})
tr = pd.DataFrame(out).query("2000 <= year <= 2021")
tr.round(3).to_csv(OUT / "research_by_drug_type_trend_who.csv", index=False)

# ------------------------------------------------------------------- print
pd.set_option("display.width", 200)
print("Populations: US 2009 %d, 2023 %d, 2024 %d; US 15-64 2023 %d; EU27 2023 %.0f; implied EU 15-64 %.0f"
      % (US_POP[2009], US_POP[2023], US_POP[2024], US_1564[2023], EU_POP[2023], eu1564_pop))
print("EU DRD: with opioids %d, without %d, reporting pop %.0f (with-opioid pop %.0f)" % (eu_with, eu_without, eu_rep_pop, eu_with_pop))
print("\nLatest deaths per million (US 2024 unless noted; EU 2023 or latest)")
print(latest[["type", "us_per_m", "eu_per_m", "ratio"]].round(1).to_string(index=False))
print("\nLike-for-like all-drug rate, per million aged 15-64 (2023): US %.1f vs EU %.1f -> %.1fx"
      % (US_DEATHS_1564[2023] / US_1564[2023] * 1e6, EDR["rate_1564_2023"],
         US_DEATHS_1564[2023] / US_1564[2023] * 1e6 / EDR["rate_1564_2023"]))
print("US 2024 15-64: %.1f per million -> %.1fx EU 2023" % (US_DEATHS_1564[2024] / US_1564[2024] * 1e6,
      US_DEATHS_1564[2024] / US_1564[2024] * 1e6 / EDR["rate_1564_2023"]))
print("German MDMA deaths 2023: %.2f per million Germans" % (EDR["mdma_de_2023"] / DE_POP_2023 * 1e6))
print("EU high-risk opioid users 860,000 as share of 15-64: %.2f%%" % (860000 / eu1564_pop * 100))
print("EU share of deaths: heroin %.0f%% (1,600) / %.0f%% (1,200); cocaine 26%% (20 countries); fentanyl %.1f%%"
      % (1600 / 7500 * 100, 1200 / 7500 * 100, 153 / 7500 * 100))
print("US share of deaths 2024: " + ", ".join(f"{k} {us.loc[2024, k] / us.loc[2024, 'all'] * 100:.0f}%" for k in COLS[1:]))
print("US benzodiazepines 2023: %.0f%% of all overdose deaths" % (US_BENZO_2023 / us.loc[2023, "all"] * 100))

print("\nUS deaths per million, by drug (NCHS)")
print(us_pm.loc[[2009, 2012, 2015, 2019, 2021, 2022, 2023, 2024]].round(1).to_string())
print("\nUS change 2009 -> 2023 peak-ish and -> 2024 (x)")
print((us_pm.loc[2023] / us_pm.loc[2009]).round(1).to_string(), "\n", (us_pm.loc[2024] / us_pm.loc[2009]).round(1).to_string())

print("\nWHO GHE deaths per 100,000 (underlying cause = drug use disorder), US vs EU")
for k in ("all", "opioid", "cocaine", "amphetamine", "other"):
    t = tr.pivot_table(index="year", columns="group", values=k)
    t["US/EU-18"] = t["US"] / t["EU-18 (Reel)"]
    t["US/EU-27"] = t["US"] / t["EU-27"]
    print(f"\n[{k}]")
    print(t.loc[[2000, 2009, 2012, 2015, 2019, 2021]].round(3).to_string())

print("\nUse ratios (US 18+ 2024 / EU 15-64 latest)")
use = {"cannabis": (23.4, 22.3, 8.4), "cocaine": (1.6, 1.5, 1.6), "mdma": (0.7, 0.7, 1.1), "meth vs amphetamines": (0.9, 0.8, 0.8)}
for k, (u18, u12, e) in use.items():
    print(f"  {k}: US 18+ {u18}% / EU {e}% = {u18 / e:.2f}x ; US 12+ {u12}% = {u12 / e:.2f}x")
print("  US meth + Rx stimulant misuse 12+: 0.8 + 1.4 = 2.2%% -> %.1fx EU amphetamines" % (2.2 / 0.8))

print("\nDeaths-to-use ratio (deaths per million / last-year use %): crude 'lethality per user' index")
for k, dpm_us, u_us, dpm_eu, u_eu in [("cocaine", us24.cocaine, 1.5, pm_eu(1051), 1.6),
                                       ("meth/amphetamines", us24.psychostim_meth, 0.8, pm_eu(nonco), 0.8)]:
    a_, b_ = dpm_us / u_us, dpm_eu / u_eu
    print(f"  {k}: US {a_:.1f}, EU {b_:.1f} -> {a_ / b_:.0f}x")
