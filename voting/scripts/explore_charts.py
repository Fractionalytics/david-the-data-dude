"""Exploratory charts (not storyboard charts) from data/processed/. Writes PNGs to charts/.

1. eligible_vs_voted.png   VEP head count vs ballots cast, 1980-2024 (millions of people)
2. vep_turnout.png         VEP turnout %, presidential vs midterm, 1920-2024
3. gallup_confidence.png   Gallup confidence in Congress vs the other institutions, 1998-2026
4. pew_trust.png           Pew trust in the federal government, 1958-2025
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from pypdf import PdfReader
import re

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / "data" / "processed", ROOT / "charts"
OUT.mkdir(exist_ok=True)

BLUE, ORANGE, GRAY, INK, MUTED = "#2a78d6", "#eb6834", "#c9c8c2", "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.grid": True, "grid.color": "#ecebe7", "grid.linewidth": 0.8})


def save(fig, name, source):
    fig.text(0.01, 0.01, source, fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT / name, dpi=150)
    plt.close(fig)


t = pd.read_csv(DATA / "turnout.csv")

# 1. Eligible vs voted, in people
c = t[t.year >= 1980]
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(c.year, c.vep_count / 1e6, color=BLUE, lw=2, label="Eligible to vote (VEP)")
for typ, mk in [("presidential", "o"), ("midterm", "s")]:
    s = c[c.type == typ]
    ax.scatter(s.year, s.ballots / 1e6, color=ORANGE, marker=mk, s=40, zorder=3,
               label=f"Ballots cast, {typ}", facecolors=ORANGE if typ == "presidential" else "white")
ax.vlines(c.year, c.ballots / 1e6, c.vep_count / 1e6, color=GRAY, lw=1, zorder=1)
for y, off, ha in [(2022, (0, -34), "center"), (2024, (10, -4), "left")]:
    r = c[c.year == y].iloc[0]
    ax.annotate(f"{r.vep_count/1e6:.0f}M eligible\n{r.ballots/1e6:.0f}M voted", (y, r.ballots / 1e6),
                xytext=off, textcoords="offset points", ha=ha, fontsize=8, color=INK)
ax.set_ylim(0, 270); ax.set_xlim(1978, 2031); ax.set_ylabel("Millions of people")
ax.set_title("Eligible voters vs. ballots cast, US general elections 1980–2024", loc="left", color=INK)
ax.legend(frameon=False, loc="upper left")
save(fig, "eligible_vs_voted.png", "Source: UF Election Lab (M. McDonald), CC BY 4.0. 1980–96 ballots = vote for highest office.")

# 2. VEP turnout %
c = t[t.year >= 1920]
fig, ax = plt.subplots(figsize=(10, 5.5))
for typ, col in [("presidential", BLUE), ("midterm", ORANGE)]:
    s = c[c.type == typ]
    ax.plot(s.year, s.vep_turnout, color=col, lw=2, marker="o", ms=4, label=typ.capitalize())
    last = s.iloc[-1]
    ax.annotate(f"{last.vep_turnout:.1f}% ({last.year})", (last.year, last.vep_turnout),
                xytext=(6, 0), textcoords="offset points", va="center", fontsize=9, color=INK)
r = c[c.year == 2018].iloc[0]
ax.annotate("2018: 50.05%, highest\nmidterm since 1914", (2018, r.vep_turnout), xytext=(-120, 18),
            textcoords="offset points", fontsize=9, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED))
ax.set_ylim(25, 75); ax.set_xlim(1918, 2034); ax.set_ylabel("% of voting-eligible population")
ax.set_title("Turnout of eligible voters, presidential vs. midterm years, 1920–2024", loc="left", color=INK)
ax.legend(frameon=False, loc="lower left")
save(fig, "vep_turnout.png", "Source: UF Election Lab national VEP turnout v1.4 (1948+ M. McDonald, CC BY 4.0; pre-1948 W. D. Burnham).")

# 3. Gallup confidence: Congress highlighted, other institutions as context
text = "\n".join(p.extract_text() for p in PdfReader(ROOT / "data/raw/gallup_confidence_topline_2026-06.pdf").pages)
names = ["Church/organized religion", "Military", "Supreme Court", "Banks", "Public schools", "Newspapers",
         "Congress", "Television news", "Organized labor", "Presidency", "Police", "Medical system",
         "Criminal justice system", "Big business", "Small business", "Tech companies", "Higher education"]
rows = []
for m in re.finditer(r"^(\d{4}) (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) ((?:\S+ ?){17})", text, re.M):
    for n, v in zip(names, m.group(2).split()[:17]):
        rows.append((int(m.group(1)), n, None if v == "--" else int(v)))
g = pd.DataFrame(rows, columns=["year", "inst", "pct"]).drop_duplicates(["year", "inst"]).dropna()
fig, ax = plt.subplots(figsize=(10, 5.5))
for n, s in g.groupby("inst"):
    if n != "Congress":
        ax.plot(s.year, s.pct, color=GRAY, lw=1)
s = g[g.inst == "Congress"]
ax.plot(s.year, s.pct, color=BLUE, lw=2.5, marker="o", ms=4)
for y in (1998, 2014, 2022, 2026):
    v = s[s.year == y].pct.iloc[0]
    ax.annotate(f"{v:.0f}%", (y, v), xytext=(0, -14), textcoords="offset points", ha="center", fontsize=9, color=INK)
ax.text(2026.4, 9, "Congress", color=BLUE, va="center", fontsize=10)
ax.text(2026.4, 61, "16 other institutions\n(gray)", color=MUTED, va="center", fontsize=9)
ax.set_xlim(1997, 2031); ax.set_ylim(0, 90); ax.set_ylabel('% "great deal" or "quite a lot"')
ax.set_title("Confidence in Congress vs. other institutions, Gallup 1998–2026", loc="left", color=INK)
save(fig, "gallup_confidence.png", "Source: Gallup June 2026 topline (trend 1998–2026). Congress record low: 7% in 2014 and 2022; 42% in 1973.")

# 4. Pew trust in the federal government
p = pd.read_csv(DATA / "trust.csv").query("series == 'pew_trust'").copy()
p["date"] = pd.to_datetime(p["date"])
yearly = p.groupby("year").value.mean()
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.scatter(p.date, p.value, color=GRAY, s=14, label="Individual polls")
ax.plot(pd.to_datetime(yearly.index.astype(str) + "-07-01"), yearly.values, color=BLUE, lw=2, label="Yearly average")
for d, v, lab in [("1964-10-15", 77, "77% (1964)"), ("2011-10-19", 10, "10% low (2011)"), ("2025-09-28", 17, "17% (2025)")]:
    ax.annotate(lab, (pd.Timestamp(d), v), xytext=(6, 4), textcoords="offset points", fontsize=9, color=INK)
ax.set_ylim(0, 85); ax.set_ylabel('% trust "always" or "most of the time"')
ax.set_title("Trust in the federal government to do what is right, 1958–2025", loc="left", color=INK)
ax.legend(frameon=False, loc="upper right")
save(fig, "pew_trust.png", "Source: Pew Research Center compilation (ANES, Gallup, CBS/NYT, ABC/Post, CNN, Pew), Dec 4, 2025.")
# 5. Turnout by age, midterm vs presidential years (small multiples, shared y)
a = pd.read_csv(DATA / "turnout_by_age.csv").query("year >= 1972").sort_values("year")
ramp = {"18 to 24": "#9cc3ee", "25 to 44": "#5d9be0", "45 to 64": "#2a78d6", "65 and Over": "#123f7a"}
fig, axes = plt.subplots(1, 2, figsize=(11, 5.5), sharey=True)
for ax, typ in zip(axes, ["midterm", "presidential"]):
    for age, col in ramp.items():
        s = a[(a.type == typ) & (a.age == age)]
        ax.plot(s.year, s.cps_total_turnout, color=col, lw=2, marker="o", ms=3.5)
        last = s.iloc[-1]
        ax.annotate(f"{age.replace(' and Over', '+')}: {last.cps_total_turnout:.0f}%", (last.year, last.cps_total_turnout),
                    xytext=(5, 0), textcoords="offset points", va="center", fontsize=8.5, color=INK)
    ax.set_title(f"{typ.capitalize()} years", loc="left", color=INK, fontsize=11)
    ax.set_xlim(1970, 2036); ax.set_ylim(0, 80)
axes[0].set_ylabel("% of age group who say they voted")
fig.suptitle("Turnout by age group, midterm vs. presidential years, 1972–2024", x=0.01, ha="left", color=INK)
save(fig, "turnout_by_age.png", "Source: Census CPS Table A-1, % of total population by age (noncitizens included). Starts 1972, after the 26th Amendment.")

# 6. Turnout gap, 65+ minus 18-24, midterm and presidential on one chart
g = a.pivot_table(index=["year", "type"], columns="age", values="cps_total_turnout").reset_index()
g["gap"] = g["65 and Over"] - g["18 to 24"]
fig, ax = plt.subplots(figsize=(10, 5.5))
for typ, col in [("midterm", ORANGE), ("presidential", BLUE)]:
    s = g[g.type == typ].sort_values("year")
    ax.plot(s.year, s.gap, color=col, lw=2, marker="o", ms=4, label=typ.capitalize())
    for y in (s.year.min(), s.year.max()):
        v = s[s.year == y].gap.iloc[0]
        ax.annotate(f"{v:.1f}", (y, v), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=9, color=INK)
pk = g[g.type == "midterm"].sort_values("gap").iloc[-1]
ax.annotate(f"{pk.gap:.1f} ({pk.year:.0f})", (pk.year, pk.gap), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=9, color=INK)
ax.set_ylim(0, 50); ax.set_ylabel("Percentage points (65+ turnout minus 18–24 turnout)")
ax.set_title("Turnout gap between voters 65+ and 18–24, 1972–2024", loc="left", color=INK)
ax.legend(frameon=False, loc="lower right")
save(fig, "age_gap.png", "Source: Census CPS Table A-1, % of total population by age who say they voted. Starts 1972, after the 26th Amendment.")

# 7. Age of Congress: mean age by chamber, and share 65+
ca = pd.read_csv(DATA / "congress_age.csv")
fig, axes = plt.subplots(1, 2, figsize=(11, 5.5))
for ax, col_name, ylab, ylim in [(axes[0], "mean_age", "Mean age at start of Congress", (45, 70)),
                                 (axes[1], "share_65_plus", "% of members 65 or older", (0, 60))]:
    for ch, col in [("Senate", "#123f7a"), ("House", "#5d9be0")]:
        s = ca[ca.chamber == ch]
        ax.plot(s.year, s[col_name], color=col, lw=2)
        last = s.iloc[-1]
        ax.annotate(f"{ch}: {last[col_name]:.1f}{'' if col_name == 'mean_age' else '%'}", (last.year, last[col_name]),
                    xytext=(5, 0), textcoords="offset points", va="center", fontsize=9, color=INK)
    ax.set_ylabel(ylab); ax.set_ylim(*ylim); ax.set_xlim(1898, 2045)
fig.suptitle("Age of Congress at the start of each Congress, 1901–2025", x=0.01, ha="left", color=INK)
save(fig, "congress_age.png", "Source: unitedstates/congress-legislators (CC0); members from the 50 states, delegates excluded. CRS figures run ~0.5 yr higher.")

# 8. 65+ share of voters vs share of adults
o = pd.read_csv(DATA / "turnout_by_age.csv").query("age == '65 and Over' and year >= 1972").sort_values("year")
fig, ax = plt.subplots(figsize=(10, 5.5))
for typ, col in [("midterm", ORANGE), ("presidential", BLUE)]:
    s = o[o.type == typ]
    ax.plot(s.year, s.share_of_voters, color=col, lw=2, marker="o", ms=4, label=f"65+ share of voters, {typ}")
ax.plot(o.year, o.share_of_adults, color=MUTED, lw=2, ls="--", label="65+ share of all adults")
for y, typ in [(1974, "midterm"), (2022, "midterm"), (1972, "presidential"), (2024, "presidential")]:
    v = o[(o.year == y)].share_of_voters.iloc[0]
    ax.annotate(f"{v:.1f}%", (y, v), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=9, color=INK)
for y in (1972, 2024):
    v = o[o.year == y].share_of_adults.iloc[0]
    ax.annotate(f"{v:.1f}%", (y, v), xytext=(0, -15), textcoords="offset points", ha="center", fontsize=9, color=MUTED)
ax.set_ylim(0, 35); ax.set_ylabel("% of all adults / of all voters")
ax.set_title("Voters 65+ as a share of the electorate vs. of the adult population, 1972–2024", loc="left", color=INK)
ax.legend(frameon=False, loc="upper left")
save(fig, "senior_share_of_voters.png", "Source: Census CPS Table A-1: population by age x % who say they voted. Self-reported.")

# 9. Adults by age group, 1970-2024 (millions)
# Starts 1972: before the 26th Amendment, CPS's "18 to 24" mostly held 21-24-year-olds (13.0M in 1970 vs 24.6M in 1972).
pa = pd.read_csv(DATA / "turnout_by_age.csv").query("year >= 1972").sort_values("year")
fig, ax = plt.subplots(figsize=(10, 5.5))
for age, col in ramp.items():
    s = pa[pa.age == age]
    ax.plot(s.year, s.population_k / 1000, color=col, lw=2.5)
    f, l = s.iloc[0], s.iloc[-1]
    ax.annotate(f"{f.population_k/1000:.0f}M", (f.year, f.population_k / 1000), xytext=(-6, 0), textcoords="offset points",
                ha="right", va="center", fontsize=9, color=INK)
    ax.annotate(f"{age.replace(' and Over', '+')}: {l.population_k/1000:.0f}M", (l.year, l.population_k / 1000),
                xytext=(6, 0), textcoords="offset points", va="center", fontsize=9, color=INK)
ax.set_xlim(1964, 2036); ax.set_ylim(0, 100); ax.set_ylabel("Adults, millions")
ax.set_title("US adults by age group, 1972–2024", loc="left", color=INK)
save(fig, "adults_by_age.png", "Source: Census CPS Table A-1, civilian noninstitutionalized population 18+ (noncitizens included), election years.")

# 10. Seniors (65+) who voted per young (18-24) voter
v = pd.read_csv(DATA / "turnout_by_age.csv").query("year >= 1972")
v = v.pivot_table(index=["year", "type"], columns="age", values="voters_k").reset_index()
v["ratio"] = v["65 and Over"] / v["18 to 24"]
fig, ax = plt.subplots(figsize=(10, 5.5))
for typ, col in [("midterm", ORANGE), ("presidential", BLUE)]:
    s = v[v.type == typ].sort_values("year")
    ax.plot(s.year, s.ratio, color=col, lw=2, marker="o", ms=4, label=typ.capitalize())
    for y in {s.year.min(), s.year.max(), s.loc[s.ratio.idxmax(), "year"]}:
        r_ = s[s.year == y].ratio.iloc[0]
        ax.annotate(f"{r_:.1f} ({y})", (y, r_), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=9, color=INK)
ax.axhline(1, color=MUTED, lw=1, ls=":")
ax.text(2024, 0.8, "1 = equal numbers of voters", fontsize=8, color=MUTED, ha="right")
ax.set_ylim(0, 6.5); ax.set_ylabel("Voters 65+ per voter aged 18–24")
ax.set_title("Voters 65+ for every voter aged 18–24, 1972–2024", loc="left", color=INK)
ax.legend(frameon=False, loc="upper left")
save(fig, "senior_to_young_voter_ratio.png", "Source: Census CPS Table A-1: population by age x % who say they voted (self-reported, noncitizens in the base).")
# Three decimals: 2014's ratio is 5.555, which must round to 5.6 as spoken in the Reel, not 5.5.
v.round(3).to_csv(DATA / "senior_to_young_ratio.csv", index=False)

print("wrote", sorted(f.name for f in OUT.glob("*.png")))
