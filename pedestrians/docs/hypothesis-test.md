# Testing the leading hypothesis (pre-registered 2026-11-05, before any test was run)

**Hypothesis** (from `docs/why-us-rose.md`): much of the post-2009 rise in US pedestrian deaths is people who walk along wide suburban roads at night because they have no car (shift workers, transit riders, unhoused people), meeting more distracted drivers in taller vehicles on roads designed for speed.

The vehicle and road-speed parts are already measured (`docs/why-us-rose.md`). These tests cover the parts that aren't. Written and committed **before** running any of them; results go in a section below, scored against these rules without changing them.

**Common setup.** Compare 2009–2011 (average per year) with 2020–2022 (average per year), FARS pedestrian deaths (PER_TYP 5, INJ_SEV 4), each geolocated to the census tract of the crash from FARS latitude/longitude. Tract characteristics come from the **pre-period** (ACS 2008–2012 five-year estimates on 2010 tract boundaries), so the outcome can't shape the grouping. Quintiles are population-weighted (each holds about a fifth of the 2010 population). Rates are deaths per 100,000 residents of the tracts in each group (2010 population). Crashes with missing or invalid coordinates are reported and excluded.

## P1. Low income

- **Prediction:** the highest-poverty quintile of tracts (share of people below the poverty line) accounts for a larger share of the added deaths than of the 2009–11 deaths, and its death rate grows by a larger percentage than the lowest-poverty quintile's.
- **Pass:** both conditions hold. **Fail:** the top quintile's rate grows by the same or a smaller percentage than the bottom quintile's.

## P2. Suburban, not downtown

- **Prediction:** tracts of middle population density (quintiles 2–4) account for more than half of the added deaths, and their rate grows by a larger percentage than the densest quintile's.
- **Pass:** both hold. **Fail:** the densest quintile's rate grows by the same or a larger percentage.

## P3. No car

- **Prediction:** tracts in the top quintile for households with no vehicle grow faster than the bottom quintile, **within** middle-density tracts (to separate "no car" from "big-city downtown", where most car-free households are).
- **Pass:** top no-car quintile's rate grows by a larger percentage than the bottom's, within density quintiles 2–4. **Fail:** otherwise.

## P4. Homelessness

- **Prediction:** across states, the change in unsheltered homeless people per 100,000 (HUD Point-in-Time counts, earliest available year near 2009 vs. 2022) correlates with the change in pedestrian deaths per 100,000 (2009–11 vs. 2020–22).
- **Pass:** Pearson r > 0.3 across the 50 states plus DC, **and** still > 0.3 with California left out. **Fail:** otherwise.

## P5. Driver distraction

- **Prediction:** the share of striking drivers in pedestrian deaths recorded as distracted by a phone or other device rises.
- **Pass:** the 2020–22 share is above the 2010–12 share (FARS distraction fields, which start around 2010). **Weak test either way:** police rarely know about phone use, so FARS undercounts it badly; a fail doesn't rule distraction out, and a pass doesn't measure it.

## Not testable with public data

- Shift work and transit dependence of the people killed (no field in FARS).
- Whether the person killed was unhoused (no field in FARS; P4 is the indirect test).

## Results

**P1–P3 (tracts): all three PASS, as written** (run 2026-11-05; `scripts/test_tracts.py`, `data/final/test_tracts_*.csv`). Deaths placed in 2010 census tracts from FARS coordinates (98.7–99.7% usable); 91–133 deaths a year fell in tracts with no quintile (zero population) and are excluded. Rates are deaths per 100,000 tract residents, per year.

| P1: poverty quintile | Rate 2009–11 | Rate 2020–22 | Change | Share of 2009–11 deaths | Share of added deaths |
|---|---|---|---|---|---|
| 1 (lowest poverty) | 0.77 | 1.15 | +50% | 11% | 8% |
| 2 | 1.04 | 1.58 | +51% | 15% | 11% |
| 3 | 1.25 | 2.10 | +69% | 18% | 18% |
| 4 | 1.61 | 2.76 | +71% | 24% | 24% |
| 5 (highest poverty) | 2.18 | 4.00 | **+83%** | 32% | **38%** |

- **P1 PASS:** the highest-poverty fifth took 38% of the added deaths (32% of the earlier deaths), and its rate grew 83% vs. 50% in the lowest-poverty fifth.

| P2: density quintile | Rate 2009–11 | Rate 2020–22 | Change | Share of added deaths |
|---|---|---|---|---|
| 1 (least dense) | 1.33 | 2.11 | +59% | 17% |
| 2 | 1.33 | 2.22 | +67% | 19% |
| 3 | 1.38 | 2.52 | +83% | 24% |
| 4 | 1.35 | 2.49 | +85% | 24% |
| 5 (densest) | 1.46 | 2.23 | **+53%** | 16% |

- **P2 PASS:** middle-density tracts took 67% of the added deaths, and their rate grew 78% vs. 53% in the densest fifth.
- **P3 PASS:** within middle-density tracts, the most car-free fifth grew 91% (2.54 → 4.84) vs. 76% for the least car-free (0.77 → 1.36). The sensitivity version (quintiles recomputed within those tracts): 86% vs. 71%, same direction.

**Not pre-registered (descriptive only):**
- Poverty × density, % change in rate: the steepest rises are in **high-poverty, middle-density tracts** (poverty quintile 5 × density quintiles 3–4: +99% and +107%; quintile 4: +97% and +93%). The smallest: **low-poverty, dense tracts** (+17%).
- After dark the same pattern is sharper: the highest-poverty fifth's dark rate doubled (+100%) vs. +60% in the lowest. In daylight the densest fifth barely moved (+10%).
- **Every group rose.** Even the richest fifth's rate grew 50%. So the hypothesis describes where the rise is steepest, not the only place it happened.

**What this does and doesn't show:** deaths rose fastest where poorer, more car-free people live in middle-density (suburban-type) areas, which fits the hypothesis. It doesn't show the people killed lived there (crashes are placed where they happened), and tract characteristics are from 2008–12, before any later gentrification or displacement.

**P4 (homelessness): FAIL, as written** (run 2026-11-05; `scripts/test_homeless.py`, `data/final/test_homeless.csv`, chart `charts/test_homeless_scatter.png`; HUD file downloaded by hand, see `data/raw/hud/SOURCE.md`).
- Base year 2009 (every state has an unsheltered count). Pearson r between the change in unsheltered homeless per 100,000 (2009 → 2022) and the change in pedestrian deaths per 100,000 (2009–11 → 2020–22): **r = −0.30 across 51; −0.39 without California.** The rule needed r > 0.3 in both. It isn't just short of the bar: the sign is negative.
- Not pre-registered: Spearman r −0.33 (−0.38 without CA); using total homeless instead of unsheltered, r −0.11 (−0.15).
- **Why it may be negative:** unsheltered homelessness grew most on the West Coast and in the Northeast (California +98 per 100,000, Hawaii +74, Washington +65, DC +48). Pedestrian deaths rose modestly in Hawaii (+7%) and DC (+13%), but not in California (+80%, 9th of 51) or Washington (+79%), against a median of +68%. *(Corrected 2026-11-10: this line said all four "rose modestly".)* Pedestrian deaths rose most in Sun Belt states where unsheltered counts *fell* (New Mexico, Louisiana, Georgia, Mississippi, Florida). And the 2009 base is unusual in places: Louisiana's count was still swollen after Hurricane Katrina, and Florida's by the recession.
- **What this does and doesn't rule out:** state-level homelessness doesn't explain which states saw the biggest pedestrian rise. It doesn't rule out homelessness inside cities (Portland and Los Angeles report a third to 70% of pedestrian deaths are unhoused people in some years); a state-level correlation can't see that.

**Scorecard:** P1 pass, P2 pass, P3 pass, P4 fail, P5 pass but uninformative. The geography supports the "no car, suburban, poor" part of the hypothesis; the state-level test doesn't support homelessness as the driver of *where* the rise happened; distraction remains unmeasured.

**P5 (driver distraction): PASS, as written, but uninformative** (`scripts/test_distraction.py`, `data/final/test_distraction.csv`, 2026-11-05).
- Phone-distracted share of striking drivers with a known distraction status: 1.15% (126 of 10,972) in 2010–12 → 1.98% (163 of 8,221) in 2020–22. That meets the pass rule.
- But drivers with "unknown" or "not reported" distraction went from 19.2% to 62.0% of all pedestrian deaths, so the pass rests on a shrinking, likely unrepresentative pool. As a share of all deaths, phone-distracted drivers *fell* (0.93% → 0.75%).
- As the rule said: a weak test either way. It neither supports nor rules out distraction.

---

# Round 2: drugs and night workers (pre-registered 2026-11-05, before any test was run)

From `docs/next-hypotheses.md`, H6 and H7. Same common setup as round 1 (2009–11 vs. 2020–22 per-year averages; FARS pedestrian deaths placed in 2010 tracts; pre-period ACS 2008–12 tract characteristics; population-weighted quintiles; rates per 100,000 residents) unless a test says otherwise. Results go below, scored against these rules without changing them.

## P6. Night workers

