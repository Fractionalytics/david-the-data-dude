"""Why do US meth users die so much more often than European ones? The arithmetic
behind docs/research-drugs/meth-gap.md.

    python scripts/research_meth_gap.py
      reads  data/raw/nida/overdose_data_1999-2023_1.16.25.xlsx   (US T43.6 deaths with / without opioids)
             data/raw/nsduh/2024-nsduh-detailed-tables-sect1pe.htm (US past-year meth use, numbers)
             data/raw/nsduh/2024-nsduh-detailed-tables-sect5pe.htm (US meth use disorder, numbers)
             data/raw/who_ghe/death-rate-amphetamine-who.csv       (WHO single-cause series)
             data/raw/census/*.csv, data/raw/eurostat/demo_gind.csv (populations)
      writes data/final/research_meth_gap_decomposition.csv
             data/final/research_meth_gap_comparators.csv
             data/final/research_meth_gap_timeline_us.csv
             data/final/research_meth_gap_who.csv

Hard-coded numbers are copied from primary documents; each line says where.
"""
import io
import sys
from math import log
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from us_eu_decompose import eurostat  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "final"
sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- populations
a = pd.read_csv(RAW / "census" / "us-est00int-alldata.csv")
b = pd.read_csv(RAW / "census" / "nc-est2020-agesex-res.csv")
c = pd.read_csv(RAW / "census" / "nc-est2024-agesex-res.csv")
US_POP = {int(y): int(p) for y, p in a[(a.MONTH == 7) & (a.AGE == 999)][["YEAR", "TOT_POP"]].values if y <= 2009}
row = b[(b.SEX == 0) & (b.AGE == 999)].iloc[0]
US_POP.update({y: int(row[f"POPESTIMATE{y}"]) for y in range(2010, 2020)})
row = c[(c.SEX == 0) & (c.AGE == 999)].iloc[0]
US_POP.update({y: int(row[f"POPESTIMATE{y}"]) for y in range(2020, 2025)})
_, EPOP = eurostat()
EU_POP_2023 = float(EPOP.loc[2023, "EU27_2020"])
CZ_POP = {y: float(EPOP.loc[y, "CZ"]) for y in (2013, 2015, 2020, 2022)}
SK_POP_2024 = float(EPOP.loc[2024, "SK"]) if 2024 in EPOP.index and pd.notna(EPOP.loc[2024, "SK"]) else float(EPOP.loc[2023, "SK"])
DE_POP_2023 = float(EPOP.loc[2023, "DE"])

# ------------------------------------------------- US deaths, NIDA from CDC WONDER
x = pd.read_excel(RAW / "nida" / "overdose_data_1999-2023_1.16.25.xlsx", "Number Drug OD Deaths", header=None)
years = [int(v) for v in x.iloc[6, 2:27].values]


def nida_row(label: str) -> dict:
    r = x[x.iloc[:, 1].astype(str).str.strip().str.startswith(label)].iloc[0]
    return dict(zip(years, [int(v) for v in r.values[2:27]]))


PS_ALL = nida_row("Psychostimulants With Abuse Potential (primarily")
PS_OPI = nida_row("Psychostimulants With Abuse Potential AND Any Opioid")
PS_NOOPI = nida_row("Psychostimulants With Abuse Potential WITHOUT Any Opioid")
SUDORS_OPIOID_SHARE = 0.688  # Tanz et al., MMWR 74(32), 2025: meth-involved deaths with opioids, 2021-mid 2024


# 2024: CDC WONDER exports by David (2026-11-11), T43.6, and T43.6 AND any of T40.0-T40.4, T40.6.
def _wonder(name):
    w = pd.read_csv(RAW / "cdc_wonder" / name, nrows=7)
    return dict(zip(w["Year Code"].astype(int), w["Deaths"].astype(int)))


