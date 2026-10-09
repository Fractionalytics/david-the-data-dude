# Idea categories

Status: **approved by David 2026-10-07 (definitions v3)**, scope: all 1,433 ideas. Implemented in `scripts/definitions.py`.

## What gets classified

- **Unit:** one idea, keyed by its `ideabrowser.com/idea/<slug>` link (1,361 distinct ideas in eras 1–2), plus the 72 newsletter-era featured ideas, which have no link. About 1,433 ideas in total.
- **Input Jev sees:**
  - **Featured ideas** (424): title plus the idea's pitch paragraph, without the rest of the email (intros, sponsors, tactics), because unrelated text lowers accuracy.
  - **"More ideas" / "Also released"** (1,010): title only. The 75 without a title get their slug, with dashes turned into spaces.
- **Robustness check:** featured ideas are also classified from the title alone, and we report how often the two answers agree. That tells us how much to trust the title-only answers.

## Questions (one judgment each, so they can be combined in code)

### Q1. Who pays? (Choice)
"Who is the paying customer for this business idea?"

| Option | Covers | Boundary cases |
|---|---|---|
| Consumers | Individuals or families paying for themselves | A parent buying for a kid → Consumers |
| Small & local businesses | Shops, clinics, contractors, restaurants, agencies, small teams | A solo therapist's practice → here, not Solo professionals |
| Solo professionals & creators | Freelancers, creators, indie hackers, job seekers, one-person operators selling their own work | |
| Larger companies & institutions | Mid-size and enterprise companies, enterprise teams, institutions (schools, hospitals, governments) | "Remote teams" with no size stated → Not clear |
| Not clear | The text doesn't say who pays | |

### Q2. Industry served (Choice)
"Which industry or life area does this idea serve? Pick the customer's industry, not the technology. If the idea works across many industries and the pitch only uses one as an example, pick the job it does (for example Marketing, sales & media) instead of the example's industry." *(v2 rule, approved by David 2026-10-07 after the pilot.)*

| Option | Boundary cases |
|---|---|
| Home services & trades | HVAC, lawn care, plumbing, cleaning, contractors |
| Real estate & construction | Agents, landlords, builders, property managers |
| Health & medical | Clinics, therapists, PT, pharmacy, patient tools |
| Fitness, wellness & beauty | Gyms, coaches, med spas, salons, sleep, nutrition |
| Finance, insurance & legal | Lending, credit, accounting, tax, insurance, law |
| Retail & e-commerce | Online stores, Shopify, product brands, resale |
| Food & restaurants | Restaurants, food brands, groceries, farms |
| Marketing, sales & media | Ads, outreach, social media, content, newsletters |
| Software & AI tools | Tools for developers, SaaS companies, AI agents themselves |
| Work, hiring & careers | HR, recruiting, job seekers, freelancers' admin |
| Education & parenting | Schools, students, tutoring, kids, family logistics |
| Travel, events & hospitality | Hotels, Airbnb, events, tourism |
| Hobbies, collectibles & pets | Collectors, crafts, games, pets |
| Automotive & transport | Car buying, dealers, repair, fleets |
| Other | Real but not listed (e.g. funeral, agriculture equipment, government) |
| Not clear | |

### Q3. What kind of business is it? (Choice)

| Option | Covers |
|---|---|
| Software / app | SaaS, mobile apps, browser extensions, dashboards |
| Marketplace | Connects two sides (buyers and sellers, clients and providers) |
| Service | Done-for-you, agency, concierge, staffing; people do the work |
| Physical product | Goods, kits, hardware |
| Media, community & data | Newsletters, directories, reports, indexes, communities |
| Not clear | |

### Q4. Is AI central to the product? (Choice: Yes / No / Not stated)
"Yes" only if the idea's core function depends on AI (AI agents, generation, detection, prediction). "No" if AI isn't mentioned or is only a side feature. "Not stated" if the text is too thin to tell.

## Computed in code, not by Jev
- Era, date, featured vs. extra (already in `ideas.csv`)
- Revenue tag and its dollar value (era 1 only)
- Whether the title literally says "AI"; this is compared with Q4 to tell "says AI" apart from "is AI"

## How answers are used
- **Strict (default):** keep Jev's top option, including Not clear and Other. Low-confidence answers stay as they are and get flagged.
- **Order-bias check:** a sample of 100 ideas is rerun with the options in a different order, and how often answers change is reported.
- **Pilot first:** 50 ideas (featured and extra, from all three eras) are run before the full batch, and you review them by hand.

## Questions for David
1. Are these the right four questions for your story about who micro-founders are building for, or is one missing (e.g. "how much money/effort to start")?
2. Are the industry buckets the ones you'd want to show on screen? Merge or split any.
3. Include the 1,010 "more ideas," or only the 424 featured ideas? Featured ideas give better input; all of them give far more data.

## Changes after approval
- **v2** (2026-10-07): industry boundary rule for cross-industry tools, after the pilot.
- **v3** (2026-10-07): "Larger companies" renamed "Larger companies & institutions", so schools and governments don't read as corporations. Definition unchanged.
