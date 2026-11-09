"""Pre-registered test P10, primary branch (docs/hypothesis-test.md, round 3):
change in state psychostimulant (T43.6, mostly methamphetamine) overdose death
rates vs. change in pedestrian death rates, 2009-11 vs. 2020-22, from CDC WONDER.

    python scripts/test_meth_wonder.py          age-adjusted rates (the planned measure)
    python scripts/test_meth_wonder.py crude    crude rates (the first run, before the age-adjusted export)
      reads  data/raw/cdc_wonder/wonder_t436_2009_2011.csv         (Multiple Cause of Death, 1999-2020)
             data/raw/cdc_wonder/wonder_t436_2020_2022_ageadj.csv  (Multiple Cause of Death, 2018-2024,
                                                                    Single Race; crude and age-adjusted)
             data/final/test_homeless.csv                          (pedestrian deaths per 100k, from FARS)
      writes data/final/test_meth_wonder[_crude].csv
             charts/test_meth_wonder_scatter[_crude].png

Both exports: MCD T43.6 with underlying cause X40-X44, X60-X64, X85, Y10-Y14,
grouped by state, three years pooled, exported by David from the WONDER web
site (its API won't return state data). Rates are the three-year pooled rate per
100,000. States marked Suppressed (<10 deaths) or Unreliable (<20) in either
period are left out, as the rule says.

The first 2020-22 export (wonder_t436_2020_2022.csv) had crude rates only, so
P10 was first run on crude rates; David re-exported 2020-22 with age-adjusted
rates (wonder_t436_2020_2022_ageadj.csv, same query), which is the planned
measure and the default here.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))  # run with python -I, which drops the script's folder
from fars_decompose import FIPS  # noqa: E402
from fars_pedestrians import FINAL, ROOT  # noqa: E402

RAW = ROOT / "data" / "raw" / "cdc_wonder"
FILES = {"2009_11": RAW / "wonder_t436_2009_2011.csv", "2020_22": RAW / "wonder_t436_2020_2022_ageadj.csv"}
CRUDE = len(sys.argv) > 1 and sys.argv[1] == "crude"
RATE, SUFFIX, LABEL = ("Crude Rate", "_crude", "crude") if CRUDE else ("Age Adjusted Rate", "", "age-adjusted")


def read(path: Path, tag: str) -> pd.DataFrame:
    d = pd.read_csv(path, dtype=str)
    d = d[d["State Code"].notna() & d["Notes"].isna()]
    d["state"] = d["State Code"].astype(int).map(FIPS)
    flag = ~d[RATE].str.replace(".", "", regex=False).str.isdigit()
    out = pd.DataFrame({"state": d.state, f"meth_deaths_{tag}": d.Deaths, f"meth_rate_{tag}": d[RATE],
                        f"flag_{tag}": d[RATE].where(flag, "")})
    out[f"meth_rate_{tag}"] = pd.to_numeric(out[f"meth_rate_{tag}"], errors="coerce")
    return out.set_index("state")


def main() -> None:
    s = read(FILES["2009_11"], "2009_11").join(read(FILES["2020_22"], "2020_22"), how="outer")
    assert len(s) == 51, len(s)
    ped = pd.read_csv(FINAL / "test_homeless.csv").set_index("state")[["ped_rate_2009_11", "ped_rate_2020_22", "ped_rate_change"]]
    s = s.join(ped)
    s["included"] = s.meth_rate_2009_11.notna() & s.meth_rate_2020_22.notna()
    s["excluded_reason"] = (s.flag_2009_11.fillna("") + " " + s.flag_2020_22.fillna("")).str.strip().where(~s.included, "")
    s["meth_rate_change"] = s.meth_rate_2020_22 - s.meth_rate_2009_11
    s.round(4).rename_axis("state").reset_index().to_csv(FINAL / f"test_meth_wonder{SUFFIX}.csv", index=False)

    i = s[s.included]
    x, y = i.meth_rate_change, i.ped_rate_change
    top = x.idxmax()
    keep = i.index != top
    r_all, r_top = x.corr(y), x[keep].corr(y[keep])
    verdict = "PASS" if r_all > 0.3 and r_top > 0.3 else "FAIL"
    print(f"Included {len(i)}; excluded {(~s.included).sum()}: "
          + ", ".join(f"{k} ({v})" for k, v in s.loc[~s.included, 'excluded_reason'].items()))
    print(f"P10 primary branch ({LABEL} rates): Pearson r, n={len(i)}: {r_all:.3f}; "
          f"without {top} (largest rise, +{x.max():.1f}), n={keep.sum()}: {r_top:.3f} => {verdict}")
    print("Not pre-registered:")
    print(f"  Spearman r: {x.corr(y, method='spearman'):.3f}; without {top}: {x[keep].corr(y[keep], method='spearman'):.3f}")
    nowv = i.index != "WV"
    print(f"  Pearson r without WV: {x[nowv].corr(y[nowv]):.3f}")
    print(i[["meth_rate_2009_11", "meth_rate_2020_22", "meth_rate_change", "ped_rate_change"]]
          .sort_values("meth_rate_change").round(2).to_string())
    scatter(i, r_all, r_top, top)


def scatter(s: pd.DataFrame, r_all: float, r_top: float, top: str) -> None:
    import matplotlib.pyplot as plt
    from chart_explore import INK, MUTED, RULE, SURFACE, style

    fig, ax = plt.subplots(figsize=(9, 7), facecolor=SURFACE)
    style(ax)
    ax.grid(color=RULE)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.scatter(s.meth_rate_change, s.ped_rate_change, s=22, color="#2a78d6", zorder=3)
    for st, (xv, yv) in s[["meth_rate_change", "ped_rate_change"]].iterrows():
        ax.annotate(st, (xv, yv), xytext=(3, 2), textcoords="offset points", fontsize=7, color=INK)
    ax.set_xlabel("Change in psychostimulant (mostly meth) overdose deaths per 100,000, 2009-11 to 2020-22", color=MUTED)
    ax.set_ylabel("Change in pedestrian deaths per 100,000, 2009-11 to 2020-22", color=MUTED)
    ax.set_title(f"States: methamphetamine overdoses vs. pedestrian deaths (r = {r_all:.2f}; "
                 f"{r_top:.2f} without {top})", loc="left", color=INK, fontsize=10)
    fig.text(0.01, 0.005, f"Sources: CDC WONDER Multiple Cause of Death (T43.6, {LABEL} rates; {len(s)} states with "
             "reliable counts in both periods); NHTSA FARS; Census via FRED. Test P10, docs/hypothesis-test.md.",
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(ROOT / "charts" / f"test_meth_wonder_scatter{SUFFIX}.png", dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    main()
