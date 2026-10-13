# Spot-checks: Radiology (deep dive, iteration 1)

> **Public version.** The private copy also has checks 1-4, which look up four individual radiologists by NPI. They passed; they're left out so this repo doesn't single out people.

Generated 2026-10-12 from the final and intermediate files (`scripts/spot_check_candidates.py`, plus queries over `data/processed/`). Each check targets one pipeline stage where we could have gone wrong. David clicks the links and fills in **Verdict** (✅ matches / ❌ wrong / 🤷 can't tell).



| # | Item | Tests | Our data says | Look up | Verdict |
|---|---|---|---|---|---|
| 5 | Maxillofacial Surgery (excluded from "physicians") | **Physician / non-physician split**: we dropped 39 provider types as non-physicians | 2024 credentials in this type: DDS 197, DMD 114, DDS+MD 114 combined, MD 21. Mostly dentists, so excluding it is right, but ~135 MDs are dropped with it | No link: a judgment call. Is excluding the whole type acceptable? (Effect on the physician total: about 0.05%) | Why would these surgeons not be considered physicians? I'm inclined to keep it in since the effect is so small. **Decided (David, 2026-10-12): count only those with an MD/DO** (404 of 946 in 2016, 287 of 601 in 2024), since oral & maxillofacial surgery is a dental specialty. Physicians now 602,317 → 645,633, still +7.2% ✅ |
| 6 | NRMP 2021, Diagnostic Radiology | **PDF parsing**: our parser reads Table 7A text, strips hidden arrow glyphs and sums PGY-1 + PGY-2 + Physician (R) | 1,139 positions offered in 2021 (PGY-1, PGY-2 and R rows of "Radiology-Diagnostic") | [NRMP 2021, Table 7A](https://www.nrmp.org/wp-content/uploads/2022/11/MRM-Results_and-Data_2021_revised.pdf#page=28), printed pages **20–21** (the PDF viewer calls them 28–29; the front matter has its own numbering). The table has **three sections**, each starting with a bold header row: "PGY-1 Positions" (p. 20), then "PGY-2 Positions" and "Physician (R) Positions" (p. 21). Ignore the "(PGY-1 Only)" rows: those are separate preliminary programs, not radiology. In each section, find the row named exactly **Radiology-Diagnostic** and read the **first number** (2021, "Offered"). You should see **122** (PGY-1) + **986** (PGY-2) + **31** (Physician R) = **1,139** | ✅ |
| 7 | NRMP 2026, Psychiatry | **Name matching**: "Psychiatry" (2026) was merged with "Psychiatry (Categorical)" (2016) | 2,516 positions in 2026 vs 1,386 in 2016 (+81.5%, top of the ranking) | **2026:** [NRMP 2026, Table 7A](https://www.nrmp.org/wp-content/uploads/2026/05/Main_Match_Results_and_Data-2026.pdf#page=44), printed page **33** (PDF page 44), "PGY-1 Positions" section: row **Psychiatry**, first number = **2,516**. Psychiatry has no row in the PGY-2 or Physician (R) sections on p. 34. **2016:** [NRMP 2016, Table 7](https://www.nrmp.org/wp-content/uploads/2021/07/Main-Match-Results-and-Data-2016.pdf#page=30), printed pages **22–23** (PDF 30–31): row **Psychiatry (Categorical)** in PGY-1 = **1,384**, plus a row **Psychiatry** in each of PGY-2 and Physician (R) on p. 23, **1** each, total **1,386**. Pass if it's clearly the same specialty under a new name, and the numbers match | ✅ |
| 8 | NRMP grand totals | **Benchmark** for "radiology kept pace with the Match" | 30,750 (2016) → 38,106 (2021) → 44,344 (2026) | Last row of each table, **GRAND TOTAL**, first number: [2016](https://www.nrmp.org/wp-content/uploads/2021/07/Main-Match-Results-and-Data-2016.pdf#page=31) printed p. **23** (PDF 31) · [2021](https://www.nrmp.org/wp-content/uploads/2022/11/MRM-Results_and-Data_2021_revised.pdf#page=29) printed p. **21** (PDF 29) · [2026](https://www.nrmp.org/wp-content/uploads/2026/05/Main_Match_Results_and_Data-2026.pdf#page=45) printed p. **34** (PDF 45). Some cells print run together (e.g. "18,88029,572"); only the first number matters | ✅ |
| 9 | FDA K231470, Lunit INSIGHT DBT | **Classification, clearest "detect" case** (code QDQ) | Group: detect. FDA definition: "intended to aid in the detection ... of lesions suspicious for cancer" | [FDA record K231470](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K231470): open the "Summary" PDF, read Indications for Use. Does it aid a reader, not replace one? | ✅ |
| 10 | FDA K231195, Brainomix 360 Triage ICH | **Classification, triage** (code QAS) | Group: triage. "Aid in prioritization and triage" of suspected brain bleeds | [FDA record K231195](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K231195): does the radiologist still read every case? | ✅ *(Claude)* Summary PDF: "notification-only, parallel workflow tool"; "does not remove cases from a reading queue and operates in parallel to the standard of care" |
| 11 | FDA K223726, Canon Aquilion Precision with AiCE | **Classification, "scanner"**: AI inside hardware, counted as not touching the read | Group: scanner (code JAK, CT system). AI is image reconstruction | [FDA record K223726](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K223726): is the AI part reconstruction or denoising? | ✅ *(Claude)* Summary PDF: AiCE is "intended to reduce image noise and improve image quality" with a deep convolutional neural network. No detection function |
| 12 | FDA K241561, MammoScreen BD | **Weakest call**: a broad-code (QIH) device that our name check flagged as possibly "detect" | Group: measure. We think "BD" = breast density, i.e. measurement, not detection | [FDA record K241561](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K241561): density assessment or cancer detection? | ✅ *(Claude)* Summary PDF: common name "Breast Density Assessment Software"; "not intended as a replacement for the review of a physician". Measurement, as classified |
| 13 | Doximity radiology pay, 2017 and 2026 reports | **Pay series**, the base of the 1.30× → 1.44× premium | $408K (2017 report, rounded; pooled 2014–17 surveys) and $609,684 (2026 report) | [Doximity 2017 report (PDF)](https://press.doximity.com/reports/physician-compensation-report-2017.pdf): appendix specialty table, Radiology · [Doximity 2026 report](https://www.doximity.com/reports/physician-compensation-report/2026): specialty table, Radiology | ✅ *(Claude)* 2017 PDF prints "Radiology $408K" (pp. 5 and 19); 2026 page lists $609,684 |
| 14 | Census 65+ population, 2016 and 2024 | **Scope / denominator** for "65+ up 24%" | 49,208,479 (2016) → 61,179,918 (2024), +24.3% | Census press releases: [2016: 49.2 million](https://www.census.gov/newsroom/press-releases/2017/cb17-100.html) · [2024: 61.2 million](https://www.census.gov/newsroom/press-releases/2025/older-adults-outnumber-children.html) | ✅ *(Claude)* Releases say 49.2 million (2016) and 61.2 million (2024); ours round to the same |
| 15 | Hinton audio and video | **Quotes**: card 3's clip and card 7's audio | 2016: "People should stop training radiologists now ... within 5 years ... might be 10" at the clip's 0:13–0:28 (unverified timestamps). 2023: "off by about a factor of three" at ~5:59 of Topol's *Ground Truths* | [2016 video, starts at 0:13](https://www.youtube.com/watch?v=2HMPRXstSvQ&t=13) · [Topol podcast](https://erictopol.substack.com/p/geoffrey-hinton-large-language-models) (play from ~5:59) | 🤷 *(Claude)* Wording verified against both transcripts (2016 in david-brain; Topol's page shows the passage at 05:59). The **clip timestamps 0:13–0:28 are unverified**: Claude can't watch video. David to confirm while editing |
| 16 | **Outside claim**: Jensen Huang, Lex Fridman #494 (2026-03-23): "the number of radiologists grew" | Does our data agree with the most-quoted "AI didn't kill radiology" claim? | Yes: radiologists billing Medicare 31,389 (2016) → 35,403 (2024), +12.8%. But BLS employment fell 29,530 (2021) → 26,770 (2025) inside a ±14% error band, and AAMC is flat (27,719 → 27,197, 2017–2021, unverified). Which count you use decides the answer | No link: a judgment call. Is citing the Medicare count, with its caveat, fair? | ✅ *(Claude's recommendation)* Fair as worded: cards 4 and 11 already say "billing Medicare". Name the source (CMS, traditional Medicare) in the post text |

## Already found while generating (not waiting on David)

**Card 5's workload number is fragile.** Row 3's outlier led to a robustness check. Radiologists billing over 100,000 Medicare services a year went from 33 (2016) to 124 (2024), and they hold 9.1% of all diagnostic radiology services in 2024 (2.3% in 2016). These are almost certainly groups or labs billing under one person's NPI. The "+10% vs +3.6%" comparison uses means, so they inflate it:

| Services per clinician, 2016 → 2024 | Diagnostic radiologists | All physicians |
|---|---|---|
| Mean (what card 5 uses) | 6,034 → 6,638 (+10.0%) | 3,315 → 3,435 (+3.6%) |
| Mean, top 1% removed | 5,424 → 5,593 (+3.1%) | 2,072 → 1,888 (−8.9%) |
| Median | 3,840 → 2,949 (−23%) | 826 → 568 (−31%) |

Radiology beats physicians on all three measures, so "rose more than for the average physician" survives. **"10% vs 3.6%" doesn't**: the per-person rise is an outlier effect, and medians fall for everyone (fewer traditional-Medicare patients per doctor as people move to Medicare Advantage). Logged as data-challenges §17. The headline (a count of radiologists, not their volume) isn't affected.

## Result (2026-10-12)

| Stage | Rows | ✅ | ❌ | 🤷 |
|---|---|---|---|---|
| Headline inputs (identity, counts, denominators) | 1–4, 8, 14 | 6 | 0 | 0 |
| Physician split | 5 | 1 (after David's MD/DO fix) | 0 | 0 |
| PDF parsing | 6–7 | 2 | 0 | 0 |
| FDA classification | 9–12 | 4 | 0 | 0 |
| Pay series | 13 | 1 | 0 | 0 |
| Quotes | 15 | 0 | 0 | 1 (clip timestamps) |
| Outside claim | 16 | 1 | 0 | 0 |

**Who checked:** David verified rows 1–4 and 6–9 by hand. Claude checked rows 10–14 against the primary documents and judged row 16; David chose to accept those. Row 5 was David's decision.

**Decision rule applied:** no ❌ anywhere, so **the dataset is fit to publish**. One open item, not blocking: confirm the 2016 clip's 0:13–0:28 timestamps while editing (row 15).

## Decision rule

- **Rows 1–4, 8 or 14 (the headline's inputs):** any ❌ blocks publishing until the count is fixed and the headline recomputed.
- **Rows 6–7 (parsing):** one ❌ means re-checking every NRMP value used on screen.
- **Rows 9–12 (classification):** if 2 or more are ❌, rework the function groups before card 5 cites "aids, doesn't replace."
- **Row 13:** a ❌ means redoing the pay premium from the corrected values before card 8 uses it.
- **Row 15:** a ❌ means fixing the quote or timestamp. Doesn't block the data.
- **Row 16:** judgment, not pass/fail. Decide whether card 4 needs a "by Medicare billing" qualifier.