_all = _wonder("wonder_meth_all_2018_2024.csv")
_with = _wonder("wonder_meth_with_opioids_2018_2024.csv")
for y in range(2018, 2024):  # WONDER must reproduce NIDA's table exactly
    assert (PS_ALL[y], PS_OPI[y]) == (_all[y], _with[y]), y
PS_ALL[2024], PS_OPI[2024] = _all[2024], _with[2024]  # 2024 total also = NCHS Data Brief 549
PS_NOOPI[2024] = _all[2024] - _with[2024]
TOX_SPECIFIED_2009 = 0.75  # NCHS DB491 notes: drugs specified on 75-79% of overdose certificates 2000-2013

# ----------------------------------------------------------- US use, NSDUH 2024
def nsduh(fname: str, table: int, label: str) -> list:
    t = (RAW / "nsduh" / fname).read_text(encoding="utf-8", errors="replace")
    d = pd.read_html(io.StringIO(t))[table]
    r = d[d.iloc[:, 0].astype(str).str.strip() == label].iloc[0]
    return [str(v).rstrip("ab") for v in r.values]


u = nsduh("2024-nsduh-detailed-tables-sect1pe.htm", 0, "Methamphetamine")  # Table 1.1A, thousands
US_PY_USE = {2023: int(u[3].replace(",", "")) * 1000, 2024: int(u[4].replace(",", "")) * 1000}
m = nsduh("2024-nsduh-detailed-tables-sect5pe.htm", 2, "Methamphetamine")  # Table 5.2A, thousands
US_MUD = {2023: int(m[1]) * 1000, 2024: int(m[2]) * 1000}
US_MUD_SEVERE = {2023: int(m[7]) * 1000, 2024: int(m[8]) * 1000}
# Han et al., JAMA Psychiatry 2021;78(12):1329, Table 1, ages 18-64 (old NSDUH method, not comparable to 2023-24)
HAN = {2015: dict(use=1_612_000, frequent=649_000, mud=741_000),
       2019: dict(use=1_971_000, frequent=1_021_000, mud=1_091_000)}

# ---------------------------------------------------------- comparators (primary docs)
CZ = dict(  # NMC, Zpráva o nelegálních drogách v ČR 2023 (data/raw/czech_nmc/)
    hr_meth={2013: 32_000, 2015: 32_700, 2020: 33_100, 2022: 37_200},  # tabulka 3-7, p. 65
    gmr_stim_deaths={2013: 10, 2015: 16, 2020: 17, 2022: 33},  # tabulka 4-10, p. 87 (Selection B, "ostatní stimulancia (pervitin)")
    smr_meth_deaths_2022=22,  # special register NRPATV, p. 86
    indirect_meth_deaths_2020=44,  # deaths "under the influence" of pervitin, other causes, p. 86
    purity_2022=68.1,  # p. 113
)
SK = dict(hr_meth=14_056, no_opioid_deaths_2024=44)  # EDR 2025 p. 98; EUDA DRD-19 (all non-opioid drug deaths)
EU = dict(ats_deaths_2023=907, ats_countries=19, nonco_de_2023=490)  # EDR 2025 p. 108 (incl. MDMA); p. 295
AU = dict(  # NDARC 2026 NIDIP deaths 2005-2024 executive summary + infographic; Degenhardt et al. MJA 2016
    ats_rate_2024=2.9, ats_rate_2005=0.40, ats_rate_2023=2.2,  # per 100,000, ATS-involved overdose deaths
    dependent_2014=160_000,  # 2013-14, ages 15-54 (95% CI 110k-232k)
    meth_related_deaths_2015=300,  # Darke et al. Addiction 2017 via UNSW newsroom: "about 150 to about 300" a year 2009-2015 (secondary)
    pop_2014=23.5e6, pop_2024=27.2e6,  # ABS, rounded (Unverified here)
)


def per_m(n, pop):
    return n / pop * 1e6


def per_k(n, users):
    return n / users * 1e3


