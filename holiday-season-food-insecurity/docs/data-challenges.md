# Thanksgiving Food Insecurity: data challenges

The inside look at what went wrong with the data, logged as it happened.

1. **The turkey's increase depends on which 2025 turkey you use.** David's brief has turkey up 10.1% to $23.68, which implies a 2025 turkey of $21.51 and makes turkey 63% of the basket's $3.45 jump. Coverage of AFBF's 2026 survey says turkey rose $2.38, which implies $21.30 in 2025, an 11.2% rise, and 69% of the jump. The Ohio Farm Bureau page also prints $22.63 for the turkey in one table, which matches neither. AFBF's own release decides it.

2. **"4.5 million fewer on SNAP" is two numbers mixed together.** USDA's monthly counts fell from 42,017,404 people (July 2025) to 37,011,096 (April 2026), a drop of 5.0M (11.9%). The 4.5M figure is CBPP's projected fiscal-year average decline (FY2026 vs FY2025), a different measure. Econofact has 5.5M from July 2025 to July 2026. USDA's monthly figures are preliminary and get revised.

3. **The national "worse" measure was cancelled.** USDA announced on 2025-09-20 that it would end the Household Food Security report. The last edition covers 2024 (13.7% of households, the highest since 2014). Sources disagree on when that last report came out: 2025-10-22, or quietly in December 2025. There is no national 2025 or 2026 food-insecurity rate from USDA to compare with the 2022 peak-price year.

4. **Average wages kept up with most bills.** BLS, October 2022 to October 2026: shelter +19.5%, electricity +17.4%, car insurance +34.1%, but piped gas −0.3%, medical care +7.5%, food at home +8.2%, all items +13.3%. Average hourly earnings rose +16.2% (all private) and +17.0% (production and nonsupervisory). For the average worker, only shelter and car insurance clearly outran pay. The squeeze story has to be about households whose income didn't rise with wages (SNAP leavers, fixed incomes, the jobless), and national averages can't show that. Pulled by `scripts/fetch_cpi.py` into `data/cpi_wages.csv`.

