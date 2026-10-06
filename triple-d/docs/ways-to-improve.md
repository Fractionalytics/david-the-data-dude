# Ways to improve: triple-d

> **Scope note:** this doc was written during the analysis, so its numbers cover all 1,634 restaurants, including the 74 outside the US. The charts and the Reel use only the 1,560 US restaurants (states, DC and Puerto Rico), so their numbers differ slightly.

Numbers use definitions v2, in which Dive includes hole-in-the-wall taquerias.

For a long-form video or written piece. The short video doesn't need any of this; it's the honest footnotes.

## The headline

**Diners, Drive-Ins and Dives has drifted away from its title.** Of restaurants first featured in 2007–11, 42% fit none of the three categories. By 2022–26 it was 84% (strict classification).

## Robustness checks we ran

| Check | Result | Verdict |
|---|---|---|
| Does the trend hold using **only foodiepie descriptions**? Recent seasons lean on web research. | 42% → 80% "Other" | Holds |
| Does it hold **excluding name-rule labels**? Early restaurants more often have "Diner" in the name. | 49% → 85% "Other" | Holds |
| Does it hold in the **forced** version, where every restaurant with any signal must pick? | Diner 49% → 16%; "Guy shrugs" 8% → 43% | Holds, from a different angle |
| Is the evidence equally rich across eras? | Median description is **79 characters for 2007–11 vs 150 for 2022–26** | **Open question.** Older restaurants were judged on half as much text. |

## Improvements, ranked

| # | Weakness | Could move the headline? | Fix | Effort |
|---|---|---|---|---|
| 1 | **No accuracy number for the classifier.** We know Jev's confidence, not whether it agrees with a human. | **High.** Every bar in the chart depends on it. | Hand-label a blind sample of ~100 restaurants, stratified by era, and report Jev's agreement rate overall and per era. | A few hours |
| 2 | **Description length doubles over time.** Thinner early descriptions could bias early labels either way. | **Medium–high.** It's the one confounder still open. | Re-classify a sample of recent restaurants using truncated (~80 character) descriptions. If their Other share drops toward early levels, part of the trend is an artifact. | An hour |
| 3 | **"Dive" is about the setting, but the descriptions are about the food.** La Santisima reads as a nice taco shop on paper; locals call it a dive. | **Medium.** It likely undercounts Dives in every era. | Add setting evidence: Yelp review snippets that mention "dive", "hole in the wall" or "sketchy", or a Street View–based judgment for a sample. | A day |
| 4 | **509 "Guy shrugs" in the forced version.** Jev was so sure they're Other that it gave no ranking of the other three. | Low for the strict headline; high for the forced chart. | Ask Jev a second three-option question ("closest to Diner, Drive-In or Dive?") for just these, or rank each yes/no score against its own category. | An hour, about a penny |
| 5 | **Our definitions are one reasonable choice among several.** | **Medium.** | Sensitivity test: rerun with a broader Dive ("any hole-in-the-wall") and a broader Diner ("any breakfast-and-lunch cafe") and see whether the trend survives. | An hour per variant |
| 6 | **Counting unit.** We count each restaurant once, in its first-aired year. Revisits (211 restaurants) and episode segments aren't counted. | Low–medium | Show the chart per appearance as well as per restaurant. | An hour |
| 7 | **Matching errors.** 336 fuzzy matches; one suspected over-merge (Bludso's Compton vs. Los Angeles). | Low | Review every fuzzy match with the same name in different cities, plus a random 50. | A few hours |
| 8 | **"Open" means "no evidence it closed".** 109 web-researched restaurants have unknown status, and the sources sometimes disagree. | Low (the status isn't part of the headline) | Check Google/Yelp business status for the unknowns, and record an as-of date. | A day |
| 9 | **Two sources disagree about who was on the show.** 53 foodiepie restaurants aren't on Wikipedia at all. | Low | Add Food Network's own episode pages as a third source to reconcile the lists and the season numbering. | A day |
| 10 | **Web research isn't reproducible by script.** Agents searched and summarized. | Low | Their sources are saved; re-verify a sample and keep the sources with the data. | A few hours |

## What we chose not to fix and why

- **The "Other" policy.** Keeping Other large is a deliberate editorial choice, because it supports the hook. The forced version exists to show the alternative.
- **Season 44.** It's excluded because it was in progress when we pulled the data, not because it was inconvenient.

## If we had a week

1. **Hand-label 100 restaurants and publish the agreement rate (#1).** It turns "the AI says" into "the AI agrees with a human X% of the time".
2. **Run the truncation test (#2).** It either closes the last confounder or rightly shrinks the headline.
3. **Add setting evidence for Dives (#3).** It's the most interesting improvement for viewers, and the La Santisima story shows why it matters.
