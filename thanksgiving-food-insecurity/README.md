# Thanksgiving food insecurity: a cheaper dinner, a thinner margin

The Thanksgiving dinner for 10 costs less than it did in 2022. But the bills people can't skip rose faster than pay at the bottom, SNAP shrank, food banks are getting less federal food, and USDA stopped publishing the national food-insecurity rate after 2024. This folder holds the data behind that picture, along with the evidence that points the other way.

This folder is the behind-the-scenes companion to David the Data Dude's Instagram Reel.

<!-- REEL LINK AND COVER: the Reel posts 2026-11-25. Add cover.jpg, then replace this comment and the line below with the usual 300px clickable cover linking to the Reel. -->
<p align="center"><i>The Reel posts on Instagram on November 25, 2026. The link and cover will be added here.</i></p>

## The result

**The national count stopped.** USDA's food-insecurity rate was 13.7% of households in 2024, its last year (the peak was 14.9% in 2011). In September 2025 USDA ended the survey, calling it "redundant." Six other federal surveys touch on food, but none publishes a national food-insecurity rate:

| Survey | Status |
|---|---|
| CDC National Health Interview Survey (NHIS) | Food security section ended after 2024 |
| Census Household Trends and Outlook Pulse Survey (HTOPS) | One question (enough to eat, past 7 days) |
| Census SIPP | No published rate |
| CDC NHANES | No published rate |
| AHRQ MEPS | No published rate |
| Federal Reserve SHED | One question |

**The meal got cheaper.** AFBF's dinner for 10 cost $64.05 in 2022 and $58.63 in 2026, down 8.5%. These are the prices each year, before inflation, to match every other change below.

**The must-pay bills didn't.** October 2022 → October 2026 (BLS CPI-U):

| | Change |
|---|---|
| Shelter | +19.5% |
| Electricity | +17.4% |
| Water, sewer and trash | +21.9% |
| Child care (day care and preschool) | +20.6% |
| Pay, lowest-paid 10% of full-time workers (Q3 → Q3) | +13.2% |

**More people out of work or underemployed** (October 2022 → October 2026): long-term jobless +62% (1.21M → 1.96M), part-time workers who want full-time +32% (3.68M → 4.84M), underemployment (U-6) 6.7% → 7.9%, up 18%.

**The help shrank.**
- SNAP participants: 41.4M (August 2025) → 35.9M (August 2026), down 13%.
- About 25M of the 47.9M food-insecure people (2024) earn too much for federal food aid.
- Feeding America: for every meal its network provides, SNAP provides nine.
- Federal TEFAP food to food banks: down 30% by weight, FY2024 → FY2026.
- Private donations: down 15% at the Community Food Bank of Southern Arizona and about 20% at the Kansas Food Bank (November 2026 vs. 2025). These are local reports, not a national count.

