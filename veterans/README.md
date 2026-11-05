# Veterans: "Thank you for your service"

About half of veterans and service members say they're uncomfortable hearing "thank you for your service," and about half of civilians say they'd walk up to someone in uniform and say it. This folder counts the 17.2 million living US veterans behind that phrase: who they are, and what they gave.

This folder is the behind-the-scenes companion to David the Data Dude's Instagram Reel.

<p align="center">
  <a href="https://www.instagram.com/reel/DfVvhRsSXCE/"><img src="cover.jpg" alt="Reel cover: Veterans" width="300"></a>
  <br>
  <b>▶ <a href="https://www.instagram.com/reel/DfVvhRsSXCE/">Watch the Reel on Instagram</a></b>
</p>

## The result

**The phrase**

| Survey | Who was asked | Result |
|---|---|---|
| USAA "Go Beyond Thanks" (Endeavor Analytics x YouGov), Sep 22–Oct 11, 2023 | 1,639 veterans and military personnel | "Half" feel uncomfortable or awkward when thanked. Nearly 70% of 18–29, about two-thirds of 30–44, 24% of 65+ |
| YouGov daily question, Nov 10, 2025 | 4,064 US adults | 53% would approach someone in uniform to thank them (22% definitely, 31% probably); 33% would not; 14% not sure |

The two surveys asked different people, two years apart. The Reel's grid of "half the civilians thanking half the veterans" multiplies them as if they were independent, so it's an illustration, not a measured overlap. The 45–64 result was never published, and the USAA survey mixes veterans with people still serving.

**Who they are** (VA's VetPop2023 projection for September 30, 2026)

- **17,260,283** living veterans, including Puerto Rico and veterans abroad. That's about **6% of US adults**: 5.9% by the Census's own count, 6.5% using VA's count over the same adults.
- **4,674,496** served in the Vietnam era (August 1964–May 1975). Many never served in Vietnam itself.
- **9,232,051** served in the Gulf War era (August 1990 on), 6,294,778 of them after 9/11. 2,734,978 served only in peacetime between Vietnam and the Gulf War.

**What they gave**

| Measure | Share of veterans | Source |
|---|---|---|
| Deployed at least once | 61% | Pew 2019 |
| Married at some point while on active duty | 47% | Pew 2019 |
| Served in a combat or war zone | 36% | Pew 2019 |
| Receive VA disability compensation | 37% (6,338,253) | VA Annual Benefits Report FY2025 |

Most common conditions VA compensates (veterans, FY2025): tinnitus 3,583,295; limited knee flexion 2,312,985; sciatic nerve paralysis 2,026,583; back or neck strain 1,791,869; **PTSD 1,760,497**; hearing loss 1,690,837. These count granted claims, not how many veterans have each condition.

## Definitions

- **Veteran:** anyone who served in the active military, naval, air or space service and was discharged under conditions other than dishonorable ([38 U.S.C. 101](https://www.law.cornell.edu/uscode/text/38/101)). VA's count includes Guard and Reserve members who were called to federal active duty, and excludes people whose only service was training.
- **Era:** VA's periods of service, which are dates, not places. A "Vietnam-era veteran" served at some point between August 5, 1964 and May 7, 1975, anywhere.
- **Deployed:** Pew's question asks about deployments away from the permanent duty station, which aren't always overseas.

## VA vs. the Census

The Census Bureau's American Community Survey counts 15.7 million veterans, about 2.2 million fewer than VA for the same year. Puerto Rico and veterans abroad explain about 171,000 of the gap. The rest is mostly under age 65, which fits VA's explanation: the Census relies on people describing themselves as veterans and misses people who move often, while VA starts from service and benefit records. Totals here use VA's count; shares of the population use the Census, so each share's top and bottom come from the same survey.

## Files

- `data/`: VetPop2023 FY2026 tables (age and sex, branch, rank, period of service, state, county), Census 2024 shares and metro counts, the VA-vs-Census comparison by age, and DoD military retirees by rank (FY2022).
- `scripts/`: how each table was built. `fetch_sources.py` downloads the public source files, which aren't republished here; `requirements.txt` lists the Python packages.
- `docs/data-challenges.md`: everything that went sideways, from a county with 5.7 times more veterans in VA's model than in the Census to a microdata file that quietly renamed its columns.
- `video/`: the Remotion source for the Reel's animated charts. It imports layout and fonts from a shared kit that isn't published here.

## Sources

- **VA, VetPop2023:** [data.va.gov](https://www.data.va.gov/), FY2026 projection, and [VetPop2023: A Brief Description](https://www.data.va.gov/d/rwgn-ekjg).
- **VA, Annual Benefits Report FY2025:** [benefits.va.gov/REPORTS/abr](https://benefits.va.gov/REPORTS/abr/).
- **Census Bureau, American Community Survey 2024:** [1-year PUMS](https://www2.census.gov/programs-surveys/acs/data/pums/2024/1-Year/) and table B21002; [Vintage 2024 metro population estimates](https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/metro/totals/).
- **Pew Research Center:** [The American Veteran Experience](https://www.pewresearch.org/social-trends/2019/09/10/the-american-veteran-experience/) (2019, 1,284 veterans) and its [topline](https://www.pewresearch.org/wp-content/uploads/sites/20/2019/09/PSDT_10.09.19_veteransexperiences_topline.pdf).
- **USAA, "Go Beyond Thanks" survey:** [USAA newsroom](https://usaa-newsroom.prgloo.com/news/go-beyond-thanks-new-survey-reveals-we-should-do-more-than-simply-thank-our-veterans-for-their-service), November 8, 2023. The 30–44 figure is from NewsNation, November 9, 2023.
- **YouGov daily question:** [results](https://yougov.com/en-us/daily-results/20251110-5e6ce-3), November 10, 2025.
- **BLS, Employment Situation of Veterans 2025:** [release](https://www.bls.gov/news.release/archives/vet_04282026.htm).
- **DoD Office of the Actuary, Statistical Report on the Military Retirement System, FY2022.**

## License

MIT, like the rest of this repo. VA, Census, BLS and DoD data are U.S. government works. The survey results belong to Pew Research Center, USAA and YouGov, and are quoted here, not republished.
