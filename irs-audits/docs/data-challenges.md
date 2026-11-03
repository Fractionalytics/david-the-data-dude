# Data challenges: IRS Audits

The data problems we hit while working out the odds of an IRS audit. Logged as they came up, with the numbers.

## 1. The most recent year looks safest, but only because the IRS hasn't gotten to it yet

Table 3-1 (FY2025 Data Book) is a snapshot as of September 30, 2025. Tax Year 2023 shows 0.10% of individual returns examined; Tax Year 2022 shows 0.29%. That drop isn't a crackdown ending: the IRS generally has 3 years after a return is due to assess more tax (6 if income was understated by 25% or more), so audit counts for recent years fill in over time. The IRS marks 2022 and 2023 as still inside the normal statute. Tax Year 2021 is the newest year mostly done: 510,375 of 161,206,833 individual returns, 0.32%, about 1 in 316. Even 2021 can still rise a little under the 6-year rule.

## 2. Older years are frozen at different dates

Tax years 2015–2023 are as of September 30, 2025. Tax years 2010–2014 stopped being updated, each at its own date (2014 as of September 30, 2024, back to 2010 as of September 30, 2020). Fine for trends, since those years were long past the statute, but the columns aren't one snapshot.

## 3. The Data Book changed how it counts

Since the FY2019 Data Book, the IRS counts audits against returns filed for the same tax year (now Table 3-1). Before that (old Tables 17b–20), it divided a fiscal year's closed audits by the prior calendar year's returns. Audit rates quoted from pre-2019 Data Books use the old method and aren't directly comparable.

## 4. Published percentages are too rounded to use

The percentage column is rounded to 0.1 and shows "[8]" (under 0.05%) for most middle incomes in recent years, so $75,000–$500,000 in Tax Year 2023 all read the same. We recompute every rate as (closed + in process) / returns filed. For individual returns this matches every published figure to within rounding. For 21 corporate cells the IRS figure differs by up to 2.4 points (e.g. corporations with $5–20 billion in assets, TY2013: published 50%, counts give 47.6%); the footnotes don't explain it. Corporate rows aren't used here.

## 5. Some counts are hidden for privacy

Cells marked "d" are suppressed so no single taxpayer can be identified, though they're included in totals. One affects us: in-process audits of EITC returns for Tax Year 2015, so that year's EITC rate can only come from the published 1.2%.

## 6. "Income" here means total positive income, not AGI

The income brackets use total positive income: every positive income amount on the return, ignoring losses. A filer with large business losses can land in a high bracket while showing low AGI. The "No total positive income" row (2.9 million returns in TY2021, audited at 1.85%) is its own category, not simply the poorest filers.

## 7. The audit-rate table doesn't say what kind of audit, and the one that does counts a different thing

Table 3-1 counts every examination the same way, whether a letter asking about one line or an in-person field audit. We first logged that no Data Book table splits them; that was wrong. Table 3-2 does, by income, but its title ("Recommended additional tax, and returns with unagreed additional tax") hid it. Two catches:
- Table 3-2 counts audits **closed in a fiscal year** (FY2025: 441,578 individual audits, 89.2% by mail), not audits of a tax year's returns. To get "odds of an in-person audit" we multiply TY2021 coverage by FY2025's in-person share, assuming the mix for TY2021 returns matches the mix of audits closed in FY2025. It's an approximation, not a published figure.
- "Field" in the Data Book combines field and office audits, and it isn't strictly in person: footnote 2 says field exams are "generally performed in person" but "some field examinations may ultimately be conducted through correspondence". So "in person" overstates it slightly, and 47,811 is a ceiling. No current table separates office from field; the closest is TRAC's FY2022 count from IRS management reports (revenue agents 52,773; tax auditors 40,822).

We tested that assumption, and it's weak. The Field share moves a lot by year: $25,000–$50,000 went 11.7% (FY2023), 7.6% (FY2024), 3.6% (FY2025); $200,000–$500,000 went 32.4%, 28.4%, 14.0%. Audits of TY2021 returns would mostly have closed around FY2023–FY2025, so pooling those years fits better than FY2025 alone: 7.6% and 23.0% for those two bands. It's still not the same audits, because the IRS doesn't publish audit type by tax year. FY2025 closures also aren't TY2021's audits in size: $500,000–$1,000,000 closed 23,004 in FY2025 against 10,645 ever examined for TY2021.