- **Measure:** share of a tract's workers (who don't work at home) who leave home for work between midnight and 4:59am (ACS B08302; 2008–12).
- **Prediction:** night-departure tracts saw bigger rises **even among tracts of similar poverty**, so it's not just poverty under another name.
- **Method:** national population-weighted quintiles of the night-departure share. Within each of the five poverty quintiles from P1, compare the % change in death rate of the top night-departure quintile with the bottom one.
- **Pass:** the top night-departure quintile grows by a larger percentage than the bottom one in **at least 4 of the 5** poverty quintiles. **Fail:** 3 or fewer.

## P7. Transit riders

- **Measure:** share of a tract's workers who commute by public transportation (ACS B08301; 2008–12).
- **Prediction and method:** as P6, with the transit share in place of the night-departure share.
- **Pass:** top transit quintile grows by a larger percentage than the bottom one in **at least 4 of the 5** poverty quintiles. **Fail:** 3 or fewer.

## P8. Drug overdoses, by state

- **Measure:** change in each state's age-adjusted drug overdose death rate per 100,000 (CDC/NCHS official state figures; 2009–11 average vs. 2020–22 average) against the change in its pedestrian death rate per 100,000 over the same periods (FARS over Census population, as in P4).
- **Prediction:** states where overdoses rose most saw the biggest rises in pedestrian deaths.
- **Pass:** Pearson r > 0.3 across the 50 states plus DC, **and** still > 0.3 with West Virginia (the state with the most extreme overdose rise in this period, named in advance) left out. **Fail:** otherwise.

## P9. Drugs in pedestrians killed

- **Measure:** among pedestrians killed who were tested for drugs (FARS drug-test fields), the share positive for a stimulant (methamphetamine, amphetamine, cocaine) or an opioid (including fentanyl).
- **Prediction:** that share rose.
- **Pass:** the 2020–22 share is at least **5 percentage points** higher than the 2009–11 share. **Fail:** otherwise. The testing rate and any change in how FARS codes drugs (it was overhauled around 2018) are reported alongside. **Weak test either way:** who gets tested varies by state and year, so a pass doesn't measure impairment and a fail doesn't rule it out.

## Not testable with public data

- Whether the pedestrian killed was on their way to or from work, or to a bus stop.
- Impairment, as opposed to a positive test (drugs can show up days after use).

## Round 2 results

Run 2026-11-05. Scripts: `scripts/test_tracts_round2.py` (P6–P7), `scripts/test_overdose.py` (P8), `scripts/test_ped_drugs.py` (P9). Outputs in `data/final/test_tracts_p6_night.csv`, `test_tracts_p7_transit.csv`, `test_overdose.csv`, `test_ped_drugs.csv`.

**P6 (night workers): PASS, as written.** Top night-departure quintile grew faster than the bottom one in 4 of 5 poverty quintiles:

| Poverty quintile | Bottom night quintile | Top night quintile |
|---|---|---|
| 1 (lowest poverty) | +43% | **+61%** |
| 2 | +44% | **+68%** |
| 3 | +73% | **+78%** |
| 4 | +65% | **+83%** |
| 5 (highest poverty) | **+85%** | +83% |

The smallest cell (top night, poverty quintile 1) has 43 deaths a year; every other cell has 78 or more. Not pre-registered: unstratified, night quintiles rise in steps from +64% (bottom) to +79% (top); dark-only deaths show the same 4-of-5 pattern.

**P7 (transit riders): FAIL, as written.** Top transit quintile grew faster in only 1 of 5 poverty quintiles (the poorest: +85% vs. +57%). In the richer quintiles, transit tracts grew *slowest* (+20% vs. +78% in quintile 1), likely big-city cores with more transit, as in P2. 29% of people live in tracts with zero transit commuters on paper; a random tie-break (fixed before looking) gives the same verdicts.

**P8 (overdoses by state): FAIL, as written.** Pearson r = −0.004 across 51; 0.033 without West Virginia (which does have the largest overdose rise: 25.9 → 84.4 per 100,000). Overdose rates: CDC/NCHS age-adjusted, 2009–11 from data.cdc.gov (xbxb-epbu), 2020–22 from NCHS's state map data (the two agree within 0.05 in their overlap years). Chart: `charts/test_overdose_scatter.png`.

**P9 (drugs in pedestrians killed): PASS, as written.** Among pedestrians killed and tested, positive for a stimulant or opioid: **13.9% (2009–11) → 33.6% (2020–22), +19.7 points** (rule: +5). Testing rate 60.3% → 55.6%. Stimulants 8.9% → 28.1%; opioids 6.1% → 11.1%. Both alternative code mappings (dropping caffeine/nicotine; first three results only) also pass (+20.0 and +19.0). FARS changed its file layout in 2018 and its drug codes in 2022 (data challenge 34).

**Not pre-registered (descriptive only):**
- **Timing.** The stimulant-positive share held at 9–11% from 2007 to 2014, then rose with the deaths: 14% (2015), 20% (2017), 23% (2018), 28% (2020), 31% (2024). Pedestrian deaths jumped at the same point (4,910 in 2014 → 6,080 in 2016). Chart: `charts/pedestrian_drug_tests.png`.
- **Rough size, an upper bound on association, not a cause.** Stimulant-positive deaths among those tested went from about 230 a year to about 1,130. If untested pedestrians resembled tested ones, that's roughly 380 → 2,030 a year, about +1,650, or nearly half the rise. Two big caveats: methamphetamine stays detectable for days, so a positive test isn't impairment; and some of these people might have died anyway in a different way, or would have been hit regardless.
- **Why P8 and P9 can disagree (OUR READING).** State overdose deaths in this period were driven mostly by opioids and fentanyl, concentrated in Appalachia and the Northeast. The stimulant rise in pedestrian deaths fits the South and West, where methamphetamine is more common. P8 may have measured the wrong drug. A follow-up would need its own pre-registration (e.g. state psychostimulant overdose deaths vs. pedestrian deaths).

**Round 2 scorecard:** P6 pass, P7 fail, P8 fail, P9 pass. **The pieces that survive two rounds:** poor, car-free, suburban-density places (P1–P3); night workers within the same income level (P6); and a large rise in stimulants among the pedestrians killed, starting exactly when deaths began rising (P9). Homelessness by state (P4), transit commuting (P7) and opioid overdoses by state (P8) didn't hold.

---

# Round 3: methamphetamine by state (pre-registered 2026-11-05, before any test was run)

Why: P8 (all drug overdoses by state) failed while P9 (drugs in pedestrians killed) passed, driven by stimulants. Overdose deaths in this period were mostly opioids, concentrated in Appalachia and the Northeast; the pedestrian rise is in the South and West. This tests the stimulant version directly.

## P10. Methamphetamine overdoses, by state

- **Measure:** each state's death rate per 100,000 from overdoses involving **psychostimulants with abuse potential** (ICD-10 T43.6, which is mostly methamphetamine), from official CDC/NCHS figures. Not CDC WONDER (it requires accepting terms in an interactive session).
- **Periods:**
  - **Primary:** 2009–11 vs. 2020–22, as in P8, if official state figures exist for both.
  - **Fallback, if they don't:** the earliest year with official state figures (expected 2015, from the NCHS provisional counts) vs. 2022, for **both** sides: psychostimulant deaths and pedestrian deaths per 100,000 (FARS over Census population). The fallback is weaker: by 2015 the pedestrian rise had begun.
- **States included:** where the source flags a state's drug-specific counts as unreliable (for example, too few death certificates name the drug), that state is left out. The number of states used is reported.
- **Prediction:** states where methamphetamine overdose deaths rose most saw the biggest rises in pedestrian deaths per 100,000.
- **Pass:** Pearson r > 0.3 across the states included, **and** still > 0.3 with the state that has the largest psychostimulant rise left out (whichever state that turns out to be). **Fail:** otherwise.
- **Weak spots, stated in advance:** a state-level match can't show that the people killed used methamphetamine; overdose deaths measure the drug's spread, not drivers or walkers on it.

## Round 3 results

**P10 (methamphetamine overdoses by state): FAIL, as written, under the fallback branch** (run 2026-11-05; `scripts/test_meth.py`, `data/final/test_meth.csv`, chart `charts/test_meth_scatter.png`; source `data/raw/cdc_meth/SOURCE.md`).
- **Branch:** fallback. No official CDC/NCHS state psychostimulant (T43.6) figures for 2009–11 were found outside CDC WONDER (NCHS data briefs give national rates only; state tables by drug start in 2016–17; the NCHS provisional counts, dataset xkb8-kh2a, start in 2015). So: 2015 vs. 2022, single years, both sides. Rates are crude (counts over FRED population); the provisional file has no age-adjusted state rates.
- **States:** 21 included (CT, GA, IA, IL, MA, MD, ME, NC, NM, NV, NY, OH, OK, OR, SC, TN, UT, VA, VT, WA, WV). 30 excluded: 26 flagged by CDC as low data quality in 2015 (including CA, TX, FL, AZ, AL, MS, CO), Louisiana with no drug-specific rows, and DC, NH and RI suppressed (fewer than 10 deaths). New York = upstate plus New York City, which the file reports separately.
- **Result:** Pearson r = **0.255** across 21 states (rule: > 0.3). Without West Virginia (the largest rise, 3.6 → 41.1 per 100,000), r = **0.556** across 20. Fails because the all-states figure misses.
- Not pre-registered: Spearman r 0.339 (0.456 without WV); using CDC's "predicted" counts, r 0.234 (0.562 without WV).
- **What this does and doesn't show:** the test is badly underpowered. Twenty-one states, with most of the Sun Belt and West (where the pedestrian rise is largest) missing for data quality, and a 2015 start, after the pedestrian rise had begun. CDC itself warns that drug-specific comparisons across states "should not be made" with this file. Leaving out West Virginia, where methamphetamine deaths exploded but pedestrian deaths barely rose, the remaining states show a moderate positive link, but that's not the test as written. **Verdict: fails; inconclusive on the evidence available, not a refutation.**

