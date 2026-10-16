# Every number, with its timeframe

Saved 2026-10-16. For the script review. **The latest BLS occupation data is May 2025** (published 2026), so the "after" period is May 2022 → May 2025, not 2026. ChatGPT launched November 30, 2022, so May 2022 is the last pre-ChatGPT reading.

## Table 1: BLS occupation employment (OEWS, May of each year; verified against BLS files)

Built by `scripts/numbers_by_period.py` → `data/processed/numbers_by_period.csv`.

| Lane | Category | May 2019 | May 2022 | May 2025 | 2019→22 change | 2019→22 % | 2022→25 change | 2022→25 % |
|---|---|---|---|---|---|---|---|---|
| Benchmark | All jobs outside office & admin support | 127,347,230 | 129,211,230 | 137,742,300 | +1,864,000 | +1.5% | +8,531,070 | +6.6% |
| Benchmark | All US jobs (all occupations) | 146,875,480 | 147,886,000 | 155,495,730 | +1,010,520 | +0.7% | +7,609,730 | +5.1% |
| Fast lane | Office & administrative support (all) | 19,528,250 | 18,674,770 | 17,753,430 | -853,480 | -4.4% | -921,340 | -4.9% |
| Fast lane | Customer service representatives | 2,919,230 | 2,879,840 | 2,595,750 | -39,390 | -1.3% | -284,090 | -9.9% |
| Fast lane | Data entry keyers | 159,930 | 157,380 | 127,080 | -2,550 | -1.6% | -30,300 | -19.3% |
| Fast lane | Bookkeeping, accounting & auditing clerks | 1,512,660 | 1,550,750 | 1,373,680 | +38,090 | +2.5% | -177,070 | -11.4% |
| Fast lane | Receptionists & information clerks | 1,057,370 | 1,011,170 | 910,180 | -46,200 | -4.4% | -100,990 | -10.0% |
| Fast lane | Telemarketers | 134,800 | 96,520 | 58,430 | -38,280 | -28.4% | -38,090 | -39.5% |
| Other suspects | Loan interviewers & clerks | 208,530 | 242,630 | 164,790 | +34,100 | +16.4% | -77,840 | -32.1% |
| Other suspects | Loan officers | 308,370 | 345,550 | 274,330 | +37,180 | +12.1% | -71,220 | -20.6% |
| Other suspects | Computer programmers | 199,540 | 132,740 | 92,230 | -66,800 | -33.5% | -40,510 | -30.5% |
| Slow lane | Paralegals & legal assistants | 329,870 | 345,240 | 392,880 | +15,370 | +4.7% | +47,640 | +13.8% |
| Slow lane | Lawyers (employees only) | 657,170 | 707,160 | 754,500 | +49,990 | +7.6% | +47,340 | +6.7% |
| Slow lane | Legal secretaries & admin assistants | 168,140 | 159,940 | 156,280 | -8,200 | -4.9% | -3,660 | -2.3% |
| Third lane | All low-AI-exposure occupations (BLS rating; 203 occupations) | 27,153,660 | 26,276,110 | 27,073,340 | -877,550 | -3.2% | +797,230 | +3.0% |
| Third lane | Nursing assistants | 1,419,920 | 1,310,090 | 1,448,910 | -109,830 | -7.7% | +138,820 | +10.6% |
| Third lane | Maids & housekeeping cleaners | 926,960 | 771,390 | 860,670 | -155,570 | -16.8% | +89,280 | +11.6% |
| Third lane | Janitors & cleaners | 2,145,450 | 2,148,350 | 2,209,760 | +2,900 | +0.1% | +61,410 | +2.9% |
| Third lane | Hand packers & packagers | 633,640 | 653,870 | 559,820 | +20,230 | +3.2% | -94,050 | -14.4% |
| Exposure groups | All very-high-AI-exposure occupations (186) | 43,236,870 | 42,687,460 | 43,473,310 | -549,410 | -1.3% | +785,850 | +1.8% |
| Exposure groups | All other rated occupations (571) | 96,283,780 | 96,577,050 | 102,430,230 | +293,270 | +0.3% | +5,853,180 | +6.1% |
| Jobs added | Data scientists | n/a | 159,630 | 262,440 | n/a | n/a | +102,810 | +64.4% |
| Jobs added | Software developers | n/a | 1,534,790 | 1,687,890 | n/a | n/a | +153,100 | +10.0% |
| Jobs added | Sales engineers | 63,550 | 59,700 | 51,790 | -3,850 | -6.1% | -7,910 | -13.2% |
| Jobs added | Electricians | 688,620 | 690,050 | 757,220 | +1,430 | +0.2% | +67,170 | +9.7% |
| Jobs added | Construction laborers | 1,020,350 | 1,012,780 | 1,096,780 | -7,570 | -0.7% | +84,000 | +8.3% |
| Jobs added | Electrical power-line installers | 111,660 | 119,510 | 131,070 | +7,850 | +7.0% | +11,560 | +9.7% |