# ------------------------------------------------------- 1. US vs Czechia decomposition
Y = 2023
us_rate = per_m(PS_ALL[Y], US_POP[Y])
cz_rate = per_m(CZ["gmr_stim_deaths"][2022], CZ_POP[2022])
us_heavy = per_m(US_MUD[Y], US_POP[Y])
cz_heavy = per_m(CZ["hr_meth"][2022], CZ_POP[2022])
us_dpu = per_k(PS_ALL[Y], US_MUD[Y])
us_dpu_noopi = per_k(PS_NOOPI[Y], US_MUD[Y])
cz_dpu = per_k(CZ["gmr_stim_deaths"][2022], CZ["hr_meth"][2022])
cz_dpu_broad = per_k(CZ["gmr_stim_deaths"][2022] + CZ["indirect_meth_deaths_2020"], CZ["hr_meth"][2022])
total = us_rate / cz_rate
f_use = 1.0
f_heavy = us_heavy / cz_heavy
f_opi = us_dpu / us_dpu_noopi
resid_raw = us_dpu_noopi / cz_dpu
f_cz_indirect = cz_dpu_broad / cz_dpu
f_nsduh = 2.0  # assumption: NSDUH misses half of US heavy users (unsheltered homeless, jails); a bound, not a measurement
resid_adj = resid_raw / f_cz_indirect / f_nsduh

dec = pd.DataFrame([
    ("Total gap: US T43.6 deaths 2023 vs Czech Selection-B meth deaths 2022, per million", total, "measured"),
    ("1. Last-year use (US 0.8% vs EU 0.8%; Czech similar)", f_use, "measured"),
    ("2. More heavy users per person (US meth use disorder vs Czech high-risk meth users)", f_heavy, "measured, definitions differ"),
    ("3. Opioid co-involvement (all US deaths per heavy user / deaths without opioids)", f_opi, "measured (US); assumes Czech meth deaths rarely involve opioids"),
    ("Remainder before measurement adjustments (deaths per heavy user, no opioids)", resid_raw, "remainder"),
    ("4a. Count Czech 'indirect' meth deaths (44, 2020) as if US-style", f_cz_indirect, "upper bound"),
    ("4b. NSDUH misses half of US heavy users", f_nsduh, "assumption"),
    ("Unexplained after maximal measurement adjustments", resid_adj, "remainder"),
], columns=["factor", "multiplier", "status"])
dec["share_of_log_gap"] = dec.multiplier.map(lambda v: log(v) / log(total) if v > 0 else float("nan"))
dec.loc[0, "share_of_log_gap"] = 1.0

