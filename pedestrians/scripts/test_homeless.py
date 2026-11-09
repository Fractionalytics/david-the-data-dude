"""Pre-registered test P4 (docs/hypothesis-test.md): across states, does the
change in unsheltered homeless people per 100,000 track the change in
pedestrian deaths per 100,000?

    python scripts/test_homeless.py
      reads  data/raw/fars/FARS<YEAR>NationalCSV.zip, 2009-2011 and 2020-2022
             data/raw/fred/<ST>POP.csv            (state population, thousands)
             data/raw/hud/*PIT-Counts-by-State*   (HUD Point-in-Time estimates by state,
                                                   one sheet per year; see data/raw/hud/SOURCE.md)
      writes data/final/test_homeless.csv         one row per state (50 + DC)
             charts/test_homeless_scatter.png     (not pre-registered)

If the HUD file is missing, the script writes the pedestrian half of the table
and stops with a message.

Steps (choices fixed before the HUD data was seen)
  1. Pedestrian deaths (PER_TYP 5, INJ_SEV 4) by state from PERSON.STATE (FIPS),
     via fars_pedestrians.year_peds + load. PERSON.STATE is used because
     ACCIDENT.STATE carries a byte-order mark in some files.
  2. Pedestrian rate per period = average deaths per year / average population
     over the same three years x 100,000. Change = 2020-22 rate - 2009-11 rate.
  3. Unsheltered homeless per 100,000 = HUD "Unsheltered Homeless" (one sheet per year) /
     FRED population that year x 100,000, for the base year and 2022.
     Base year: 2009 if every state has an unsheltered count for it, else the
     nearest year with full coverage, trying 2008, 2010, 2007, 2011 in that order.
     Change = 2022 rate - base-year rate.
  4. Pre-registered: Pearson r across the 51, and with California left out.
     PASS if both r > 0.3.
  5. Not pre-registered extras: Spearman r (both samples); Pearson r using total
     ("Overall") homeless instead of unsheltered; scatter plot.
"""

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fars_pedestrians import FINAL, ROOT, load, year_peds  # noqa: E402
from fars_decompose import FIPS, state_pop  # noqa: E402

HUD = ROOT / "data" / "raw" / "hud"
EARLY, LATE = [2009, 2010, 2011], [2020, 2021, 2022]
BASE_ORDER = [2009, 2008, 2010, 2007, 2011]
STATES = sorted(FIPS.values())


def ped_by_state() -> pd.DataFrame:
    rows = []
    for y in EARLY + LATE:
        d, _ = year_peds(y)
        p = load(y, "person", ["ST_CASE", "VEH_NO", "PER_NO", "STATE"])
        d = d.merge(p, on=["ST_CASE", "VEH_NO", "PER_NO"], how="left", validate="1:1")
        if d.STATE.isna().any():
            raise SystemExit(f"{y}: {d.STATE.isna().sum()} pedestrian deaths without PERSON.STATE")
        c = d.STATE.map(FIPS).value_counts()
        rows += [{"state": s, "year": y, "deaths": int(c.get(s, 0))} for s in STATES]
        print(y, len(d), "deaths,", c.size, "states", flush=True)
    t = pd.DataFrame(rows).merge(state_pop(), on=["state", "year"], how="left", validate="1:1")
    out = {}
    for tag, ys in (("2009_11", EARLY), ("2020_22", LATE)):
        g = t[t.year.isin(ys)].groupby("state")
        out[f"ped_deaths_{tag}"] = g.deaths.mean()
        out[f"ped_rate_{tag}"] = g.deaths.mean() / g.population.mean() * 1e5
    s = pd.DataFrame(out)
    s["ped_rate_change"] = s.ped_rate_2020_22 - s.ped_rate_2009_11
    return s


