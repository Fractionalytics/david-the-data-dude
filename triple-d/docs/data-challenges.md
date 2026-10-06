# Data challenges: triple-d

> **Scope note:** this doc was written during the analysis, so its numbers cover all 1,634 restaurants, including the 74 outside the US. The charts and the Reel use only the 1,560 US restaurants (states, DC and Puerto Rico), so their numbers differ slightly.

The "inside look" behind the chart: what got in the way, in roughly the order it came up.

## Getting the list

1. **"How many seasons?" has two answers.** Food Network's numbering suggests about 56 seasons. Wikipedia's episode list has 44, because the two count seasons differently. Before we could "stop before the current season", we had to pick a numbering: Wikipedia seasons 1–43 (April 2007 to September 2026). Season 44 premiered the same day we pulled the data.
2. **The two sources don't agree on how many restaurants there are.** foodiepie lists 1,410 restaurants. Wikipedia lists 1,667 restaurant names. foodiepie is missing about 280, mostly from recent seasons, and 53 of foodiepie's restaurants couldn't be found on Wikipedia at all. Neither source is complete on its own, so Wikipedia became the master list and foodiepie added details.
3. **"Closed" isn't a field anywhere.** foodiepie has no closed flag. It just hides closed restaurants unless you flip a toggle. We downloaded the list twice, with the toggle on and off, and diffed the two. Wikipedia marks some restaurants "(Closed)" inside the name text. Web research added a third opinion, and the three sometimes disagree. Wikipedia says Guacaya Bistreaux closed, while a 2026 article describes it in the present tense.
4. **Wikipedia's tables are built for people, not code.**
   - Merged cells (one episode spans several restaurant rows).
   - Footnote markers stuck to titles.
   - "(Closed)" embedded in restaurant names.
   - Dates written two ways ("February 16, 2024" vs "Feb 16, 2024").
   - A brand-new season with a placeholder row and no restaurant name.

## Filling the gaps

5. **278 restaurants had no description, so we researched them one by one.** Web-search agents looked up each one. The first pass hit a search limit partway through and left 70 unsearched, so a second pass finished the job. Only 1 restaurant is still a mystery: Danger Dave's in Bentonville, AR.
6. **The wrong restaurant is worse than no restaurant.**
   - Search turned up a Rincon Argentino in Coral Gables, FL when we needed the one in Boulder, CO.
   - It turned up a Holy Crepe food truck in Redding, CA instead of Boulder.
   - Wikipedia's "Artiso's" in Salt Lake City matched no restaurant anywhere, because it's a typo for Aristo's.

   The researchers were told to leave a gap rather than guess.
7. **Restaurants don't sit still.** They move, rebrand and change hands:
   - Taylor's Automatic Refresher is now Gott's Roadside.
   - Piroshki on 3rd became Pinoyshki and moved across town.
   - Big Star Diner became Madison Diner.

   "Open" has to mean "still operating in some form", and that's a judgment call.
8. **The descriptions are about the food, not the place.** "Dive" is mostly about atmosphere and neighborhood. foodiepie's notes are about dishes ("Oaxaca black mole chicken taco...") and rarely mention a cracked floor or a sketchy block. A place locals call a dive can look like a nice taco shop on paper. See La Santisima in the spot-checks.

## Matching ("entity resolution")

9. **The same restaurant is spelled differently across the two lists.** "BBQ" vs "Barbeque" vs "Bar-B-Que", "&" vs "and", "Café" vs "Cafe", and extra words ("Perly's" vs "Perly's Restaurant and Delicatessen"). Exact matching linked 1,053 restaurants. Fuzzy rules linked another 336, using shared words, same city and same first word, with a boost when episode titles matched.
10. **The same restaurant is spelled differently within one list.**
    - 211 restaurants appeared more than once (187 twice, 24 three times).
    - Wikipedia often names a revisit differently from the original visit: "Louie Mueller BBQ" in 2007, "Louie Mueller's Barbecue" in 2014.
    - Some names carry notes, like "Caplansky's (New Location)" or "The Elegant Farmer (Name changed to The Farmer & New Location)".

    These had to collapse into one restaurant with several air dates.
11. **Locations are written differently.** Wikipedia writes "Manhattan, New York City, New York", while foodiepie writes "New York, NY". State names had to become postal codes. Restaurants in Havana, Barcelona, Sicily, London and Mexico have no US state to match on.
12. **Sometimes merging is wrong.** Bludso's BBQ (Compton, season 17) and Bludso's Bar & Que (Los Angeles, season 34) may be two different restaurants that got merged into one. It's on the spot-check list.

## Classifying

13. **Diner, Drive-In and Dive have no official definitions.** We wrote our own, and they're the biggest judgment call in the project. Is a hole-in-the-wall taqueria a dive, or only a bar? Is a food truck a drive-in?
14. **Most places aren't any of the three.** Strictly applied, 67% of restaurants are "Other". We kept both versions: a strict one, and an "if Guy had to pick" one that forces every restaurant into one of the three.
15. **The AI's yes/no scores can't be compared with each other.** We asked the classifier (TypeSafe's Jev) "is it a diner?", "a drive-in?" and "a dive?" separately. The dive score ran high for almost any casual place. Picking the highest score called 951 restaurants Dives, so the forced pick uses the classifier's head-to-head choice instead.
16. **The computer picked "Diner" because it came first in the list.** When the classifier was sure a place was "Other", it gave Diner, Drive-In and Dive all 0% (it rounds to whole percentages). Asked to break that three-way tie, the code took the first column, so 495 restaurants became "Diners" by accident. They now stay "Other" in the forced version: Guy shrugs.
17. **Names settle some of it.** 85 restaurants have "Diner", "Drive-In" or "Dive" in their name, and those are labeled by rule, not by AI. Even that has edge cases: Chef Lou's Westside Drive-In is a drive-in by name.

## Logistics

18. **Being a polite scraper takes time.** We fetched about 1,500 pages at one per second. Two connections dropped and were retried. Every page was cached so the analysis could rerun offline.
19. **Bots get blocked.** One search engine served a CAPTCHA, which we didn't try to get around, and some sites rejected automated requests outright.
20. **Are we even allowed to do this?** Before publishing we checked each site's rules.
    - foodiepie's robots.txt (the file where a site tells bots what's off-limits) allows everything, and the site has no terms of service.
    - Wikipedia's content is free to reuse with credit.
    - Our scraper went slowly (one page per second, each fetched once and cached) and named itself honestly.
    - We didn't get everything right. When the research agents hit their search limit, they worked around it by loading Bing and DuckDuckGo result pages directly. That's 47 fetches, 21 of them on Bing pages that Bing's robots.txt forbids bots to load. The agents stopped at the CAPTCHAs, but the real lesson is that "don't bypass CAPTCHAs" wasn't specific enough. Now, instead of improvising, the AI stops and asks me before anything in that gray area, and I decide case by case. The 37 restaurants whose research touched those pages were re-checked using only legitimate search.

    The line we care about is facts vs. writing. Restaurant names, air dates and closures are facts anyone can use. foodiepie's dish descriptions are one person's writing from 15 years of watching TV, so they stay in our private files and never appear in what we publish. We credit foodiepie and Wikipedia by name.