# ---------------------------------------------------------------- 2. comparators
comp = pd.DataFrame([
    dict(place="United States", year=2023, last_year_use="0.8% (2024, 12+; 2.62M users 2023)", heavy_users=US_MUD[2023],
         heavy_def="NSDUH meth use disorder, 12+", deaths=PS_ALL[2023], deaths_def="T43.6 involved, X40-44/X60-64/X85/Y10-14",
         pop=US_POP[2023]),
    dict(place="United States, without opioids", year=2023, last_year_use="", heavy_users=US_MUD[2023],
         heavy_def="NSDUH meth use disorder, 12+", deaths=PS_NOOPI[2023], deaths_def="T43.6 without T40.0-40.4, T40.6", pop=US_POP[2023]),
    dict(place="United States", year=2024, last_year_use="0.8% (12+; 2.38M users)", heavy_users=US_MUD[2024],
         heavy_def="NSDUH meth use disorder, 12+", deaths=PS_ALL[2024], deaths_def="T43.6 involved (DB549)", pop=US_POP[2024]),
    dict(place="United States (old NSDUH method)", year=2015, last_year_use="1.6M users 18-64", heavy_users=HAN[2015]["mud"],
         heavy_def="NSDUH MUD 18-64 (Han 2021)", deaths=PS_ALL[2015], deaths_def="T43.6 involved, all ages", pop=US_POP[2015]),
    dict(place="United States (old NSDUH method), without opioids", year=2015, last_year_use="", heavy_users=HAN[2015]["mud"],
         heavy_def="NSDUH MUD 18-64 (Han 2021)", deaths=PS_NOOPI[2015], deaths_def="T43.6 without opioids", pop=US_POP[2015]),
    dict(place="Czechia", year=2022, last_year_use="n/a here", heavy_users=CZ["hr_meth"][2022],
         heavy_def="high-risk meth users (multiplier), >90% inject", deaths=CZ["gmr_stim_deaths"][2022],
         deaths_def="general register, Selection B, non-cocaine stimulants", pop=CZ_POP[2022]),
    dict(place="Czechia, broad (+ indirect deaths)", year=2022, last_year_use="", heavy_users=CZ["hr_meth"][2022],
         heavy_def="as above", deaths=CZ["gmr_stim_deaths"][2022] + CZ["indirect_meth_deaths_2020"],
         deaths_def="+ 44 deaths under the influence of pervitin (2020)", pop=CZ_POP[2022]),
    dict(place="Czechia", year=2015, last_year_use="", heavy_users=CZ["hr_meth"][2015], heavy_def="as above",
         deaths=CZ["gmr_stim_deaths"][2015], deaths_def="general register, Selection B", pop=CZ_POP[2015]),
    dict(place="Slovakia (upper bound)", year=2024, last_year_use="", heavy_users=SK["hr_meth"],
         heavy_def="high-risk meth users (EDR p. 98)", deaths=SK["no_opioid_deaths_2024"],
         deaths_def="ALL drug deaths without opioids (DRD-19), so a ceiling", pop=SK_POP_2024),
    dict(place="EU (19 of 21 reporting countries)", year=2023, last_year_use="0.8% amphetamine+meth, 15-64", heavy_users=float("nan"),
         heavy_def="no EU-wide estimate", deaths=EU["ats_deaths_2023"], deaths_def="ATS incl. MDMA involved; floor", pop=EU_POP_2023),
    dict(place="Germany", year=2023, last_year_use="", heavy_users=float("nan"), heavy_def="no estimate",
         deaths=EU["nonco_de_2023"], deaths_def="non-cocaine stimulants involved (EDR p. 295)", pop=DE_POP_2023),
    dict(place="Australia", year=2015, last_year_use="2.1% (2013, 14+; secondary)", heavy_users=AU["dependent_2014"],
         heavy_def="dependent meth users 15-54, 2013-14 (MJA 2016)", deaths=AU["meth_related_deaths_2015"],
         deaths_def="ALL meth-related deaths incl. disease, suicide, accident (Darke 2017; secondary)", pop=AU["pop_2014"]),
    dict(place="Australia", year=2024, last_year_use="", heavy_users=AU["dependent_2014"],
         heavy_def="2013-14 estimate (stale, so deaths per user is an upper bound)", deaths=AU["ats_rate_2024"] * AU["pop_2024"] / 1e5,
         deaths_def="ATS-involved overdose deaths (NDARC 2026), from the rate", pop=AU["pop_2024"]),
])
comp["deaths_per_million"] = comp.deaths / comp["pop"] * 1e6
comp["heavy_users_per_million"] = comp.heavy_users / comp["pop"] * 1e6
comp["deaths_per_1000_heavy_users"] = comp.deaths / comp.heavy_users * 1e3

# ------------------------------------------------------------------ 3. US timeline
tl = pd.DataFrame({"psychostim_all": PS_ALL, "with_opioids": PS_OPI, "without_opioids": PS_NOOPI})
tl = tl.loc[2009:]
tl["pop"] = [US_POP[y] for y in tl.index]
for col in ("psychostim_all", "with_opioids", "without_opioids"):
    tl[col + "_per_m"] = tl[col] / tl["pop"] * 1e6
tl["share_with_opioids"] = tl.with_opioids / tl.psychostim_all
tl.index.name = "year"

