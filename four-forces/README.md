# Four Forces: where AI is (and isn't) costing jobs

After the [Radiology](../radiology/) Reel, a viewer said it picked "the one tiny area" where Geoffrey Hinton was off, and that "AI is already displacing Jobs in millions." Fair challenge. So we looked at every occupation in U.S. government data and asked: how many jobs could AI plausibly be behind, where are they, and why do some jobs fall fast while others keep growing?

This folder is the behind-the-scenes companion to David the Data Dude's [Instagram Reel](https://www.instagram.com/reel/Dekc7YeyVgM/) and [carousel](https://www.instagram.com/p/DekkuSUlKk-/).

<p align="center">
  <a href="https://www.instagram.com/reel/Dekc7YeyVgM/"><img src="cover.jpg" alt="Four Forces Reel cover" width="300"></a>
  <br>
  <b>▶ <a href="https://www.instagram.com/reel/Dekc7YeyVgM/">Watch the Reel on Instagram</a></b>
</p>

## The finding

**About 870,000 jobs that could plausibly be AI's doing, not millions, and mostly in office work.**

| Step (May 2022 → May 2025) | Jobs |
|---|---|
| The most AI-exposed occupations grew this much slower than all other occupations | 1.8M |
| Adjusted for their slower growth *before* ChatGPT (office work was already shrinking) | −670K |
| Minus loan and insurance processing (interest rates, not AI; see corrections) | −260K |
| **What's left: jobs lost or never created that could be attributed to AI** | **≈870K** |

That's a gap against the rest of the economy, not a count of layoffs, and not proof AI caused it.

- **The fast lane is office work.** Customer service reps fell 9.9% (2.88M → 2.60M, May 2022 → May 2025); before ChatGPT they'd fallen 1.3% (May 2019 → May 2022). Office and administrative support overall fell 921,000 (−4.9%) while all jobs outside office work grew 6.6%. The call center industry lost 31% of its jobs (440K → 303K, Aug 2022 → Aug 2026, preliminary).
- **The slow lane is the licensed professions.** Paralegals *grew* 13.8% (May 2022 → May 2025). Radiologists grew too (see the Radiology project).

## The framework

Four forces slow AI's effect on a job. The stronger the force, the more secure the job.

| Force | The question | Fast lane (customer service, office & admin) | Slow lane (radiology, law) |
|---|---|---|---|
| 1. Task vs. job | Is the automatable task most of the job, or just one slice? | Most of the job | One slice (radiologists spend about 36% of their time reading images) |
| 2. Gatekeepers | Regulations, liability, licensing: who has to sign? | Light | Heavy (FDA, malpractice, the bar) |
| 3. Demand | Does cheaper work create more or less demand for it? | No: people don't call support more because it got cheaper | Yes: cheaper scans mean more scans (Jevons paradox) |
| 4. Checking | Is the AI's work cheap to check, or do mistakes surface late? | Cheap | Expensive, and mistakes surface late |

## Definitions

- **Most AI-exposed** = occupations BLS rates **"Very high"** in its [AI exposure categories](https://www.bls.gov/emp/publications/ai-exposure-categories.htm) (2025–35 Employment Projections). BLS says exposure "does not imply job loss."
- **Comparison group (waterfall)** = all other rated occupations. The comparison uses a balanced panel of 757 detailed occupations present in every OEWS year (94% of May 2025 employment).
- **Jobs outside office work (customer service and paralegal comparisons)** = all occupations minus SOC 43, office and administrative support, from BLS's official totals.
- **Pre-ChatGPT adjustment** = the most-exposed group's growth gap vs. the comparison group from May 2019 to May 2022, subtracted from its May 2022 → May 2025 gap (a difference-in-differences; descriptive, not causal).
- **Call center industry** = BLS CES NAICS 56142, telephone call centers (series CEU6056142001, not seasonally adjusted, so both ends are August).

## Corrections

We found these after the Reel shipped. None changes the story, but we'd rather call ourselves out. Details in [docs/corrections.md](docs/corrections.md).

1. **"Loan processing" also removed two insurance jobs** (claims clerks and underwriters). Removing only the loan jobs leaves about **877,000**, not 870,000.
2. **"Other jobs" meant two different groups** on two charts: all other rated occupations on the waterfall, and all jobs outside office work on the paralegal chart.
3. **"The ChatGPT era, between 2022 and 2025" starts six months early.** The survey is taken in May; ChatGPT launched November 30, 2022.
4. **Paralegals aren't the same "office work"** as the fast lane: BLS files them under legal occupations.

## What's here

- `data/raw/`: the public source files (BLS OEWS national files for May 2019 and 2022–2025, BLS AI exposure categories, BLS CES call centers, NY Fed recent-graduate data).
- `data/processed/`: every table the charts read. The Reel's numbers: `exposure_waterfall.csv`, `takeaway_numbers.csv`, `call_centers_ces.csv`, and `numbers_by_period.csv` (every figure with both periods).
- `scripts/`: the pipeline (Python). Start with `exposure_ledger.py`, then `exposure_waterfall.py`, `takeaway_numbers.py`, `call_centers_ces.py` and `video_data.py`.
- `docs/`: [data challenges](docs/data-challenges.md) (12 problems we hit, with numbers), [corrections](docs/corrections.md), [numbers by period](docs/numbers-by-period.md), and the [rubric table](docs/rubric-table.md).
- `charts/`: exploratory charts, including a rebuild of Derek Thompson's "New Grad Gap" chart and the full exposure waterfall (down to 0.64M if you also remove the health care hiring boom).
- `video/` and `videos/`: the Remotion source and the rendered chart clips and stills, one per storyboard card.
- `carousel/`: the six carousel slides and a PDF.

## What didn't make the Reel

We also looked at the entry-level "canaries" research, AI-washed layoffs (companies citing AI for cuts that aren't about AI), the jobs AI has created (data centers, forward deployed engineers), a possible solo-business boom, and Hinton's full record of job predictions. Those may become their own pieces.

## Sources and licenses

BLS data (OEWS, CES, Employment Projections) are U.S. government works. The recent-graduate data come from the Federal Reserve Bank of New York, *The Labor Market for Recent College Graduates*, and belong to the NY Fed. The radiology time figure is from Dhanoa et al., *Journal of the American College of Radiology* (2013). Code, docs and charts are MIT-licensed (see the top-level [LICENSE](../LICENSE)).
