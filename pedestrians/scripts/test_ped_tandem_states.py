"""P25 (docs/hypothesis-test.md): meth and deadly roads in tandem, across states, 2018-2024 pooled.

    python scripts/test_ped_tandem_states.py
      reads  FARS (via fars_pedestrians.load) and data/raw/cdc_wonder/wonder_meth_state_year_2018_2024.csv,
             wonder_fent_and_meth_state_2024.csv
      writes data/final/test_ped_tandem_states.csv (one row per state) and data/final/test_ped_tandem_groups.csv

M = meth (T43.6) overdose deaths per 100,000; R = estimated no-stimulant pedestrians killed per million a year;
Y = estimated meth-positive pedestrians killed per million a year (all killed x share of tested). Scored exactly
as pre-registered; extras are reported, not scored.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ped_drugs import FINAL, INVALID, KEY, load, results  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
WONDER = ROOT / "data" / "raw" / "cdc_wonder"
YEARS = range(2018, 2025)
METH3, METH4 = {400, 401, 408, 417}, {3019, 3053}
COKE3, COKE4 = {402, 407, 410, 430}, {3022, 3032, 3033, 3039, 3080, 3081, 3082}


def fars_by_state() -> pd.DataFrame:
    rows = []
    for y in YEARS:
        peds, r, _ = results(y)
        peds = peds.assign(state=peds.ST_CASE // 10000)
        r = r.assign(code=r.code.astype(int))
        v = r[~r.code.isin(INVALID)]
        new = y >= 2022
        v = v.assign(meth=v.code.isin(METH4 if new else METH3), coke=v.code.isin(COKE4 if new else COKE3))
        per = v.groupby(KEY)[["meth", "coke"]].any().reset_index().merge(peds, on=KEY)
        per["stim"] = per.meth | per.coke
        p = load(y, "person", KEY + ["PER_TYP", "INJ_SEV"])
        occ = p[(p.PER_TYP.isin([1, 2])) & (p.INJ_SEV == 4)].assign(state=lambda d: d.ST_CASE // 10000)
        g = pd.DataFrame({
            "killed": peds.groupby("state").size(),
            "tested": per.groupby("state").size(),
            "meth_pos": per.groupby("state").meth.sum(),
            "no_stim": (~per.stim).groupby(per.state).sum(),
            "occ_killed": occ.groupby("state").size(),
        }).fillna(0)
        rows.append(g.assign(year=y))
    return pd.concat(rows).groupby(level=0).sum().drop(columns="year")


def main() -> None:
    w = pd.read_csv(WONDER / "wonder_meth_state_year_2018_2024.csv", dtype={"State Code": str})
    w = w[w.State.notna() & w["Year Code"].notna()]
    w["Year Code"] = w["Year Code"].astype(float).astype(int)
    w = w[w["Year Code"].isin(YEARS)]
    suppressed = w[w.Deaths.astype(str) == "Suppressed"][["State", "Year Code"]]
    w["deaths"] = pd.to_numeric(w.Deaths, errors="coerce").fillna(0)
    w["pop"] = pd.to_numeric(w.Population, errors="coerce")
    s = w.groupby(["State Code", "State"]).agg(meth_od=("deaths", "sum"), pop_years=("pop", "sum")).reset_index()
    s["fips"] = s["State Code"].astype(int)
    f = fars_by_state()
    d = s.merge(f, left_on="fips", right_index=True, how="left").fillna({"killed": 0, "tested": 0})
    d["M"] = d.meth_od / d.pop_years * 1e5
    d["test_rate"] = d.tested / d.killed
    d["R"] = d.killed * (d.no_stim / d.tested) / d.pop_years * 1e6
    d["Y"] = d.killed * (d.meth_pos / d.tested) / d.pop_years * 1e6
    d["Y_floor"] = d.meth_pos / d.pop_years * 1e6
    d["occ"] = d.occ_killed / d.pop_years * 1e6
    dropped = d[d.tested < 30]
    d = d[d.tested >= 30].copy()

    def groups(df: pd.DataFrame, rcol: str, ycol: str, mcol: str = "M") -> pd.DataFrame:
        df = df.assign(hiM=df[mcol] > df[mcol].median(), hiR=df[rcol] > df[rcol].median())
        num = (df[ycol] * df.pop_years)
        g = df.assign(num=num).groupby(["hiM", "hiR"]).agg(num=("num", "sum"), pop=("pop_years", "sum"), n=("State", "size"),
                                                          states=("State", lambda x: ", ".join(sorted(x))))
        g["Y"] = g.num / g["pop"]
        return g.drop(columns="num")

    def score(g: pd.DataFrame) -> tuple[bool, float]:
        hh, hl, lh, ll = (g.loc[(True, True), "Y"], g.loc[(True, False), "Y"], g.loc[(False, True), "Y"], g.loc[(False, False), "Y"])
        ratio = hh / max(hl, lh)
        return bool(ratio >= 1.5 and hl > ll and lh > ll), ratio

    g = groups(d, "R", "Y")
    a_pass, a_ratio = score(g)

    # P25b: weighted log-log regression, Y ~ M + R (states with Y, M, R > 0)
    import statsmodels.api as sm
    r = d[(d.Y > 0) & (d.M > 0) & (d.R > 0)]
    X = sm.add_constant(np.log(r[["M", "R"]]))
    fit = sm.WLS(np.log(r.Y), X, weights=r.pop_years).fit()
    ci = fit.conf_int()
    b_pass = bool(ci.loc["M", 0] > 0 and ci.loc["R", 0] > 0)

    out = []
    out.append(f"States kept: {len(d)}; dropped (<30 tested): {', '.join(dropped.State) or 'none'}")
    out.append(f"Suppressed meth state-years counted as 0: {len(suppressed)} ({', '.join(sorted(set(suppressed.State)))})")
    out.append(f"Medians: M {d.M.median():.2f} per 100k, R {d.R.median():.2f} per million")
    out.append("\nP25a groups (Y = est. meth-positive pedestrians killed per million a year):")
    out.append(g[["n", "Y"]].round(2).to_string())
    out.append(f"P25a: high/high = {g.loc[(True, True), 'Y']:.2f}, {a_ratio:.2f}x the larger one-factor group -> {'PASS' if a_pass else 'FAIL'}")
    out.append(f"\nP25b: log Y = {fit.params['const']:.2f} + {fit.params['M']:.2f} log M + {fit.params['R']:.2f} log R "
               f"(M 95% CI {ci.loc['M', 0]:.2f} to {ci.loc['M', 1]:.2f}; R {ci.loc['R', 0]:.2f} to {ci.loc['R', 1]:.2f}; "
               f"n={len(r)}, R2={fit.rsquared:.2f}) -> {'PASS' if b_pass else 'FAIL'}")

    out.append("\nReported, not scored:")
    gf = groups(d, "R", "Y_floor")
    out.append(f"1. Floor (tested and meth-positive only): groups\n{gf[['n', 'Y']].round(2).to_string()}\n   ratio {score(gf)[1]:.2f}x -> would be {'PASS' if score(gf)[0] else 'FAIL'}")
    out.append(f"   Testing rate by state: median {d.test_rate.median():.0%}, range {d.test_rate.min():.0%}-{d.test_rate.max():.0%}")
    go = groups(d, "occ", "Y")
    out.append(f"2. Roads = vehicle occupants killed per million: groups\n{go[['n', 'Y']].round(2).to_string()}\n   ratio {score(go)[1]:.2f}x -> would be {'PASS' if score(go)[0] else 'FAIL'}")
    fm = pd.read_csv(WONDER / "wonder_fent_and_meth_state_2024.csv", dtype={"State Code": str})
    fm = fm[fm.State.notna()]
    fm["fm"] = pd.to_numeric(fm.Deaths, errors="coerce").fillna(0)
    m24 = w[w["Year Code"] == 2024][["State Code", "deaths", "pop"]]
    x = m24.merge(fm[["State Code", "fm"]], on="State Code")
    x["M_nofent"] = (x.deaths - x.fm).clip(lower=0) / x["pop"] * 1e5
    d2 = d.merge(x[["State Code", "M_nofent"]], on="State Code")
    gn = groups(d2, "R", "Y", "M_nofent")
    out.append(f"3. M = 2024 meth overdoses without fentanyl: groups\n{gn[['n', 'Y']].round(2).to_string()}\n   ratio {score(gn)[1]:.2f}x -> would be {'PASS' if score(gn)[0] else 'FAIL'}")
    out.append("4. Group members (P25a):")
    for k, row in g.iterrows():
        out.append(f"   high M={k[0]}, high R={k[1]}: {row.states}")
    text = "\n".join(out)
    print(text)
    (FINAL / "test_ped_tandem_states.txt").write_text(text, encoding="utf-8")
    d.drop(columns=["State Code"]).round(4).to_csv(FINAL / "test_ped_tandem_states.csv", index=False)
    g.reset_index().round(4).to_csv(FINAL / "test_ped_tandem_groups.csv", index=False)


if __name__ == "__main__":
    main()