**P10 primary branch: planned re-run (noted 2026-11-05, before any WONDER data was seen).** The written rule's primary branch (2009–11 vs. 2020–22) was skipped only because CDC WONDER requires accepting its data-use terms in person. David will accept them and export the state psychostimulant (T43.6) figures himself. The re-run uses the P10 measure, periods and pass/fail rule unchanged, with WONDER's age-adjusted rates; states WONDER marks "Unreliable" (fewer than 20 deaths) in any period are left out, as the exclusion rule says. **Disclosure:** the fallback result (fail, r = 0.255) was known before this re-run was planned, so the re-run is reported alongside it, never instead of it.

**P10 primary branch (CDC WONDER): PASS, as written, with one deviation** (run 2026-11-05; `scripts/test_meth_wonder.py`, `data/final/test_meth_wonder.csv`, chart `charts/test_meth_wonder_scatter.png`; source `data/raw/cdc_wonder/SOURCE.md`).
- **Periods:** 2009–11 vs. 2020–22 (the primary branch), three years pooled per state, exported by David from the WONDER web site.
- **States:** 38 included. 13 left out as Suppressed (fewer than 10 deaths) or Unreliable (fewer than 20) in 2009–11: CT, DE, DC, NH, ND, RI, SD, VT (suppressed); ME, MD, MS, MT, WY (unreliable). Unlike the fallback, this keeps California, Texas, Florida, Arizona, Georgia and the rest of the Sun Belt.
- **Result:** both above 0.3: **PASS** (numbers below, crude and age-adjusted).
- **First run on crude rates** (the first 2020–22 export had no age-adjusted column): r = 0.364; 0.652 without WV. **Then on age-adjusted rates, the planned measure**, after David re-exported 2020–22 with that column (same query; `wonder_t436_2020_2022_ageadj.csv`): **r = 0.348 across 38 states; 0.651 without West Virginia** (largest rise, +43.4 per 100,000 age-adjusted). Same 38 states. **PASS on the planned measure.** The crude run reproduces exactly from the new file. Outputs: `data/final/test_meth_wonder.csv` (age-adjusted), `test_meth_wonder_crude.csv`; charts `test_meth_wonder_scatter.png` and `_crude.png`.
- Not pre-registered: Spearman r 0.602 age-adjusted (0.659 without WV); 0.596 (0.654) crude.
- **Reading the scatter:** states where methamphetamine overdoses rose most (New Mexico, Arizona, Tennessee, South Carolina, Louisiana, Oregon, California) also saw the biggest pedestrian rises; Northeast and upper-Midwest states with small meth rises saw small pedestrian rises. Appalachia (West Virginia, Kentucky) is the exception: huge meth rises, modest pedestrian rises.
- **The two branches disagree, and why (OUR READING):** the 2015 fallback (fail, r = 0.255) had only 21 states and lost the Sun Belt to CDC's data-quality flags, and by 2015 both curves had already started rising. The primary branch has the full periods and 38 states. Both results stand in this file; the primary branch is the test as originally designed.
- **What it does and doesn't show:** states where methamphetamine spread most saw the biggest rises in pedestrian deaths. It doesn't show that the people killed, or the drivers, were on methamphetamine; P9 is the closer evidence for that (stimulant-positive share of pedestrians killed 9% → 28%).

**Overall scorecard (three rounds):** pass: P1 poverty, P2 suburban density, P3 no car, P6 night workers, P9 stimulants in pedestrians killed, P10 methamphetamine by state (primary branch, age-adjusted; the 2015 fallback failed). Fail: P4 homelessness by state, P7 transit, P8 all overdoses by state. Uninformative: P5 distraction.

---

# Round 4: drivers, old vehicles, population growth (pre-registered 2026-11-05, before any test was run)

From `docs/next-hypotheses.md`, H10, H9 and H8. Following the playbook's control-group rule, P11 and P12 compare pedestrian crashes with fatal crashes that involved no pedestrian, since forces that hit every crash (an aging fleet, more unlicensed drivers overall) would move both. Results go below, scored against these rules without changing them.

**Common setup for P11–P12.** 2009–11 vs. 2020–22, all years pooled within each period. The **pedestrian group** is the vehicle that struck each pedestrian killed (PERSON PER_TYP 5, INJ_SEV 4; striking vehicle from N_MOT_NO / STR_VEH, as in `scripts/fars_pedestrians.py`), one row per death. The **control group** is every vehicle in a fatal crash with no pedestrian (PER_TYP 5) record at all.

## P11. Unlicensed drivers (H10)

- **Measure:** driver license status (VEHICLE.L_STATUS). Not validly licensed = 0 not licensed, 1 suspended, 2 revoked, 3 expired, 4 cancelled or denied. Valid = 6. Unknown = 7 (no driver present or unknown) and 9, left out of the share and reported separately.
- **Prediction:** the not-validly-licensed share among drivers who struck a pedestrian rose more than among drivers in the control group.
- **Pass:** the pedestrian group's share rises by **at least 2 percentage points**, **and** by **at least 1 point more** than the control group's. **Fail:** otherwise.
- **Weak spot, stated in advance:** hit-and-run drivers mostly have unknown status, and hit-and-run rose (17% → 24% of pedestrian deaths). If fleeing drivers are disproportionately unlicensed, the known-status pool understates the rise. The hit-and-run share is reported beside the result.

## P12. Old vehicles (H9)

