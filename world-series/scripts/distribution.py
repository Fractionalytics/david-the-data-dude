"""Surname-type distribution for all 2026 players, by region and by country (birth country).

Input: data/processed/players_final.csv (build_rosters.py). Counts players, not unique surnames
(both are printed overall). Countries with fewer than 20 players are shown only within regions.

Regions (birth country): USA/Canada; Latin America & Caribbean (incl. Puerto Rico, Aruba,
Curacao, Bahamas); Asia (Japan, Korea, Taiwan); Europe; Oceania (Australia).

Outputs: data/processed/distribution.csv (long: group_kind, group, type, n, share) and
counts.csv (group_kind, group, type, known, jev_only, total). "known" means the type rests on a
source (Wiktionary or web research) or a hand decision; "jev_only" is Jev's answer with no source.
"""
from pathlib import Path

import pandas as pd
from scipy.stats import fisher_exact

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
REGION = {
    "USA": "USA/Canada", "Canada": "USA/Canada",
    "Japan": "Asia", "Republic of Korea": "Asia", "Taiwan": "Asia",
    "Germany": "Europe", "Italy": "Europe", "United Kingdom": "Europe", "Slovakia": "Europe",
    "Australia": "Oceania",
}
# Patronymic includes merged Matronymic (build_rosters.py).
ORDER = ["Patronymic", "Cognominal", "Ornamental/artificial", "Acquired/assigned",
         "Occupational", "Toponymic", "Patronage", "Compound", "Other"]


def shares(df, kind, col):
    t = df.groupby([col, "surname_type"]).size().unstack(fill_value=0).reindex(columns=ORDER, fill_value=0)
    long = t.stack().rename("n").reset_index().rename(columns={col: "group", "surname_type": "type"})
    long["share"] = long.n / long.groupby("group").n.transform("sum")
    long.insert(0, "group_kind", kind)
    return t, long


def main():
    p = pd.read_csv(DATA / "players_final.csv")
    p["region"] = p.birth_country.map(REGION).fillna("Latin America & Caribbean")
    p["all"] = "All players"

    out = []
    for kind, col in [("all", "all"), ("region", "region"), ("country", "birth_country")]:
        sub = p if kind != "country" else p[p.birth_country.map(p.birth_country.value_counts()) >= 20]
        t, long = shares(sub, kind, col)
        out.append(long)
        pct = (t.div(t.sum(axis=1), axis=0) * 100).round(0).astype(int)
        pct.insert(0, "n", t.sum(axis=1))
        print(f"\n== {kind} (% of players) ==\n{pct.to_string()}")
    pd.concat(out).to_csv(DATA / "distribution.csv", index=False)

    # Player counts, split by how the type is known ("known" = a source or a hand decision).
    p["known"] = p.evidence.isin(["source", "hand"])
    rows = []
    for kind, col in [("all", "all"), ("region", "region"), ("country", "birth_country")]:
        for known, label in [(True, "known"), (False, "jev_only")]:
            t = p[p.known == known].groupby([col, "surname_type"]).size().unstack(fill_value=0)
            t = t.reindex(columns=ORDER, fill_value=0).reindex(p[col].unique(), fill_value=0)
            rows.append(t.stack().rename(label).reset_index().rename(columns={col: "group", "surname_type": "type"})
                        .assign(group_kind=kind).set_index(["group_kind", "group", "type"]))
        both = pd.concat(rows[-2:], axis=1)
        known_t = both.known.unstack().reindex(columns=ORDER)
        known_t.insert(0, "known", known_t.sum(axis=1))
        known_t.insert(1, "all", both.sum(axis=1).unstack().sum(axis=1))
        print(f"\n== {kind}: players with a known type (source or hand decision) ==\n"
              f"{known_t.droplevel(0).sort_values('all', ascending=False).to_string()}")
    c = pd.concat(rows[i] for i in range(0, len(rows), 2))
    c = c.join(pd.concat(rows[i] for i in range(1, len(rows), 2)))
    c["total"] = c.known + c.jev_only
    c.reset_index().to_csv(DATA / "counts.csv", index=False)

    u = p.drop_duplicates(["surname", "birth_country"]).surname_type.value_counts(normalize=True).mul(100).round(0)
    print(f"\nunique (surname, country) pairs, %:\n{u.to_string()}")

    a = p[p.region == "Latin America & Caribbean"]
    b = p[p.region == "USA/Canada"]
    tab = [[(a.surname_type == "Patronymic").sum(), (a.surname_type != "Patronymic").sum()],
           [(b.surname_type == "Patronymic").sum(), (b.surname_type != "Patronymic").sum()]]
    odds, pval = fisher_exact(tab)
    print(f"\nPatronymic, Latin America {tab[0][0]}/{len(a)} vs USA/Canada {tab[1][0]}/{len(b)}: "
          f"odds ratio {odds:.2f}, Fisher p = {pval:.2g}")


if __name__ == "__main__":
    main()
