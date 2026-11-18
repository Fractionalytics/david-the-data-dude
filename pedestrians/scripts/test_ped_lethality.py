"""Pre-registered test P24 (docs/hypothesis-test.md, 2026-11-15): did getting hit become deadlier, or were more
pedestrians hit?

    python scripts/test_ped_lethality.py
      reads  data/raw/ges_crss/GES<2009-2015>.zip, CRSS<2016-2024>.zip (scripts/fetch_ges_crss.py)
             FARS via fars_pedestrians.year_peds (deaths, light condition)
      writes data/final/test_ped_lethality.csv   one row per year
             data/final/test_ped_lethality.txt   scored results and unscored checks

H (hit) = police-reported pedestrians injured (GES/CRSS PER_TYP 5, INJ_SEV 1-3, weighted) + FARS deaths.
L = deaths / H. Lethality share = log(L2/L1) / log(D2/D1). Segments never cross the 2016 GES -> CRSS break.
Sampling error: Taylor linearization of weighted totals, strata x PSUs (GES 2009-10 have no variance strata,
so PSUs are treated as one stratum); yearly variances added for 3-year sums; share interval by simulation.
"""
import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fars_pedestrians import FINAL, year_peds  # noqa: E402

RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "ges_crss"
YEARS = range(2009, 2025)
SEGMENTS = {"P24a (GES)": ([2009, 2010, 2011], [2013, 2014, 2015]),
            "P24b (CRSS)": ([2016, 2017, 2018], [2022, 2023, 2024])}
DARK = {2, 3, 6}  # dark not lighted, dark lighted, dark unknown lighting


def read(z: zipfile.ZipFile, key: str) -> pd.DataFrame:
    name = [n for n in z.namelist() if n.lower().split("/")[-1].startswith(key)][0]
    raw = z.read(name)
    sep = "\t" if b"\t" in raw[:2000] else ","
    return pd.read_csv(io.BytesIO(raw), sep=sep, encoding="latin1", low_memory=False)


def year_sample(y: int) -> pd.DataFrame:
    z = zipfile.ZipFile(RAW / f"{'GES' if y < 2016 else 'CRSS'}{y}.zip")
    p = read(z, "person.")
    a = read(z, "accident.")
    im = "INJSEV_H" if "INJSEV_H" in p else "INJSEV_IM"
    strat = "PSUSTRAT" if "PSUSTRAT" in p else None
    clus = "PSU_VAR" if "PSU_VAR" in p else "PSU"
    lgt = "LGTCON_IM" if "LGTCON_IM" in a else ("LGTCON_I" if "LGTCON_I" in a else "LGT_COND")
    p = p.merge(a[["CASENUM", lgt]].rename(columns={lgt: "light"}), on="CASENUM", how="left")
    out = pd.DataFrame({
        "strat": p[strat] if strat else 0, "clus": p[clus], "w": p.WEIGHT,
        "ped": p.PER_TYP == 5, "sev": p.INJ_SEV, "sev_im": p[im], "dark": p.light.isin(DARK),
    })
    out["year"] = y
    return out


def total_and_var(s: pd.DataFrame, mask: pd.Series) -> tuple[float, float]:
    """Weighted total of persons in mask, with stratified-cluster (with-replacement) variance."""
    y = (s.w * mask).groupby([s.strat, s.clus]).sum()
    var = 0.0
    for _, g in y.groupby(level=0):
        n = len(g)
        if n > 1:
            var += n / (n - 1) * ((g - g.mean()) ** 2).sum()
    return float(y.sum()), var


