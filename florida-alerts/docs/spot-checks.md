# Spot checks: florida-alerts

> **Public version.** The private copy also lists each check's exact values and a link to the archived FDLE report. Those columns hold exact dates and towns, which this repo leaves out (see the README).

Each check targets one stage of the pipeline where something could plausibly have gone wrong. Open the link, find the item, and fill in **Verdict** with ✅ (matches), ❌ (doesn't match, say what you saw) or 🤷 (can't tell).

Wayback links open FDLE's original PDF as archived in 2019–2021. Page numbers refer to the PDF.

**The headline numbers these checks protect:**
- **Florida Silver Alerts, 2012–2020:** 2,070 state alerts; 222 people found as a direct result (10.7%).
- **National AMBER Alerts, 2006–2024:** 3,638 alerts; 780 found as a direct result (21.4%).
- **Almost everyone is recovered,** e.g. 287 Silver Alerts and 280 recoveries in 2021.

## A. Reading FDLE's monthly totals (Wayback PDFs → `silver_monthly_totals.csv`)

| # | Item | Tests | Verdict |
| --- | --- | --- | --- |
| 1 | December 2016 and December 2017 reports, bottom lines | The yearly "direct" count is the difference between two December cumulative totals | ✅ |
| 2 | November 2019 report, bottom lines | The report wording changed and the first parser read the wrong total | ✅ |
| 3 | July 2011 report, bottom lines | Our explanation for why the direct total "drops" from 45 to 30 |  |

## B. Reading the case rows (→ `silver_monthly_cases.csv`, 2,215 de-identified alerts)

| # | Item | Tests | Verdict |
| --- | --- | --- | --- |
| 4 | December 2014, count the table rows, and rows 8 and 10 | The case-row parser drops rows | Your fix is correct. ✅ |
| 5 | July 2018, rows 12–14 | The weakest parse: age/sex written backwards ("Male/ 88"), and a place name wrapped onto two lines | Your fix is correct. ✅ |

### B2. Recovered outside Florida (→ `silver_recovery_states.csv`, chart 5 candidate)

Our data: 168 of 2,219 state Silver Alerts (7.6%), 2011–2020, were recovered outside Florida, in 22 states. Georgia 82, Alabama 22, South Carolina 14, North Carolina 8, Tennessee 6, and 17 other states with 1–5 each. These checks test the farthest cases and the rows with no recovery place.

| # | Item | Tests | Verdict |
| --- | --- | --- | --- |
| 16 | December 2014, row 21 | The farthest southwest recovery | ✅ |
| 17 | March 2014, row 8 | A full state name, no two-letter code |  |
| 18 | June 2017 (updated report), row 8 | The farthest recovery, and "Washington" = the state | ✅ (David, 2026-10-08) |
| 19 | October 2016, rows 22 and 27 | Rows where we found no recovery place |  |

## C. Which rows count as "direct" (asterisk on the recovery location)

| # | Item | Tests | Verdict |
| --- | --- | --- | --- |
| 6 | November 2016, all 15 rows | The biggest gap between the two ways of counting direct recoveries | ✅ No other marks; the report doesn't explain the +7 |
| 7 | August 2020, row 11 (Miami) | The asterisk means "direct" |  |

## D. Classifying the success stories (→ `silver_success_stories.csv`, keyword rules)

| # | Item | Tests | Verdict |
| --- | --- | --- | --- |
| 8 | November 2019, Dade County | The clearest citizen + highway-sign story | ✅ |
| 9 | October 2016, Volusia County | One of 2 stories where the finder is unclear | ✅ "Unclear" is right; the passive sentence never says who recognized her |
| 10 | August 2017, Citrus County | Two labels in one sentence | ✅ Keep "family" as its own label |

## E. Hand-typed newsletter figures (→ `newsletter_stats.csv`)

| # | Item | Tests | Verdict |
| --- | --- | --- | --- |
| 11 | Spring 2021 newsletter, page 1 box | Numbers spelled out in words, checked only by eye | ✅ |
| 12 | Spring 2024 newsletter, page 5 | The all-types 2023 rate, and the broader "direct" definition |  |

## F. National AMBER reports (→ `amber_national_yearly.csv`)

| # | Item | Tests | Verdict |
| --- | --- | --- | --- |
| 13 | 2012 report, page 27 | The year whose summary page extracted as jumbled text |  |
| 14 | 2022 report, pages 7–8 | The outlier year (8.8%), and Florida's count disagreeing with FDLE | ✅ |

## G. Scope

