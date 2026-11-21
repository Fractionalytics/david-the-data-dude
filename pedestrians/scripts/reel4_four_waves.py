"""Reel 4: the four waves of the opioid epidemic, rebuilt from CDC WONDER the way
Friedman, Palamar, Ciccarone et al. (medRxiv 2026, Figure 1) and Ciccarone
(Int J Drug Policy 2019, Figure 1) built them. See docs/reel4-wonder-pull.md.

    python scripts/reel4_four_waves.py
      reads  data/raw/cdc_wonder/wonder_w4_*_{1999_2020,2018_2024,2024_2026}.csv  (24 exports by David, 2026-11-19;
             2025 from the provisional database, 2026 partial and dropped)
      writes data/final/reel4_four_waves.csv        (deaths, crude and age-adjusted rates by year)
             charts/reel4_four_waves_2026def.png    (F26 definitions, crude rate, 1999-2024)
             charts/reel4_three_waves_2019def.png   (C19 definitions, age-adjusted, 1999-2024)

Wave definitions (F26 Methods and Figure 1 caption):
    wave1 = Rx (T40.2) minus Rx AND fentanyl (T40.4)
    wave2 = heroin (T40.1) minus heroin AND fentanyl
    wave3 = fentanyl minus fentanyl AND (cocaine T40.5 or meth T43.6)
    wave4 = fentanyl AND (cocaine or meth)
    stim_no_fent = (cocaine or meth) minus wave4
Rates for the subtracted series are computed from deaths / population, so they're
crude; age-adjusted rates exist only for the un-subtracted queries.
"""
import io
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "cdc_wonder"
OUT = ROOT / "data" / "final"
CHARTS = ROOT / "charts"
sys.stdout.reconfigure(encoding="utf-8")

QUERIES = ["od_all", "rx", "rx_and_fent", "heroin", "heroin_and_fent", "fent", "fent_and_stim", "stim"]


def read_wonder(path):
    """Data rows of a WONDER export (everything above the '---' footer)."""
    text = path.read_text(encoding="utf-8")
    body = text.split('"---"')[0]
    df = pd.read_csv(io.StringIO(body))
    df = df[df["Notes"].isna() & df["Year Code"].notna()].copy()
    df["year"] = df["Year Code"].astype(int)
    df["deaths"] = df["Deaths"].astype(int)
    df["pop"] = df["Population"].astype(int)
    df["aadj"] = pd.to_numeric(df["Age Adjusted Rate"], errors="coerce")  # "Unreliable"/"Suppressed" -> NaN
    return df.set_index("year")[["deaths", "pop", "aadj"]]


frames = {}
for q in QUERIES:
    old = read_wonder(RAW / f"wonder_w4_{q}_1999_2020.csv")
    new = read_wonder(RAW / f"wonder_w4_{q}_2018_2024.csv")
    assert list(old.index) == list(range(1999, 2021)), (q, list(old.index))
    assert list(new.index) == list(range(2018, 2025)), (q, list(new.index))
    # Check 1: the two databases agree on deaths in the overlap years.
    for y in (2018, 2019, 2020):
        assert old.loc[y, "deaths"] == new.loc[y, "deaths"], (q, y, old.loc[y, "deaths"], new.loc[y, "deaths"])
    # 2025 from the provisional database (exported 2026-11-19, deaths through Nov 7, 2026).
    # Its 2024 is final data and must match exactly; 2026 is partial and dropped.
    prov = read_wonder(RAW / f"wonder_w4_{q}_2024_2026.csv")
    assert prov.loc[2024, "deaths"] == new.loc[2024, "deaths"], (q, prov.loc[2024, "deaths"], new.loc[2024, "deaths"])
    # Old database through 2017, new (single race, current populations) from 2018, provisional 2025.
    frames[q] = pd.concat([old.loc[:2017], new, prov.loc[[2025]]])

df = pd.DataFrame({q: f["deaths"] for q, f in frames.items()})
pop = frames["od_all"]["pop"]
for q in ("od_all", "rx", "heroin", "fent", "stim"):
    df[f"{q}_aadj"] = frames[q]["aadj"]

df["wave1_rx_no_fent"] = df.rx - df.rx_and_fent
df["wave2_heroin_no_fent"] = df.heroin - df.heroin_and_fent
df["wave3_fent_no_stim"] = df.fent - df.fent_and_stim
df["wave4_fent_and_stim"] = df.fent_and_stim
df["stim_no_fent"] = df.stim - df.fent_and_stim
df["pop"] = pop
for c in ("wave1_rx_no_fent", "wave2_heroin_no_fent", "wave3_fent_no_stim", "wave4_fent_and_stim", "stim_no_fent", "od_all"):
    df[f"{c}_crude"] = (df[c] / df["pop"] * 1e5).round(2)

