"""Queries-per-almond under different water accounting choices, and the assumptions
Altman's 38,000 implies. Every input is sourced in docs/sources.md.

Run from the repo root: python projects/altman-vs-almonds/scripts/scenarios.py
Writes data/scenarios.csv and prints the tables.
"""
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "data"

GAL_L = 3.78541
OZ_G = 28.3495

# Almond side. Fulton, Norton & Shilling, Ecological Indicators 96 (2019), section 3.1.1:
# 2004-2015 average per kg of kernels, converted per almond "at 1.2 grams per kernel".
BLUE_L_PER_KG, GREEN_L_PER_KG, GREY_L_PER_KG = 5_290, 570, 4_380
FOOTPRINT_L_PER_KG = BLUE_L_PER_KG + GREEN_L_PER_KG + GREY_L_PER_KG  # 10,240
FULTON_KERNEL_G = 1.2
NASS_KERNEL_G = 1.60  # NASS 2025 Objective Measurement report, all varieties

almonds = {
    "Total footprint (blue+green+grey), Fulton kernel": FOOTPRINT_L_PER_KG * FULTON_KERNEL_G / 1000,
    "Blue (irrigation) only, Fulton kernel": BLUE_L_PER_KG * FULTON_KERNEL_G / 1000,
    "Total footprint, NASS kernel weight": FOOTPRINT_L_PER_KG * NASS_KERNEL_G / 1000,
    "Blue only, NASS kernel weight": BLUE_L_PER_KG * NASS_KERNEL_G / 1000,
}

# Query side, mL per query.
ALTMAN_WH = 0.34
REN_US_WUE = 0.55   # L/kWh onsite, US average (Li, Yang, Islam & Ren, Table 1)
REN_US_PUE = 1.17
REN_US_EWIF = 3.142  # L/kWh offsite (electricity generation), US average

queries = {
    "Altman / OpenAI, 0.000085 gal (unverified)": 0.000085 * GAL_L * 1000,
    "Google Gemini median prompt, onsite (Aug 2025)": 0.26,
    "Altman's 0.34 Wh x US onsite + electricity water": ALTMAN_WH / 1000 * (REN_US_WUE + REN_US_PUE * REN_US_EWIF) * 1000,
    "Ren et al. GPT-3, US average, onsite + electricity": 16.904,
    "Mistral Large 2 lifecycle, 400-token reply": 45.0,
}

rows = [
    {"almond_basis": a, "almond_L": al, "query_basis": q, "query_mL": qm, "queries_per_almond": al * 1000 / qm}
    for a, al in almonds.items() for q, qm in queries.items()
]
df = pd.DataFrame(rows)
OUT.mkdir(exist_ok=True)
df.round(3).to_csv(OUT / "scenarios.csv", index=False)

pd.set_option("display.width", 200, "display.max_colwidth", 60)
print("Almond water per nut (L):")
for k, v in almonds.items():
    print(f"  {v:6.2f}  {k}")
print("\nWater per query (mL):")
for k, v in queries.items():
    print(f"  {v:7.3f}  {k}")
print("\nQueries per almond:")
print(df.pivot(index="query_basis", columns="almond_basis", values="queries_per_almond").round(0).astype(int).to_string())

# Back out what 38,000 requires.
total_L = almonds["Total footprint (blue+green+grey), Fulton kernel"]
print(f"\n38,000 queries per almond needs {total_L * 1000 / 38_000:.3f} mL per query (with the {total_L:.1f} L total footprint).")
print(f"  With the blue-only almond it needs {almonds['Blue (irrigation) only, Fulton kernel'] * 1000 / 38_000:.3f} mL per query.")
print(f"  Of the {total_L:.1f} L, grey (theoretical dilution) water is {GREY_L_PER_KG * FULTON_KERNEL_G / 1000:.2f} L "
      f"({GREY_L_PER_KG / FOOTPRINT_L_PER_KG:.0%}), green (rain) {GREEN_L_PER_KG * FULTON_KERNEL_G / 1000:.2f} L.")
print(f"  At 0.34 Wh per query, 0.32 mL means {0.000085 * GAL_L * 1000 / ALTMAN_WH:.2f} L per kWh, "
      f"vs {REN_US_WUE} onsite-only and {REN_US_WUE + REN_US_PUE * REN_US_EWIF:.2f} onsite+electricity (US average).")