| # | Item | Tests | Verdict |
| --- | --- | --- | --- |
| 15 | What a *state* Silver Alert is | Whether our Silver numbers cover all Silver Alerts or only some | ✅ A state alert requires "traveling by motor vehicle with an identified license plate number or other vehicle information", after a local alert |

**Your daughter's question, for context:** Agencies with "Miami" or "Dade" in their names (Miami-Dade PD, Miami PD, North Miami Beach PD, Miami Shores PD and others) issued 120 of the 2,215 state Silver Alerts in the 2011–2020 reports. That's a name match, so neighbors like Hialeah or Doral aren't included. FDLE's success stories include 13 from Dade County, 4 of them found through the highway message signs. Check 7 is one of the 120. It's likely the same person as the August 2020 Dade success story (73-year-old male), which credits a state trooper who recognized the car from the BOLO.

## Decision rule

- **The headline stands** if checks 1, 2, 11 and 14 all pass. Those carry the numbers that go on screen.
- **If check 4 or 5 fails** (the parser dropped or mangled rows), fix the case-row parser before quoting anything from `silver_monthly_cases.csv` (ages, agencies, Miami counts). The yearly rates don't depend on it.
- **If check 6 shows markers we missed,** switch the yearly "direct" count to the row markers. **If it doesn't,** keep the cumulative totals and say on screen that FDLE's two counts differ slightly (217 vs 222 over 2012–2020).
- **Chart 5 (recovered outside Florida) is cleared** only if checks 4, 5 and 16–19 all pass. One ❌ among 16–18 means fixing the state reader. A ❌ on 19 means the parser is missing a recovery place.
- **If 2 or more of checks 8–10 are wrong,** don't put the "who found them" breakdown (citizens 107, law enforcement 84) on screen until the rules are fixed.
- **Any ❌ on 3, 12 or 15** means the definition caveats in the script need rewording, not the numbers.

## Results (2026-10-07, updated 2026-10-08)

| Stage | Checked | ✅ | ❌ | 🤷 | Open |
|---|---|---|---|---|---|
| A. Monthly totals | 1, 2 | 2 | 0 | 0 | 3 |
| B. Case rows | 4, 5 | 2 | 0 | 0 | |
| B2. Recovered outside Florida | 16, 18 | 2 | 0 | 0 | 17, 19 (Wayback returned 429s) |
| C. Direct markers | 6 | 1 | 0 | 0 | 7 |
| D. Success-story labels | 8, 9, 10 | 3 | 0 | 0 | |
| E. Newsletter figures | 11 | 1 | 0 | 0 | 12 |
| F. National AMBER | 14 | 1 | 0 | 0 | 13 |
| G. Scope | 15 | 1 | 0 | 0 | |

**Decision:**
- **The headline stands.** Checks 1, 2, 11 and 14 all pass, and those carry the numbers that go on screen: about 1 in 10 for Florida Silver Alerts, about 1 in 5 for AMBER nationally, and nearly everyone recovered.
- **Check 6: the yearly "direct" count stays on FDLE's cumulative totals.** The November 2016 report has no other marks and no explanation for its +7. If the script cites a count, it should say FDLE's own two counts differ slightly (222 from its running totals, 217 marked row by row, 2012–2020), so 10.5% to 10.7%. (This read 216 before the parser fix of 2026-10-08, which recovered an asterisk that had wrapped onto a second line.)
- **The "who found them" breakdown can go on screen** (checks 8–10 pass): citizens 107, law enforcement 84, the person themself 3, family 1, unclear 2, out of 197 FDLE success stories (2014–2022). These are FDLE's chosen success stories, not all recoveries.
- **Scope confirmed** (check 15): the 2011–2020 Silver numbers are *state* Silver Alerts, meaning a person missing in a vehicle with a known plate, after police have issued a local alert. A Silver Alert on a highway sign is by definition a state alert, so it's in scope.
- **Case-level details can be quoted** (checks 4 and 5 pass against the fixed parser): ages, agencies, recovery places and the Miami counts.
- **Chart 5 goes ahead on David's call (2026-10-08).** Check 16 (Phoenix, AZ) passed. Checks 17–19 couldn't be completed because the Wayback Machine returned 429 (too many requests), and David chose to move forward without them rather than wait. The rule above asked for all of 16–19, so chart 5 rests on checks 4, 5 and 16 plus the parser diff. If the Reel names a specific far-away case (Puyallup, WA or Bloomington, Minnesota), recheck that one row first.
- **Not checked, lower stakes:** 3, 7, 12 and 13.
