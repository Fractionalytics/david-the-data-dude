"""Why cocaine kills ~28x more people per head in the US than in the EU, when
about the same share of people use it: the arithmetic behind
docs/research-drugs/cocaine-gap.md.

    python scripts/research_cocaine_gap.py
      reads  data/raw/census/*.csv                     (US population)
             data/raw/eurostat/demo_gind.csv           (EU population, Spain)
             data/raw/ons/2025substances.xlsx          (England & Wales deaths by substance, 1993-2025 registrations)
             data/raw/ons/ewpop_timeseries.json        (England & Wales mid-year population)
             data/raw/cdc_meth/vsrr_...xkb8-kh2a.csv   (US provisional 2025 cocaine count)
             data/final/research_by_drug_type_trend_who.csv (WHO GHE, from research_by_drug_type.py)
      writes data/final/research_cocaine_gap_decomposition.csv
             data/final/research_cocaine_gap_comparators.csv
             data/final/research_cocaine_gap_trend.csv

Every hard-coded number is copied from a primary document; the comment on each
line says which one. "EDR" = European Drug Report 2025 full-book PDF, PDF page
numbers. Anything marked ASSUMPTION or ESTIMATE is ours, not a published figure.
"""
import json
import math
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from us_eu_decompose import eurostat  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "final"

# ---------------------------------------------------------------- populations
a = pd.read_csv(RAW / "census" / "us-est00int-alldata.csv")
b = pd.read_csv(RAW / "census" / "nc-est2020-agesex-res.csv")
c = pd.read_csv(RAW / "census" / "nc-est2024-agesex-res.csv")
US_POP = {int(y): int(p) for y, p in a[(a.MONTH == 7) & (a.AGE == 999)][["YEAR", "TOT_POP"]].values if y <= 2009}
row = b[(b.SEX == 0) & (b.AGE == 999)].iloc[0]
US_POP.update({y: int(row[f"POPESTIMATE{y}"]) for y in range(2010, 2020)})
row = c[(c.SEX == 0) & (c.AGE == 999)].iloc[0]
US_POP.update({y: int(row[f"POPESTIMATE{y}"]) for y in range(2020, 2025)})
US_POP[2025] = US_POP[2024]  # ESTIMATE: Vintage 2025 not downloaded; 2024 used, so 2025 rate is ~0.5-1% too high

_, EPOP = eurostat()
EU_POP_2023 = float(EPOP.loc[2023, "EU27_2020"])
ES_POP_2023 = float(EPOP.loc[2023, "ES"])

ew = json.load(open(RAW / "ons" / "ewpop_timeseries.json", encoding="utf-8"))
EW_POP = {int(y["year"]): float(y["value"]) for y in ew["years"]}  # ONS series EWPOP, mid-year

# --------------------------------------------- US cocaine deaths, with/without opioids
# NCHS Data Brief 384, data table for Figure 4 (2009-2010) and Data Brief 474, data table
# for Figure 1 (2011-2021): T40.5 deaths, and those also coded T40.0-T40.4 or T40.6.
US_COC = {  # year: (total, with_opioids, without_opioids)
    2009: (4350, 2210, 2140), 2010: (4183, 2086, 2097),
    2011: (4681, 2505, 2176), 2012: (4404, 2448, 1956), 2013: (4944, 2831, 2113),
    2014: (5415, 3414, 2001), 2015: (6784, 4506, 2278), 2016: (10375, 7263, 3112),
    2017: (13942, 10131, 3811), 2018: (14666, 10887, 3779), 2019: (15883, 11998, 3885),
    2020: (19447, 15338, 4109), 2021: (24486, 19250, 5236),
}
# 2022-2024: CDC WONDER exports by David (2026-11-11), same definitions as the Data Briefs
# (UCD X40-X44, X60-X64, X85, Y10-Y14; MCD T40.5, and T40.5 AND any of T40.0-T40.4, T40.6).
def _wonder(name):
    w = pd.read_csv(RAW / "cdc_wonder" / name, nrows=7)
    return dict(zip(w["Year Code"].astype(int), w["Deaths"].astype(int)))


