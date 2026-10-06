# Back in my day: triple-d

> **Scope note:** this doc was written during the analysis, so its numbers cover all 1,634 restaurants, including the 74 outside the US. The charts and the Reel use only the 1,560 US restaurants (states, DC and Puerto Rico), so their numbers differ slightly.

**About two weeks of evenings in 2021. About an hour in 2026, and most of that hour was me making decisions.**

"Five years ago" means October 2021. GitHub Copilot was a technical preview. The GPT-3 API still had a waitlist and returned free text, not structured answers. Stack Overflow was the copilot.

## Then vs. now

| Stage | 5 years ago (estimated) | Now (measured) |
|---|---|---|
| **Understanding the sources** | View page source, hunt for the right table tags, figure out the pagination and that foodiepie hides closed restaurants. *~2 hours.* | Claude downloaded sample pages and found the row structure, the 57-page pagination and the "Hide Closed" toggle in a few minutes. |
| **Scraping ~1,500 pages** | Stack Overflow: "BeautifulSoup find table rows", "requests 406 Not Acceptable", "how to add delay between requests". Write, break, fix. *~0.5–1 day.* | `fetch.py`, about 70 lines, with caching and resume built in. Ran in the background while other work continued. |
| **Parsing Wikipedia's tables** | Stack Overflow: "parse wikipedia table with rowspan python", "strptime abbreviated month". Merged cells are a classic trap. *~0.5 day.* | `parse.py`. The rowspan bug and the "Feb 16" vs "February 16" date bug were found and fixed in the same session. |
| **Matching the two lists** | fuzzywuzzy, a threshold tuned by eye, then reviewing hundreds of candidate pairs in a spreadsheet. *~1–2 days.* | `match.py`: exact match plus three fuzzy rules. 1,053 exact and 336 fuzzy matches, audited from samples, plus 1 manual fix. |
| **Filling 278 missing descriptions** | Google each one: 278 × 3–5 min ≈ **15–25 hours**. Realistically, skipped. | Research agents worked in parallel and found 277 of 278, each with sources and an open/closed status. |
| **Classifying 1,634 restaurants** | Keyword rules on names and Yelp categories, or hand-label ~300 and train a scikit-learn model on thin text. Hand-labeling everything at ~30 s each ≈ **14 hours**. *~2–4 days.* | Jev: 2,845 calls including the pilot and reruns, for **$0.12** in total. Each restaurant got a label, a confidence and three 0–1 likelihoods. |
| **Changing my mind** | Each change of definition means re-labeling, so you get maybe one revision. | Edit `definitions.py`, rerun, compare. The forced-pick method was rebuilt in minutes after the first version said "951 dives". |
| **Total** | **~1.5–2 weeks part-time**, and still missing 17% of restaurants | **~1 hour of wall-clock** (first page fetched 17:23, final table 18:17), including the time I spent on decisions |

## What we'd have skipped

- **The 278 restaurants foodiepie doesn't cover.** A 17% hole, mostly recent seasons. That would have quietly erased the end of the trend line, and the end of the trend line is the story.
- **Confidence scores.** A 2021 classifier gives you a label. It doesn't tell you La Santisima is "Other at 99%" while Jake's Good Eats is a coin-flip "Dive".
- **Two versions of the answer.** Strict and "if Guy had to pick" would have been one or the other, because labeling twice wasn't affordable.
- **Catching our own mistakes.** The Artiso's/Aristo's typo, the Bludso's over-merge suspicion, and the "Dive" score that runs high for everything were found because checking was cheap.

## What didn't change

- **Deciding what a "dive" is.** No tool did that. The definitions, the decision to keep "Other" large for the hook, and the call to research the gaps all came from me.
- **Knowing the data could lie.** The season-count mismatch, closed restaurants hidden by a toggle, and the descriptions being about food rather than the setting all needed a skeptical person asking "wait, is that right?"
- **Spot-checking.** I still look restaurants up myself before anything goes in a video.

## The receipts

| Number | Source |
|---|---|
| 17:23 first page cached, 18:17 final table built | File timestamps in `data/raw/cache/` and `data/final/` (2026-10-02) |
| 662 lines of Python across the pipeline scripts | `wc -l scripts/*.py` |
| 2,845 Jev calls, 2.88M input tokens, $0.12 | `data/interim/jev_answers.jsonl`, at $0.042 per million input tokens |
| 277 of 278 gap restaurants researched | `data/interim/web/results/*.json` |
| 1,053 exact + 336 fuzzy + 1 manual matches | `scripts/match.py` output |
| "Then" times | Estimates, with the reasoning shown in each row. Not measured. |

## Voiceover lines

- "In 2021 this was two weeks of Stack Overflow and spreadsheets. Tonight it took an hour, and twelve cents of AI."
- "The robots did the scraping. I still had to decide what a dive is."
- "Back in my day, we'd have skipped the 278 hardest restaurants. That's where the story was."