5. **The average hides the bottom, and the bottom has no 2026 income data except for full-time workers.** BLS usual weekly earnings, Q3 2022 to Q3 2026, with CPI +13.1%: 10th percentile $560 → $634 (+13.2%, real +0.1%), 25th +17.3%, median +15.1%. So the lowest-paid full-time workers just kept pace with overall inflation, but not with shelter (+19.5%), electricity (+17.4%) or car insurance (+34.1%). Nothing covers part-time workers, the jobless or SNAP households for 2026. (I first told David the Census income-by-quintile data stopped at 2024. It doesn't: the 2025 report came out 2026-09-15, with record median income, poverty down to 10.2%, and the bottom fifth at 3% of income. Axios says lower earners lost ground. It covers 2025, mostly before the SNAP cuts.) BLS also left October 2025 blank (the shutdown), which broke the first script run. `scripts/fetch_low_end.py`.

6. **"Redundant," but nothing repeats it.** USDA called the report "redundant, costly, politicized, and extraneous." Each survey still running measures something different. Purdue's Consumer Food Insights uses USDA's 6-item module on about 1,200 adults a month (2025: 14.2%, 1.7 points above its own 2024). Urban's WBNS asks adults about their household (24.2% in December 2025). Census HTOPS, a federal survey, asks about food *insufficiency*, a narrower measure. None of them is the 30,000-household CPS supplement, and their levels can't be spliced onto USDA's 13.7%. Only trends within one source compare. One search summary also called the last report "2024, covering 2023 data". It covers 2024.

7. **The one federal food measure still running points the other way.** Census HTOPS, "sometimes or often not enough to eat" in the last 7 days: 11.5% of adults in September 2022, 6.7% in September–October 2026. The wording is the same, but the survey isn't: Household Pulse (2022) became HTOPS, a fresh mail-invited sample each round with a 10–12% response rate. The tables publish only weighted counts, so the shares were computed in code, leaving out "did not report". Counting non-reporters in the denominator gives 10.2% and 6.1%.

8. **Three blocked doors.** evictionlab.org, fns.usda.gov (and fna.usda.gov) and 211counts.org all returned HTTP 403 to automated requests, even for robots.txt. Their terms of use couldn't be read, so the agents stopped. The latest SNAP counts are secondhand (FRAC, news), and USDA revised its past months on 2026-09-22.

9. **A delinquency rate labelled two ways.** The research agent reported credit-card serious delinquency as "annualized quarterly, 3.69% → 6.87%". Rerunning its parser on the NY Fed workbook gives 3.69% → 6.90% as a four-quarter moving sum, the same basis as the zip-code-income series. The moving-sum figures are the ones used.

10. **"Turkey costs up 60%" for food banks.** It comes from one NBC Philadelphia story about one New Jersey food bank, with no comparison period. USDA's wholesale frozen-hen price for Q4 2026 is forecast at 175.0¢/lb, +1.6% over Q4 2025. The 2026 annual average is +29%, and Q1 2026 vs Q1 2025 is +79%. Whether the claim sounds true depends on which months are compared.

11. **NEADA disagrees with itself on utility debt.** Its 2026 documents say "about $25B" in some places and "approaching $23B" in others, with no as-of date. Its July 2026 release also calls EIA's 13.4M shutoff *events* "more than 13 million households".

12. **USDA's revision flipped my own correction.** In entry 2, I called the brief's "−4.5M (−11%), July 2025 to April 2026" wrong, using news figures of 42,017,404 → 37,011,096. USDA's Keydata report (generated 2026-11-13, after the 2026-09-22 revision) has 41,599,407 → 37,108,727: −4.49M (−10.8%). The brief was right. Through August 2026 the drop is −5.73M (−13.8%). The file covers only FY2025–FY2026, and recent months are preliminary.

13. **The first Eviction Lab file was the wrong one.** David's download, `tract_proprietary_valid_2000_2018_y2024m12.csv` (35MB), is tract-level filings for 2000–2018. It's no help for 2026. The 2026 numbers live in the Eviction Tracking System's own directory (`/ets`). Eviction Lab's terms page lists only required citations, one per directory.

14. **211 Counts was down for everyone.** On 2026-11-23, 211counts.org gave David's browser a Cloudflare "bad gateway" and gave one scripted request a 403. Fall-2026 211 numbers stay missing. The latest figures in hand are the October 2025 shutdown spike.

15. **Eviction Lab's column names mislead, and its cities report on different schedules.** In the ETS monthly file, the column called `filings_2020` holds each month's filings for every year from 2020 to 2026. The "states" file labels rows `rhode_island` that carry Arkansas FIPS codes (05…), or no state at all, so I didn't use it. The 43 cities' 2026 data ends anywhere from June to November. The comparison uses January–July for the 39 cities with data in 2022, 2025 and 2026. The downloads total about 700MB (the weekly file is 358MB), so they're gitignored and only the derived table is kept.

16. **"21.5 million behind on energy bills" isn't new.** NEADA said about 20 million households (1 in 6) were behind in August 2022, and says about 21.5 million (still "roughly 1 in 6") now. The count barely moved. The debt grew: $16.1B (Aug 2022) → $21.4B (Mar 2025) → about $23–25B (2026; NEADA's own documents disagree).

17. **One agent read a Nashville number backwards.** An earlier research pass logged a Nashville pantry's "donations down 40%". WSMV (2026-11-19) reports requests for help up 40%. A second check caught it.

18. **"USDA cut $1B in food-bank aid" mixes two programs.** The March 2025 cancellation of Local Food Purchase Assistance (about $420M, food banks) came alongside Local Food for Schools (about $660M, school meals). The roughly $500M of TEFAP deliveries cancelled the same month is a third, separate cut. Feeding America says TEFAP pounds fell 30% from FY2024 to FY2026.

19. **BNPL late-payment rates vary twofold by source.** For people using buy-now-pay-later: 47% paid late in the past year (LendingTree, opt-in panel), 26% (Fed SHED, representative), and 4.1% of *loans* got a late fee (CFPB, lender data, 2023). Among BNPL grocery users the Fed's figure is 43% late fee or overdraft. Each counts something different, so only the Fed numbers stand for the country.

20. **The SNAP drop is more than double what the law was scored to cause.** CBO estimated the work rules would cut about 2.4M people in an average month over 2025–2034. Observed: −5.73M from July 2025 to August 2026, after a −0.74M slide that began before the law (Jan–Jun 2025). No source splits the drop by cause. About 2M of it is children (a CBPP extrapolation), mostly outside the work rules.

21. **"Non-SNAP pantry visits up 6.5%" has three possible baselines and one hidden mix.** The Central Pennsylvania Food Bank's post (2026-05-26) says only "since February 2026". Coverage reads it as February–April 2026 vs the same months of 2025, and the food bank's later report measures from January 2025 (non-SNAP +10.3%, SNAP +7.0%). The "non-SNAP" group also mixes people who were never eligible with people who just lost SNAP: central Pennsylvania's rolls fell 10.9%, about 40,000 people. So it can't on its own show "earns too much for SNAP". The post doesn't say how pantries record SNAP status.