# Like-for-like: irrigation-only almond vs. query water = onsite cooling + power-plant water,
# with research/training compute spread over queries by OpenAI's reported spend split.
# Grid water factors (L/kWh) from the power-mix research in docs/sources.md: ERCOT and US-average
# mixes x Macknick et al. (2012) per-fuel medians, excluding hydro unless noted.
MSFT_WUE, MSFT_PUE = 0.34, 1.16  # Microsoft Americas FY25 (WUE is withdrawal-based)
grids = [
    ("ERCOT, low factors", MSFT_WUE, MSFT_PUE, 0.68),
    ("ERCOT, median factors", MSFT_WUE, MSFT_PUE, 0.92),
    ("Texas-heavy fleet (60% ERCOT)", MSFT_WUE, MSFT_PUE, 1.08),
    ("US average, no hydro", MSFT_WUE, MSFT_PUE, 1.31),
    ("Li et al. state mix, with hydro", MSFT_WUE, MSFT_PUE, 2.43),
    ("Li et al. US average, with hydro", REN_US_WUE, REN_US_PUE, REN_US_EWIF),
]
# (research + inference) / inference compute spend; Epoch AI reading of reported figures.
training = [
    ("Inference only", 1.0),
    ("+ final training runs (2024)", (0.47 + 1.8) / 1.8),
    ("+ all R&D (2025, ~even split)", 2.0),
    ("+ all R&D (2024, $5.0B vs $1.8B)", (5.0 + 1.8) / 1.8),
]
blue_L = almonds["Blue (irrigation) only, Fulton kernel"]
lfl = []
for g, wue, pue, ewif in grids:
    inference_mL = ALTMAN_WH / 1000 * (wue + pue * ewif) * 1000
    for t, mult in training:
        q = blue_L * 1000 / (inference_mL * mult)
        lfl.append({"grid": g, "training": t, "query_mL": inference_mL * mult,
                    "queries_per_almond": q, "altman_too_high_by": 38_000 / q})
lfl = pd.DataFrame(lfl)
lfl.round(3).to_csv(OUT / "like_for_like.csv", index=False)
print("\nLike-for-like (irrigation-only almond), Altman's 38,000 is too high by:")
print(lfl.pivot(index="grid", columns="training", values="altman_too_high_by")
      .reindex(index=[g[0] for g in grids], columns=[t[0] for t in training]).round(1).to_string())

# The ladder: start from Altman's own inputs (his 0.32 mL is the Texas best case) and change
# one assumption per rung. Rungs 1-3 are cumulative; 4-6 are each applied to rung 3 on its own.
# Rung 3 is shown two ways, since it's unknown whether 0.34 Wh already includes PUE.
ALTMAN_ML = 0.000085 * GAL_L * 1000
US_NO_HYDRO = 1.31
R_AND_D_2025 = 2.0
R_AND_D_2024 = (5.0 + 1.8) / 1.8
ECOLOGITS_GPT5_300TOK_WH = (0.46 + 0.66) / 2  # data/ecologits_energy.csv midpoint
WITH_HYDRO = (REN_US_WUE + REN_US_PUE * REN_US_EWIF) / (MSFT_WUE + MSFT_PUE * US_NO_HYDRO)


def queries(almond_L, query_mL):
    return almond_L * 1000 / query_mL


rung3 = {
    "0.34 Wh x PUE": ALTMAN_WH / 1000 * (MSFT_WUE + MSFT_PUE * US_NO_HYDRO) * 1000,
    # WUE is per kWh of IT energy, so back the overhead out of 0.34 Wh before applying it.
    "0.34 Wh incl. PUE": ALTMAN_WH / 1000 * (MSFT_WUE / MSFT_PUE + US_NO_HYDRO) * 1000,
}
ladder = [("0. Altman: total almond, his query water", total_L, ALTMAN_ML),
          ("1. Irrigation-only almond", blue_L, ALTMAN_ML),
          ("2. + research & training (2025 split)", blue_L, ALTMAN_ML * R_AND_D_2025)]
for k, mL in rung3.items():
    base = mL * R_AND_D_2025
    ladder += [(f"3. US grid, no hydro [{k}]", blue_L, base),
               (f"4. + 300-token GPT-5 reply (EcoLogits) [{k}]", blue_L, base * ECOLOGITS_GPT5_300TOK_WH / ALTMAN_WH),
               (f"5. 2024 R&D split instead [{k}]", blue_L, base * R_AND_D_2024 / R_AND_D_2025),
               (f"6. count hydro evaporation [{k}]", blue_L, base * WITH_HYDRO)]
lad = pd.DataFrame([{"rung": r, "almond_L": a, "query_mL": q, "queries_per_almond": queries(a, q),
                     "altman_too_high_by": 38_000 / queries(a, q)} for r, a, q in ladder])
lad.round(3).to_csv(OUT / "ladder.csv", index=False)
print("\nThe ladder:")
print(lad.round(2).to_string(index=False))

# Is 38,000 a lot?
PROMPTS_PER_DAY = 2.5e9           # OpenAI to Axios, July 2025
CROP_LB = 3.00e9                  # NASS 2025 Objective Measurement forecast, meat pounds
almonds_per_year = CROP_LB * 453.592 / NASS_KERNEL_G
prompts_per_year = PROMPTS_PER_DAY * 365
print(f"\n38,000 queries = {38_000 / PROMPTS_PER_DAY * 86_400:.2f} seconds of global ChatGPT traffic (2.5B/day).")
print(f"  At 20 prompts a day, one person takes {38_000 / 20 / 365:.1f} years.")
print(f"California almonds per year ~{almonds_per_year / 1e9:.0f} billion; ChatGPT prompts per year ~{prompts_per_year / 1e9:.0f} billion.")
print(f"  A year of ChatGPT at Altman's ratio = {prompts_per_year / 38_000 / 1e6:.0f} million almonds' water "
      f"= {prompts_per_year / 38_000 / almonds_per_year:.4%} of the crop.")