_all = _wonder("wonder_cocaine_all_2018_2024.csv")
_with = _wonder("wonder_cocaine_with_opioids_2018_2024.csv")
for y in (2018, 2019, 2020, 2021):  # WONDER must reproduce the Data Brief values exactly
    assert US_COC[y][:2] == (_all[y], _with[y]), y
for y in (2022, 2023, 2024):
    US_COC[y] = (_all[y], _with[y], _all[y] - _with[y])
US_WITH_SHARE_2024 = US_COC[2024][1] / US_COC[2024][0]
# SUDORS Jan 2021-Jun 2024: 92,697 cocaine-involved deaths, 73,292 with opioids (79.1%)
# (Tanz et al., MMWR 74(32), 2025, table). Used to estimate 2022-24 before the WONDER export.
SUDORS_WITH_SHARE = 73292 / 92697
# 2025: VSRR provisional, 12 months ending December 2025, US, Cocaine (T40.5), reported value.
v = pd.read_csv(RAW / "cdc_meth" / "vsrr_provisional_drug_overdose_xkb8-kh2a.csv")
US_COC_2025 = float(v[(v.State == "US") & (v.Indicator == "Cocaine (T40.5)") & (v.Year == 2025)
                      & (v.Month == "December")]["Data Value"].iloc[0])

# --------------------------------------------- England & Wales (ONS), registrations
x = pd.read_excel(RAW / "ons" / "2025substances.xlsx", sheet_name="All data", header=2)
x = x[(x.Sex == "Persons") & (x["Usual residence name"] == "England and Wales") & (x.Substance == "14 Cocaine")]
EW_COC = x[x.Mentioned == "On the death certificate"].set_index("Year of death registration").Deaths
EW_COC_ALONE = x[x.Mentioned == "Without other drugs"].set_index("Year of death registration").Deaths

# --------------------------------------------- EU, Spain, survey inputs
EU_COC_2023 = 1051          # EDR p. 87: cocaine in 1,051 (26%) of drug-induced deaths, 20 countries, 2023
EU_COC_2022 = 956           # EDR p. 87: 956 (27%) in 2022
EU_COC_2024 = 1133          # EDR 2026 drug-induced deaths page, p. 8: 1,133 (27%), 20 countries, 2024 (2023 revised to 1,053)
ES_COC_2023 = 737           # OEDA, Informe 2025 Indicador Mortalidad, p. 12: cocaine in 737 of 1,267 deaths (2023)
ES_COC_WITH_OPI = 357       # same page: 357 cases with cocaine and opioids (48.4% of 737)
ES_COC_2022_EDR = 621       # EDR p. 87: Spain 621 of 1,037 in 2022

USE = {  # last-year cocaine use, % (survey, age range)
    "US": 1.5,      # NSDUH 2024, Table 1.8B, 12+ (4,257,000 people, Table 1.8A)
    "EU": 1.6,      # EDR p. 33, 15-64 (4.5 million)
    "ES": 2.5,      # EDADES 2024 executive report, p. 7, 15-64 (cocaine powder and/or base)
    "EW": 2.1,      # ONS/CSEW, Drug misuse in England and Wales YE March 2025, powder cocaine, 16-59
}
US_USERS = 4_257_000        # NSDUH 2024 Table 1.8A, past-year cocaine, 12+
US_PAST_MONTH = 1_671_000   # NSDUH 2024 Table 1.8A, past-month cocaine, 12+
US_CRACK = 749_000          # NSDUH 2024 Table 1.9A, past-year crack, 12+
US_CUD = 1_211_000          # NSDUH 2024 Table 5.1A, cocaine use disorder in past year, 12+
ENG_CRACK_PER_1000 = 3.3 + 1.4  # DHSC/UKHSA, opiate and crack use estimates England 2022-23: opiates+crack 3.3, crack only 1.4 per 1,000 aged 15-64
ENG_OCU, ENG_OCU_RATE = 310_718, 8.5  # same: OCU count and rate per 1,000 (implies the 15-64 base)
ES_PAST_MONTH = 1.4         # EDADES 2024, p. 7: last-month cocaine 1.4% (15-64)