22. **AFBF disagrees with itself on the turkey, and David's brief was right.** AFBF's 2025 release put the turkey at $21.50, and its 2026 release at $23.68: +$2.18 (+10.1%), 63% of the dinner's $3.45 rise. AFBF's Market Intel piece says +$2.38, and news copied that, which made entry 1 look like a conflict. The 63% / +10.1% in David's first brief matches AFBF's two releases.

23. **The SNAP income line moved while we were checking it.** The FY2026 limits I quoted from memory ($1,696 a month for one person, $2,888 for three) were right, but FY2027 started 2026-10-01: $1,729 and $2,960 (CRS, 2026-11-04). At the new line, a family of three earning the 10th-percentile full-time wage (about $33,000) is under the limit, not "right at" it. Social Security has also announced its 2027 raise (3.6%), so "this year's raise" is ambiguous in late 2026.

24. **A quote attributed to the wrong person.** "Feeling the pinch" from "cuts to SNAP" is widely credited to Dollar General's CFO on the Q1 2026 call. The transcript has neither phrase; the only SNAP remarks are the CEO's ("reductions in SNAP benefit payment"). The wording traces to Reuters via NACS Daily, so it may be a reporter's paraphrase.

25. **Local Thanksgiving numbers shrank on inspection.** Of nine local figures from the first research pass, two had no findable source (Youngstown +5%, a Nashville +14%), one was misdescribed (Fairbanks "flat" is actually "abnormally high" need), and San Antonio's +17% is food demand, not people served. Phoenix's turkey shortfall moved during the season (about 11,500 short on Nov 11, about 2,000 on Nov 23), and a 2021 story has a near-identical "2,200 short" figure.

26. **Blocked doors, second round.** cbo.gov, cbpp.org, usda.gov, fns.usda.gov, ssa.gov, axios.com, ktar.com and newsfromthestates.com returned 403. So the CBO noncitizen estimate, CBPP's 2M children and the end date of emergency allotments still come through intermediaries. The audit found a second request to cbo.gov and to cbpp.org after a 403, against the stop-on-block instruction. Both were refused again, and nothing was obtained.

27. **"Health insurance" in the CPI fell 34.6%.** From October 2022 to October 2026, the CPI's health-insurance index dropped by a third. BLS measures it indirectly, through insurers' retained earnings, so it swings with insurer profits rather than the premiums families pay. It's left out of the essential-costs comparison.

28. **"$1.11B" was a monthly level, not a monthly loss rate.** SNAP paid $7.82B in July 2025 and $6.70B in August 2026, so the monthly level is $1.11B lower. Claude first wrote "−$1.11B a month", which reads like a loss every month. Summed, the August 2025–August 2026 shortfall against the July 2025 level is $7.56B. Comparing the same October–August months of FY2025 and FY2026, it's −$9.5B.

29. **Is there really no other government measure?** CDC's National Health Interview Survey has asked a 10-item, 30-day version of USDA's food-security questions (5.9% of adults in 2021). If its 2025 survey still does, "no other government report measures it" is wrong. CDC's preliminary 2025 codebook (75 pages, Q2 early release) has no food-security items, but it covers selected variables only, so that absence isn't proof. Unresolved. Census's weekly survey also asks a narrower "enough to eat" question.

30. **Purdue's survey can't see the people this story is about.** Purdue's Consumer Food Insights uses USDA's six-question short form, not the 18 questions the national report used. It also counts a household as food insecure only if its income is under 185% of the poverty line, so the "earns too much for SNAP" group is mostly invisible to it.

31. **The "is it really redundant?" inventory came too late.** CDC's survey (entry 29) surfaced during the third script review, after David had already written card 6 around "no other government report measures it". A full inventory, run once he asked, found 12 sources:
    - The CDC survey's food-security section was paid for by USDA and was dropped after 2024. Its 2024 survey outline lists "FDS Food Security"; the 2025 outline doesn't.
    - USDA's December 2025 survey was never fielded.
    - Four federal surveys still ask USDA's questions but publish no national rate.
    - The only 2025–26 federal numbers measure food insufficiency (one question), not food insecurity.
    - Purdue's tracker ended in April 2026.

    The lesson: when a story's claim is "nothing else exists", run the full inventory of what could exist before the script is written, not card by card during reviews.

32. **The shutdown left a hole in the inflation math.** Adjusting each year's Thanksgiving dinner for inflation uses October's CPI, because AFBF's shoppers price the dinner around then. BLS never published October 2025 (the federal shutdown), so 2025 uses the average of September and November 2025. AFBF's own historical-pricing PDF has also moved (fb.org returned a 404), so 2019–2021 and 2023–2024 prices come from fb.org's release pages.