def main() -> None:
    rows = []
    for y in YEARS:
        s = year_sample(y)
        peds, _ = year_peds(y)
        r = {"year": y, "deaths": len(peds), "deaths_dark": int(peds.dark.sum())}
        masks = {
            "inj": s.ped & s.sev.isin([1, 2, 3]),                # scored, as pre-registered
            "inj_im": s.ped & s.sev_im.isin([1, 2, 3]),          # NHTSA's imputed severity
            "inj_unk": s.ped & (s.sev == 5),                     # injured, severity unknown (not in H)
            "serious": s.ped & (s.sev == 3),
            "inj_dark": s.ped & s.sev.isin([1, 2, 3]) & s.dark,
        }
        for k, m in masks.items():
            r[k], r[k + "_var"] = total_and_var(s, m)
        rows.append(r)
        print(y, f"deaths {r['deaths']}, injured {r['inj']:,.0f} (se {r['inj_var'] ** 0.5:,.0f})", flush=True)
    t = pd.DataFrame(rows)
    t["hit"] = t.inj + t.deaths
    t["L"] = t.deaths / t.hit
    t["L_serious"] = t.deaths / (t.serious + t.deaths)
    t["L_im"] = t.deaths / (t.inj_im + t.deaths)
    t["L_dark"] = t.deaths_dark / (t.inj_dark + t.deaths_dark)
    t.to_csv(FINAL / "test_ped_lethality.csv", index=False)

    rng = np.random.default_rng(24)
    lines = []

    def split(e, l, inj="inj", dcol="deaths"):
        E, Lt = t[t.year.isin(e)], t[t.year.isin(l)]
        d1, d2 = E[dcol].sum(), Lt[dcol].sum()
        i1, i2 = E[inj].sum(), Lt[inj].sum()
        v1, v2 = E[inj + "_var"].sum(), Lt[inj + "_var"].sum()
        h1, h2 = i1 + d1, i2 + d2
        share = 1 - np.log(h2 / h1) / np.log(d2 / d1)
        sim_i1 = rng.normal(i1, v1 ** 0.5, 20000)
        sim_i2 = rng.normal(i2, v2 ** 0.5, 20000)
        sim = 1 - np.log((sim_i2 + d2) / (sim_i1 + d1)) / np.log(d2 / d1)
        lo, hi = np.percentile(sim, [2.5, 97.5])
        dh = np.log(h2 / h1)
        dh_se = ((v1 + v2) ** 0.5) / ((h1 + h2) / 2)  # approx se of log ratio
        return dict(d1=d1, d2=d2, i1=i1, i2=i2, h1=h1, h2=h2, L1=d1 / h1, L2=d2 / h2, share=share, lo=lo, hi=hi,
                    dh=dh, dh_lo=dh - 1.96 * dh_se, dh_hi=dh + 1.96 * dh_se, se1=v1 ** 0.5, se2=v2 ** 0.5)

    def verdict(r):
        if r["dh_lo"] <= 0 <= r["dh_hi"]:
            return "INCONCLUSIVE (change in H within sampling error)"
        if r["share"] <= 1 / 3:
            return "MOSTLY MORE PEOPLE HIT (supports exposure)"
        if r["share"] >= 0.5:
            return "MOSTLY DEADLIER WHEN HIT (cuts against exposure)"
        return "MIXED"

    for seg, (e, l) in SEGMENTS.items():
        r = split(e, l)
        lines.append(
            f"{seg} {e[0]}-{e[-1]} -> {l[0]}-{l[-1]}: deaths {r['d1']:,} -> {r['d2']:,} "
            f"({r['d2'] / r['d1'] - 1:+.1%}); injured {r['i1']:,.0f} (se {r['se1']:,.0f}) -> {r['i2']:,.0f} "
            f"(se {r['se2']:,.0f}); hit {r['h2'] / r['h1'] - 1:+.1%} (95% CI on log ratio {r['dh_lo']:+.3f} to "
            f"{r['dh_hi']:+.3f}); L {r['L1']:.2%} -> {r['L2']:.2%}; lethality share {r['share']:.0%} "
            f"(95% {r['lo']:.0%} to {r['hi']:.0%}) => {verdict(r)}")
    lines.append("\n-- unscored --")
    for lab, inj, dcol in (("1. serious only", "serious", "deaths"), ("   imputed severity", "inj_im", "deaths"),
                           ("2. dark only", "inj_dark", "deaths_dark")):
        for seg, (e, l) in SEGMENTS.items():
            r = split(e, l, inj, dcol)
            lines.append(f"{lab} {seg}: L {r['L1']:.2%} -> {r['L2']:.2%}; lethality share {r['share']:.0%} "
                         f"(95% {r['lo']:.0%} to {r['hi']:.0%})")
    for seg, (e, l) in SEGMENTS.items():
        E, Lt = t[t.year.isin(e)], t[t.year.isin(l)]
        lines.append(f"2b. dark share of deaths {seg}: {E.deaths_dark.sum() / E.deaths.sum():.1%} -> "
                     f"{Lt.deaths_dark.sum() / Lt.deaths.sum():.1%}; of injured "
                     f"{E.inj_dark.sum() / E.inj.sum():.1%} -> {Lt.inj_dark.sum() / Lt.inj.sum():.1%}")
    lines.append("3. by year: year deaths injured(se) hit L L_serious injured-unknown-severity")
    for _, r in t.iterrows():
        lines.append(f"   {int(r.year)} {int(r.deaths):,} {r.inj:,.0f} ({r.inj_var ** 0.5:,.0f}) {r.hit:,.0f} "
                     f"{r.L:.2%} {r.L_serious:.1%} {r.inj_unk:,.0f}")
    (FINAL / "test_ped_lethality.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