def hud_sheet(path: Path, year: int) -> pd.DataFrame | None:
    """State, unsheltered and overall counts for one year's sheet, or None."""
    engine = "pyxlsb" if path.suffix == ".xlsb" else None
    try:
        raw = pd.read_excel(path, sheet_name=str(year), header=None, engine=engine)
    except ValueError:
        return None
    hdr = next(i for i in range(10) if raw.iloc[i].astype(str).str.strip().eq("State").any())
    d = raw.iloc[hdr + 1:].copy()
    d.columns = raw.iloc[hdr].astype(str).str.strip()
    # older editions suffix the year ("Unsheltered Homeless, 2009"); the 2007-2024 file doesn't
    suffix = f", {year}" if f"Unsheltered Homeless, {year}" in d.columns else ""
    want = {"state": "State", "unsheltered": f"Unsheltered Homeless{suffix}", "overall": f"Overall Homeless{suffix}"}
    missing = [c for c in want.values() if c not in d.columns]
    if missing:
        print(f"HUD sheet {year}: missing columns {missing}", flush=True)
        return None
    d = d[list(want.values())].set_axis(list(want), axis=1)
    d["state"] = d.state.astype(str).str.strip()
    d = d[d.state.isin(STATES)]
    for c in ("unsheltered", "overall"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d.set_index("state")


def main() -> None:
    FINAL.mkdir(parents=True, exist_ok=True)
    s = ped_by_state()
    files = sorted(HUD.glob("*PIT-Counts-by-State*.xls*")) if HUD.exists() else []
    if not files:
        s.round(4).reset_index().to_csv(FINAL / "test_homeless.csv", index=False)
        raise SystemExit("No HUD PIT-by-state file in data/raw/hud/ (see SOURCE.md). Wrote pedestrian half only.")
    path = files[-1]
    print("HUD file:", path.name)

    late = hud_sheet(path, 2022)
    base_year, base = None, None
    for y in BASE_ORDER:
        b = hud_sheet(path, y)
        if b is not None and b.unsheltered.reindex(STATES).notna().all():
            base_year, base = y, b
            break
    if late is None or base is None or late.unsheltered.reindex(STATES).isna().any():
        raise SystemExit("HUD file lacks full state unsheltered counts for 2022 or any base year")
    print("base year:", base_year)

    pop = state_pop().pivot(index="state", columns="year", values="population")
    for kind in ("unsheltered", "overall"):
        s[f"{kind}_{base_year}"] = base[kind]
        s[f"{kind}_2022"] = late[kind]
        s[f"{kind}_rate_{base_year}"] = base[kind] / pop[base_year] * 1e5
        s[f"{kind}_rate_2022"] = late[kind] / pop[2022] * 1e5
        s[f"{kind}_rate_change"] = s[f"{kind}_rate_2022"] - s[f"{kind}_rate_{base_year}"]
    s["hud_base_year"] = base_year
    s = s.reindex(STATES)
    assert len(s) == 51 and s.notna().all().all(), s[s.isna().any(axis=1)]
    s.round(4).reset_index().to_csv(FINAL / "test_homeless.csv", index=False)

    x, y = s.unsheltered_rate_change, s.ped_rate_change
    no_ca = s.index != "CA"
    r_all, r_noca = x.corr(y), x[no_ca].corr(y[no_ca])
    verdict = "PASS" if r_all > 0.3 and r_noca > 0.3 else "FAIL"
    print(f"\nP4 (pre-registered) Pearson r, n=51: {r_all:.3f}; without CA, n=50: {r_noca:.3f} => {verdict}")
    print("Extras (not pre-registered):")
    print(f"  Spearman r: {x.corr(y, method='spearman'):.3f}; without CA: {x[no_ca].corr(y[no_ca], method='spearman'):.3f}")
    xo = s.overall_rate_change
    print(f"  Pearson r, total homeless: {xo.corr(y):.3f}; without CA: {xo[no_ca].corr(y[no_ca]):.3f}")
    print(s[["unsheltered_rate_change", "ped_rate_change"]].sort_values("unsheltered_rate_change").round(2).to_string())
    scatter(s, base_year, r_all, r_noca)


def scatter(s: pd.DataFrame, base_year: int, r_all: float, r_noca: float) -> None:
    import matplotlib.pyplot as plt
    from chart_explore import INK, MUTED, RULE, SURFACE, style

    fig, ax = plt.subplots(figsize=(9, 7), facecolor=SURFACE)
    style(ax)
    ax.grid(color=RULE)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.axvline(0, color=MUTED, linewidth=0.8)
    ax.scatter(s.unsheltered_rate_change, s.ped_rate_change, s=22, color="#2a78d6", zorder=3)
    for st, (xv, yv) in s[["unsheltered_rate_change", "ped_rate_change"]].iterrows():
        ax.annotate(st, (xv, yv), xytext=(3, 2), textcoords="offset points", fontsize=7, color=INK)
    ax.set_xlabel(f"Change in unsheltered homeless per 100,000, {base_year} to 2022", color=MUTED)
    ax.set_ylabel("Change in pedestrian deaths per 100,000, 2009-11 to 2020-22", color=MUTED)
    ax.set_title(f"States: unsheltered homelessness vs. pedestrian deaths (Pearson r = {r_all:.2f}; "
                 f"{r_noca:.2f} without CA)", loc="left", color=INK, fontsize=10)
    fig.text(0.01, 0.005, "Sources: HUD Point-in-Time estimates by state; NHTSA FARS; Census via FRED. "
             "Test P4, pre-registered in docs/hypothesis-test.md.", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(ROOT / "charts" / "test_homeless_scatter.png", dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    main()
