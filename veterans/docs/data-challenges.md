# Veterans: data challenges

The inside look at what went wrong with the data, logged as it happened.

1. **VA's model puts 120,000 veterans in a county where Census finds 21,000.** VetPop2023 ranks Lake County, Illinois 8th in the country (120,161 in FY2024). ACS 2024 says 20,925 ± 2,092, a ratio of 5.74. The median across 297 counties is 1.12. Lake County is home to Naval Station Great Lakes, the Navy's boot camp, so a military-address artifact is a candidate explanation, not a confirmed one. County rankings here use ACS instead.

2. **Three official counts of the same population.** VetPop 17.26M (FY2026 projection), CPS 17.2M (Aug 2025), ACS 15.70M (2024). The CPS agreement may be coincidence. Comparing the same year (FY2024 vs 2024) puts the VA-ACS gap at 2.18M. Puerto Rico and veterans abroad account for 171,000 of it, and group quarters account for none. Most of the rest falls under age 65 (VA 26% higher at 17-44), which fits VA's own explanation: ACS self-reporting, and a two-month residence rule that misses people who move often.

3. **Post-9/11 veterans range from 4.7M to 6.3M.** VetPop 6.29M (adding the four post-9/11 groups), BLS 5.65M, ACS 4.74M. That's a 1.5M spread on the group most people would ask about first.

4. **Older veterans go the other way.** ACS has 518,874 people with wartime service between 1941 and 1955. VetPop has about 307,000 for WWII and Korea combined. The ACS is self-reported, and VetPop is a model, so at least one of them is well off for the oldest veterans. VA says records are incomplete for some veterans who served only before 1970 and never dealt with VA, which may explain the ACS's higher older-age counts, and it points to the 1973 fire that destroyed records at the National Personnel Records Center.

5. **The 2024 Census microdata quietly changed.** The state column went from `ST` to `STATE`, and the service-period columns were merged and relabelled. My first run used older labels and reported 1.35M Vietnam veterans, when the real figure is 4.91M. The number looked wrong, and the 2024 data dictionary confirmed the mismatch.

6. **"Pension" is three programs.** VA disability compensation (6.34M), military retired pay (2.0M) and VA Pension (123,261) differ by a factor of 50, and people overlap between them. A search result's 2.27M retiree figure turned out to be a secondhand forecast, and DoD's own report replaced it.

7. **The two best combat numbers measure different things.** Pew 2019 says 29%, requiring a combat zone plus a key engagement. NSV 2010 says 33.9% for "combat or war zone". In that same NSV appendix, the next question, on exposure to dead, dying or wounded people, shows the identical 33.9% / 66.1%. That may be real, or it may be a table error.

8. **Nobody knows how many veterans live abroad, officially.** GAO says neither DoD nor VA tracks it, yet VA's own benefits report prints an estimate of 94,419.

9. **Some sources refuse automated access.** Three Defense Department hosts returned 403 to my scripts, and VA took its mortality study offline, so only archived copies exist. David offered his own Chrome, where the DoD report and an Internet Archive copy of the VA study both opened, and I read them there. The Census API now needs a key, and one Census table file returned "Request Rejected". VA's newer benefits report also sat at a different URL pattern, so first attempts saved HTML error pages under `.pdf` names, which only a file-type check caught.

10. **My own sum doubled the retirees.** Adding up DoD's rank table in the browser gave 3,123,540 retirees, because the table's own total row was counted as data. The report's printed total of 1,561,770 caught it, and the rank groups then summed back to that figure exactly.

11. **A viral post's two numbers both mean something else.** "Less than 1% of Americans serve" is true only of people serving now (0.35% on active duty). Veterans are 4.6% of all residents and 10.7% of adult men. "1 in 10 see direct combat" is closest to the share of deployed troops in combat-arms jobs, while 15% of veterans say they fired at the enemy.

12. **Three Army posts changed names twice.** Fort Bragg, Fort Hood and Fort Benning were renamed in 2023 to drop Confederate namesakes, then given their old spellings back in 2025 to honor different soldiers. A name alone doesn't say who is honored.

13. **"How many have PTSD" has three answers.** Rated for compensation 1.76M, VA-diagnosed patients 14-24%, and national survey 7% lifetime. Each counts a different thing.

14. **The questions most people would ask have the weakest data.** Years served, final rank and how people entered have no national source covering all living veterans. The best general survey is from 2010, when 22 million veterans were alive.
