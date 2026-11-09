# Pedestrians: why did US pedestrian deaths rise while Europe's fell?

Around 2009, US pedestrian deaths started rising while Europe's kept falling. This folder tests the usual explanations (smartphones, SUVs, street design) and the one that held up best: methamphetamine.

This folder is the behind-the-scenes companion to David the Data Dude's Instagram Reel.

<p align="center">
  <a href="https://www.instagram.com/reel/DfiKS-Gyysa/"><img src="cover.jpg" alt="Reel cover: Pedestrians" width="300"></a>
  <br>
  <b>▶ <a href="https://www.instagram.com/reel/DfiKS-Gyysa/">Watch the Reel on Instagram</a></b>
</p>

## The result

**US vs. Europe** (pedestrian deaths per 100,000 people)

| | 2000 | 2009 | 2024 |
|---|---|---|---|
| US | 1.72 | 1.37 | 2.16 |
| Europe (18 EU members) | 2.29 | 1.40 | 0.75 |

In 2009 the two were about even. By 2024 the US rate was 2.9 times Europe's.

**Where the US rise happened** (share of the increase from 4,109 deaths in 2009 to 7,593 in 2022)

| | Share of the increase |
|---|---|
| Urban or suburban | 99% (rural deaths: 1,146 in both years) |
| After dark (6pm–6am) | 84% |
| Mid-block, not at an intersection | 84% |
| On arterial roads | 71% |
| Adults 25–64 | 75% |
| Men | 72% |
| South and West (62% of the population) | 84% |

The pedestrian death rate rose 83% in the poorest fifth of neighborhoods and 50% in the richest fifth (2009–11 to 2020–22).

**The usual suspects**
- **Smartphones and SUVs:** Europe got both. SUVs went from 7% of new EU cars in 2009 to 49% in 2024, and Europe's pedestrian deaths kept falling.
- **Taller hoods:** about 10% of the US rise, per the New York Times' own model (Keller, June 21, 2026).
- **Vision Zero:** of 18 US cities that pledged early (2012–2016), only New York had a statistically significant drop in pedestrian deaths (Ferenchak, 2023).

**Methamphetamine**
- Among pedestrians killed and tested for drugs, the share positive for a stimulant held at 9–11% from 2007 to 2014, then rose to 31% by 2024. In the four states that tested at least 70% of pedestrians killed every year (Maryland, New Jersey, Washington, West Virginia), it rose from about 8% to about 21%, so the rise isn't a change in who gets tested.
- States with bigger rises in meth overdose deaths had bigger rises in pedestrian deaths (2009–11 to 2020–22): r = 0.35 across 38 states, 0.65 without West Virginia. The Reel's scatterplot leaves West Virginia out; both checks were set in advance.
- When meth overdose deaths fell (35,982 in 2023 → 26,260 in 2025, CDC provisional), pedestrian deaths fell too, but so did other road deaths.
- A positive test shows a drug was present, not that the person was impaired. On the Bradford Hill criteria, the evidence meets temporality, biological gradient, plausibility and consistency, half-meets experiment, and doesn't show strength, specificity, coherence or analogy. That builds a case, not proof.

## Definitions

- **Pedestrian death:** NHTSA FARS person type 5 (pedestrian), injury severity 4 (fatal). For the US vs. Europe comparison, people on personal conveyances (skateboards, scooters and similar) are added, to match how Europe counts pedestrians.
- **Europe:** the 18 EU members that reported pedestrian deaths to Eurostat every year from 2000 to 2024, so every year compares the same countries.
- **Stimulant-positive:** at least one drug result of methamphetamine, amphetamine or cocaine among pedestrians killed with a valid drug test. FARS changed its drug codes in 2022; the named drugs were matched across both schemes.
- **Meth overdose deaths:** death certificates listing psychostimulants with abuse potential (ICD-10 T43.6), mostly methamphetamine.
- **Neighborhood poverty:** 2010 census tracts, ranked by share of residents below the poverty line (ACS 2008–12), in fifths of the population; crashes are placed in tracts by their coordinates.
- **Pre-registered tests:** each test's prediction and pass/fail rule was written down and committed before it was run (`docs/hypothesis-test.md`), and every result is reported against its rule, passes and failures alike.

## Files

- `data/`: the final datasets behind every number and chart in the Reel.
- `scripts/`: the pipeline. `fetch_fars.py`, `fetch_eurostat.py` and `fetch_fred.py` download the public source files, which aren't republished here. CDC WONDER and HUD files were downloaded by hand from their sites; `requirements.txt` lists the Python packages.
- `docs/hypothesis-test.md`: every pre-registered test, its rule and its result.
- `docs/bradford-hill.md`: how the evidence scores on each of Hill's nine viewpoints, and why.
- `docs/data-challenges.md`: what went sideways, from drug codes that changed four years after a file "overhaul" to two official numbers for the same country's deaths.
- `video/`: the Remotion source for the Reel's animated charts. It imports layout and fonts from a shared kit that isn't published here.

## Sources

- NHTSA, [Fatality Analysis Reporting System (FARS)](https://www.nhtsa.gov/research-data/fatality-analysis-reporting-system-fars), 2000–2024; [Early Estimate of Motor Vehicle Traffic Fatalities in 2025](https://crashstats.nhtsa.dot.gov/Api/Public/ViewPublication/813800) (DOT HS 813 800).
- Eurostat, road fatalities by category of person (`tran_sf_roadus`).
- ICCT, European Vehicle Market Statistics Pocketbook 2025/26 (EU SUV share); BEA via FRED (US light-truck share).
- CDC WONDER, Multiple Cause of Death (T43.6, age-adjusted, by state); CDC/NCHS Provisional Drug Overdose Death Counts (data.cdc.gov `xkb8-kh2a`).
- Census Bureau, American Community Survey 2008–12 and TIGER/Line 2010 tracts.
- GHSA, Pedestrian Traffic Fatalities by State: 2025 Data (projection).
- Keller, M. H., "The Deadly Rise of Giant Trucks and S.U.V.s," *The New York Times*, June 21, 2026.
- Ferenchak, N. (2023), "U.S. Vision Zero Cities: modal fatality trends and strategy effectiveness," *Transportation Letters* 15(8), 957–968.
- Hill, A. B. (1965), "The Environment and Disease: Association or Causation?" *Proceedings of the Royal Society of Medicine* 58(5), 295–300.

Made by [Fractionalytics](https://github.com/Fractionalytics).

## License

Code, docs and charts are under the repo's [MIT License](../LICENSE). FARS, Census, CDC and BEA data are U.S. government works. Eurostat data is reused under Eurostat's reuse policy, with attribution. EU SUV shares are read from ICCT's pocketbook and belong to ICCT. The New York Times, GHSA and the cited papers are quoted and cited, not republished.