def pm(n, pop):
    return n / pop * 1e6


# ============================================================ decomposition (2023/2024)
us_tot = pm(US_COC[2024][0], US_POP[2024])
us_wo = pm(US_COC[2024][2], US_POP[2024])
eu_tot = pm(EU_COC_2023, EU_POP_2023)                      # floor: 20 countries / whole EU
ES_WO_SHARE = 1 - ES_COC_WITH_OPI / ES_COC_2023            # 51.6% of Spain's cocaine deaths had no opioid
eu_wo = eu_tot * ES_WO_SHARE                               # ASSUMPTION: EU opioid mix like Spain's
es_wo = pm(ES_COC_2023 - ES_COC_WITH_OPI, ES_POP_2023)
es_wo_per_pt = es_wo / USE["ES"]
eu_wo_spainlike = es_wo_per_pt * USE["EU"]                 # ASSUMPTION: EU counted as completely as Spain

total = us_tot / eu_tot
use_f = USE["US"] / USE["EU"]
opioid_f = (us_tot / eu_tot) / (us_wo / eu_wo)
meas_max = eu_wo_spainlike / eu_wo
rest_if_meas_max = total / (use_f * opioid_f * meas_max)
rest_if_meas_none = total / (use_f * opioid_f)

steps = [
    ("Total gap: US vs EU cocaine-involved deaths per million", us_tot, eu_tot, total,
     "US 2024 (DB549) / EU 20 countries 2023 (EDR p.87) over EU-27 population"),
    ("1. Use: last-year users per 100 people", USE["US"], USE["EU"], use_f, "NSDUH 2024 12+ / EDR p.33 15-64"),
    ("2. Opioid co-involvement (fentanyl era)", 1 - US_WITH_SHARE_2024, ES_WO_SHARE, opioid_f,
     "share of cocaine deaths WITHOUT opioids: US 2024 (CDC WONDER) vs Spain 2023 (assumed EU-wide)"),
    ("   -> gap in cocaine deaths WITHOUT opioids", us_wo, eu_wo, us_wo / eu_wo, "per million"),
    ("3. EU under-counting, upper bound (EU counted like Spain)", eu_wo_spainlike, eu_wo, meas_max,
     "Spain's no-opioid cocaine deaths per % of users x EU use, vs EU as reported"),
    ("4. Remainder if measurement is at its upper bound", None, None, rest_if_meas_max,
     "heavy/dependent share, crack, age, cardiac risk, unexplained"),
    ("4b. Remainder if measurement explains nothing", None, None, rest_if_meas_none, ""),
]
dec = pd.DataFrame(steps, columns=["step", "us_value", "eu_value", "factor", "note"])
dec["share_of_log_gap_pct"] = [None] + [100 * math.log(f) / math.log(total) for f in dec.factor[1:]]
dec.loc[3, "share_of_log_gap_pct"] = None
dec.round(3).to_csv(OUT / "research_cocaine_gap_decomposition.csv", index=False)

