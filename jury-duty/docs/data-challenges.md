# Data challenges: Jury Duty

The data problems we hit while working out the odds that a summoned juror ends up on a long trial. Logged as they came up, with the numbers.

## 1. Federal courts stopped publishing how many people they summon

The Administrative Office's FY2023 juror tables (J-2, J-10) start at the courthouse door: 171,099 people present on jury-selection days. Nothing in the current tables counts summonses mailed, people excused or deferred, or no-shows. The last national "called for jury duty" figure found was 194,211 for fiscal 2016, from a news summary, not a table. So the federal funnel can only begin at "you showed up," not at "you got summoned."

## 2. The trial-length table mixes in trials with no jury

Table T-2 sorts 10,536 FY2023 trials by length, but 7,499 of them were bench trials (T-1). T-2 doesn't split by jury, so it can't say how long jury trials run. 6,923 trials lasted one day, and most of those are probably bench trials, but the table doesn't let us prove it. The only jury-only length measure is an average: 15,601 jury trial days over 3,508 juries selected, about 4.4 days each (J-10).

## 3. More juries were picked than jury trials were finished

In FY2023, 3,508 juries were selected (J-2) but only 3,037 jury trials were completed (T-1), a gap of 471. Possible reasons: trials that ended in a plea or settlement after the jury was sworn, mistrials, or jury trials run by magistrate judges, which T-1 leaves out. The tables don't say which, so the gap can't stand in for "the case went away after you were seated."

## 4. The newest federal tables had moved, not vanished

On 2026-10-19, uscourts.gov returned HTTP 503 when we guessed FY2024 and FY2025 addresses using FY2023's naming pattern. We first logged this as a possible block. It wasn't one: the newer tables live under different paths (`/sites/default/files/2025-01/jb_j10_0930.2024.pdf`, `/sites/default/files/document/jb_<table>_0930.2025.pdf`), which a search turned up, and they downloaded normally. The federal funnel now uses FY2025: 146,290 jurors present on selection days, 21.6% selected, 2,701 juries, 12,307 jury trial days (about 4.6 per jury). Lesson: a failed guessed URL is not evidence the file is missing.

## 5. No single source covers both ends of the funnel

The sources that start at the summons (Milwaukee, California, Michigan) stop at the sworn juror. The ones that say how long jurors serve (Massachusetts, by days served; federal, as an average) are either a decade old or have no summons count. Massachusetts comes closest to covering the whole question, but its public annual tables end at FY2015, and on 2026-10-19 mass.gov returned 403 Forbidden to an automated fetch of its newer quarterly report.

## 6. Massachusetts stopped publishing how long jurors serve after 2015

