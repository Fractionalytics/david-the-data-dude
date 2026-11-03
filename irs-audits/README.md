# IRS Audits: how likely are you to get audited?

The fear is big; the odds are small. This folder works out the real odds of an IRS audit from the IRS's own Data Book, band by band, and how many of those audits happen in person rather than by mail.

This folder is the behind-the-scenes companion to David the Data Dude's Instagram Reel.

<p align="center">
  <a href="https://www.instagram.com/reel/DfShYlsyQYf/"><img src="cover.jpg" alt="Reel cover: IRS Audits" width="300"></a>
  <br>
  <b>▶ <a href="https://www.instagram.com/reel/DfShYlsyQYf/">Watch the Reel on Instagram</a></b>
</p>

## The result

Of the 161,206,833 individual tax returns filed for 2021, the IRS had audited 510,375 by September 30, 2025: **about 1 in 316**.

| Income band | Returns filed (2021) | Audited | Odds | In person (audits closed FY2023–25) |
|---|---|---|---|---|
| $1–$50K | 82,662,484 | 310,411 | 1 in 266 | 5% |
| $50K–$200K | 62,861,997 | 97,889 | **1 in 642** | 22% |
| $200K–$500K | 9,597,600 | 21,062 | 1 in 456 | 23% |
| $500K–$1M | 1,779,838 | 10,645 | 1 in 167 | 25% |
| $1M–$5M | 867,592 | 8,174 | 1 in 106 | 46% |
| $5M–$10M | 71,862 | 2,771 | 1 in 26 | 85% |
| $10M+ | 51,250 | 3,375 | **1 in 15** | 86% |

- **$50K–$200K is the safest band**, at 1 in 642. If you're audited, it's almost certainly by mail.
- **Above that, the odds rise with income**, and so does the chance an audit is in person: $10M+ returns are audited at 1 in 15, and 86% of those audits are in person.
- **Under $50K, the odds are 2.4 times those of the next band up** (0.38% vs. 0.16%). The reason is the Earned Income Tax Credit (below).

## Why under $50K is audited more: the EITC

- **The credit's audits fill the gap.** 224,123 of the 32,216,183 returns claiming the EITC for 2021 were audited (1 in 144). If they all sit under $50K, which the IRS doesn't state (see `docs/data-challenges.md`, 8), they're about 72% of that band's audits, and the rest of the band is audited at 0.17%, the same as $50K–$200K.
- **Nearly all of them are by mail.** 98.9% of EITC audits closed in FY2025 were correspondence audits (92,817 of 93,857).
- **What the credit is.** The Congressional Research Service describes it as a way to "lighten the burden of Social Security taxes on low-income workers" (RS20470) and "one of the federal government's largest antipoverty programs" (R44825). Running it through the tax return costs the IRS "less than 1% of benefits delivered" (R43873, quoting the National Taxpayer Advocate).
- **Its reach.** In 2024 the EITC and the refundable Child Tax Credit together kept 6.8 million people out of poverty under the Supplemental Poverty Measure, next to 28.7 million for Social Security and 3.6 million for SNAP (Census P60-287, Table B-7). Census publishes no EITC-only figure, and these effects don't add up.

## Definitions

- **Audit:** a return the IRS examined (Data Book Table 3-1, "returns examined"). It includes audits by mail. It doesn't include CP2000 underreporter notices (987,460 cases closed in FY2025, Table 3-8) or math-error notices (1,440,328, Table 3-9), the letters people often mistake for audits.
- **Odds:** returns audited ÷ returns filed for tax year 2021, as of September 30, 2025. 2021 is the newest year mostly past the IRS's usual three-year window; newer years look safer only because their audits aren't finished. These count returns, not people.
- **Income band:** total positive income (TPI), which counts income sources and ignores losses. The IRS's brackets are merged into seven bands by adding their returns and audits (`scripts/reel_bands.py`). "Under $50K" is $1–$50K; returns with no positive income are a separate IRS category and aren't shown. Split further, $1–$25K is 1 in 198 and $25K–$50K is 1 in 454.
- **In person:** the IRS's "field" examinations as a share of all examinations closed, pooled over FY2023–FY2025 (Data Book Table 18 for FY2023 and FY2024, Table 3-2 for FY2025). "Field" covers office audits too, and some field cases finish by mail, so it's a ceiling. The IRS doesn't publish audit type by tax year, so the odds and the in-person share don't count the exact same audits.

## Files

- `data/reel_bands.csv`: the seven bands, with returns, audits, odds and in-person shares (FY2023–25 pooled and FY2025 alone).
- `data/table_3_1_long.csv`: Data Book Table 3-1 for tax years 2010–2023, one row per year and category.
- `data/odds_by_income.csv`, `data/audit_types_by_bracket.csv`: mail and in-person audits for every IRS bracket and the EITC row. `data/audit_types_trac_fy2022.csv`: revenue agents vs. tax auditors by income (TRAC).
- `data/raw/`: the Data Book spreadsheets the scripts read, as downloaded from the IRS.
- `scripts/`: the pipeline, in order: `parse_table_3_1.py`, `audit_type_odds.py`, `audit_types_by_income.py`, `chart_odds_vs_field_share.py`, `reel_bands.py`. `requirements.txt` lists the Python packages.
- `charts/`: exploratory scatterplots of audit odds against in-person share.
- `docs/data-challenges.md`: everything that went sideways, from a newest year that only looks safest to the letters that aren't audits.
- `video/`: the Remotion source for the Reel's graphics. `videos/` has the rendered animation, without David.

## Sources

- **IRS Data Book, FY2025:** Tables 3-1, 3-2, 3-8 and 3-9; Table 18 from the FY2023 and FY2024 Data Books. [irs.gov/statistics/soi-tax-stats-irs-data-book](https://www.irs.gov/statistics/soi-tax-stats-irs-data-book)
- **Congressional Research Service:** [RS20470](https://www.everycrsreport.com/reports/RS20470.html), [R44825](https://www.everycrsreport.com/reports/R44825.html), [R43873](https://www.everycrsreport.com/reports/R43873.html).
- **U.S. Census Bureau:** [Poverty in the United States: 2024](https://www.census.gov/library/publications/2025/demo/p60-287.html) (P60-287), Table B-7, p. 51.
- **TRAC:** [IRS audits by examiner type, FY2022](https://tracreports.org/reports/706/).

## License

MIT, like the rest of this repo. The IRS and Census figures are U.S. government works; CRS reports are public. The Caveat font in `video/fonts/` is under the SIL Open Font License.