# ============================================================ comparators
ew_25 = pm(EW_COC[2025], EW_POP[2025])
ew_24 = pm(EW_COC[2024], EW_POP[2024])
es_tot = pm(ES_COC_2023, ES_POP_2023)
comp = pd.DataFrame([
    dict(place="United States", year=2024, last_year_use_pct=USE["US"], use_ages="12+",
         dependent_or_high_risk=f"cocaine use disorder {US_CUD/1e6:.2f}M ({US_CUD/US_USERS:.0%} of users); crack past-year {US_CRACK/1e3:.0f}k",
         cocaine_deaths=US_COC[2024][0], deaths_per_million=us_tot, deaths_per_m_per_use_pt=us_tot / USE["US"],
         with_opioids_pct=100 * US_WITH_SHARE_2024, without_opioids_per_million=us_wo,
         source="NCHS DB549; NSDUH 2024 T1.8A/1.9A/5.1A; CDC WONDER 2024 opioid split"),
    dict(place="United States", year=2025, last_year_use_pct=None, use_ages="",
         dependent_or_high_risk="", cocaine_deaths=US_COC_2025, deaths_per_million=pm(US_COC_2025, US_POP[2025]),
         deaths_per_m_per_use_pt=None, with_opioids_pct=None, without_opioids_per_million=None,
         source="VSRR provisional, 12 months ending Dec 2025; 2024 population"),
    dict(place="EU (20 countries' deaths / EU-27 pop)", year=2023, last_year_use_pct=USE["EU"], use_ages="15-64",
         dependent_or_high_risk="no EU estimate; 35,000 first-time cocaine treatment entrants, 9,900 crack treatment entries (EDR p.83)",
         cocaine_deaths=EU_COC_2023, deaths_per_million=eu_tot, deaths_per_m_per_use_pt=eu_tot / USE["EU"],
         with_opioids_pct=None, without_opioids_per_million=None, source="EDR 2025 pp. 33, 83, 87"),
    dict(place="England & Wales", year=2025, last_year_use_pct=USE["EW"], use_ages="16-59 (powder)",
         dependent_or_high_risk=f"England crack users {ENG_CRACK_PER_1000:.1f} per 1,000 aged 15-64 (2022-23), 70% also use opiates",
         cocaine_deaths=int(EW_COC[2025]), deaths_per_million=ew_25, deaths_per_m_per_use_pt=ew_25 / USE["EW"],
         with_opioids_pct=None, without_opioids_per_million=None,
         source="ONS 2025 registrations; CSEW YE Mar 2025; DHSC/UKHSA OCU 2022-23"),
    dict(place="Spain", year=2023, last_year_use_pct=USE["ES"], use_ages="15-64",
         dependent_or_high_risk=f"last-month use {ES_PAST_MONTH}% ({ES_PAST_MONTH/USE['ES']:.0%} of last-year users)",
         cocaine_deaths=ES_COC_2023, deaths_per_million=es_tot, deaths_per_m_per_use_pt=es_tot / USE["ES"],
         with_opioids_pct=100 * (1 - ES_WO_SHARE), without_opioids_per_million=es_wo,
         source="OEDA Informe 2025 mortalidad p.12; EDADES 2024 p.7"),
])
comp.round(2).to_csv(OUT / "research_cocaine_gap_comparators.csv", index=False)

# ============================================================ trend 2009 ->
who = pd.read_csv(OUT / "research_by_drug_type_trend_who.csv")
who_eu = who[who.group.str.startswith("EU-18")].set_index("year").cocaine * 10   # per 100k -> per million
who_us = who[who.group.str.startswith("US")].set_index("year").cocaine * 10 if who.group.str.startswith("US").any() else None
rows = []
for y in range(2009, 2026):
    r = dict(year=y)
    if y in US_COC:
        t, w, wo = US_COC[y]
        r.update(us_cocaine=t, us_with_opioids=w, us_without_opioids=wo,
                 us_without_is_estimate=False,
                 us_per_m=pm(t, US_POP[y]), us_without_per_m=pm(wo, US_POP[y]))
    if y == 2025:
        r.update(us_cocaine=US_COC_2025, us_per_m=pm(US_COC_2025, US_POP[2025]))
    if y in EW_COC.index:
        r.update(ew_cocaine=int(EW_COC[y]), ew_cocaine_only_drug=int(EW_COC_ALONE[y]), ew_per_m=pm(EW_COC[y], EW_POP[y]))
    if y in who_eu.index:
        r["who_eu18_cocaine_per_m"] = who_eu[y]
    if who_us is not None and y in who_us.index:
        r["who_us_cocaine_per_m"] = who_us[y]
    rows.append(r)
