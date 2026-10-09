"""Exploratory charts (not storyboard charts) for David to react to.

Writes PNGs to projects/ideabrowser/charts/exploratory/. Featured ideas only (424),
because who-pays / business-type / AI answers from titles alone proved unreliable.

Usage: python projects/ideabrowser/scripts/exploratory_charts.py
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

import classify as c
from classify_greg13 import TYPES

OUT = Path(__file__).resolve().parents[1] / "charts" / "exploratory"
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#1f1f1e", "#6b6a63", "#e6e5df"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
PERIODS = ["Era 1\nJul 2025–Jan 2026", "Era 2\nJan–Jul 2026", "Newsletter\nbefore Sep 12", "Newsletter\nSep 12 on"]
ERAS = ["Era 1\nJul 2025–Jan 2026", "Era 2\nJan–Jul 2026", "Newsletter era\nJul 28 2026 on"]
SEP12 = pd.Timestamp("2026-09-12")


def load():
    a = pd.DataFrame(map(json.loads, c.ANSWERS.open(encoding="utf-8")))
    main = a[(a.definitions_version == "v3") & (a["mode"] == "main")].drop_duplicates("key", keep="last")
    g = pd.DataFrame(map(json.loads, (c.DATA / "greg13_answers.jsonl").open(encoding="utf-8")))
    g = g.drop_duplicates("key", keep="last")
    d = c.load_ideas()
    d = d[d.role == "featured"][["key", "era", "title", "date_utc"]].merge(main, on="key").merge(g, on="key")
    d["date"] = pd.to_datetime(d.date_utc).dt.tz_localize(None)
    d["period"] = (d.era - 1).where(d.era < 3, 2 + (d.date >= SEP12))
    return d


def style(ax, title, subtitle):
    ax.set_facecolor(SURFACE)
    ax.figure.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=MUTED, length=0, labelsize=9)
    ax.figure.text(0.06, 0.95, title, fontsize=13, weight="bold", color=INK, ha="left")
    ax.figure.text(0.06, 0.905, subtitle, fontsize=9.5, color=MUTED, ha="left")


def share_lines(d, series, title, subtitle, fname, ymax=100, three_eras=False):
    """series: {label: boolean Series aligned with d}. three_eras pools the newsletter era (no Sep 12 split)."""
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.subplots_adjust(left=0.08, right=0.8, top=0.82, bottom=0.17)
    period, labels = (d.era - 1, ERAS) if three_eras else (d.period, PERIODS)
    last = len(labels) - 1
    n = d.groupby(period).size()
    pcts = {label: flag.groupby(period).mean().reindex(range(last + 1)) * 100 for label, flag in series.items()}
    # End labels: keep at least 7 points apart so lines that finish close together stay readable.
    ends = sorted(((p.iloc[-1], lab) for lab, p in pcts.items()), reverse=True)
    label_y = {}
    for y, lab in ends:
        label_y[lab] = min(y, min(label_y.values(), default=y + 7) - 7 * ymax / 100)
    for color, (label, pct) in zip(SERIES, pcts.items()):
        ax.plot(range(last + 1), pct, color=color, linewidth=2, marker="o", markersize=8,
                markeredgecolor=SURFACE, markeredgewidth=2)
        ax.annotate(f"{label}  {pct.iloc[-1]:.0f}%", (last, pct.iloc[-1]), xytext=(last + 0.06, label_y[label]),
                    textcoords="data", va="center", fontsize=9.5, color=INK)
        for x, y in enumerate(pct):
            if x < last:
                # A label goes below its point when another series sits just above it.
                below = any(0 <= o.iloc[x] - y < 6 and o is not pct for o in pcts.values())
                # Near the floor there's no room below, so the label sits to the left.
                xy = (-10, -4) if below and y < 8 else (0, -15 if below else 9)
                ax.annotate(f"{y:.0f}%", (x, y), xytext=xy, textcoords="offset points",
                            ha="right" if xy[0] else "center", fontsize=8, color=MUTED)
    ax.set_xticks(range(last + 1), [f"{p}\n(n={n.get(i, 0)})" for i, p in enumerate(labels)])
    ax.set_ylim(0, ymax)
    ax.set_yticks(range(0, ymax + 1, ymax // 5 if ymax >= 50 else 5))
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    if not three_eras:
        ax.axvline(2.5, color=MUTED, linewidth=1, linestyle=(0, (3, 3)))
        ax.text(2.53, ymax * 0.97, "Greg's post\nSep 12", fontsize=8, color=MUTED, va="top")
    style(ax, title, subtitle)
    fig.savefig(OUT / fname, dpi=160)
    plt.close(fig)


def weekly_services(d):
    n3 = d[d.era == 3].copy()
    n3["week"] = n3.date.dt.to_period("W").dt.start_time
    w = n3.groupby("week").agg(n=("key", "size"), svc=("business_type", lambda s: (s == "Service").sum()))
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.82, bottom=0.14)
    straddle = [wk <= SEP12 < wk + pd.Timedelta(days=7) for wk in w.index]
    colors = [MUTED if st else SERIES[0] for st in straddle]
    ax.bar(range(len(w)), w.svc / w.n * 100, color=colors, width=0.8, edgecolor=SURFACE, linewidth=2)
    for x, (s, k) in enumerate(zip(w.svc, w.n)):
        ax.annotate(f"{s} of {k}", (x, s / k * 100), xytext=(0, 4), textcoords="offset points",
                    ha="center", fontsize=8, color=MUTED)
    ax.set_xticks(range(len(w)), [f"{wk:%b} {wk.day}" for wk in w.index],
                  fontsize=8)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    i = straddle.index(True)
    split = i - 0.4 + 0.8 * (SEP12 - w.index[i]).days / 7  # Sep 12's position within its week's bar
    top = w.svc.iloc[i] / w.n.iloc[i] * 100 + 8  # start above the straddling bar's label
    ax.vlines(split, top, 100, color=INK, linewidth=1, linestyle=(0, (3, 3)))
    ax.text(split + 0.08, 97, "Greg's post, Sep 12\n(gray week straddles it;\nOct 5 week is 3 days)",
            fontsize=8, color=MUTED, va="top")
    style(ax, "Service ideas per week, newsletter era",
          "Share of each week's featured ideas classified as service businesses (weeks start Monday)")
    fig.savefig(OUT / "3_weekly_services.png", dpi=160)
    plt.close(fig)


# Draft theme names (docs/themes.md), stability >= 0.45 only.
STABLE_THEMES = {2: "Tools for AI agents themselves", 13: "Health & caregiving apps", 3: "Teaching & learning",
                 4: "Home improvement & energy", 15: "AI phone & voice agents", 10: "Video & content creation",
                 16: "Death, estates & inheritance"}


def themes_dumbbell():
    cl = pd.read_csv(c.DATA / "clusters_centered.csv")
    share = pd.crosstab(cl.k17, cl.era, normalize="columns") * 100
    rows = share.loc[list(STABLE_THEMES), [1, 3]].assign(change=lambda t: t[3] - t[1]).sort_values("change")
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.subplots_adjust(left=0.3, right=0.95, top=0.8, bottom=0.12)
    for y, (k, r) in enumerate(rows.iterrows()):
        ax.plot([r[1], r[3]], [y, y], color=GRID, linewidth=2, zorder=1)
        ax.scatter(r[1], y, s=70, color=MUTED, edgecolor=SURFACE, linewidth=2, zorder=2)
        ax.scatter(r[3], y, s=70, color=SERIES[0], edgecolor=SURFACE, linewidth=2, zorder=3)
        ax.annotate(f"{r[3]:.0f}%", (r[3], y), xytext=(0, 9), textcoords="offset points", ha="center",
                    fontsize=8, color=INK)
    ax.set_yticks(range(len(rows)), [STABLE_THEMES[k] for k in rows.index], fontsize=9.5, color=INK)
    ax.set_xlim(0, 20)
    ax.set_xticks(range(0, 21, 5))
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.text(0.99, 1.02, "● Era 1 (Jul 2025–Jan 2026)", transform=ax.transAxes, ha="right", fontsize=8.5, color=MUTED)
    ax.text(0.99, 1.07, "● Newsletter era (Jul 28 2026 on)", transform=ax.transAxes, ha="right", fontsize=8.5,
            color=SERIES[0])
    style(ax, "Bottom-up themes: era 1 vs. newsletter era",
          "Share of featured ideas in each theme; stable themes only (stability 0.45 or above)")
    ax.grid(axis="y", visible=False)
    fig.savefig(OUT / "4_themes_era1_vs_newsletter.png", dpi=160)
    plt.close(fig)


def agent_titles(d):
    t = d.title.str.lower()
    says_agent = t.str.contains(r"\bagents?\b") & ~t.str.contains(r"(?:real estate|insurance|travel) agents?")
    share_lines(d, {"Title says \"agent\"": says_agent},
                "Featured idea titles that say \"agent\"", "Share of featured ideas per period (real estate, "
                "insurance and travel agents excluded)", "5_agent_titles.png", ymax=20)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.family"] = "Segoe UI"
    d = load()
    bt = d.business_type
    share_lines(d, {"Software / app": bt == "Software / app", "Service": bt == "Service",
                    "Marketplace": bt == "Marketplace"},
                "Featured ideas by business type",
                "Share of featured ideas by business type (Jev classification, 424 featured ideas)",
                "1_business_type.png")
    share_lines(d, {"Software / app": bt == "Software / app", "Service": bt == "Service",
                    "Marketplace": bt == "Marketplace"},
                "Featured ideas by business type, three eras",
                "Share of featured ideas by business type (Jev classification, 424 featured ideas)",
                "1b_business_type_three_eras.png", three_eras=True)

    yes = d[list(TYPES)] >= 0.5
    non_agent = yes.drop(columns=["vertical_agent", "domain_harness"]).any(axis=1)
    share_lines(d, {"Fits a non-agent type": non_agent, "AI-native service firm": yes.ai_service_firm,
                    "Marketplace / social": yes.marketplace_social},
                "Featured ideas fitting Greg Isenberg's list",
                "Share fitting his 'only businesses left to build' types (agent types excluded; Jev yes/no, 424 ideas)",
                "2_greg_list_drift.png")
    weekly_services(d)
    themes_dumbbell()
    agent_titles(d)
    print(f"wrote {len(list(OUT.glob('*.png')))} charts to {OUT}")


if __name__ == "__main__":
    main()
