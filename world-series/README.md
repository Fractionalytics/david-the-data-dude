# The World Series of Last Names

A game where all you need is a last name. Every 2026 Major League Baseball player was sorted into a team by what kind of surname he has: a place, a nickname, a parent's name or a job. Each team then fielded its best roster by WAR (wins above replacement), and the highest total won.

This folder is the behind-the-scenes companion to David the Data Dude's Instagram Reel and carousel.

<p align="center">
  <a href="https://www.instagram.com/reel/DegxmR8Bf4h/"><img src="cover.jpg" alt="Reel cover: the World Series of Last Names" width="300"></a>
  <br>
  <b>▶ <a href="https://www.instagram.com/reel/DegxmR8Bf4h/">Watch the Reel on Instagram</a></b> · <a href="https://www.instagram.com/p/DehLzE8lCwS/">See the carousel</a>
</p>

## The result

| Rank | Team | Surname type (Wikipedia's term) | Roster WAR |
|---|---|---|---|
| 1 | **The Places** | Toponymic | **67.85** |
| 2 | The Nicknames | Cognominal | 67.79 |
| 3 | The Sons of Somebody | Patronymic (includes 2 matronymics) | 64.65 |
| 4 | The Jobs | Occupational | 53.49 |

- **It was a squeaker.** The Places won by 0.06 WAR. Pete Crow-Armstrong (9.83 WAR, the best player in the data) plays for The Nicknames, because both halves of his name are nicknames.
- **One classification can flip the title.** If Parker Messick's surname (possibly from Messac, in Brittany) counted as unknown, or Tarik Skubal's (a Czech nickname, "plucked") counted as a nickname rather than a job, The Nicknames would win instead. `scripts/scenarios.py` runs these what-ifs.
- **The biggest team wasn't the best.** The Sons of Somebody had 514 players, the most of any type, and finished third.
- **Latin American players aren't more patronymic than US players.** Among players whose surname type is backed by a source, it's 43% for Latin America & Caribbean and 41% for USA/Canada (not significant). The real difference is place names: 38% vs. 25%.

Season: the 2026 MLB regular season, 1,472 players who appeared in a game.

## Definitions

**Surname types** follow the "Origins of particular surnames" section of Wikipedia's [Surname](https://en.wikipedia.org/wiki/Surname) article. The exact option text given to the classifier is in [`scripts/definitions.py`](scripts/definitions.py). In short:

| Team | Type | A surname that comes from… |
|---|---|---|
| The Places | Toponymic | where the first bearer lived, a landscape feature, or a town or estate (Hill, Torres, Ohtani "big valley") |
| The Nicknames | Cognominal | a nickname for the first bearer: looks, personality, ethnic origin, or an office he only resembled (Brown, Moreno "dark", King) |
| The Sons of Somebody | Patronymic, plus matronymic | a father's or mother's first name (Johnson, Rodriguez, McGonigle "son of Congal") |
| The Jobs | Occupational | the first bearer's job or trade (Smith, Miller, Herrera "the smithy") |

The other categories (Patronage, Acquired/assigned, Compound, Ornamental/artificial, and origin unknown) couldn't field a full team. Patronage, the biggest of them with 14 players, has no catcher, second baseman or DH.

**Roster.** Four pitchers, three outfielders and one player at each of C, 1B, 2B, 3B, SS and DH: the highest 2026 WAR at each spot. A player's position is the one he played most in 2026. Shohei Ohtani counts with his pitching and batting WAR combined, and plays P or DH, whichever helps his team more. Short teams fill empty spots with any player they have.

**WAR** is Baseball-Reference's version (bWAR).

## How it was made

1. **Players and WAR:** Baseball-Reference's published WAR files, joined to MLB's player list for birthplaces and to MLB's game logs for positions ([`scripts/build_players.py`](scripts/build_players.py), [`scripts/fetch_positions.py`](scripts/fetch_positions.py)).
2. **What each name means:** Wiktionary's etymology for every surname ([`scripts/fetch_etymology.py`](scripts/fetch_etymology.py)). For the uncertain players good enough to change a roster, there was targeted web research in surname dictionaries (96 names). Six hyphenated names and four disputed ones were decided by hand ([`data/overrides.csv`](data/overrides.csv), [`data/compound_parts_research.csv`](data/compound_parts_research.csv)), with sources.
3. **Classification:** Jev, TypeSafe's classification model (`jev-1.13.0`), read each surname with its etymology and picked a type ([`scripts/classify.py`](scripts/classify.py)). 1,002 of 1,472 types are backed by a source or a hand decision. The rest are the model's own call, and [`data/players_surname_types.csv`](data/players_surname_types.csv) marks which is which (`evidence`).
4. **Rosters and standings:** [`scripts/build_rosters.py`](scripts/build_rosters.py).

Everything that went sideways is in [`docs/data-challenges.md`](docs/data-challenges.md), and each rostered player's name meaning, with how solid it is, is in [`docs/name-meanings.md`](docs/name-meanings.md).

## Files

- `data/`: the surname type for every player (no WAR), the rosters with WAR, standings, what-if scenarios, counts by region and country, and the most common US surnames per team (2010 Census).
- `scripts/`: the pipeline. `requirements.txt` lists the Python packages.
- `design/`: the four team logos and the script that draws them.
- `video/`: the Remotion source for the Reel's animation. `videos/` has the rendered animation, without David.
- `carousel/`: the ten carousel slides and the LinkedIn PDF.

## License

MIT, like the rest of this repo. Third-party data isn't republished here: Baseball-Reference's full-season WAR files, MLB's data feeds, and Wiktionary's etymology text (CC BY-SA 4.0) stay with their sources. The scripts fetch them. Only the rostered players' WAR appears in `data/rosters.csv`.
