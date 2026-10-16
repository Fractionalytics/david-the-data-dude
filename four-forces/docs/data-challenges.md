# Data challenges: Amara's Law

The data problems we hit while testing "AI takes some jobs fast, some slowly, and some predicted changes never come." Logged as they came up, with the numbers.

## 1. BLS's newest occupation years can't be fetched the way older years can

OEWS May 2019, 2022 and 2023 sit in plain HTML tables on bls.gov. May 2024 and May 2025 moved to a JavaScript app (data.bls.gov/oes) that a script can't read. The BLS public API has May 2025 but returns "No Data Available" for May 2024. So a 2022–25 trend line currently has a hole in 2024 until the `oesm24nat.zip` file is downloaded. And that download is blocked too: on 2026-10-15 bls.gov served its HTML pages to the research agent's fetcher, but returned **403 Forbidden** to a plain command-line request for the `oesm{YY}nat.zip` files. (The Radiology project had every bls.gov page blocked.) We stopped there; the files need a browser download or a registered BLS API key.

## 2. The two government job counts disagree, sometimes on direction

- **Size:** "computer programmers" are 381,000 in the household survey (CPS, 2025) but 92,230 in the employer survey (OEWS, May 2025). People call themselves programmers when employers classify them as developers.
- **Direction:** bookkeeping clerks fell 11.4% from 2022 to 2025 in OEWS but *rose* in CPS (1,132k to 1,254k).

Pick one series per chart and never mix them.

## 3. The employer survey smooths away sudden change

BLS says it "does not encourage" using OEWS as a time series. Each May estimate pools three years of survey panels, so May 2025 still contains responses from late 2022. A fast AI effect would show up in OEWS late and blurred, which works against the "fast" category the story wants to test.

## 4. Many "AI-exposed" jobs were shrinking long before ChatGPT

Computer programmers fell 33.5% from 2019 to 2022 (OEWS), *before* ChatGPT, and another 30.5% from 2022 to 2025. Telemarketers fell 28.4%, then 39.5%. A drop after 2022 means nothing without the trend before it. Customer service reps are the cleanest break found so far: −1.3% from 2019 to 2022, then −9.9%.

## 5. The headline entry-level number depends on whose payroll you look at

Stanford's "Canaries" paper finds young workers in AI-exposed jobs 19% behind their peers in ADP payroll data (the August 2026 revision). The same comparison in the Census Bureau's ACS gives about 2 points for 2022–24, against 13 in ADP over the same window. The two agree in professional, information and finance jobs but split in education, health and public administration. The direction holds up across datasets; the size doesn't.

## 6. A month that was never collected still has a number

The CPS wasn't collected in October 2025 because of the government shutdown (BLS's 2025 annual averages cover 11 months). Yet the NY Fed's recent-graduate file has an October 2025 value (recent grads 5.811%, all workers 4.183%). Its values move smoothly from month to month, which suggests a moving average, but the file doesn't say which, and doesn't say how the missing month was filled. Ask or check the NY Fed's methodology before leaning on any single month, and treat month-to-month wiggles as smoothed, not raw.

## 7. One year can jump 16% and then fall back

The OEWS files (verified 2026-10-15) show technical writers at 47,970 (2023), 55,530 (2024), 45,500 (2025): up 16%, then down 18%, with a reported relative standard error of only about 2%. Writers and authors carry an RSE of 5–8%. Single-year moves in small occupations can be artifacts of the survey's rotating panels, so compare endpoints several years apart and show the RSE.

## 8. The employer survey can't see partners or solo practitioners

OEWS counts wage-and-salary employees only. Law-firm partners and solo practitioners aren't in the 754,500 lawyers. Ratios like "paralegals per lawyer" therefore mix employed lawyers (associates, in-house, government) with the support staff of firms whose partners are invisible. The Radiology project hit the same wall: radiology-group partners are missing from OEWS.

## 9. Census quietly moved a flood of filings from one bucket to another

From late 2024, a wave of business applications "associated with internet sales" looked like high-propensity (likely-to-hire) filings but rarely hired anyone. In the January 2026 release, Census removed them from the high-propensity series for the whole history, which put them in the "likely non-employer" bucket that measures solo businesses. Before the fix, high-propensity applications looked like about 200k a month in late 2025; after it, about 140k. Any "solo business boom" chart built on total minus high-propensity filings carries this reclassification, and Census's annual revision on 2026-11-12 will restate 2021–26 again. The Census API also now refuses requests without a key, so the series came from FRED's copies.

## 10. A code change knocks the biggest AI-exposed job out of the comparison

To compare 2019 with 2025, an occupation has to exist under the same code in every year. May 2019 used a hybrid code that lumped software developers and QA testers together (15-1256), so software developers, at 1.69 million the largest occupation in the "very high" exposure group, drop out of the balanced panel along with 72 other occupations. The panel still covers 93.8% of May 2025 employment, but the single most-discussed AI job isn't in the headline comparison. Developers grew 10% from 2022 to 2025, so including them would narrow the gap slightly.

## 11. Two BLS surveys tell different stories about *when* call-center jobs fell

The occupation survey (OEWS) shows customer service reps nearly flat from May 2022 to May 2023 (−0.7%), then falling about 4.7% a year. That reads like slow diffusion after ChatGPT. But OEWS pools three years of panels, so it shows sudden change late. The monthly industry survey (CES, telephone call centers, NAICS 56142) has no such lag. It shows the call-center industry **already down 11.5% in the year before ChatGPT launched (November 2021 → November 2022)**, then 11.2% from May 2022 to May 2023, and 31.0% from August 2022 to August 2026 (439.8k → 303.3k). That comparison uses the same month at both ends because the series isn't seasonally adjusted; an earlier November-to-August comparison mixed months and has been dropped. Total US payroll jobs rose 3.7% over the same months. The two count different things (an occupation everywhere vs. everyone at call-center firms), but the timing lesson holds: OEWS's slow first year is probably the survey's smoothing, not a diffusion lag.

## 12. The 870K can't be split into job groups honestly

David's card 11 note asked to show how the 870K breaks out by category. Computing each occupation group's share of the gap gives parts that don't add up: sales jobs grew so much that they count as a −470K "negative gap," and business and finance jobs boomed during COVID and then slowed, so the pre-2022 adjustment inflates their share. Forcing the parts to sum to 870K would be a made-up split. Card 11 instead shows the four biggest actual job declines among very-high-exposure occupations (May 2022 → May 2025). All four are office work, led by customer service (−284K).