mass.gov refused the automated fetch, but the same PDFs opened in a normal browser (with David's OK), and we read their text there. The FY2012–FY2015 annual reports have the whole funnel: summoned, responded, disqualified, served, and days served (1, 2, 3, 4+). The current reports (2021–2026) are demographic surveys that keep only three counts: answered the survey, appeared, impaneled (CY2025: 752,736 → 181,383 → 24,510). So the "more than one day" step is a decade old. The four years agree closely, though: 10.7% to 11.3% of jurors who served were there more than one day, and 3.9% to 4.1% were there four or more days.

## 7. The two ends of the Massachusetts funnel count different people

The summons count covers trial *and* grand jurors. The days-served table covers trial jurors only, and it counts everyone who served that year, including people summoned in earlier years who had postponed. So "served ÷ summoned" (31.5% in FY2015) treats each year as a steady state rather than following a single group of summoned people.

## 8. Massachusetts never published days served after FY2015

The Office of Jury Commissioner's annual funnel reports stop at FY2015 (the documents numbered -0 to -3 on mass.gov; probing -4 to -12 returned 404). Two later state audits (FY2014–15, issued 2016; FY2021–22, issued 2024) give one summary line (calendar 2014: 664,634 summoned, 174,748 served) but no breakdown of days served. Newer numbers would have to come from the office directly.

## 9. Federal case records have trial dates for civil cases but not criminal ones

The FJC Integrated Database's civil file records the date each trial began and ended (`TRIBEGAN`, `TRIALEND`), along with how the case was disposed of. That's enough to measure civil jury-trial length case by case. The criminal file, one row per defendant with 145 fields, has filing, disposition, sentencing and termination dates but no trial dates. So federal criminal jury-trial length is only available mixed in with bench trials (T-2).

## 10. The codebook said the trial dates were dead. They weren't.

The FJC civil codebook says the trial start and end dates were "rarely entered in the past" and the fields are "no longer being used." In the data, 79% of FY2023 civil jury trials (1,109 of 1,408) have both dates, and every year from 2012 to 2026 is similar. We measured them instead of trusting the documentation. Two cautions:
- **Calendar days overstate length.** A two-week trial spans 12 calendar days, so we count weekdays. That moved FY2023's 10–19-day bucket from 155 trials down to 95, below T-2's 113 for *all* civil trials of that length, as it should be.
- **The 21% without dates may differ** from those with dates, and we can't tell how.

Cross-check against T-2 (FY2023, all civil trials, jury and bench): from 2 days up, every bucket of measured jury trials is at or below T-2's total. At 1 day it's 45 jury trials against 1,654 in T-2, so one-day federal trials are almost all bench trials.

## 11. The Milwaukee report is a standard Wisconsin form, not a one-off

The Milwaukee PDF behind the Marquette blog post is form "CCAP-35, Basic Jury System Evaluation Report". A Wisconsin Supreme Court rule requires every county to evaluate its jury system each year, and the form records each county's summonses, responses, voir dire, sworn jurors and **trial days**. Milwaukee 2024: 127,057 summonses, 16,306 reported, 16,927 sent to voir dire (more than reported, because a juror can be sent to more than one), 6,151 sworn, 524 voir dires, 869 trial days. The forms go to each district court administrator but aren't posted centrally. Counties publish them only by choice: Waukesha County posts a fuller "Annual Jury Program Report" (2025: 87 jury trials, 174 trial days). Racine County's site returned 403 to a script.

## 12. Every source draws the funnel's lines in a different place

Putting 10 sources side by side for one Sankey, the stage boundaries don't line up:
- **"Eligible" differs.** Florida's "summoning yield" counts jurors available on the first day of the term. Massachusetts' "scheduled" still includes people who are later cancelled or postponed (66%, against 27–45% elsewhere). Waukesha's "qualified" includes postponed jurors (we subtract them).
- **"Sent to voir dire" can exceed "reported"** (Milwaukee 104%), because one juror can sit in more than one voir dire.
- **Pennsylvania's "3.8% empaneled"** doesn't say whether it's 3.8% of those who reported or of those sent to selection.
- **New Mexico's "seated"** mixes trial and grand juries.

So we report ranges, not a single pooled number, and each source's own definitions are noted in `docs/funnel-ranges.md`.

## 13. Florida's report prints two indices on one line

Each Florida county page lays out its indices in pairs, so a single text line reads "Miami-Dade 57.3 56.8 64.9 55.5 Miami-Dade 192 166 147 129": panel size on the left, trial counts on the right. A first pass read the left half for every index, and trial counts came out as fractions (1,810.3 rural trials). Two more traps: Madison County's page begins with chart debris ahead of its title, and small counties report 0.0% for quarters with no trials. We now read both halves of each line, find titles anywhere on the page, and average only the quarters with activity. All 67 counties parse; Oregon's 36 county totals add up exactly to the statewide 829,744.

## 14. Racine changed how it counts "summoned" partway through

Racine County switched from a one-step to a two-step system in 2020. Before, one mailing was both the questionnaire and the summons (15,153 in 2019). Since then, a questionnaire screens people first (16,673 in 2025) and only those who qualify get a summons (10,793). So "sworn per summons" jumps for reasons that have nothing to do with juries: the denominator changed. Per questionnaire, Racine's 2025 rate is 3.7%; per summons, 5.7%. Racine's reports also needed a browser: racinecounty.gov returns 403 to scripts but served all eleven PDFs (2015–2025) to the built-in browser, opened with David's OK.

## 15. "Sent to voir dire" counts seats, not people

Wisconsin's form counts each voir dire a juror sits in, so Milwaukee reports 16,927 sent to voir dire from only 16,306 people who reported. To count people, we use reported minus "Not Used" (reported but never sent to a courtroom): Milwaukee 12,405, Racine 2025 2,043, Waukesha 2,496. That moved the spine's courtroom stage from 166 to 155 per 1,000 summoned. The re-read of Racine's 11 reports in the browser also added called-off, not-used, questioned and no-trial-start-day counts to `data/racine_ccap35_2015_2025.csv`.