# ------------------------------------------------------------------ 4. WHO series
w = pd.read_csv(RAW / "who_ghe" / "death-rate-amphetamine-who.csv")
w.columns = ["entity", "code", "year", "rate_per_100k"]
who = w[w.entity.isin(["United States", "Canada", "Australia", "Czechia", "Germany", "Slovakia", "Sweden", "Finland"])
        & w.year.isin([2009, 2015, 2021])].pivot(index="entity", columns="year", values="rate_per_100k")
who["x_2009_2021"] = who[2021] / who[2009]

# ------------------------------------------------------------------ write + print
OUT.mkdir(exist_ok=True)
dec.to_csv(OUT / "research_meth_gap_decomposition.csv", index=False)
comp.to_csv(OUT / "research_meth_gap_comparators.csv", index=False)
tl.to_csv(OUT / "research_meth_gap_timeline_us.csv")
who.to_csv(OUT / "research_meth_gap_who.csv")

pd.set_option("display.width", 250, "display.max_columns", 20, "display.max_colwidth", 80)
print("US use:", US_PY_USE, "MUD:", US_MUD, "severe:", US_MUD_SEVERE)
print(f"MUD share of past-year users 2024: {US_MUD[2024] / US_PY_USE[2024]:.0%}; Han frequent share 2019: {HAN[2019]['frequent'] / HAN[2019]['use']:.0%}")
print("\nDECOMPOSITION (US 2023 vs Czechia 2022)")
print(dec.round(2).to_string(index=False))
print(f"check: heavy x opioids x remainder = {f_heavy * f_opi * resid_raw:.1f} (total {total:.1f})")
print(f"US rate {us_rate:.1f}/M, CZ rate {cz_rate:.2f}/M; deaths per 1,000 heavy users US {us_dpu:.1f}, US no opioids {us_dpu_noopi:.1f}, CZ {cz_dpu:.2f}, CZ broad {cz_dpu_broad:.2f}")
eu_rate = per_m(EU["ats_deaths_2023"], EU_POP_2023)
print(f"\nEU ATS deaths floor {eu_rate:.2f}/M -> US/EU {us_rate / eu_rate:.0f}x (2023), {per_m(PS_ALL[2024], US_POP[2024]) / eu_rate:.0f}x (US 2024)")
print(f"Implied EU heavy users if EU deaths per heavy user = Czech: {eu_rate / cz_dpu * 1e3:,.0f} per million "
      f"({eu_rate / cz_dpu * 1e3 * EU_POP_2023 / 1e6:,.0f} people); heavy-use factor {us_heavy / (eu_rate / cz_dpu * 1e3):.1f}x")
print("\nCOMPARATORS")
print(comp[["place", "year", "heavy_users", "deaths", "deaths_per_million", "heavy_users_per_million", "deaths_per_1000_heavy_users"]].round(2).to_string(index=False))
print("\nUS TIMELINE")
print(tl[["psychostim_all", "with_opioids", "without_opioids", "psychostim_all_per_m", "without_opioids_per_m", "share_with_opioids"]].round(2).to_string())
r = tl.loc[2023] / tl.loc[2009]
print(f"2009->2023: all x{r.psychostim_all:.1f}, with opioids x{r.with_opioids:.1f}, without x{r.without_opioids:.1f}")
print(f"2009 all adjusted for 75% drug specification: {PS_ALL[2009] / TOX_SPECIFIED_2009:,.0f} -> growth x{PS_ALL[2023] / (PS_ALL[2009] / TOX_SPECIFIED_2009):.1f}")
print(f"Czech Selection-B meth deaths 2013->2022: {CZ['gmr_stim_deaths'][2013]} -> {CZ['gmr_stim_deaths'][2022]}; HR users {CZ['hr_meth'][2013]:,} -> {CZ['hr_meth'][2022]:,}")
print("\nWHO amphetamine use disorders, deaths per 100,000")
print(who.round(2).to_string())
