# Greg's 13

Status: **approved by David 2026-10-07 (version g1), run on all 424 featured ideas.** 5 and 12 kept separate. Exploratory: tests whether Ideabrowser's featured ideas match Greg Isenberg's list of "the only businesses left to build" (X post, Sep 12 2026, saved in David's Sublime), and whether the match changed around that date.

## Design
- **Ideas:** the 424 featured ideas (title + pitch), not the title-only "more ideas", which proved too thin for judgments like this.
- **One yes/no question per type.** Greg's types overlap (a vertical agent can also be a service firm), so each idea gets 13 separate yes/no scores instead of a forced single pick. Code combines them:
  - **Fits Greg's list:** yes on at least one type.
  - **Count per type:** how many ideas fit each type, by period.
- **Threshold:** Jev's yes probability of 0.5 or more counts as yes. We also report how many land between 0.4 and 0.6, so a borderline threshold is visible.
- **Periods:** era 1, era 2, newsletter before Sep 12, newsletter from Sep 12. Dates and counts stay in code.

## Definitions (Greg's names, our boundaries)

| # | Greg's type | Yes if… | Boundary |
|---|---|---|---|
| 1 | AI native service firms | The customer buys a finished result (bookkeeping done, calls answered), delivered by a firm using AI, not software they run themselves | A SaaS tool the customer operates is No |
| 2 | Offline businesses | The business mainly operates in the physical world: in person, local, on site | An app for an offline industry is No |
| 3 | Distribution (media, community, audience) | The business *is* an audience: newsletter, media brand, community, creator channel | Using social media for marketing is No |
| 4 | Proprietary datasets | The core asset is data others can't easily get, collected or built by the business | Using public data or an API is No |
| 5 | Domain specific harnesses | Software or an agent that runs one industry's whole workflow end to end | One task within a workflow is No (see 12) |
| 6 | Robotics and physical AI | Robots, drones, sensors or AI acting in the physical world | |
| 7 | Physical products with a fan following | A physical product sold to an enthusiast or fan community | Commodity goods are No |
| 8 | Compute and energy | Selling compute, chips, power, energy or energy savings | |
| 9 | Health, longevity, and care | Health, medical care, longevity, caregiving, elder or child care | General fitness apps: yes only if health is the core claim |
| 10 | Marketplaces and social networks | Connects two sides (buyers and sellers, people, or agents), or is a social network | |
| 11 | Real assets | Owns, finances or trades property, equipment, land or infrastructure | Software for real estate agents is No |
| 12 | Vertical agents | An AI agent that does one specific job for one industry | A general-purpose AI tool is No |
| 13 | Security | Cybersecurity, fraud prevention, physical security, identity | |

## Questions for David
1. Do these boundaries capture what Greg means? He gave only the names.
2. Types 5 and 12 (harness vs. vertical agent) will overlap heavily. Keep them separate, or merge them into one "industry-specific AI agent" type for the charts?

## What the first run showed
- Jev said "vertical agent" for 303 of 424 ideas, including 127 that the main classification says aren't AI-centred (e.g. "Be the eBay of burial plots"). It reads "agent" as any single-industry tool. In the analysis, types 5 and 12 count only when the main classification also says AI is central (computed in code; no definitions change).
- Harness and vertical agent overlap: 13 ideas are both, out of 21 harness yeses.
