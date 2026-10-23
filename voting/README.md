# Voting: the midterm power gap

In the 2022 midterm, how many voters aged 65 and over were there for every voter aged 18–24? And what happened in 2018, when young people closed part of that gap? This folder has the numbers behind the Reel, all the way back to 1972, the first election after the voting age dropped to 18.

This folder is the behind-the-scenes companion to David the Data Dude's Instagram Reel.

<p align="center">
  <a href="https://www.instagram.com/reel/De1wb5Lygix/"><img src="cover.jpg" alt="Reel cover: The political power of young Americans" width="300"></a>
  <br>
  <b>▶ <a href="https://www.instagram.com/reel/De1wb5Lygix/">Watch the Reel on Instagram</a></b>
</p>

## The result

Voters 65+ for every voter aged 18–24, midterms (`data/senior_to_young_ratio.csv`):

| Midterm | Voters 18–24 | Voters 65+ | 65+ per 18–24 |
|---|---|---|---|
| 1974 | 6.1M | 10.8M | **1.8** |
| 1978 | 6.5M | 12.9M | **2.0** |
| 1982 | 7.1M | 15.3M | **2.1** |
| 1986 | 5.8M | 16.9M | **2.9** |
| 1990 | 5.1M | 18.0M | **3.6** |
| 1994 | 5.1M | 19.1M | **3.8** |
| 1998 | 4.2M | 19.2M | **4.5** |
| 2002 | 4.7M | 20.7M | **4.4** |
| 2006 | 5.5M | 21.7M | **3.9** |
| 2010 | 5.7M | 23.0M | **4.0** |
| 2014 | 4.7M | 26.2M | **5.6** |
| 2018 | 8.7M | 33.1M | **3.8** |
| 2022 | 7.4M | 37.1M | **5.0** |

- **In the 2022 midterm, about 5 people aged 65+ voted for every voter aged 18–24.** In 1974 it was 1.8.
- **Midterms always tilt older than presidential elections.** In presidential years the ratio was 1.0 in 1972, the first election after the voting age dropped to 18, and 3.3 in 2024.
- **The 2018 comeback.** Young midterm voters nearly doubled, from 4.7M (2014) to 8.7M (2018), and the ratio fell from 5.6 to 3.8. In 2022 it went back up to 5.0.

## Two reasons for the gap

The ratio is the population gap times the turnout gap.

**1. Demographics, which no one controls.** Adults by age group (`data/turnout_by_age.csv`, `population_k`):

| | 1972 | 2024 |
|---|---|---|
| 18–24 | 24.6M | 30.0M |
| 65+ | 20.1M | 60.4M |

The 18–24 group has stayed roughly flat. The 65+ group tripled, and it grew fastest from 2011, when the first baby boomers (born 1946) turned 65.

**2. Turnout, which each group controls.** Citizens who say they voted, 2020 presidential → 2022 midterm:

| | 2020 | 2022 | Change |
|---|---|---|---|
| 65+ | 74.5% | 66.8% | −8 pts |
| 18–24 | 51.4% | 27.6% | −24 pts |

From the 2014 to the 2018 midterm, 18–24 turnout rose from 17.1% to 32.4% (+89%). CIRCLE at Tufts University found youth turnout rose in every one of the 34 states with data.

## Definitions

- **Age groups:** the Census Bureau's 18–24 and 65+ groups. "Grandparents" in the Reel is shorthand for 65+.
- **Voters** in an age group = everyone in that group (citizens and noncitizens) × the share of everyone in the group who say they voted. That's the only turnout rate that multiplies with the Census population counts. The ratio is 65+ voters ÷ 18–24 voters.
- **Turnout changes** (−8, −24, +89%) use the share of **citizens** who say they voted, the Census Bureau's headline measure. Citizen turnout by age is published only from 2002.
- **Self-reported:** the Current Population Survey asks people whether they voted. Survey turnout runs above official counts, so treat levels as approximate. The gaps between age groups and years are more reliable than any single level.
- **Starting point:** age-group figures begin in 1972. Before the 26th Amendment, the survey's "18–24" group mostly held 21–24-year-olds (13.0M in 1970, against 24.6M in 1972).