# ---------------------------------------------------------------- checks against published numbers
# NCHS Data Brief 329 (Hedegaard et al. 2018), 2017 counts.
assert df.loc[2017, "od_all"] == 70237
assert df.loc[2017, "fent"] == 28466, df.loc[2017, "fent"]
assert df.loc[2017, "heroin"] == 15482, df.loc[2017, "heroin"]
assert df.loc[2017, "rx"] == 14495, df.loc[2017, "rx"]
# Friedman & Shover 2023: fentanyl + stimulant deaths 235 (2010), 34,429 (2021).
assert df.loc[2010, "fent_and_stim"] == 235
assert df.loc[2021, "fent_and_stim"] == 34429
# Friedman, Palamar, Ciccarone et al. 2026 (p. 6): 2023 = 31,193 without / 41,583 with stimulants;
# 2024 provisional 19,673 / 28,062; stimulants without fentanyl 18,142 (2023), 18,907 (2024).
assert df.loc[2023, "wave3_fent_no_stim"] == 31193
assert df.loc[2023, "wave4_fent_and_stim"] == 41583
# Final 2024 data moves one death from "without" to "with" (19,672 / 28,063); same total, 47,735.
assert abs(df.loc[2024, "wave3_fent_no_stim"] - 19673) <= 1, df.loc[2024, "wave3_fent_no_stim"]
assert abs(df.loc[2024, "wave4_fent_and_stim"] - 28062) <= 1, df.loc[2024, "wave4_fent_and_stim"]
assert df.loc[2023, "stim_no_fent"] == 18142, df.loc[2023, "stim_no_fent"]
assert abs(df.loc[2024, "stim_no_fent"] - 18907) <= 2, df.loc[2024, "stim_no_fent"]
# Earlier project exports (data/raw/cdc_wonder/SOURCE.md): fentanyl 2023 = 72,776; 2024 total = 79,384.
assert df.loc[2023, "fent"] == 72776
assert df.loc[2024, "od_all"] == 79384
print("All checks passed.")

OUT.mkdir(exist_ok=True)
df.index.name = "year"
df.to_csv(OUT / "reel4_four_waves.csv")

# ---------------------------------------------------------------- peaks and turning points
cols = {"wave1_rx_no_fent": "Wave 1 Rx (no fentanyl)", "wave2_heroin_no_fent": "Wave 2 heroin (no fentanyl)",
        "wave3_fent_no_stim": "Wave 3 fentanyl (no stimulant)", "wave4_fent_and_stim": "Wave 4 fentanyl + stimulant",
        "stim_no_fent": "Stimulants (no fentanyl)", "od_all": "All overdose deaths"}
print(f"\n{'series':32} {'1999':>7} {'peak yr':>7} {'peak':>7} {'2024':>7} {'2025p':>7}  peak crude rate")
for c, label in cols.items():
    s = df[c]
    print(f"{label:32} {s[1999]:>7,} {s.idxmax():>7} {s.max():>7,} {s[2024]:>7,} {s[2025]:>7,}  {df[c + '_crude'].max():.1f}")
print("\nWhen each wave passed the one before it (deaths):")
for a, b in [("wave2_heroin_no_fent", "wave1_rx_no_fent"), ("wave3_fent_no_stim", "wave2_heroin_no_fent"),
             ("wave3_fent_no_stim", "wave1_rx_no_fent"), ("wave4_fent_and_stim", "wave3_fent_no_stim")]:
    yrs = df.index[df[a] > df[b]]
    print(f"  {cols[a]} > {cols[b]}: first {yrs.min() if len(yrs) else 'never'}")
print(df[list(cols)].to_string())

# ---------------------------------------------------------------- exploratory charts
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

COLORS = {"wave1_rx_no_fent": "#1b9e77", "wave2_heroin_no_fent": "#56b4e9", "wave3_fent_no_stim": "#0072b2",
          "wave4_fent_and_stim": "#d55e00", "stim_no_fent": "#cc79a7"}
fig, ax = plt.subplots(figsize=(10, 6))
for c, col in COLORS.items():
    ax.plot(df.index, df[c + "_crude"], marker="o", ms=3, color=col, lw=2.5, label=cols[c],
            ls="--" if c == "stim_no_fent" else "-")
ax.set_title("Four waves of US overdose deaths, 1999–2025 (Friedman, Ciccarone et al. 2026 definitions)")
ax.set_ylabel("Deaths per 100,000 (crude)")
ax.grid(alpha=0.3)
ax.legend(frameon=False)
fig.text(0.01, 0.01, "Source: CDC WONDER Multiple Cause of Death, UCD X40–44, X60–64, X85, Y10–14. "
         "Rx and heroin exclude deaths also involving fentanyl. 2025 is provisional (deaths through Nov 7, 2026).", fontsize=8, color="#555")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(CHARTS / "reel4_four_waves_2026def.png", dpi=150)

fig, ax = plt.subplots(figsize=(10, 6))
for c, label, col, ls in [("rx_aadj", "Natural and semisynthetic opioids (T40.2)", "#222", "-"),
                          ("heroin_aadj", "Heroin (T40.1)", "#222", "--"),
                          ("fent_aadj", "Synthetic opioids, e.g. fentanyl (T40.4)", "#222", ":")]:
    ax.plot(df.index, df[c], color=col, ls=ls, lw=2, label=label)
ax.axvline(2017, color="#999", lw=1)
ax.text(2017.2, ax.get_ylim()[1] * 0.95, "Ciccarone 2019 chart ends", fontsize=8, color="#666", va="top")
ax.set_title("Ciccarone's triple wave chart (2019 definitions), extended to 2024")
ax.set_ylabel("Deaths per 100,000, age-adjusted")
ax.grid(alpha=0.3)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(CHARTS / "reel4_three_waves_2019def.png", dpi=150)
print("\nwrote", OUT / "reel4_four_waves.csv", "and two charts in", CHARTS)
