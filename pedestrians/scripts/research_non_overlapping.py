"""Arithmetic for docs/research-drugs/non-overlapping-drugs.md.

Which drugs are big in one region and rare in the other, and how prescription
opioid consumption compares, US vs. major EU countries.

Inputs (all local):
- data/raw/incb/INCB-Narcotics_Drugs_Technical_Publication_2018.pdf, Table XIV.1.a
  (average 2015-2017) and data/raw/incb/INCB_Narcotics_ebook_2023.pdf, Table XIV.1.a
  (average 2020-2022). Rows are hand-entered below from the PDF text, because the
  extracted text uses spaces as thousands separators and can't be split reliably.
  Each row is checked: the drug columns must sum to the published Total (within 3,
  INCB rounds each cell). Buprenorphine is reported beside the Total, not in it.
- data/raw/ju2022/ju2022-main.pdf, table on pp. e337-e338 (MME per 1000 per day,
  2015 and 2019). Hand-entered.
- data/raw/cdc_meth/vsrr_provisional_drug_overdose_xkb8-kh2a.csv (NCHS VSRR,
  12-month-ending counts, reported "Data Value").
- data/raw/eurostat/demo_gind.csv (EU-27 population).
- Numbers quoted from the EUDA European Drug Report 2025 and the UNODC World
  Drug Report 2025 key findings are typed in with their page numbers.

Run: python scripts/research_non_overlapping.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------- INCB S-DDD
# Columns in Table XIV.1.a, in order after the country name:
COLS = ["buprenorphine", "codeine", "fentanyl", "hydrocodone", "hydromorphone",
        "methadone", "morphine", "oxycodone", "pethidine", "others", "total"]
# "—" (none reported) and "<<" (under 1) are entered as 0.
INCB = {
    "2015-2017": {  # 2018 technical publication, PDF page 250
        "United States": [4376, 0, 5900, 17832, 825, 6435, 1581, 6203, 18, 1444, 40240],
        "Germany":       [2565, 2, 18086, 9, 924, 2285, 541, 1462, 8, 5544, 28862],
        "Spain":         [974, 0, 10462, 0, 61, 2000, 242, 588, 30, 3, 13385],
        "Netherlands":   [358, 10, 11648, 2, 39, 1831, 310, 1552, 5, 718, 16114],
        # UK's buprenorphine cell is unclear in the extracted text ("39 943");
        # the drug columns below sum to the Total, so only buprenorphine is uncertain.
        "United Kingdom": [None, 0, 5602, 0, 12, 4778, 831, 734, 13, 604, 12575],
        "Sweden":        [2285, 1, 5851, 0, 104, 1055, 642, 2240, 1, 121, 10014],
        "France":        [2026, 1, 5057, 0, 23, 1739, 783, 933, 0, 1, 8537],
        "Italy":         [410, 27, 3941, 0, 154, 2323, 100, 675, 5, 295, 7521],
        "Poland":        [485, 0, 1406, 0, 0, 228, 177, 222, 11, 30, 2073],
    },
    "2020-2022": {  # 2023 technical publication (E/INCB/2023/2), PDF pages 263-264
        "United States": [9322, 0, 2521, 15384, 592, 8259, 990, 4749, 4, 214, 32713],
        "Germany":       [1715, 1, 10410, 0, 1168, 1476, 569, 1387, 3, 6804, 21820],
        "Spain":         [739, 0, 12342, 0, 102, 4000, 372, 685, 12, 14, 17525],
        "Netherlands":   [404, 2, 10927, 0, 29, 1677, 307, 1543, 3, 586, 15074],
        "United Kingdom": [2357, 2, 2085, 0, 9, 2271, 1541, 1003, 4, 1338, 8253],
        "Sweden":        [1544, 6, 3760, 0, 77, 949, 193, 2630, 0, 98, 7714],
        # France's buprenorphine cell is "—" in this table (France does use it;
        # treat as not reported).
        "France":        [None, 1, 4674, 0, 15, 2386, 745, 980, 0, 0, 8801],
        "Italy":         [0, 0, 4262, 0, 69, 2308, 103, 373, 6, 2, 7124],
        "Poland":        [471, 1, 1209, 0, 0, 617, 250, 416, 3, 29, 2525],
    },
}

rows = []
for period, table in INCB.items():
    for country, vals in table.items():
        r = dict(zip(COLS, vals))
        parts = sum(r[c] for c in COLS[1:-1])
        assert abs(parts - r["total"]) <= 3, (period, country, parts, r["total"])
        r.update(period=period, country=country,
                 total_excl_methadone=r["total"] - r["methadone"])
        rows.append(r)
incb = pd.DataFrame(rows)

print("=== INCB S-DDD per million inhabitants per day (narcotic drugs, excl. Schedule III preps) ===")
for period in INCB:
    d = incb[incb.period == period].set_index("country")
    us = d.loc["United States"]
    print(f"\n{period}")
    print(f"{'country':16} {'total':>7} {'excl.methadone':>15} {'%ofUS(excl.meth)':>17} {'fentanyl':>9} {'fent/US':>8} {'hydrocodone+oxy':>16}")
    for c, r in d.sort_values("total_excl_methadone", ascending=False).iterrows():
        print(f"{c:16} {r.total:7.0f} {r.total_excl_methadone:15.0f} "
              f"{100 * r.total_excl_methadone / us.total_excl_methadone:16.0f}% "
              f"{r.fentanyl:9.0f} {r.fentanyl / us.fentanyl:8.1f} {r.hydrocodone + r.oxycodone:16.0f}")

print("\nChange 2015-17 -> 2020-22, total excluding methadone:")
a = incb[incb.period == "2015-2017"].set_index("country")
b = incb[incb.period == "2020-2022"].set_index("country")
for c in a.index:
    x, y = a.loc[c, "total_excl_methadone"], b.loc[c, "total_excl_methadone"]
    print(f"  {c:16} {x:7.0f} -> {y:7.0f}  ({100 * (y / x - 1):+.0f}%)")
print("US hydrocodone + oxycodone share of US total excl. methadone, 2020-22: "
      f"{100 * (b.loc['United States', 'hydrocodone'] + b.loc['United States', 'oxycodone']) / b.loc['United States', 'total_excl_methadone']:.0f}%")
print("Germany fentanyl + 'others' (mostly tilidine) share of DE total excl. methadone, 2020-22: "
      f"{100 * (b.loc['Germany', 'fentanyl'] + b.loc['Germany', 'others']) / b.loc['Germany', 'total_excl_methadone']:.0f}%")

# ---------------------------------------------------------------- Ju et al. 2022
JU = {  # MME per 1000 inhabitants per day, 2015 and 2019 (opioid analgesics; methadone/buprenorphine excluded)
    "USA": (1331.99, 737.51), "Canada": (1580.67, 987.60), "Germany": (881.40, 879.04),
    "Spain": (675.04, 863.14), "Switzerland": (773.84, 897.60), "Austria": (776.54, 747.98),
    "Denmark": (991.23, 860.81), "Netherlands": (617.71, 717.34), "Belgium": (705.01, 705.69),
    "UK": (706.81, 638.72), "Sweden": (614.20, 572.16), "France": (412.92, 437.95),
    "Italy": (286.58, 344.29), "Poland": (105.01, 131.43), "Portugal": (211.16, 355.97),
    "Czech Republic": (309.24, 376.58),
}
print("\n=== Ju et al. 2022 (IQVIA sales), MME per 1000 per day ===")
us15, us19 = JU["USA"]
for c, (x, y) in sorted(JU.items(), key=lambda kv: -kv[1][1]):
    print(f"  {c:15} 2015 {x:8.1f} ({100 * x / us15:4.0f}% of US)   2019 {y:8.1f} ({100 * y / us19:4.0f}% of US)   change {100 * (y / x - 1):+5.0f}%")
print(f"  US 2015 vs Germany 2015: US = {us15 / JU['Germany'][0]:.2f}x Germany; 2019: US = {us19 / JU['Germany'][1]:.2f}x Germany")

# ---------------------------------------------------------------- CDC VSRR deaths
v = pd.read_csv(ROOT / "data/raw/cdc_meth/vsrr_provisional_drug_overdose_xkb8-kh2a.csv")
v = v[(v.State == "US") & (v.Month == "December") & (v.Year.isin([2019, 2023, 2024]))]
p = v.pivot_table(index="Indicator", columns="Year", values="Data Value", aggfunc="first")
US_POP = {2019: 328.3e6, 2023: 335e6, 2024: 340e6}  # same rounding as docs/drugs-us-vs-europe-and-p14-lessons.md (2023, 2024); 2019 Census estimate, Unverified here
print("\n=== US overdose deaths, 12 months ending December (NCHS VSRR, reported values) ===")
for ind in ["Synthetic opioids, excl. methadone (T40.4)", "Heroin (T40.1)", "Cocaine (T40.5)",
            "Psychostimulants with abuse potential (T43.6)", "Natural & semi-synthetic opioids (T40.2)",
            "Methadone (T40.3)", "Number of Drug Overdose Deaths"]:
    s = " ".join(f"{y}: {p.loc[ind, y]:7.0f} ({p.loc[ind, y] / US_POP[y] * 1e6:5.1f}/M)" for y in (2019, 2023, 2024))
    print(f"  {ind[:45]:45} {s}")
h19, h24 = p.loc["Heroin (T40.1)", 2019], p.loc["Heroin (T40.1)", 2024]
print(f"  Heroin deaths 2019 -> 2024: {100 * (h24 / h19 - 1):+.0f}%")
syn24, all24 = p.loc["Synthetic opioids, excl. methadone (T40.4)", 2024], p.loc["Number of Drug Overdose Deaths", 2024]
print(f"  Synthetic opioids (mostly fentanyl) share of all overdose deaths 2024: {100 * syn24 / all24:.0f}%")

# ---------------------------------------------------------------- EU comparisons
e = pd.read_csv(ROOT / "data/raw/eurostat/demo_gind.csv")
eu = e[(e.geo == "EU27_2020") & (e.indic_de == "JAN")].set_index("TIME_PERIOD").OBS_VALUE
eu_pop = float(eu.loc[2023])
print(f"\nEU-27 population 1 Jan 2023 (Eurostat demo_gind JAN): {eu_pop / 1e6:.1f} M")
eu_heroin_deaths = 1200   # EDR 2025 p. 211, minimum, 18 Member States, 2023
print(f"EU heroin-involved deaths 2023 (min., 18 MS): {eu_heroin_deaths} = {eu_heroin_deaths / eu_pop * 1e6:.1f}/M of all EU residents (understates: only 18 MS)")
print(f"US heroin-involved deaths 2024: {h24:.0f} = {h24 / US_POP[2024] * 1e6:.1f}/M")
eu_fent_deaths = 159      # EDR 2025 p. 155, 'at least', 2022, fentanyl + derivatives, Europe
us_syn_2023 = p.loc["Synthetic opioids, excl. methadone (T40.4)", 2023]
print(f"Fentanyl-type deaths: Europe >= {eu_fent_deaths} (2022) vs US synthetic-opioid deaths {us_syn_2023:.0f} (2023): ratio {us_syn_2023 / eu_fent_deaths:.0f}x in count")
print(f"  per million: Europe >= {eu_fent_deaths / eu_pop * 1e6:.2f}/M vs US {us_syn_2023 / US_POP[2023] * 1e6:.0f}/M -> {(us_syn_2023 / US_POP[2023]) / (eu_fent_deaths / eu_pop):.0f}x")

fent_global_t = 19.5      # WDR 2025 key findings p. 42, 2023, 99% North America
nitaz_eu_kg, new_opioids_eu_kg = 10, 22.0   # EDR 2025 p. 144 / p. 155 (2023)
print(f"Seizures 2023: fentanyl ~{fent_global_t * 0.99:.1f} t in North America vs nitazenes {nitaz_eu_kg} kg in EU "
      f"-> {fent_global_t * 0.99 * 1000 / nitaz_eu_kg:.0f}x by weight; all new synthetic opioids EU {new_opioids_eu_kg} kg -> {fent_global_t * 0.99 * 1000 / new_opioids_eu_kg:.0f}x")

meth_eu_t, meth_tr_t = 1.8, 11.5   # EDR 2025 p. 110, 2023
cbp_meth_lb = 174000               # CBP FY2024 per press coverage; Unverified
print(f"Meth seized: EU 1.8 t (2023) vs CBP border ~{cbp_meth_lb * 0.4536 / 1000:.0f} t (FY2024, Unverified) -> ~{cbp_meth_lb * 0.4536 / 1000 / meth_eu_t:.0f}x")
coke_eu_t = 419                    # EDR 2025 p. 19, 2023
cbp_coke_lb = 68215                # CBP FY2024 per press coverage; Unverified
print(f"Cocaine seized: EU 419 t (2023) vs CBP border ~{cbp_coke_lb * 0.4536 / 1000:.0f} t (FY2024, Unverified; CBP only, excludes Coast Guard and domestic seizures)")

# Past-year use (different age bands; see doc)
use = {"cannabis": (22.3, 8.4), "cocaine": (1.5, 1.6), "MDMA": (0.7, 1.1), "meth (US) vs amphetamines (EU)": (0.8, 0.8)}
print("\nPast-year use, US 12+ (NSDUH 2024) vs EU 15-64 (EDR 2025):")
for k, (u, x) in use.items():
    print(f"  {k:32} US {u:4.1f}%  EU {x:4.1f}%  ratio {u / x:.1f}")
print(f"US cannabis daily-ish vs EU: EU daily/near-daily 1.5% of adults (EDR p.17)")
print(f"Czechia high-risk meth users 37,900 = 5.48 per 1000 (EDR p.98); Czechia 189 of 250 EU meth labs = {100 * 189 / 250:.0f}%")