## Also in this folder

Charts that didn't make the Reel, in `charts/`:

- **Turnout of eligible voters, 1920–2024** (`vep_turnout.png`, from the University of Florida Election Lab). The 2018 midterm's 50.05% was the highest since 1914. Midterm turnout has trailed the preceding presidential election by 15.9 points on average since 1950.
- **Eligible voters against ballots cast, 1980–2024** (`eligible_vs_voted.png`). In 2022, 243M people were eligible and 112M voted.
- **65+ share of voters against their share of adults** (`senior_share_of_voters.png`). In the 2022 midterm, 65+ were 22.5% of adults and 30.4% of voters.
- **Turnout gap by age, and turnout by age group** (`age_gap.png`, `turnout_by_age.png`).
- **Age of Congress, 1901–2025** (`congress_age.png`, `data/congress_age.csv`). Congress was youngest in 1981, with a mean age of 49.5 across both chambers, and was 58.7 in 2025: 57.4 in the House and 64.0 in the Senate, where half the members are 65 or older. The 65+ share of midterm voters and Congress's mean age rose together (correlation +0.88 for midterms, 1974–2022). That's a correlation, not proof that one caused the other: the whole country got older too. Our ages run about half a year below the Congressional Research Service's (57.9 and 63.9 for 2025), which counts age differently. Quote theirs for an exact figure.

Also included: `docs/data-challenges.md` (what got in the way), the pipeline in `scripts/`, the Reel's Remotion source in `video/`, and the animation on black in `videos/voting-animation.mp4`.

## Data and scripts

| File | What it is |
|---|---|
| `data/turnout_by_age.csv` | Census CPS Table A-1 by age group and election, 1964–2024: population, turnout (citizens and all adults), voters, shares |
| `data/senior_to_young_ratio.csv` | Voters 18–24, 25–44, 45–64 and 65+, and the 65+ per 18–24 ratio, every election 1972–2024 |
| `data/turnout.csv` | National turnout by election: VEP turnout 1789–2024, eligible voters and ballots 1980–2024, Census citizen turnout and registration |
| `data/congress_age.csv` | Mean and median age, and share 65+, by chamber, for each Congress, 1901–2025 |

Rebuild with `python scripts/build_series.py`, `python scripts/build_congress_age.py` and `python scripts/explore_charts.py`, after downloading the sources below into `data/raw/` (file names in each script). `build_series.py` also reads the Gallup and Pew trust series used in early research. Those aren't republished here, so comment out its `gallup()` and `pew()` calls, and the trust charts in `explore_charts.py`, if you don't download them.

## Sources and licenses

- **U.S. Census Bureau**, Current Population Survey, Voting and Registration Supplement, [Historical Table A-1](https://www.census.gov/data/tables/time-series/demo/voting-and-registration/voting-historical-time-series.html) (1964–2024). U.S. government work.
- **University of Florida Election Lab** (Michael McDonald), [national VEP turnout rates](https://election.lab.ufl.edu/dataset/national-vep-turnout-rates-1789-present-v1-4/) and state turnout files for [1980–2022](https://election.lab.ufl.edu/dataset/1980-2022-general-election-turnout-rates-v1-2/) and [2024](https://election.lab.ufl.edu/dataset/2024-general-election-turnout-rates-v0-4/). 1948 onward is under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); figures before 1948 were compiled by Walter Dean Burnham. `data/turnout.csv` carries these figures under the same license.
- **[unitedstates/congress-legislators](https://github.com/unitedstates/congress-legislators)**, every member of Congress with birthdays and terms. Public domain (CC0).
- **CIRCLE at Tufts University**, [2018 youth turnout by state](https://now.tufts.edu/2019/04/02/youth-voter-turnout-analysis-shows-across-board-increases-2018-midterms). Cited, not republished.
- **Congressional Research Service**, [Membership of the 119th Congress: A Profile](https://www.everycrsreport.com/reports/R48535.html). Cited.

How and when to vote in your state: [vote.gov](https://vote.gov).
