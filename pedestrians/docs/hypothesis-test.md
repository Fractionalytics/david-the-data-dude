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
- **Why it may be negative:** unsheltered homelessness grew most on the West Coast and in the Northeast (California +98 per 100,000, Hawaii +74, Washington +65, DC +48), where pedestrian deaths rose modestly. Pedestrian deaths rose most in Sun Belt states where unsheltered counts *fell* (New Mexico, Louisiana, Georgia, Mississippi, Florida). And the 2009 base is unusual in places: Louisiana's count was still swollen after Hurricane Katrina, and Florida's by the recession.
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