**Need shows up anyway.**
- NBC News surveyed the 90 largest food banks in October 2026, and 48 responded. Nearly three-quarters reported more visitors this year.
- Utility debt: $16.1B (August 2022) → about $23–25B (2026; NEADA's releases give both figures).
- Credit-card balances newly 90+ days late, lowest-income quarter of zip codes: 6.2% (Q3 2022) → 10.3% (Q3 2026).
- Buy now, pay later for groceries: 14% (2024) → 29% (2026) of BNPL users (LendingTree, an opt-in panel).

**What points the other way.** This is shown in the Reel, too.
- Census's hunger measure: the share of adults whose household sometimes or often didn't have enough to eat in the past 7 days fell from 11.5% (September 2022) to 6.7% (September–October 2026). The survey changed in between (Household Pulse became HTOPS), so it isn't a clean trend.
- Official poverty fell to 10.2% in 2025, down 0.5 points from 2024. That's mostly before the SNAP drop.
- Purdue's Consumer Food Insights survey, which uses USDA's questions, rose from 12.5% (2024) to 14.2% (2025).

Without USDA's count, whether food insecurity rose after 2024 is a judgment, not a measurement. The Reel's answer is a guess: probably yes.

## Definitions

- **Food insecurity (USDA):** limited or uncertain access to adequate food. USDA measured it with an 18-question module in the Current Population Survey's December supplement, about 30,000 households a year.
- **SNAP:** the Supplemental Nutrition Assistance Program, formerly food stamps. Counts are people in USDA's national monthly data; recent months are preliminary and get revised.
- **TEFAP:** The Emergency Food Assistance Program, USDA food delivered to food banks.
- **Long-term jobless:** unemployed 27 weeks or more (BLS LNS13008636).
- **Part-time workers who want full-time:** part-time for economic reasons (BLS LNS12032194).
- **Underemployment:** the U-6 rate, which adds discouraged and marginally attached workers and part-time for economic reasons to the unemployed (BLS LNS13327709).
- **Lowest-paid 10% of full-time workers:** the 10th percentile of usual weekly earnings, full-time wage and salary workers, excluding the incorporated self-employed (BLS LEU0252911200). $560 → $634.
- **Water, sewer and trash:** BLS publishes one index for all three (CUUR0000SEHG).
- **Child care:** BLS "day care and preschool" (CUUR0000SEEB03).
- **Census hunger measure:** a share of adults who answered, leaving out "did not report," computed from Census's weighted counts.

## Where to help, or get help

- **To give:** find your local food bank at [feedingamerica.org/find-your-local-foodbank](https://www.feedingamerica.org/find-your-local-foodbank).
- **To get help:** call or text 211, or visit [211.org](https://www.211.org/) or [findhelp.org](https://www.findhelp.org/).

## Files

- `data/`: BLS prices and pay (`cpi_wages.csv`), AFBF dinner prices with an inflation-adjusted column (`dinner_real.csv`), and USDA's monthly SNAP and WIC counts (`snap_wic_monthly.csv`). `data/raw/` holds the government files the scripts read: ERS's food-security trends, USDA's SNAP Keydata workbook, and the Census food tables.
- `scripts/`: how each number was pulled. The BLS scripts use the public API (no key). `fetch_nyfed.py` downloads the NY Fed workbooks, which aren't republished here. `requirements.txt` lists the Python packages.
- `docs/data-challenges.md`: everything that went sideways, from AFBF disagreeing with itself on the turkey to a delinquency rate labelled two ways and three websites that blocked automated reads.
- `video/`: the Remotion source for the Reel's receipt-style charts. It imports layout from a shared kit that isn't published here, and its preview compositions expect speaker frames that aren't included.

## Sources

- **USDA ERS:** [Food Security in the U.S., Key Statistics](https://www.ers.usda.gov/topics/food-nutrition-assistance/food-security-in-the-us/key-statistics-graphics). USDA's release ending the survey, September 20, 2025: ["USDA Terminates Redundant Food Insecurity Survey"](https://content.govdelivery.com/accounts/USDAOC/bulletins/3f39eb1).
- **CDC NHIS:** [2025 survey outline](https://ftp.cdc.gov/Pub/Health_Statistics/NCHS/Survey_Questionnaires/NHIS/2025/2025-nhisflow.pdf), with no food security section (compare [2024](https://ftp.cdc.gov/Pub/Health_Statistics/NCHS/Survey_Questionnaires/NHIS/2024/nhisflow-508.pdf)).
- **AFBF Thanksgiving dinner survey:** [2026 release](https://www.fb.org/news-release/cost-of-thanksgiving-dinner-increases-remains-below-2022-record-high) and earlier years' releases.
- **BLS:** CPI series [CUUR0000SAH1](https://data.bls.gov/timeseries/CUUR0000SAH1), [CUUR0000SEHF01](https://data.bls.gov/timeseries/CUUR0000SEHF01), [CUUR0000SEHG](https://data.bls.gov/timeseries/CUUR0000SEHG), [CUUR0000SEEB03](https://data.bls.gov/timeseries/CUUR0000SEEB03); earnings [LEU0252911200](https://data.bls.gov/timeseries/LEU0252911200); labor [LNS13008636](https://data.bls.gov/timeseries/LNS13008636), [LNS12032194](https://data.bls.gov/timeseries/LNS12032194), [LNS13327709](https://data.bls.gov/timeseries/LNS13327709).
- **USDA FNS:** [SNAP data tables](https://www.fns.usda.gov/pd/supplemental-nutrition-assistance-program-snap) (Keydata report, August 2026).
- **Feeding America:** [Map the Meal Gap 2026](https://www.feedingamerica.org/about-us/press-room/Map-the-Meal-Gap-2026), [SNAP facts](https://www.feedingamerica.org/snapfacts), and its [federal nutrition programs fact sheet](https://feedingamericaaction.org/wp-content/uploads/FactSheet-Federal-Nutrition-Programs.pdf) (TEFAP, July 2026).
- **Donations:** [KOLD](https://www.kold.com/2026/11/14/more-people-need-fewer-food-donations-community-food-bank-southern-arizona/), November 13, 2026; [KWCH](https://www.kwch.com/2026/11/13/kansas-food-bank-feeling-pinch-costs-rise-donations-decrease/), November 12, 2026.
- **NBC News food bank survey, October 9, 2026:** [Morning Rundown](https://www.nbcnews.com/news/us-news/hunger-rural-trump-cuts-hurricane-isaias-gulf-coast-morning-rundown-rcna602461) and [West Virginia story](https://www.nbcnews.com/news/us-news/west-virginia-hunger-trump-cuts-food-stamps-gas-prices-iran-rcna601637).
- **NEADA:** [Energy Hardship Report, November 2022](https://neada.org/wp-content/uploads/2022/11/NEADA-Energy-Hardship-Report_Final.pdf) and [April 2026 release](https://neada.org/wp-content/uploads/2026/04/PresidentBudget2027Response.pdf).
- **NY Fed:** [Liberty Street Economics, November 10, 2026](https://libertystreeteconomics.newyorkfed.org/2026/11/a-look-at-the-wider-divide-in-credit-card-delinquency-by-income/).
- **LendingTree:** [BNPL statistics](https://www.lendingtree.com/personal/buy-now-pay-later-loan-statistics/).
- **Census:** Household Pulse [September 2022 food table](https://www2.census.gov/programs-surveys/demo/tables/hhp/2022/wk49/food1_week49.xlsx), HTOPS [September 2026 food table](https://www2.census.gov/programs-surveys/demo/tables/hhp/2026/2609/food1.xlsx), and [Poverty in the United States: 2025](https://www.census.gov/library/publications/2026/demo/p60-290.html).
- **Purdue:** [Consumer Food Insights, January 2026](https://ag.purdue.edu/news/2026/01/consumer-food-insights-survey-assesses-2025-grocery-spending.html).

## License

MIT, like the rest of this repo. BLS, USDA, Census and CDC data are U.S. government works. AFBF's prices, Feeding America's estimates, NEADA's, the NY Fed's, LendingTree's, NBC News's and Purdue's figures belong to their publishers and are quoted, not republished. The IBM Plex Mono fonts in `video/` are under the SIL Open Font License.