The mail share rose overall, with one dip: 79.5% of individual audits closed in FY2020, 84.9% in FY2021, 85.1% in FY2022, 84.4% in FY2023, 86.4% in FY2024, 89.2% in FY2025 (Tables 18 and 3-2 of each year's Data Book). Field audits of individuals went from 92,795 in FY2020 to a peak of 99,591 in FY2021, then down to 47,811 in FY2025.

## 8. EITC audits can't be placed in an income bracket exactly

Table 3-1 shows EITC returns as a separate row whose audits are "included in the appropriate TPI classes above", without saying which ones. To test whether the heavy audit rate under $50,000 is EITC-driven, we assume every EITC audit sits under $50,000 of total positive income. That's close but not exact: in 2021 the credit phased out at about $57,000 for a family with three children, and TPI can run above AGI. Under that assumption, EITC audits were 72% of under-$50,000 audits in TY2021 (224,123 of 310,411), and the remaining under-$50,000 filers were audited at about 0.17%, the same as $50,000–$200,000 (0.16%). The precise split would need return-level data the IRS doesn't publish.

## 9. The letters people dread most often aren't audits

Table 3-1 counts examinations only. An Automated Underreporter notice (a CP2000, sent when a W-2 or 1099 doesn't match the return) and a math-error notice aren't counted there. In fiscal 2025 the IRS closed 987,460 underreporter cases with a notice (Table 3-8) and sent 1,440,328 math-error notices (951,789 on 2024 returns plus 488,539 on earlier years; Table 3-9). These are fiscal-year counts, not per tax year, so they can't be divided by the same returns-filed figure as audits without a mismatch. The units differ too: one is closed cases, the other notices, and a mail audit is itself a letter, so "letters vs. audits" isn't a clean split. We first blurred this ourselves, and described math errors as typos when the IRS definition also covers failing eligibility rules and unsupported claims.

Only audits can be split by income. Tables 3-8 and 3-9 have no income rows, and we found no published split of underreporter cases. On math errors, the IRS told the Taxpayer Advocate in 2018 that it "does not track, report, or collect this data" on recipients' income. The Advocate's own run gives only median income for 12 selected error types in calendar 2017, from $13,238 to $85,488. So "notices per audit, by income" can't be computed.

Table 3-2's income rows also don't add up to its total, and our first bracket table missed why: 2,463 audits (2,447 of them Field) are on international returns, which have no income bracket. The income rows add to 439,115 of 441,578.

## 10. Sixty years of audit rates, three different rulers

The trend goes back to at least 1965, but in three regimes. The Commissioner's Annual Reports (to 1999) and Data Books through FY2018 divide audits closed in a fiscal year by returns filed the year before; Table 3-1 counts a tax year's returns ever audited. The income brackets change too: none in 1965, nonbusiness vs. business splits in 1980, AGI in Table 9b (FY2008–2018), total positive income in Table 3-1. Even the overall line has a suspicious cliff: 1.67% in FY1995 to 0.49% in FY2000, during the same years service-center exams shrank. We found no IRS note of a counting change, so it may be real or a break. The 1960s–1990s reports are scanned PDFs with garbled OCR, so their numbers were read off the page images. FY1965 gives only counts (3,092,000 individual and fiduciary returns examined, 66,952,000 filed), so its 4.6% rate is ours, not the IRS's.

## 11. The Data Book changed what it publishes about Schedule C

Through FY2018, Table 9a split audit rates by return type: Schedule C filers by gross receipts, EITC returns by receipts, nonbusiness returns with and without Schedules C, E and F. Schedule C with $100,000–$200,000 of receipts was audited at 2.4% vs. 0.2% for simple nonbusiness returns (calendar 2017 returns). From FY2019 on, the tables split only by total positive income, so the self-employment risk can't be updated from the Data Book.

## 12. Nobody publishes the EITC's poverty effect on its own

Census reports one row for refundable tax credits: 6.8 million people kept out of poverty in 2024, the EITC and the refundable Child Tax Credit together. It also has a Child Tax Credit row (2.5 million), but no EITC row, and CRS cautions that these effects don't add, so subtracting isn't valid. A chart bar labeled "EITC" at 6.8 million would overstate it.