tr = pd.DataFrame(rows)
tr["us_over_ew"] = tr.us_per_m / tr.ew_per_m
tr["us_without_opioids_over_ew_all"] = tr.us_without_per_m / tr.ew_per_m
tr.loc[tr.year == 2022, "eu20_cocaine"] = EU_COC_2022
tr.loc[tr.year == 2023, "eu20_cocaine"] = EU_COC_2023
tr.loc[tr.year == 2024, "eu20_cocaine"] = EU_COC_2024
tr.round(2).to_csv(OUT / "research_cocaine_gap_trend.csv", index=False)

# ============================================================ print
pd.set_option("display.width", 220)
print("DECOMPOSITION (multiplicative; factors multiply to the total)")
print(dec.round(2).to_string(index=False))
print(f"\ncheck: use x opioid x meas_max x rest = {use_f*opioid_f*meas_max*rest_if_meas_max:.2f} (total {total:.2f})")
print("\nCOMPARATORS"); print(comp.drop(columns=["source", "dependent_or_high_risk"]).round(2).to_string(index=False))
print("\nTREND"); print(tr.round(1).to_string(index=False))
print("\nOTHER ARITHMETIC")
print(f"US past-month / past-year cocaine users: {US_PAST_MONTH/US_USERS:.0%}; Spain {ES_PAST_MONTH/USE['ES']:.0%}")
print(f"US crack share of past-year cocaine users: {US_CRACK/US_USERS:.0%}; crack past-year per 1,000 (12+): {US_CRACK/(US_USERS/USE['US']*100)*1000:.1f}")
eng_1564 = ENG_OCU / ENG_OCU_RATE * 1000
print(f"England crack users (15-64) implied: {ENG_CRACK_PER_1000*eng_1564/1000:,.0f} of {eng_1564/1e6:.1f}M; share also using opiates {3.3/ENG_CRACK_PER_1000:.0%}")
print(f"US deaths per 1,000 people with cocaine use disorder: all {US_COC[2024][0]/US_CUD*1000:.1f}, without opioids {US_COC[2024][2]/US_CUD*1000:.1f}")
print(f"Spain share of EU 20-country cocaine deaths: 2022 {ES_COC_2022_EDR/EU_COC_2022:.0%} (EDR's own figures); Spain is {ES_POP_2023/EU_POP_2023:.0%} of EU population")
print(f"EU 20-country cocaine deaths 2022->2023 {EU_COC_2023/EU_COC_2022-1:+.0%}; 2023->2024 {EU_COC_2024/EU_COC_2023-1:+.0%}")
print(f"US cocaine deaths 2023->2024 {US_COC[2024][0]/US_COC[2023][0]-1:+.0%}; 2024->2025 (VSRR vs final) {US_COC_2025/US_COC[2024][0]-1:+.0%}")
print(f"E&W cocaine deaths 2011->2024 x{EW_COC[2024]/EW_COC[2011]:.1f}; 2024->2025 {EW_COC[2025]/EW_COC[2024]-1:+.0%}")
print(f"US 2025 vs EU 2024 floor (2023 EU population): {pm(US_COC_2025,US_POP[2025])/pm(EU_COC_2024,EU_POP_2023):.1f}x")
# SUDORS age table (MMWR 74(32)): no-opioid 55-64 6,466 and 65+ 2,824 of 19,405; with opioids 15,537 and 3,920 of 73,292
print(f"SUDORS no-opioid cocaine deaths aged 55+: {(6466+2824)/19405:.0%} (with opioids: {(15537+3920)/73292:.0%})")
