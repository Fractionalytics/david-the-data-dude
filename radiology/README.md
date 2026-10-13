# Radiology: AI was supposed to replace radiologists. What happened?

In October 2016, Geoffrey Hinton said "people should stop training radiologists now," predicting deep learning would outperform them within 5 to 10 years. Ten years later, what happened to radiologists?

This folder is the behind-the-scenes companion to David the Data Dude's [Instagram Reel](https://www.instagram.com/reel/Decxhi7SGek/) on the question.

<p align="center">
  <a href="https://www.instagram.com/reel/Decxhi7SGek/"><img src="cover.jpg" alt="Reel cover: an Amara's law sketch of what we expect vs. what happens, over the short and long run" width="300"></a>
  <br>
  <b>▶ <a href="https://www.instagram.com/reel/Decxhi7SGek/">Watch the Reel on Instagram</a></b>
</p>

The Reel is under 3 minutes, so most of the work didn't make the cut. Here's the data, the code, a dated log of the predictions, every chart, and the problems we hit along the way.

## The finding

**Radiologists got more expensive relative to other doctors, not less.** Radiologists' average pay as a multiple of the average doctor's:

| | 2017 report | 2026 report |
|---|---|---|
| Radiologists | $408,000 | $609,684 |
| Average doctor | $313,542 | $422,625 |
| **Radiology premium** | **1.30×** | **1.44×** |

If AI were replacing radiologists, their price relative to other doctors should fall. It rose. Medscape's surveys show the same thing (1.34× → 1.48×, 2017 to 2025 pay).

Supporting evidence, 2016–2024:
- **Headcount:** radiologists billing Medicare grew 12.8% (31,389 → 35,403), against 7.2% for all physicians (602,317 → 645,633).
- **Demand:** the 65+ population grew 24% (49.2M → 61.2M), and imaging services per traditional-Medicare patient rose 38%, against 27% for all physician services.
- **Supply per patient:** radiologists per 100,000 Americans aged 65+ fell 9%.
- **AI did arrive:** 1,230 of the FDA's 1,614 AI-enabled medical devices (76%, through June 29, 2026) were reviewed by its radiology panel. Every radiology detection and triage product code is defined as aiding or assisting a clinician, not replacing one.

These are correlations. They show radiologists weren't replaced, not why.

## Definitions

- **Radiologists** = CMS provider types Diagnostic Radiology plus Interventional Radiology.
- **Physicians** = CMS's physician provider types (39 non-physician types such as nurse practitioners and physician assistants excluded). Oral and maxillofacial surgeons count only if they hold an MD or DO, since it's a dental specialty.
- **Billing Medicare** = an individual NPI in CMS's Medicare Physician & Other Practitioners file for that year: traditional (fee-for-service) Medicare only, with CMS's 11-beneficiary minimum. Medicare Advantage claims aren't in it.
- **Average doctor** (Doximity) = the unweighted mean of the 48 specialties listed in both the 2017 and 2026 reports, since Doximity publishes no all-physician dollar average. The 2017 report pools surveys from 2014–2017; the 2026 report covers 2025 pay.
- **Hinton's prediction** has two halves, scored separately: the capability claim (deep learning beats radiologists at reading scans) is late by his own account. In 2023 he called it "a daring and incorrect prediction" and said he was "off by about a factor of three." The prescription ("stop training radiologists now") was wrong: demand outran supply.

## What's here

| Folder | What |
|---|---|
| `data/processed/` | The tables behind every number: CMS physician and radiologist counts, demand controls (Census, CMS enrollment and services), pay by specialty, FDA AI devices by year and by function, NRMP Match positions |
| `data/claims/` | A dated log of 23 public claims about AI and radiologists, predictions and rebuttals (Hinton, Khosla, Ng, Huang and others), with the venue, a primary link and whether the wording was checked against the primary |
| `scripts/` | The pipeline. Raw downloads (about 1.4 GB) aren't included; each script names where its source comes from |
| `docs/` | [Data challenges](docs/data-challenges.md): what went wrong along the way. [Spot-checks](docs/spot-checks.md): how the numbers were verified by hand |
| `charts/exploratory/` | An early exploratory chart |
| `video/` | The Remotion source for the Reel's animated charts |
| `videos/` | The rendered charts and their final frames, in the Reel's card order |

## Sources

- CMS, [Medicare Physician & Other Practitioners](https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners), by provider, 2016 and 2024
- U.S. Census Bureau, national population estimates by single year of age
- FDA, list of AI-enabled medical devices, and its product classification file
- Doximity Physician Compensation Reports, [2017](https://press.doximity.com/reports/physician-compensation-report-2017.pdf) and [2026](https://www.doximity.com/reports/physician-compensation-report/2026); Medscape Physician Compensation Reports (via trade-press reprints)
- NRMP Main Residency Match results, 2016–2026
- Dhanoa et al., "The evolving role of the radiologist: the Vancouver workload utilization evaluation study," *J Am Coll Radiol* 2013;10(10):764–769 (36% of time on image interpretation)
- Hinton: [Creative Destruction Lab, 2016](https://www.youtube.com/watch?v=2HMPRXstSvQ); [Eric Topol's *Ground Truths*, 2023](https://erictopol.substack.com/p/geoffrey-hinton-large-language-models); The New York Times, May 14, 2025

## License

Code, docs and charts are under the repo's [MIT License](../LICENSE). CMS, Census and FDA data are U.S. government works. Pay figures belong to Doximity and Medscape, and quoted statements to their speakers and publishers.
