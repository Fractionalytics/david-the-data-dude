"""Static mockups of Reel 3's new charts (DDD15 Script v6), in Reel 1's road-sign look.

Mockups only: the production versions are Remotion components, built after David's Start times
(docs/video-playbook.md section 6). Each mockup is a full 1080x1920 frame: Reel 1's wall color and
stills of the speaker (video/public/speaker-*.png; Reel 3 was filmed against a different wall) with the sign plate in the head-low band (video/src/look.tsx).
Titles are David's words, so every title is "[TBD: David]"; axis and data labels are ours.

Outputs: charts/mockups/reel3/card-*.png and contact_sheet.png. Plan: docs/reel3-visual-plan.md.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from fontTools.ttLib import TTFont
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT.parents[1] / "shared" / "video-kit" / "fonts"
OUT = ROOT / "charts" / "mockups" / "reel3"
OUT.mkdir(parents=True, exist_ok=True)

# Barlow Condensed ships as woff2 for Remotion; matplotlib needs TrueType.
FONT_DIR = OUT / ".fonts"
FONT_DIR.mkdir(exist_ok=True)
for w in ("700", "800"):
    ttf = FONT_DIR / f"BarlowCondensed-{w}.ttf"
    if not ttf.exists():
        f = TTFont(KIT / f"BarlowCondensed-{w}.woff2")
        f.flavor = None
        f.save(ttf)
    font_manager.fontManager.addfont(str(ttf))
plt.rcParams["font.family"] = "Barlow Condensed"

# look.tsx colors
PLATE, BORDER, INK, MUTED, GRID = "#FBFBF7", "#1A1C1E", "#1A1C1E", "#5E6368", "#D9DCD4"
US, CZ, METH = "#B3261E", "#1F4E9C", "#7A5A00"
BAND = (120, 250, 960, 800)
PW, PH = BAND[2] - BAND[0], BAND[3] - BAND[1]
PX = 72 / 100  # points per pixel at dpi 100


def px(n):
    return n * PX


def plate(title="[TBD: David]"):
    """A plate-sized figure (840x550 px) with the sign border and a title. Returns fig, ax."""
    fig = plt.figure(figsize=(PW / 100, PH / 100), dpi=100)
    fig.patch.set_alpha(0)
    fig.patches.append(FancyBboxPatch((0.004, 0.006), 0.992, 0.988, boxstyle="round,pad=0,rounding_size=0.035",
                                      transform=fig.transFigure, facecolor=PLATE, edgecolor=BORDER, lw=px(7) * 2,
                                      mutation_aspect=PW / PH, zorder=-10))
    fig.text(40 / PW, 1 - 26 / PH, title.upper(), ha="left", va="top", fontsize=px(58), weight=800,
             color=MUTED if title.startswith("[TBD") else INK)
    ax = fig.add_axes((0.14, 0.17, 0.80, 0.62))
    ax.set_facecolor("none")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
        ax.spines[s].set_linewidth(2)
    ax.tick_params(colors=MUTED, labelsize=px(36), length=0)
    return fig, ax


def frame(fig, name, note, speaker="a"):
    """Composite the plate onto a Reel 1 still of the speaker on that card; save the frame."""
    tmp = OUT / f".{name}.png"
    fig.savefig(tmp, dpi=100, transparent=True)
    plt.close(fig)
    img = Image.open(ROOT / "video" / "public" / f"speaker-{speaker}.png").convert("RGBA")
    img.alpha_composite(Image.open(tmp).convert("RGBA"), (BAND[0], BAND[1]))
    tmp.unlink()
    img.convert("RGB").save(OUT / f"{name}.png")
    NOTES.append((name, note))


NOTES = []
b = pd.read_csv(ROOT / "data" / "final" / "three_buckets.csv").set_index(["country", "period"])
us_e, us_l = b.loc[("US", "cz_early_years")], b.loc[("US", "cz_late_years")]
cz_e, cz_l = b.loc[("Czechia", "early")], b.loc[("Czechia", "late")]
r = pd.read_csv(ROOT / "data" / "final" / "eu_pedestrian_rates.csv")
pop = r[r.geo == "US"].assign(pop=lambda d: d.deaths / d.rate_per_100k * 1e5).set_index("year")["pop"]

# Chart E: same numbers as scripts/chart_dose_ladder.py ladder()
floor = us_l.stim_floor_per_million / cz_l.stim_floor_per_million
cz_pp = 31600 / 10.55e6
users = {k: (v / pop[2016]) / cz_pp for k, v in (("lo", 1.3e6), ("best", 3.2e6), ("hi", 5.3e6))}
risk = {"best": floor / users["best"], "lo": floor / users["hi"], "hi": floor / users["lo"]}


def chart_e(whiskers):
    fig, ax = plate()
    rows = [("Heavy meth users\nper person", users["best"], (users["lo"], users["hi"]), METH),
            ("Stimulant-positive\ndead pedestrians\nper person", floor, None, US),
            ("Risk per\nheavy user", risk["best"], (risk["lo"], risk["hi"]), MUTED)]
    for i, (lab, v, rng, col) in enumerate(rows):
        ax.barh(i, v, color=col, height=0.58)
        if whiskers and rng:
            ax.plot(rng, [i, i], color=INK, lw=4, solid_capstyle="butt")
            for x in rng:
                ax.plot([x, x], [i - 0.17, i + 0.17], color=INK, lw=4)
            ax.text(rng[1] + 0.3, i, f"{rng[0]:.1f}–{rng[1]:.1f}×", va="center", fontsize=px(36), color=MUTED,
                    weight=700)
        ax.text(0.25, i, f"{v:.0f}×" if v > 10 or rng else f"{v:.1f}×", va="center", fontsize=px(48),
                color=PLATE, weight=800)
    ax.axvline(1, color=INK, lw=3, ls=(0, (4, 3)))
    ax.text(1.2, -0.68, "1× = same as Czechia", fontsize=px(30), color=MUTED, weight=700)
    ax.set_yticks(range(3), [x[0] for x in rows], fontsize=px(34), color=INK, weight=700)
    ax.set_ylim(2.55, -0.85)
    ax.set_xlim(0, 14)
    ax.set_xticks([0, 5, 10], ["0", "5×", "10×"])
    ax.set_position((0.38, 0.12, 0.57, 0.66))
    return fig


frame(chart_e(False), "card-15-17_chart-e",
      f"Cards 15-17. Bars build top to bottom: users {users['best']:.1f}x (15), dead pedestrians {floor:.1f}x (16), "
      f"risk per user {risk['best']:.1f}x (17). Linear axis.")
frame(chart_e(True), "card-18-19_chart-e-whiskers",
      f"Cards 18-19. Whiskers draw in: users {users['lo']:.1f}-{users['hi']:.1f}x, risk {risk['lo']:.1f}-{risk['hi']:.1f}x. "
      "Dead pedestrians has no whisker (one count).")

# Cards 22-23: absolute bars per million, then ratios (Czechia = 1)
groups = [("Stimulant-\npositive", us_l.stim_floor_per_million, cz_l.stim_floor_per_million),
          ("No stimulants\nfound", us_l.tested_neg_per_million, cz_l.tested_neg_per_million)]


def bars(ratio):
    fig, ax = plate()
    w = 0.36
    for i, (lab, u, c) in enumerate(groups):
        uv, cv = (u / c, 1.0) if ratio else (u, c)
        ax.bar(i - w / 2, uv, w, color=US)
        ax.bar(i + w / 2, cv, w, color=CZ)
        ax.text(i - w / 2, uv + 0.2, (f"{uv:.0f}×" if uv > 10 else f"{uv:.1f}×") if ratio else f"{uv:.2f}", ha="center", va="bottom",
                fontsize=px(44), weight=800, color=US)
        ax.text(i + w / 2, cv + 0.2, "1×" if ratio else f"{cv:.2f}", ha="center", va="bottom", fontsize=px(44),
                weight=800, color=CZ)
    ax.set_xticks(range(2), [g[0] for g in groups], fontsize=px(36), color=INK, weight=700)
    ax.set_ylim(0, 15 if ratio else 10.5)
    ax.set_yticks([0, 5, 10], ["0", "5×", "10×"] if ratio else ["0", "5", "10"])
    ax.yaxis.grid(True, color=GRID, lw=2)
    ax.set_axisbelow(True)
    ax.set_xlim(-0.5, 1.5)
    ax.text(0.25, 14 if ratio else 9.8, "US", color=US, fontsize=px(44), weight=800, ha="center")
    ax.text(0.25, 12.5 if ratio else 8.8, "Czechia", color=CZ, fontsize=px(44), weight=800, ha="center")
    ax.set_ylabel("US ÷ Czechia" if ratio else "Dead pedestrians\nper million a year", fontsize=px(32),
                  color=MUTED, weight=700)
    return fig


frame(bars(False), "card-22_bars-per-million",
      "Card 22. Tested dead pedestrians per million a year, 2016-21. Most had no stimulants in both countries.", "b")
frame(bars(True), "card-23_bars-ratio",
      f"Card 23. The same bars divided by Czechia: stimulant-positive {groups[0][1] / groups[0][2]:.0f}x, "
      f"no stimulants {groups[1][1] / groups[1][2]:.1f}x. The short pair becomes the tall one.")


def slope(series, ymax, yticks, name, note):
    fig, ax = plate()
    for lab, a, z, col, ls, nudge in series:
        ax.plot([0, 1], [a, z], color=col, lw=7, ls=ls, marker="o", ms=14)
        ax.text(-0.05, a + nudge, f"{a:.1f}", ha="right", va="center", fontsize=px(40), weight=800, color=col)
        ax.text(1.05, z + nudge, f"{z:.1f}  {lab}", ha="left", va="center", fontsize=px(36), weight=800, color=col)
    ax.set_xlim(-0.3, 1.9)
    ax.set_ylim(-ymax * 0.04, ymax)
    ax.tick_params(axis="x", pad=14)
    ax.set_xticks([0, 1], ["2003–05", "2016–21"], fontsize=px(38), color=INK, weight=700)
    ax.set_yticks(yticks)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", labelleft=False)
    ax.yaxis.grid(True, color=GRID, lw=2)
    ax.set_axisbelow(True)
    ax.text(-0.3, ymax, "Dead pedestrians per million a year", fontsize=px(30), color=MUTED, weight=700, va="bottom")
    frame(fig, name, note)


slope([("US, no stim.", us_e.tested_neg_per_million, us_l.tested_neg_per_million, US, "-", 0),
       ("Czechia, no stim.", cz_e.tested_neg_per_million, cz_l.tested_neg_per_million, CZ, "-", 0),
       ("US, stim.+", us_e.stim_floor_per_million, us_l.stim_floor_per_million, US, (0, (2, 1.5)), 0.4),
       ("Czechia, stim.+", cz_e.stim_floor_per_million, cz_l.stim_floor_per_million, CZ, (0, (2, 1.5)), -0.3)],
      11, [0, 5, 10], "card-25_slope-two-groups",
      "Card 25. Tested victims only: no stimulants found (solid) and stimulant-positive (dotted). "
      "The two stimulant lines sit near the floor, so their labels are nudged apart.")
slope([("US", us_e.total_per_million, us_l.total_per_million, US, "-", 0),
       ("Czechia", cz_e.total_per_million, cz_l.total_per_million, CZ, "-", 0)],
      31, [0, 10, 20, 30], "card-26_slope-all-pedestrians",
      f"Card 26. All pedestrian deaths, tested or not. Czechia was {cz_e.total_per_million / us_e.total_per_million:.1f}x "
      "the US in 2003-05 and about half of it by 2016-21. Scale differs from card 25 (these include untested victims).")

# Card 44: working in tandem, both indexed to 2009 = 1
rand = {2009: 1.7, 2012: 2.1, 2013: 2.5, 2014: 2.8, 2015: 3.4, 2016: 3.2}  # RAND RR3140 Table 2.6, millions
m = pd.read_csv(ROOT / "data" / "final" / "ped_meth_vs_cocaine.csv").set_index("year")
yrs = [y for y in range(2009, 2025) if y in pop.index]
meth_pm = (m.loc[yrs, "meth_amph"] / pop[yrs])
meth_ix = meth_pm / meth_pm[2009]
users_pp = pd.Series({y: v * 1e6 / pop[y] for y, v in rand.items()})
users_ix = users_pp / users_pp[2009]
fig, ax = plate()
ax.plot(meth_ix.index, meth_ix.values, color=US, lw=7)
ax.plot(users_ix.index, users_ix.values, color=METH, lw=7, marker="o", ms=10)
ax.text(2016.4, users_ix[2016] + 1.6, f"Heavy meth users ×{users_ix[2016]:.1f}\n(RAND ends 2016)", color=METH,
        fontsize=px(34), weight=800, va="center")
ax.text(2015.8, meth_ix[2016] + 0.4, f"×{meth_ix[2016]:.0f}", color=US, fontsize=px(40), weight=800, ha="right",
        va="bottom")
last = max(yrs)
ax.text(2018.3, 15, f"Meth-positive dead\npedestrians ×{meth_ix[last]:.0f} by {last}", color=US,
        fontsize=px(34), weight=800, ha="right", va="bottom")
ax.axhline(1, color=INK, lw=3, ls=(0, (4, 3)))
ax.set_xlim(2008.5, last + 0.5)
ax.set_ylim(0, 20)
ax.set_xticks([2009, 2016, last])
ax.set_yticks([1, 5, 10, 15], ["1", "5", "10", "15"])
ax.yaxis.grid(True, color=GRID, lw=2)
ax.set_axisbelow(True)
ax.text(2008.5, 20, "Per person, 2009 = 1", fontsize=px(30), color=MUTED, weight=700, va="bottom")
frame(fig, "card-44_tandem",
      f"Card 44. Per person, 2009 = 1. Users x{users_ix[2016]:.1f} by 2016; meth-positive dead pedestrians "
      f"x{meth_ix[2016]:.1f} by 2016, x{meth_ix[last]:.0f} by {last} (tested and positive only; 2009's base is 56 people). "
      f"The widening gap is risk per user. The {last} dip follows fewer tests "
      f"({m.loc[last, 'tested']:,} vs. {m.loc[last - 1, 'tested']:,} in {last - 1}).")

# Contact sheet
names = [n for n, _ in NOTES]
thumbs = [Image.open(OUT / f"{n}.png").crop((0, 150, 1080, 1500)).resize((432, 540)) for n in names]
sheet = Image.new("RGB", (432 * 4, 540 * 2), "white")
for i, t in enumerate(thumbs):
    sheet.paste(t, ((i % 4) * 432, (i // 4) * 540))
sheet.save(OUT / "contact_sheet.png")
for n, note in NOTES:
    print(f"{n}: {note}")
