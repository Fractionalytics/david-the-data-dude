# Back in my day: Florida Alerts

**Five years ago (2021), this would have been about two weeks of evenings, and the hardest parts would probably have been skipped. This time it took about a day and a half from idea to a posted Reel and a public repo.**

"Now" is measured from git history, file counts and the session itself. "Then" is an estimate, with the reasoning shown. Wall-clock time isn't effort. The 26.5 hours from scaffolding the project (October 7, 2:34 pm) to publishing it (October 8, 5:08 pm) include a night's sleep, David writing and rewriting the script, recording, and editing. Claude's time inside that window was a fraction of it.

## Then vs. now

| Stage | 5 years ago (2021) | Now |
|---|---|---|
| **Finding the sources** | Click around FDLE's site, find the empty "Monthly Reports" page and the broken newsletter frame, and probably conclude the data doesn't exist. 2–4 hours, and a real chance of giving up here | About 30 requests across 5 small recon scripts, robots.txt checked first. Found the lost reports in the Archive's index, plus 13 unlinked newsletters by guessing their URL pattern |
| **Recovering the lost reports** | The Wayback Machine and its CDX index existed, but few people knew the index API. More likely: open 120 archived PDFs one at a time in a browser, about 1–2 minutes each (2–4 hours), or spend an evening on a script after searching Stack Overflow for "how to download all files from a Wayback Machine snapshot" | 1 index query listed all 120. 2 short scripts downloaded 119, a few seconds apart, skipping the 1 the Archive can't serve and stopping on rate limits |
| **Parsing 119 PDF tables** | PyPDF2, pdfplumber and PyMuPDF all existed. Writing a parser that survives ten years of template drift (rows without periods, backwards age/sex, wrapped names) by trial and error, after "extract table from PDF python" searches: 1–2 days | One ~130-line parser, fixed quirk by quirk, with old and new output diffed after every fix and rows reconciled against each report's own totals |
| **Newsletter and press-release figures** | Type 40-odd numbers by hand, about an hour. The same as now, minus the checker | 44 figures typed with page and quote, then a script that verifies every quote against the source text, proven by planting an error |
| **Labeling 197 success stories** | Keyword rules in pandas: the same method, 1–2 hours | Keyword rules, tightened twice after reading the misses, in minutes |
| **National AMBER reports** | Find, download and read 19 reports, typing the figures: 2–3 hours | Indexed, downloaded (except 5 that robots.txt disallows, which David saved by hand) and extracted with one sentence pattern |
| **Fact-checking the script** | Re-derive each number by hand against the spreadsheet, per draft | Five review passes on David's drafts, every number traced to its file, and word counts and runtime checked each time |
| **Five animated charts timed to the voice** | Hand-animate in After Effects or Keynote, keyframing each bar, dot and map zoom to the audio: about a day per chart, so 3–5 days. Remotion had only just launched (early 2021) | About 600 lines of Remotion and React. Each animation finishes on David's timecode, and key frames were checked as stills before rendering |
| **Spot checks** | The same: a person opens the PDFs and compares | The same: David checked 13 by hand. Claude picked which rows to check, with code |

**Rough total, then:** about 2 days of data work plus 3–5 days of animation, so 1.5–2 weeks of evenings for one person, if they didn't stop at the empty reports page.

## What we'd have skipped

- **The Internet Archive.** Most people would have taken FDLE's empty page at its word, and the story would have been "the state doesn't publish this", with no 2011–2020 numbers.
- **The second count.** We checked FDLE's running "direct recovery" totals against the asterisks on individual rows (217 vs. 222). Nobody would have built two independent counts by hand.
- **The parser diffs.** Without them, 4 dropped alerts, 3 blank ages and 6 shifted columns would have gone unnoticed. Nothing errored.
- **Extending to 2023.** Chasing FDLE's anniversary press releases to carry the running total from 2020 to October 2023 is the kind of last mile that gets cut when every step is manual.
- **The 34-entry "inside look".** Logging every surprise as it happened, with numbers, is what made the data-challenges doc, and this one, possible.
- **The card 6 vs. card 7 cross-tab.** It took seconds to see that citizen stories rarely name a channel. By hand, that's another evening, so the apparent contradiction probably ships.

## What didn't change

- **The question and the story.** David's daughter asked it, David chose to focus on Silver Alerts, and David wrote every word of the script.
- **The calls that change the answer.** Framing card 7 as public vs. police, publishing coarsened case rows to protect privacy, going ahead without the last two spot checks, and not filing a public-records request were all David's decisions.
- **Checking.** The spot checks were David opening the PDFs. The tooling chose what to check; a person still had to look.
- **Where the time went.** It moved from typing to thinking: what to trust, what to cut, and how to say it.

## The receipts

| Number | Source |
|---|---|
| 26.5 hours, scaffold to publish (includes overnight, writing, recording, editing) | `git log --date=iso -- projects/florida-alerts`: first commit 2026-10-07 14:34, last 2026-10-08 17:08 (EDT) |
| 11 commits | `git log -- projects/florida-alerts` |
| ~1,200 lines of Python (23 scripts) | `wc -l projects/florida-alerts/scripts/*.py` |
| ~600 lines of chart code | `wc -l` over `video/src/*.tsx` and `video/src/charts/*.tsx` |
| 119 of 120 monthly reports recovered | `data/raw/silver_monthly_pdfs/`, `scripts/wayback_download.py` log |
| 2,219 alert rows, 197 stories, 44 hand-typed figures | `data/interim/silver_monthly_cases.csv`, `silver_success_stories.csv`, `newsletter_stats.csv` |
| 13 spot checks passed, 0 failed | `docs/spot-checks.md` |
| 34 data-challenge entries | `docs/data-challenges.md` |

## For the video or carousel

[TBD: David]. The playbook keeps every script line and caption David's. The receipts above are the raw material.