- **Measure:** vehicle age = crash year − model year (VEHICLE.MOD_YEAR; 9998 and 9999 left out; negative ages, next year's models, set to 0). Old = 15 years or more.
- **Prediction:** the old-vehicle share among vehicles that struck a pedestrian rose more than among control-group vehicles.
- **Pass:** the pedestrian group's 15+ share rises by **at least 2 percentage points more** than the control group's. **Fail:** otherwise.

## P13. Population growth (H8)

- **Measure:** tract population growth, ACS 2008–12 to ACS 2015–19 (B01003, both on 2010 tract boundaries, so tracts match one to one). Same tract deaths as P1–P3.
- **Rates:** 2009–11 deaths per 100,000 of the ACS 2008–12 population; 2020–22 deaths per 100,000 of the ACS 2015–19 population (the latest ACS on 2010 boundaries). Per-resident rates, so a tract doesn't "rise" just by adding people.
- **Growth quintiles:** population-weighted (2008–12 population), as in P1. Tracts with zero 2008–12 population get no quintile.
- **P13a, per resident:** within each of the five poverty quintiles from P1, compare the % change in rate of the top growth quintile with the bottom one. **Pass:** top grows faster in **at least 4 of the 5**. **Fail:** 3 or fewer.
- **P13b, population shift:** how much of the national rise in the per-resident rate comes from people moving into higher-rate places. Cells = growth quintile × poverty quintile × density quintile (125 cells). Counterfactual 2020–22 rate = each cell's 2009–11 rate weighted by its 2015–19 population. Composition share = (counterfactual rate − 2009–11 rate) ÷ (actual 2020–22 rate − 2009–11 rate). **Pass:** composition share **at least 10%**. **Fail:** below 10%.
- **Weak spots, stated in advance:** cells only capture moves between kinds of tracts, not moves within one; and crashes are placed where they happen, not where the person killed lived.

## Not tested this round

- **H11 (US cities that copied Europe):** needs a design David agrees to first (which cities, which policy dates, which comparison cities). Choosing them after seeing the data would make it a fishing trip.
- **H12 (phones):** no public crash-level data.

## Round 4 results

Run 2026-11-05, after the pre-registration above was committed (`b946f58`). Scripts: `scripts/test_drivers.py` (P11–P12), `scripts/test_growth.py` (P13). Outputs: `data/final/test_drivers.csv`, `test_growth_p13a.csv`, `test_growth_p13b.csv`, `test_growth_tracts.csv`.

**P11 (unlicensed drivers): FAIL, as written.** Not-validly-licensed share among drivers with a known license status:

| Group | 2009–11 | 2020–22 | Change |
|---|---|---|---|
| Struck a pedestrian (12,868 → 21,628 deaths) | 8.7% | 12.7% | +4.1 pts |
| Control: fatal crashes with no pedestrian | 11.9% | 16.4% | **+4.5 pts** |

- The pedestrian share passes the 2-point bar, but the control group rose as much (gap −0.4 points; the rule needed +1). Unlicensed driving rose across all fatal crashes, not specially in pedestrian crashes.
- **The weak spot named in advance is real:** license status is unknown for 11.5% → 16.3% of pedestrian deaths (1.4% → 2.4% in the control group), mostly hit-and-run drivers (17.5% → 23.7% of pedestrian deaths). If fleeing drivers are disproportionately unlicensed, the pedestrian figure is understated. That caveat can't be tested with FARS. About 1% of 2009–10 pedestrian deaths have a blank license field or no matching vehicle row (counted as unknown).

**P12 (old vehicles): FAIL, as written.** Share of vehicles 15 or more model years old, among vehicles with a known model year:

| Group | 2009–11 | 2020–22 | Change |
|---|---|---|---|
| Struck a pedestrian | 14.2% | 27.5% | +13.3 pts |
| Control: fatal crashes with no pedestrian | 16.9% | 34.3% | **+17.5 pts** |

- The striking vehicles got older, but less than vehicles in other fatal crashes (gap −4.2 points; the rule needed +2). The whole fleet aged after the recession (mean age in the control group 9.1 → 11.2 years). In both periods, vehicles that hit pedestrians were *younger* than other crash vehicles.
- The vehicle-age jump in the brief (deaths involving 15+-year-old vehicles 471 → 1,863) is real but general: it's the fleet aging, not something particular to pedestrian deaths.

**P13 (population growth): FAIL on both parts, as written.** 363 deaths (182 in 2009–11, 181 in 2020–22) fell in tracts missing a quintile and are excluded. Growth quintiles run from tracts that shrank more than 5% (bottom) to tracts that grew more than 13.5% (top).

| Poverty quintile | Bottom growth (shrinking) | Top growth |
|---|---|---|
| 1 (lowest poverty) | **+84%** | +33% |
| 2 | **+77%** | +37% |
| 3 | **+79%** | +54% |
| 4 | **+78%** | +56% |
| 5 (highest poverty) | **+94%** | +47% |

- **P13a FAIL:** the fastest-growing tracts grew faster in 0 of 5 poverty quintiles. The pattern is the reverse: per resident, the rate rose most in tracts that were *losing* people, at every income level.
- **P13b FAIL:** moving people into higher-rate kinds of tracts explains **0.7%** of the national rise in the per-resident rate (1.370 → 2.205 per 100,000; counterfactual 1.376). The rule needed 10%.
- **Not pre-registered:** counted per 2010 resident, as in P1–P3, deaths in the fastest-growing fifth rose 87% (997 → 1,861 a year) vs. 62% in the shrinking fifth. That gap is just more people: more residents, more pedestrians, more deaths. Per person, growing places got *less* dangerous relative to the rest.
- **Denominator note:** 2020–22 rates use ACS 2015–19 (the last on 2010 boundaries). Growing tracts kept growing after that, so their true 2020–22 rates are a little lower than shown. That bias works in the hypothesis's favor, and it still failed.

**Round 4 scorecard:** P11 fail, P12 fail, P13 fail (both parts). Riskier drivers and older cars rose across all fatal crashes, so they don't explain why pedestrians in particular broke away. Population moving to fast-growing suburbs doesn't explain it either. The rise per resident was steepest in places people were leaving.

**Overall scorecard (four rounds):** pass: P1 poverty, P2 suburban density, P3 no car, P6 night workers, P9 stimulants in pedestrians killed, P10 methamphetamine by state (primary branch). Fail: P4 homelessness by state, P7 transit, P8 all overdoses by state, P10 fallback (2015), P11 unlicensed drivers (control rose as much), P12 old vehicles (control rose more), P13 population growth. Uninformative: P5 distraction.

---

# Round 5: does the decline line up too? (pre-registered 2026-11-06, before any 2022–2024 data was looked at)

Why: US pedestrian deaths fell from 7,593 (2022) to 7,080 (2024). If methamphetamine is part of the cause, meth overdose deaths should have fallen too, and the states where they fell most should have seen pedestrian deaths fall most. A failure here counts against the meth explanation. (P14–P16 are reserved for the H11 draft, `docs/h11-design-draft.md`, so this is P17.)

## P17. Meth overdoses and pedestrian deaths, 2022 → 2024

- **Source:** NCHS VSRR provisional drug overdose death counts (data.cdc.gov xkb8-kh2a, the file already in `data/raw/cdc_meth/`; re-downloaded if it doesn't reach December 2024). Indicator "Psychostimulants with abuse potential (T43.6)", 12 months ending December, reported deaths ("Data Value"). Pedestrian deaths: FARS PER_TYP 5, INJ_SEV 4, by state. Rates per 100,000 over FRED state population. Same code paths as P10's fallback (`scripts/test_meth.py`).
- **P17a, national:** psychostimulant overdose deaths fall by **at least 5%** from 2022 to 2024. **Fail:** otherwise.
- **P17b, states:** Pearson r between the change in psychostimulant deaths per 100,000 and the change in pedestrian deaths per 100,000 (2024 minus 2022) is **> 0.3** across included states, **and still > 0.3** with the state that has the largest psychostimulant decline left out. **Fail:** otherwise.
- **Exclusions:** as in P10: states with values withheld for low data quality or suppressed (<10) in 2022 or 2024 are left out and listed. New York = NY + YC.
- **Weak spots, stated in advance:** two single years; provisional 2024 counts can still change; a two-year change is small, so noise is large; and a national fall in both could share a general cause (e.g. fewer people on the street at night, more enforcement), so P17a alone can't separate meth from other forces.

## Round 5 results

Run 2026-11-06, after the pre-registration was committed. `scripts/test_meth_decline.py`, `data/final/test_meth_decline.csv`. VSRR file downloaded 2026-11-05, with data through May 2026, so December 2024 is about 17 months old (provisional, but mostly complete).

**P17a (national): PASS.** Psychostimulant overdose deaths, 12 months ending December: **34,842 (2022) → 29,641 (2024), −14.9%** (rule: at least −5%). Pedestrian deaths over the same years: 7,593 → 7,080 (−6.8%).

**P17b (states): FAIL, as written.** Pearson r = **0.254** across 46 states (rule: > 0.3); **0.377** without West Virginia (the largest decline, −14.5 per 100,000). Fails because the all-states figure misses. Excluded: Florida (2024 low data quality), Louisiana (no drug-specific rows), North Dakota and Nebraska (low quality both years), Pennsylvania (2022 low quality).
- Meth death rates fell in 35 of 46 states; pedestrian rates fell in 27 of 46.
- **Counter-examples:** Arizona (meth +1.4 per 100,000, pedestrians −0.72) and Oregon (meth +3.9, pedestrians −0.65) went opposite ways. Nevada, Washington, Alaska and Hawaii went the same way, up on both.
- Not pre-registered: Spearman 0.247.

**What this does and doesn't show:** nationally, the decline lines up (both fell). State by state, the two-year changes line up only weakly, with West Virginia again the outlier. As stated in advance, two-year changes are small and noisy, and a shared national fall could have a general cause. **Verdict: a direction match nationally, not a clean state-level confirmation.**

**Overall scorecard (five rounds):** pass: P1, P2, P3, P6, P9, P10 (primary), P17a. Fail: P4, P7, P8, P10 (fallback), P11, P12, P13, P17b. Uninformative: P5.

---

# Round 6: questions from the Reel's comments (pre-registered 2026-11-10, before any of these numbers were computed)

Why: after the Reel posted, viewers raised three checkable objections. (1) The Reel showed the rise with stimulant tests in pedestrians killed but checked the 2022–2024 decline with meth overdoses, two different measures. (2) "Stimulant" includes amphetamine, which also comes from prescriptions (Adderall). (3) The meth signal could be in drivers, not pedestrians. Same FARS files and drug definitions as P9 (`scripts/test_ped_drugs.py`, "primary" definition, all result rows; 2022 on uses the 4-digit codes throughout, so 2022–2024 is one coding scheme).

## P18. Stimulants in pedestrians killed, 2022 → 2024 (the decline, on the same measure as the rise)

- **Measure:** share of tested pedestrians killed who were positive for a stimulant (P9 primary).
- **Pass:** the 2024 share is **lower than the 2022 share by at least 1 percentage point**. **Fail:** otherwise. 2023 is reported, not scored.
- **Weak spots:** two single years; testing rates can shift; P17 showed meth overdoses peaked in 2023, so a flat 2022–2024 would not be a strong contradiction.

## P19. How much of the stimulant rise is methamphetamine?

- **Measure:** share of tested pedestrians killed positive for methamphetamine (3-digit 417; 4-digit 3053), and the share positive for amphetamine (401, 400, 408; 3019) **without** methamphetamine, 2009–11 vs 2020–22 (pooled). Amphetamine is also a breakdown product of meth, so amphetamine-without-meth is the group that could be prescription use.
- **Pass:** the rise in the meth-positive share is **at least half** of the rise in the stimulant share (P9 primary). **Fail:** otherwise.
- **Weak spot:** labs may report only amphetamine for some meth users; that would push toward a fail.

## P20. Stimulants in drivers who killed pedestrians

- **Groups:** drivers (PER_TYP 1) of the vehicle that struck each pedestrian killed (as in P11), one row per pedestrian death; control: drivers of every vehicle in fatal crashes with no pedestrian.
- **Measure:** share of tested drivers positive for a stimulant (P9 primary), 2009–11 vs 2020–22.
- **Driver explanation supported** if the striking drivers' share rises **at least 3 percentage points more** than the control drivers' share. **Not supported** otherwise.
- **Weak spots:** surviving drivers are tested far less often than people who die, and testing may target drivers who seem impaired; hit-and-run drivers are often never identified (no test). Testing rates are reported for both groups.

## Round 6 results

Run 2026-11-10, after the pre-registration was committed (2aab032). `scripts/test_comments.py`, `data/final/test_comments.csv`. FARS 2024 is the final file.

**P18 (the decline, same measure as the rise): FAIL.** Stimulant share among tested pedestrians killed: **28.5% (2022) → 29.6% (2023) → 31.4% (2024)**, +2.9 points (rule: at least −1). On the measure the Reel used for the rise, the share did not fall while meth overdoses did.
- Not pre-registered, for context: the testing rate fell from 54.9% to 49.0%, so the 2024 share comes from fewer tests. Counted per pedestrian killed instead of per tested, stimulant-positive deaths went 1,189 → 1,090 (15.7% → 15.4% of all deaths), roughly flat. Either way, there is no fall in stimulant involvement among pedestrians killed to match the fall in deaths.
- So P17a (national meth overdoses fell along with pedestrian deaths) and P18 point different ways. The 2022–2024 decline in pedestrian deaths is **not** explained by fewer stimulant-positive pedestrians.

**P19 (meth vs. prescription amphetamine): PASS.** 2009–11 → 2020–22, among tested pedestrians killed: stimulant **+19.2 points** (8.9% → 28.1%), methamphetamine **+17.1 points** (2.5% → 19.6%), amphetamine without meth **+0.8 points** (0.7% → 1.6%). Meth is **89%** of the stimulant rise (rule: at least half). Prescription amphetamine can't account for it.

**P20 (stimulants in drivers who killed pedestrians): NOT SUPPORTED.** Stimulant share among tested drivers of the striking vehicle: **4.4% → 9.9% (+5.6 points)**; control drivers in fatal crashes with no pedestrian: **6.9% → 16.7% (+9.8 points)**. Gap −4.2 (rule: +3 or more). Stimulant-positive drivers rose across all fatal crashes, and less among drivers who hit pedestrians.
- **Big caveat:** only **18% (2009–11) and 14% (2020–22)** of striking drivers had a test result, against 41% and 38% of control drivers (many control drivers died; most drivers who kill a pedestrian survive). 88 or so deaths a year have no driver record at all (mostly hit-and-run). Drivers who hit pedestrians are the least-tested group in the file, so this is weak evidence either way.

**Round 6 scorecard:** P18 fail, P19 pass, P20 not supported. Prescription stimulants are ruled out as the source of the rise (P19), and the data doesn't point to impaired drivers (P20, weakly). But on the Reel's own measure, stimulant involvement among pedestrians killed kept rising through 2024 while deaths fell (P18), which weakens the "decline lines up" point the Reel made with overdose counts.

**Overall scorecard (six rounds):** pass: P1, P2, P3, P6, P9, P10 (primary), P17a, P19. Fail: P4, P7, P8, P10 (fallback), P11, P12, P13, P17b, P18. Not supported: P20. Uninformative: P5.

---

# Round 7: H11, speed cameras (pre-registered 2026-11-10, before any city's pedestrian deaths were counted)

Why: the Reel's most-liked critique was that street design and safer vehicles matter whatever the drug picture. Published studies (Ferenchak 2023; Schneider et al. 2026) tested Vision Zero pledges, which bundle very different actions, and had no clean comparison group. This tests one concrete European tool, automated speed cameras, against cities whose state law kept cameras out. Design: `docs/h11-design-draft.md` P14. David said "run it" (2026-11-10), so the suggested settings in that draft are used as written. Camera dates: `docs/h11-policy-dates.md` plus a second research pass (2026-11-10; summarized in `docs/h11-camera-dates.md`).

## P14. Automated speed cameras

- **Sample:** the 73 incorporated places with 2010 Census population of 250,000 or more, on fixed 2010 TIGER boundaries. Urban Honolulu is dropped because it is a CDP with no place population estimates before 2010.
- **Deaths:** pedestrians killed (PER_TYP 5, INJ_SEV 4), placed in a city by FARS crash coordinates.
- **Population:** Census place estimates (intercensal 2005–09, Vintage 2020 for 2010–19, Vintage 2024 for 2020–22). Rate is per 100,000, pooled over the three years of each period.
- **Treated (3):** Washington DC (photo radar from 2001, about 87 cameras by 2016), New York (from January 2014, 140 zones in 2014), Chicago (from October 2013, about 150 cameras by 2016). All three meet the rule: on city streets by the end of 2016, at least 20 locations, still running in 2020–22.
- **Excluded from treatment by the rule:**
  - Baltimore was off from 2013 to 2017.
  - Portland had 1 corridor in 2016.
  - Denver ran about 5 vans.
  - Phoenix ended in 2019.
  - New Orleans and Toledo paused in 2020–21.
  - Tucson and Cleveland had voter bans in 2014–15.
- **Sensitivity only, not scored:** Seattle had 28 cameras in 14 school zones by 2015, which is borderline on "20 locations".
- **Comparison (13):** cities in states that barred speed cameras over the outcome periods:
  - Texas (from June 2007): Houston, San Antonio, Dallas, Austin, Fort Worth, El Paso, Arlington, Corpus Christi, Plano.
  - New Jersey (never authorized): Newark.
  - Wisconsin (1990s): Milwaukee.
  - Nevada (officer-operated only, 1999): Las Vegas, Henderson.
  - **Deviation from the draft:** Texas's ban starts in mid-2007, so it doesn't cover the 2005–07 pre-trend years. No Texas city of 250,000+ is known to have run speed cameras then.
- **Matching:** standardize three things across the sample: the 2009–11 pedestrian rate, the poverty rate (ACS 2008–12, place level), and log density (2010 population over land area). Each treated city's comparison is the ban-state cities in its Census region, weighted by 1/(distance + 0.25). If the region has fewer than 2 such cities, all 13 are used; that applies to New York, which has only Newark, and to Chicago, which has only Milwaukee.
  - **Deviation from the draft:** poverty and density are measured at the place level, not aggregated from tracts.
- **Measure:** each city's relative change in rate, 2009–11 to 2020–22. The treated figure is the mean of the three cities. The comparison figure is the mean of each treated city's weighted comparison.
- **Pre-trend check:** compare the change from 2005–07 to 2009–11 (per 100,000), treated minus matched comparison. If it differs by more than **0.3**, the result is **NOT INTERPRETABLE**.
- **Pass:** the treated relative rise is at most **75%** of the comparison rise (at least 25% smaller), **and** the gap ranks in the most favorable **10%** of 1,000 placebo runs. Each placebo draws 3 "treated" cities at random from the 57 cities that are neither treated nor comparison (seed 20261110). **Fail:** otherwise.
- **Not scored:** each treated city on its own, Seattle added, and a year-by-year chart.
- **Weak spots, stated in advance:**
  - Only 3 treated cities, all large and dense, so the matching is crude and the placebo test has little power.
  - Cameras cover a small part of each city's streets.
  - Texas dominates the comparison group.
  - Place estimates follow current boundaries, while deaths are placed on 2010 boundaries; annexation can push later rates down a little in growing Sun Belt cities.
  - A pass would show only that camera cities did better, not that cameras caused it. New York bundled cameras with the 25 mph limit and Vision Zero.

## Round 7 results

Run 2026-11-10, after the pre-registration was committed (f1a3ed9). `scripts/test_cameras.py run`, `data/final/test_cameras*.csv`. 24,079 pedestrian deaths placed in the 73 cities over 2005–22, out of 98,098 nationally. 0.1–2.8% of deaths a year had no usable coordinates.

**P14: NOT INTERPRETABLE, as written.** The pre-trend difference was **−0.3006 per 100,000** against a limit of ±0.3, so it missed by 0.0006. Under the pre-registered rule that ends the scoring, whatever the other numbers say. From 2005–07 to 2009–11, the camera cities' rates had already fallen faster than their matched comparisons, by 0.30 per 100,000.

**Not scored, for the record.** The other two parts would have passed:
- Treated cities' rate rose **+15%** from 2009–11 to 2020–22, against **+75%** for their matched comparisons. The bar was 75% of +75%, or +56%.
- The gap of −0.60 ranked in the most favorable **0.3%** of placebo draws, where the bar was 10%.

**One city at a time (not scored):**

| City | 2009–11 → 2020–22 | Matched comparison | Pre-trend gap |
|---|---|---|---|
| New York | **−29%** (1.72 → 1.23) | +71% | +0.23 |
| Washington DC | **+6%** (1.93 → 2.03) | +79% | −0.80 (cameras since 2001, so its pre-period was already treated) |
| Chicago | **+68%** (1.27 → 2.14) | +75% | −0.33 |
| Seattle (sensitivity) | +78% | +77% | +0.84 |

With Seattle added, the rise is +31% against +76%, with a pre-trend gap of −0.015.

**What this does and doesn't show:**
- The camera cities as a group did much better than the ban-state cities. That rests on New York and DC. Chicago, a camera city since 2013, rose about as much as its comparisons, and so did Seattle.
- The selection problem stated in advance is visible in the table. Dense cities without cameras also rose little: San Francisco −11%, Buffalo +2%, Pittsburgh +9%, Minneapolis +11%. Boston (+50%) and Philadelphia (+62%) are dense too. No ban-state city is as dense as New York (10,400 people per km²; Newark is 4,400), so the matching can't separate cameras from density.
- New York's drop came with Vision Zero and the 25 mph limit, all in 2014.
- **Verdict:** P14 can't be scored. The descriptive pattern fits "cameras and dense-city policy packages help." It doesn't isolate cameras, and one camera city of the three (Chicago) shows no advantage.

**Overall scorecard (seven rounds):**
- **Pass:** P1, P2, P3, P6, P9, P10 (primary), P17a, P19.
- **Fail:** P4, P7, P8, P10 (fallback), P11, P12, P13, P17b, P18.
- **Not supported:** P20.
- **Uninformative or not interpretable:** P5, P14.

# Round 8: do European drug users also get hit? (pre-registered 2026-11-11, before any Spanish report earlier than 2023 was looked at)

Why: a commenter (bfuller181) argued that Europeans have drugs too, so drugs shouldn't explain the US–Europe pedestrian gap, just as phones didn't. Spain's forensic institute (INTCF) publishes yearly toxicology for pedestrians killed (`data/raw/intcf_spain/`). **Already seen before this was written:** Spain 2023 (cocaine 19, amphetamine-type 4, of 200 tested) and 2025 (13 and 3 of 171), and US FARS shares for 2009 (9.0%), 2010 (8.7%), 2015 (14.4%), 2022–2024 (`docs/research-drugs/pedestrian-link.md`). Not seen: any Spanish report on deaths before 2023, and the pooled US 2010–2013 figure.

## P21. Spain's stimulant-positive pedestrians: same start as the US, no US-sized rise

- **Spain measure:** for each INTCF annual report on deaths in a given year, pedestrians positive for cocaine plus pedestrians positive for "amphetamine and related" (or the report's nearest group: amphetamines, methamphetamine), divided by pedestrians tested. Counts can overlap, so this is an upper bound; it is used the same way in every year. Years are pooled (sum of positives / sum of tested).
- **US measure:** P9 primary stimulant share among tested pedestrians killed (`data/final/test_ped_drugs.csv`), pooled the same way.
- **Early period:** whichever of data years 2010, 2011, 2012, 2013 have an INTCF report with pedestrian counts by drug; the US uses the same years. **Late period:** Spain 2023 and 2025 (already seen: 39 of 371 on this measure, 10.5%); US 2023–2024.
- **P21a (similar start):** Spain's early share is within **5 percentage points** of the US early share.
- **P21b (no US-sized rise):** Spain's change from early to late, in points, is **less than half** of the US change.
- **Pass:** both hold. **Fail:** either fails. If P21a fails because Spain started far below the US, the US–Spain difference isn't new; if P21b fails, Spain saw a comparable rise.
- **Not scoreable:** fewer than two early years with pedestrian counts by drug, or a report that gives drug results only for all victims combined.
- **Weak spots:** testing methods got more sensitive over a decade (pushes Spain's share up, toward a fail on P21b); Spain's tested share of pedestrian deaths may have changed; Spain is cocaine-heavy and says little about meth; small Spanish counts (tens of positives).

## Round 8 results

Run 2026-11-11 (`scripts/compare_ped_tox_spain.py`). Spanish early counts are from INTCF "Memoria Tráfico" 2010–2013, pedestrian section "casos con resultados positivos a drogas de abuso", which lists each person's drug combination, so they are counts of people (`data/raw/intcf_spain/`). "Otros" there means anti-inflammatories, analgesics and antihistamines. No MDMA or methamphetamine appeared among pedestrians in those years.

| | Spain tested | Spain stimulant-positive | US stimulant share |
|---|---|---|---|
| 2010 | 211 | 8 (3.8%) | 8.7% |
| 2011 | 192 | 8 (4.2%) | 9.0% |
| 2012 | 164 | 10 (6.1%) | 10.0% |
| 2013 | 161 | 3 (1.9%) | 10.5% |
| **2010–13 pooled** | 728 | 29 (**4.0%**) | **9.6%** |
| Late (Spain 2023+2025; US 2023–24) | 371 | 39 (**10.5%**) | **30.4%** |

**P21: FAIL, as written.**
- **P21a (similar start): FAIL.** Spain started 5.6 points below the US (rule: within 5).
- **P21b (no US-sized rise): PASS.** Spain +6.5 points against the US +20.9; half of the US change is 10.4.

What the numbers also show, unscored:
- In proportion, Spain's share rose about as much as the US's: ×2.6 against ×3.2. So "Europe didn't see the rise" is wrong for Spain's dead pedestrians. Spain's share rose from a lower base, so the gap in points widened, while the ratio stayed about 2.4–2.9×.
- **Weak spots that bear on this:**
  - The 2010–13 reports cover cases analysed in INTCF labs. The 2023 and 2025 reports add the regional institutes' labs (IMLCF), so who is tested changed.
  - Laboratory methods got more sensitive over the decade.
  - The yearly Spanish counts are small (3 to 10 positives).

## P22. Stimulant-positive pedestrians: mostly with opioids, or mostly without?

Pre-registered 2026-11-13, before running. Question from David's Argument tab, point 12: does meth's role in pedestrian deaths come "especially combined with IMF" (fentanyl)? In US overdose deaths the pair dominates: 61% of meth deaths in 2024 also involved an opioid. Is it the same among pedestrians killed?

- **Data:** FARS pedestrians killed and tested, same drug definitions as P9 "primary" (`scripts/test_ped_drugs.py`): stimulant = meth, amphetamine or cocaine (and metabolites); opioid = the narcotic-analgesic class (includes fentanyl and heroin).
- **Measure:** among tested pedestrians positive for a stimulant, the share also positive for an opioid. Pooled 2022–2024.
- **P22 (David's claim):** PASS if **50% or more** of stimulant-positive pedestrians in 2022–24 are also opioid-positive. FAIL if under 50%: then most stimulant-positive pedestrians had no opioid, and the pedestrian story is mostly stimulants without the pair.
- **My expectation, stated beforehand:** FAIL. Fentanyl sedates, and meth keeps people up and moving, so I expect stimulant-only pedestrians to outnumber the pair. I'm not confident: in overdose deaths the pair dominates.
- **Reported, not scored:**
  1. The same share for every year 2009–2024.
  2. Fentanyl specifically, by drug-name label, instead of any opioid.
  3. Only pedestrians who died within the first hour (LAG_HRS = 0), to limit opioids given by ambulance crews or hospitals. Fentanyl is a common trauma painkiller, which pushes toward PASS.
  4. Both-positive and stimulant-only as shares of all tested pedestrians, to see which grew.
- **Weak spots:**
  - Medical opioids (above).
  - Before 2018, at most 3 results per person were recorded. That could hide a second drug, but rarely matters for 2022–24.
  - A positive test shows presence, not impairment.
  - About half of pedestrians killed have no test result.

## Round 9 results

Run 2026-11-13 (`scripts/test_ped_pair.py`, output `data/final/test_ped_pair.csv`).

**P22: FAIL.**
- **Scored measure:** in 2022–24, 836 of 3,540 stimulant-positive pedestrians killed (**23.6%**) were also opioid-positive. The rule needed 50% or more.
- **Fentanyl specifically:** 697 (19.7%).
- **Stimulant without any opioid:** 2,704 (76.4%).

Reported, not scored:
- **First-hour deaths only** (LAG_HRS = 0), to limit opioids given in care: 22.0% with an opioid, 18.4% with fentanyl. Medical opioids barely move it.
- **The pair is growing, from a small base:**
  - Share of stimulant-positive pedestrians with an opioid: 12.9% (2009), 7.6% (2015), 18.6% (2020), 24.4% (2024).
  - With fentanyl: 0.5% (2009), 1.2% (2015), 11.4% (2020), 21.1% (2024).
- **Most of the rise is stimulants without opioids.** As shares of all tested pedestrians, 2009 → 2024:
  - stimulant without opioid: 7.8% → 23.8% (+16.0 points);
  - stimulant with opioid: 1.2% → 7.7% (+6.5 points).
- **Contrast with overdose deaths:** 61% of US meth overdose deaths in 2024 also involved an opioid, against 24% of stimulant-positive pedestrians.

## P23. Drugs on fast roads: are stimulant-positive pedestrians killed on faster roads?

Pre-registered 2026-11-14, before running. The question comes from the iteration 2 discussion of chrisgottsacker's and callmemr.magoo's comments, and from the Czechia finding: lots of heavy meth users, few meth-positive dead pedestrians, mostly on 50 km/h city streets. Does the US stimulant story run through high-speed roads? The first Reel showed the rise is on arterials after dark, but never split it by drug result.

- **Data:**
  - FARS pedestrians killed (PER_TYP 5, INJ_SEV 4) with a valid drug test.
  - Stimulant = the same "primary" definition as P9: meth, amphetamine, cocaine and metabolites (`scripts/test_ped_drugs.py`).
  - **Road speed** = the posted speed limit of the road the striking vehicle was on (VEHICLE.VSPD_LIM, via PERSON.STR_VEH). Single-vehicle crashes use vehicle 1. Codes 98/99 mean unknown; they're dropped from the denominator and counted.
  - VSPD_LIM starts in 2010, so the early period is **2010–12**.
  - "Fast road" = **posted 40 mph or more**.
- **P23a (concentration):** PASS if, in 2022–24, the share of stimulant-positive pedestrians killed on fast roads is **at least 5 points higher** than the share among tested stimulant-negative pedestrians.
- **P23b (the rise):** PASS if **70% or more** of the increase in stimulant-positive pedestrian deaths was on fast roads. The increase is measured among tested pedestrians, 2010–12 → 2022–24, as three-year sums.
- **My expectation, stated beforehand:**
  - **P23b: PASS.** Most pedestrian deaths are on fast roads anyway, so most of any rise will be too.
  - **P23a: unsure, leaning FAIL.** Stimulant users may die in the same places as everyone else, since the overall rise is already concentrated on fast roads.
- **Reported, not scored:**
  1. The same comparison for alcohol (BAC 0.08+ vs. 0.00 among alcohol-tested pedestrians, PERSON.ALC_RES), to see whether any concentration is about impairment in general rather than stimulants.
  2. Functional class instead of speed (arterial vs. other).
  3. Dark only, and urban only.
  4. Testing rate by road speed. If fast-road deaths are tested more often, the comparison is biased.
  5. Fast-road share by year, 2010–2024, for stimulant-positive and stimulant-negative pedestrians.
- **Weak spots:**
  - **FARS has deaths only,** not how many impaired people walk where. A higher fast-road share among stimulant-positive deaths could mean impaired people walk near fast roads more (where cheap housing and motels are), not that fast roads kill them more readily. This test can't separate "exposure" from "lethality".
  - About half of pedestrians killed have no drug result.
  - Posted limit, not actual speed.

## Round 10 results

Run 2026-11-14 (`scripts/test_ped_roads.py`, output `data/final/test_ped_roads.csv`). Speed limit unknown for 4.7% of pedestrians killed.

- **P23a: PASS, by a hair.**
  - In 2022–24, **69.9%** of stimulant-positive pedestrians killed (2,363 of 3,382) were on roads posted 40 mph or more.
  - The share for tested stimulant-negative pedestrians was **64.8%** (5,214 of 8,041).
  - The difference is +5.03 points; the rule needed 5.
- **P23b: PASS, by a hair.**
  - Stimulant-positive deaths on fast roads went from 502 (2010–12) to 2,363 (2022–24), +1,861.
  - Under 40 mph they went from 226 to 1,019, +793.
  - So **70.1%** of the rise was on fast roads; the rule needed 70%. Another 129 had an unknown speed.

Reported, not scored:
1. **Alcohol shows the same thing.** Pedestrians at BAC 0.08+ were 70.7% on fast roads, against 64.8% for BAC 0 (+5.9). So the concentration is about impairment in general, not stimulants specifically.
2. **By road class there's no difference at all.** Arterials were 61.7% of stimulant-positive deaths and 61.8% of stimulant-negative deaths.
3. **Most of the gap is darkness.**
   - **Dark only:** 71.4% vs. 69.7% (+1.7).
   - **Urban only:** 66.6% vs. 61.3% (+5.4).
   - Impaired pedestrians die more at night, and night deaths are on fast roads.
4. **Testing rate:** 56.3% on fast roads vs. 51.2% under 40 mph. Fast-road deaths are tested slightly more often, a small bias toward PASS.
5. **The gap shrank over time.** The fast-road share was 69.5% vs. 59.2% in 2012 (+10.3) and 68.1% vs. 65.9% in 2024 (+2.2). Sober pedestrians caught up as the overall rise moved onto fast roads.

**What it means:**
- Stimulant-positive pedestrians die **where all US pedestrians die**: about 7 in 10 on roads posted 40 mph or more, mostly at night.
- They're only slightly more concentrated there than sober pedestrians, and drunk pedestrians show the same slight tilt.
- So this supports "the US kills pedestrians on fast roads, impaired or not." It gives **no evidence of a meth-specific road effect.**
- The test can't tell whether fast roads kill impaired pedestrians more readily or whether impaired people walk near fast roads more.

## P24. Did getting hit become deadlier, or were more pedestrians hit?

Pre-registered 2026-11-15, before any data is downloaded or run. The question comes from the Reel 3 discussion. Comparing the US with Czechia (`docs/reel3-skeleton-v2.md`), each US heavy meth user is about 10× as likely to die as a pedestrian, but that ratio mixes **exposure** (how often people are hit) with **lethality** (how often being hit kills). FARS has deaths only. NHTSA's injury-crash samples also count pedestrians who were hit and survived, so they can split the US *rise* into the two.

- **Data:**
  - **Deaths:** FARS pedestrians killed (PER_TYP 5, INJ_SEV 4), as in every earlier test.
  - **Hit and survived:** police-reported pedestrians injured (PER_TYP 5, INJ_SEV 1–3: possible, minor or serious), weighted national estimates (sum of WEIGHT).
    - **GES** (General Estimates System) for 2009–2015.
    - **CRSS** (Crash Report Sampling System), which replaced GES in 2016, for 2016–2024.
    - Both downloaded from NHTSA's static file site, the same host as FARS.
  - **Hit** H = injured + killed. **Lethality** L = killed ÷ H. Deaths D = H × L, so the rise splits on a log scale: log(D₂/D₁) = log(H₂/H₁) + log(L₂/L₁).
  - **Lethality share** = log(L₂/L₁) ÷ log(D₂/D₁).
- **Never compare across the 2016 GES → CRSS redesign.** It changed the sample. So the test has two segments:
  - **P24a (the start of the rise, GES):** 2009–11 → 2013–15, three-year sums.
  - **P24b (the later rise, CRSS):** 2016–18 → 2022–24, three-year sums.
- **Scoring, each segment:**
  - **Lethality share ≤ 33%:** "mostly more people hit." This **supports** the exposure reading, and Reel 1's meth mechanism along with it.
  - **Lethality share ≥ 50%:** "mostly deadlier when hit." This **cuts against** it: the rise is mainly about outcomes once hit (vehicles, crash speeds, the crash mix), not more people in harm's way.
  - **Between:** mixed.
  - **Inconclusive:** the change in H is within its sampling error. Use NHTSA's published standard errors for pedestrian injury estimates, or the design variables (PSU, strata) if those are workable.
- **My expectation, stated beforehand:** unsure, leaning toward **mixed** in P24a. From memory, and unverified, NHTSA's yearly fact sheets show pedestrian injuries rising more slowly than deaths in 2009–2015. If that holds, lethality rose too. This test can embarrass the exposure reading.
- **Reported, not scored:**
  1. **Serious injuries only:** L_serious = killed ÷ (serious injured + killed). Minor and possible injuries are the most under-reported, and police reporting practices change.
  2. **L by light condition** (dark vs. daylight), and by posted speed where the file has it. A shift of crashes into the dark or onto fast roads raises L without any single crash getting deadlier.
  3. **H and L by year,** 2009–2024, drawn with the 2016 break marked.
  4. **2020–21 separately:** pandemic traffic changes.
- **Weak spots:**
  - **Police-reported injuries only.** Many minor pedestrian injuries are never reported, and the reporting rate may change over time.
  - **L mixes "the same crash got deadlier" (vehicles, speeds) with "the crash mix changed"** (more night and arterial crashes, frailer or impaired victims). Unscored item 2 shows part of that; it can't fully separate them.
  - **No drug results** for injured pedestrians in GES or CRSS, so this splits the *whole* rise, not the stimulant bucket.
  - **Sampling error,** especially for serious injuries.

## Round 11 results

Run 2026-11-15 (`scripts/test_ped_lethality.py`; outputs `data/final/test_ped_lethality.csv` and `.txt`; files fetched by `scripts/fetch_ges_crss.py`).
- **Sanity check against NHTSA's published injury estimates:** our injured counts plus the "injured, severity unknown" group give about 58,400 (2009), 74,800 (2012) and 66,600 (2022). NHTSA's yearly fact sheets give about 59,000, 76,000 and 67,336.

**Scored, exactly as pre-registered: both segments are INCONCLUSIVE.** In each, the change in pedestrians hit was within sampling error.

| Segment | Deaths (FARS) | Injured (weighted) | Hit | Lethality L | Lethality share (95%) |
|---|---|---|---|---|---|
| **P24a** GES, 2009–11 → 2013–15 | 12,868 → 15,183 (+18.0%) | 186,348 → 195,575 | +5.8% (log-ratio CI −0.08 to +0.19) | 6.46% → 7.20% | **66%** (−20% to 147%) |
| **P24b** CRSS, 2016–18 → 2022–24 | 18,529 → 22,040 (+18.9%) | 226,235 → 203,997 | −7.7% (log-ratio CI −0.21 to +0.05) | 7.57% → 9.75% | **146%** (72% to 219%) |

**The pre-registered "inconclusive" rule was badly chosen for P24b.** "The change in H is within its sampling error" doesn't mean the lethality share is uncertain. In P24b the share's own 95% interval (72–219%) lies entirely above the 50% line. The score stays INCONCLUSIVE as written. On the share itself, though, the later rise was mostly "deadlier when hit."

Reported, not scored:
1. **Serious injuries only** (better reported than minor ones): the lethality share is 48% in P24a (−23% to 119%) and **34%** in P24b (−28% to 95%), which would score MIXED. Part of P24b's large share comes from fewer *minor* injuries being reported.
   - With NHTSA's imputed severity instead of raw, the results are almost identical: 69% and 143%.
2. **Dark only:**
   - **P24a: L barely moved (12.19% → 12.60%; lethality share 18%, −60% to 96%).** Crashes also moved into the dark: the dark share of deaths went 70.6% → 72.2% and the dark share of injuries 35.1% → 38.8%. Dark crashes are about twice as deadly. So **much of P24a's overall rise in L is the crash mix shifting to night**, not any one crash getting deadlier. That points to exposure, but the intervals are wide.
   - **P24b: L rose at night too (13.77% → 16.83%; share 103%, 40% to 164%).**
3. **By year:** L was 6.2–7.5% in 2009–2015 and 6.7–8.1% in 2016–2019. It jumped to **10.9–11.2% in 2020–21** and eased to 10.4%, 9.9% and 9.0% in 2022–24. Hits were about 74,000–90,000 a year in 2016–19, about 60,000–67,000 in 2020–21, and about 73,000–79,000 in 2022–24.
4. **2020–21:** the pandemic years carry most of P24b's rise in L. Comparing 2016–18 with 2019 alone, L went from 7.57% to 7.78%.

**What it means:**
- **The start of the rise (2009–15): no verdict.** The point estimate is mixed, but within night crashes lethality barely changed while more crashes happened at night. That's mildly consistent with "more pedestrians hit at night" (exposure), but not established.
- **The later period (2016–24): getting hit became deadlier, mostly in a jump in 2020–21 that has partly eased.**
  - Serious-injury data soften this to "mixed."
  - L can't separate the same crash getting deadlier (speed, vehicles) from frailer or more impaired victims, or from changes in reporting.
- **For Reel 1:** nothing here touches who died, the stimulant rise, or the state pattern.
- **For "roads didn't change" (Brumbelow):**
  - It holds for the start of the rise. Lethality per night crash didn't move.
  - After 2020 something made being hit deadlier. Candidates (not tested here): faster driving on emptier pandemic roads, heavier vehicles, frailer or more impaired victims.

## P25. Meth and deadly roads in tandem, across states

Pre-registered 2026-11-17, before any state-level numbers are computed. The question comes from Reel 3's card 44 ("meth usage and unsafe roads appear to work in tandem"). The tandem chart over time stopped in 2016, where RAND's count of heavy users stops, and no consistent US user count covers 2017–2024. This test looks at the same idea across states, in recent years, with no survey.

- **Units:** the 50 states plus DC. **Years:** 2018–2024 pooled. Both sources keep one method over these years: CDC WONDER's "2018–2024, Single Race" database, and FARS's separate drug file.
- **Meth (M):** overdose deaths with methamphetamine (T43.6) named, per 100,000 people (`data/raw/cdc_wonder/wonder_meth_state_year_2018_2024.csv`). Suppressed state-years (under 10 deaths) count as 0 and are listed.
- **Roads (R):** estimated pedestrians killed with **no stimulant found**, per million people a year. That's all pedestrians killed × the share of tested pedestrians with no meth, amphetamine or cocaine. It's the three-buckets method, which assumes untested pedestrians look like tested ones. R stands for how deadly a state's roads are for pedestrians who aren't on stimulants.
- **Outcome (Y):** estimated **meth-positive** pedestrians killed per million people a year, computed the same way (all killed × meth/amphetamine-positive share of tested). Meth codes are as in `scripts/ped_meth_vs_cocaine.py`.
- **Populations** come from the WONDER files.
- **Groups:** each state is high or low on M, and high or low on R, split at the median state. Each of the four groups' Y is pooled: its estimated meth-positive deaths ÷ its population.
- **P25a (tandem):** PASS if the high-M/high-R group's Y is **at least 1.5× the larger** of the two one-factor groups (high-M/low-R and low-M/high-R), **and** both one-factor groups are above low/low.
- **P25b (both factors count, state by state):** PASS if, in a regression of log Y on log M and log R across states (weighted by population), **both coefficients are positive with 95% intervals above 0**.
- **States** with fewer than 30 tested pedestrians in 2018–24 are dropped and listed.
- **My expectation, stated beforehand:** P25b PASS. P25a unsure, leaning PASS: the West and South are high on both, so the high/high group may be large partly because it's geographic.
- **Reported, not scored:**
  1. **Floor version:** tested and meth-positive only, per million. This needs no assumption about untested pedestrians, but it's sensitive to each state's testing rate. Each state's testing rate is reported too.
  2. **A roads measure that isn't pedestrians:** traffic deaths of vehicle occupants per million (FARS), in place of R.
  3. **Fentanyl:** 2024 only, where the state file splits it. M as meth overdoses without fentanyl (`wonder_fent_and_meth_state_2024.csv`).
  4. **Each state's M, R and Y,** and the four groups' members.
- **Weak spots:**
  - **R and Y share a factor** (all pedestrians killed), so states with many pedestrian deaths score high on both partly by construction. Item 2 checks this with a roads measure that doesn't count pedestrians.
  - **Meth overdoses aren't heavy users.** After about 2016 many are driven by fentanyl in the supply.
  - **Testing rates differ a lot by state.**
  - **States aren't independent:** neighbors share drug markets and road design. This shows a pattern, not a cause.

## Round 12 results

Run 2026-11-17 (`scripts/test_ped_tandem_states.py`; outputs `data/final/test_ped_tandem_states.csv`, `test_ped_tandem_groups.csv` and `.txt`).
- 49 states kept. Vermont and Wyoming were dropped: fewer than 30 tested pedestrians in 2018–24. Vermont's two suppressed meth state-years were counted as 0, as pre-registered.
- Medians: M 6.75 meth overdose deaths per 100,000; R 12.6 no-stimulant pedestrian deaths per million a year.

**P25a: PASS.** Estimated meth-positive pedestrians killed per million a year:

| | Safer roads (low R) | Deadlier roads (high R) |
|---|---|---|
| **Less meth (low M)** | 0.85 (15 states) | 3.33 (10) |
| **More meth (high M)** | 3.74 (10) | **7.80** (14) |

High/high is **2.09×** the larger one-factor group; the rule needed 1.5×. Both one-factor groups are well above low/low.

**P25b: PASS.** log Y = −4.81 + **1.43** log M + **1.12** log R (95% intervals 1.15–1.72 and 0.62–1.61; 49 states, population-weighted, R² 0.76).

Reported, not scored:
1. **Floor (tested positives only):** 0.51 / 1.54 / 2.75 / **4.72**, so high/high is 1.72×. Testing rates run from 7% to 91% of pedestrians killed (median 70%).
2. **Roads measured by vehicle occupants killed: the pattern disappears.** 0.81 / 4.21 / 6.95 / 5.84, high/high 0.84×. States where drivers and passengers die most tend to be rural (Mississippi, Arkansas, Montana top the list). The states deadliest for pedestrians are Florida, New Mexico and South Carolina. So the tandem holds for how deadly roads are **to people on foot**, not for traffic danger in general. Because R and Y share a factor (all pedestrians killed), part of P25a is built in. Item 2 is the check against that, and it doesn't back the result.
3. **2024 meth overdoses without fentanyl as M:** 1.02 / 2.35 / 4.36 / **7.82**, high/high 1.79×. Fentanyl isn't driving the pattern.
4. Group members:
   - **High meth, deadly roads:** AL, AK, AZ, CA, HI, KY, LA, MS, NV, NM, NC, OK, SC, TN.
   - **High meth, safer roads:** CO, IN, KS, ME, MO, OH, OR, UT, WA, WV.
   - **Low meth, deadly roads:** AR, CT, DE, DC, FL, GA, MD, MI, NJ, TX.
   - **Low on both:** ID, IL, IA, MA, MN, MT, NE, NH, NY, ND, PA, RI, SD, VA, WI.

**How big is "tandem":**
- High/high is 9.2× low/low.
- If the two factors simply **added**, high/high would be about 6.2. If they fully **multiplied**, it would be about 17.
- The real 7.8 sits between: more than adding, well short of full multiplication.

**What it means:**
- Across states in 2018–24, meth-positive pedestrian deaths are highest where **both** meth is common and roads are deadly for pedestrians. Each factor alone gives about 4× the low/low rate; together, about 9×. The pattern holds on the floor counts and without fentanyl.
- **The roads half is the weak half.** It holds only with a pedestrian-based roads measure, which shares a factor with the outcome. With traffic deaths in general it fails.
- This is states, not people, and a pattern, not a cause.