**Notes:**
- The low-exposure, very-high-exposure and "all other rated" rows come from the 757-occupation balanced panel, which covers 94% of jobs. The benchmark rows use BLS's official totals. Don't mix the two in one comparison.
- 2019→22 includes COVID. Maids and nursing assistants fell then and rebounded after.
- Data scientists and software developers have no 2019 value, because 2019 used older combined codes.
- OEWS counts employees only, so it leaves out the self-employed, partners and solo practitioners.

## Table 2: other numbers, each with its own timeframe

These don't come from OEWS, so they don't fit the 2019 / 2022 / 2025 columns.

| Topic | Number | Timeframe | Source | Status |
|---|---|---|---|---|
| Radiologists (slow lane) | Pay premium over the average doctor 1.30× → 1.44× | 2017 → 2026 reports | Doximity, via the Radiology Reel | Released (Radiology) |
| Radiologists (slow lane) | Billing Medicare +12.8% vs +7.2% for all physicians | 2016 → 2024 | CMS, via the Radiology Reel | Released (Radiology) |
| Radiology force 1 | Reading images = 36% of a radiologist's time | Study published 2012 | VALUE study (Canada) | Used in the Radiology Reel |
| AI-washing check | 4% of service firms laid off workers due to AI; ~15% hired fewer; ~13% hired more | Past six months, survey published Sep 1, 2026 | NY Fed regional surveys | Agent read it; not yet opened myself |
| AI-cited layoff announcements | 54,836 | Calendar 2025 | Challenger, Gray & Christmas | Primary (agent) |
| AI-cited layoff announcements | 120,136 (~21% of all cuts) | Jan–Sep 2026 | Challenger | Primary (agent) |
| AI-cited layoff announcements | 38,579 (40% of the month's cuts) | May 2026 | Challenger May report | Verified (PDF) |
| Data center construction spending | Record $85B annual rate, +73% vs a year earlier | August 2026 | Census via KPMG | Secondary; re-pull from Census |
| Data center operations jobs (NAICS 518) | −29k (CES) / +5k (QCEW) | Nov 2022 → Sep 2026 (CES), Mar 2026 (QCEW) | BLS | Agent via BLS API |
| Nonresidential construction jobs (all causes) | +370k | Nov 2022 → Sep 2026 | BLS CES | Agent via BLS API |
| Utilities jobs | +44k | Nov 2022 → Sep 2026 | BLS CES | Agent via BLS API |
| Semiconductor manufacturing jobs | −26k (CES) / about −9k (QCEW) | Nov 2022 → Sep 2026 / 2022 → Mar 2026 | BLS | Agent via BLS API |
| Genuinely new AI white-collar jobs | ~100,000–250,000 (estimate) | Late 2022 → 2026 | Synthesis of LinkedIn, Lightcast, OEWS | Estimate, not measured |
| Forward deployed engineer postings | ~200 → ~1,200 → 5,200+ | 2024 → 2025 → Jan–Jul 2026 | Lightcast | Primary (Lightcast blog) |
| Forward deployed engineer roles | ~15,000 total | 2023 → Sep 2026 | LinkedIn via WSJ | Secondary |
| Most-exposed jobs' gap vs rest | 0.6M–1.8M fewer jobs (method-dependent) | May 2022 → May 2025 | Exposure ledger (OEWS + BLS ratings) | Computed |
