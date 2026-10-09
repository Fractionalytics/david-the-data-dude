# Ideabrowser: what a startup-idea feed recommends, and how that changed

Ideabrowser emails one featured startup idea every day. Fourteen months of those emails sat in David's Gmail, so he treated the inbox as a database: every edition downloaded, every featured idea classified by an AI model, and the mix tracked over time.

This folder is the behind-the-scenes companion to David the Data Dude's [Instagram Reel](https://www.instagram.com/reel/DeSmb2hSPaw/) on the question.

<!-- Reel cover thumbnail (about 300px, linking to the Reel) goes here once David supplies cover.jpg. -->
<p align="center"><b>▶ <a href="https://www.instagram.com/reel/DeSmb2hSPaw/">Watch the Reel on Instagram</a></b></p>

## The finding

**For about a year, almost none of Ideabrowser's featured ideas were services businesses. Starting July 28, 2026, the day the email switched to a newsletter format, 41% have been.**

| Featured ideas classified as services | Count | Share |
|---|---|---|
| Era 1: Jul 29, 2025 – Jan 25, 2026 | 4 of 173 | 2% |
| Era 2: Jan 26 – Jul 27, 2026 | 5 of 179 | 3% |
| The 74 days before July 28, 2026 | 2 of 74 | 3% |
| **Newsletter era: Jul 28 – Oct 9, 2026 (74 days)** | **30 of 74** | **41%** |

- **It happened in one step, not gradually.** May and June 2026 had no service ideas at all (0 of 59); the first two days of the new format both featured one.
- **Software was the default before.** 158 of 173 featured ideas in era 1 were software or apps (91%), against 26 of 74 in the newsletter era (35%).
- **It isn't a straight line.** August 2026 leaned services (15 services, 8 software), and September leaned back to software (8 services, 15 software).
- **The timing lines up with the "service as software" thesis** argued by Foundation Capital (June 2025) and Sequoia (March 2026): that AI will sell finished work rather than tools, in a services market far bigger than software. This is a correlation in one feed, not proof of a market shift; the change coinciding exactly with a redesign suggests an editorial decision.

Data through **October 9, 2026**. Eras follow the email's own template changes (Jan 26 and Jul 28, 2026).

## Definitions

**Featured idea.** The one idea each daily email leads with: 426 emails, one featured idea each. Before July 28, 2026 the emails also listed about three extra ideas a day (1,010 in all, usually just a title); those stopped with the redesign, so every comparison across eras uses featured ideas only.

**Business type.** Each featured idea's title and the first 150 words of its pitch were given to Jev (TypeSafe's classification model, `jev-1.13.0`) with this question, "What kind of business is this idea?", and these options:

| Option | Definition given to the model |
|---|---|
| Software / app | SaaS, mobile apps, browser extensions, dashboards. |
| Marketplace | Connects two sides, such as buyers and sellers or clients and providers. |
| Service | Done-for-you, agency, concierge or staffing work where people do the work. |
| Physical product | Goods, kits or hardware. |
| Media, community & data | Newsletters, directories, reports, indexes or communities. |
| Not clear | The text does not say what kind of business it is. |

The idea counts as the option Jev rates most likely. Who pays, industry and "is AI central?" were classified the same way; all four questions are in [`scripts/definitions.py`](scripts/definitions.py) and the reasoning behind them in [`docs/categories.md`](docs/categories.md).

## How sure are the labels?

- **Reordering the options** (models can favor whichever comes first) changed 1–3 answers in 100 per question, and none of those that were 0.8 confident or more.
- **A 50-idea pilot** was reviewed by hand before the full run; it led to one rule change (cross-industry tools are classed by the job they do, not the industry the pitch uses as an example).
- **Close calls exist.** Every label comes with Jev's confidence in [`data/daily_featured_labels.csv`](data/daily_featured_labels.csv). For example, the October 9 idea is a 0.48 call for services; counting it as software would make the newsletter-era share 39% instead of 41%.

## What's here

| Folder | What |
|---|---|
| [`data/`](data/) | `daily_featured_labels.csv`: one row per day, with Jev's four answers and their confidence (no idea titles or text). `business_type_by_era.csv` and `business_type_by_month.csv`: the counts behind every number above. `chart-data/`: what the Reel's charts draw. |
| [`scripts/`](scripts/) | The whole pipeline: download the emails, parse them, classify with Jev, check robustness, cluster bottom-up, make the charts. |
| [`docs/`](docs/) | [`data-challenges.md`](docs/data-challenges.md): everything that got in the way, from Gmail's rate limit to an AI that believed the example instead of the product. [`categories.md`](docs/categories.md): the classification design. [`greg-13.md`](docs/greg-13.md): the ideas scored against Greg Isenberg's "only businesses left to build" list. |
| [`charts/exploratory/`](charts/exploratory/) | Every exploratory chart, including the ones that didn't make the cut. |
| [`video/`](video/), [`videos/`](videos/) | The Remotion source for the Reel's animated charts, and the rendered videos. |

## What's not here, and why

- **The emails, idea titles and pitches.** They're Ideabrowser's content in a personal inbox, so only labels and counts are published. The scripts will rebuild everything from your own subscription.
- **The Claude and TypeSafe logos** and the conveyor animation that shows them; they belong to their companies. `video/src/charts/Conveyor.tsx` falls back to text if you set `LOGOS` to `null`.

## License

Code, docs, labels and charts are under the repo's [MIT License](../LICENSE). Ideabrowser's emails and ideas are its own and aren't included.
