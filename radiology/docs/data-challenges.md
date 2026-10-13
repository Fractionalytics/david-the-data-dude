# Data challenges: Radiology

The data problems we hit while testing "AI was supposed to replace radiologists, but the workforce grew." Logged as they came up, with the numbers.

## 1. There is no single "number of radiologists", and the free sources disagree by about 10,000

Four sources, four answers for roughly the same years:

| Source | What it counts | Value |
|---|---|---|
| BLS OEWS, May 2025 (SOC 29-1224) | Wage-and-salary radiologist **jobs** | 26,770 (RSE 7.3%) |
| AAMC Physician Specialty Data Report 2022 (2021 data) | Active "radiology and diagnostic radiology" physicians | 27,197 (secondary source; see #3) |
| CMS Medicare Part B PUF, 2024 | NPIs with provider type "Diagnostic Radiology" billing Medicare (11+ beneficiaries) | 32,843 (35,403 with Interventional Radiology) |
| Neiman HPI / JACR, 2023 | Radiologists **enrolled** to treat Medicare patients | 37,482 (press coverage) |

The gap is mostly definitions. OEWS surveys employers, so partners who own their radiology group (a common setup) count as self-employed and are left out. AAMC uses the AMA Masterfile's self-reported primary specialty. CMS counts anyone whose billing specialty is radiology, including part-timers and teleradiologists. Neiman counts Medicare enrollment, not billing. **Pick one series and keep it for the whole trend line. Never compare levels across sources.**

## 2. The BLS series cuts against the hypothesis, but it is too noisy to carry it

OEWS radiologist employment: 29,530 (2021), 29,250 (2022), 31,960 (2023), 26,770 (2025). From 2021 to 2025 that's down 9%. From 2023 to 2025 it's down 16%. The relative standard errors are 9.2%, 6.3%, 5.2% and 7.3%, so a 95% interval on the 2025 figure runs about ±14%. These swings are inside the noise. They also measure jobs, not people. Over the same years the mean wage rose from $301,720 to $381,530 (+26%), which fits a shortage better than a glut. The May 2025 median ($420,860) sits *above* the mean ($381,530), which is unusual and worth checking against the BLS page.

## 3. Two primary sources blocked automated access

- **bls.gov** returned HTTP 403 "Access Denied" to every page fetch, including the OEWS occupation pages and the Employment Projections tables. We stopped there and did not work around it. Only the **BLS public API** answered, and it only holds the latest OEWS year (May 2025). The 2021–2023 OEWS figures and the 2024–34 projection (+2.7%, ~800 openings a year) come from search-result summaries and are marked `search_snippet_unverified`. Look them up by hand before publishing.
- **aamc.org** puts its PDF downloads (`/media/<id>/download`) and data pages behind a JavaScript "Client Challenge" bot check, and its current specialty data lives in a Power BI dashboard. We stopped there too. The only AAMC numbers we have, 27,719 (2017) and 27,197 (2021), come from secondary summaries.

## 4. The radiologist SOC code is new, so the BLS series starts in 2021

Before the 2018 SOC revision, radiologists had no code of their own. They sat inside "Physicians and surgeons, all other" (29-1069). OEWS rolled the new codes in over the May 2019 and May 2020 panels, and the first year we found with a standalone 29-1224 page is May 2021. So BLS can't show 2010 vs. today for radiologists. It starts five years after Hinton's 2016 comment.

## 5. In the AAMC data, the headcount looks flat, not growing

Secondary reporting of AAMC's data shows "radiology and diagnostic radiology" active physicians at 27,719 in 2017 and 27,197 in 2021, which is −1.9%. Press summaries of AAMC data also say the 2007–2021 count fell about 1% while population per radiologist rose about 10%. If that holds up against the primary, "radiologists grew" is wrong for headcount. The defensible line is closer to "radiologists didn't shrink, demand per radiologist went up, and the training pipeline expanded." The CMS billing count tells a different story (+12% for Diagnostic Radiology from 2013 to 2024, +16% with IR), but the total number of NPIs billing Medicare grew 36% over the same years, mostly from new nurse practitioners and PAs. Radiologists' share of Medicare billers therefore fell.

## 6. Interventional radiology split off from diagnostic radiology in 2016

ACGME and NRMP created Interventional Radiology (Integrated) as its own specialty in 2016. Its positions and residents came partly out of DR:

- ACGME DR residents *fell* from 4,769 (2016–17) to 4,551 (2019–20), while IR-integrated residents went from 13 to 424. Combined, DR + IR rose from 4,782 to 4,975, and then to 5,581 by 2024–25.
- NRMP DR positions rose from 1,168 in 2016 to 1,268 in 2026 (+8.6%). DR + IR rose from 1,183 to 1,513 (+27.9%).

**Always sum DR and IR after 2016.** Otherwise the trend shows a fake dip right when the AI story starts.

## 7. NRMP's tables change shape across editions

- Each Results and Data book holds only five years, so the 2007–2026 series is stitched from four editions (2011, 2016, 2021, 2026).
- DR is split into PGY-1 categorical, PGY-2 advanced and, from 2013, "Physician (R)" PGY-2 seats reserved for applicants with prior training. The 2011 edition has no R section, so 2007–2011 totals may fold R seats into PGY-2 or leave them out.
- The column "U.S. Seniors" (2011, 2016 editions) became "MD Seniors" (2021) and then "U.S. MD Seniors" (2026). DO seniors joined the single Match after the 2020 accreditation merger. The "% filled by U.S. MD seniors" drop since 2009 (86.6% → 65.1% in 2026) partly reflects DOs taking seats, not just lost interest. The all-applicant fill rate in 2026 is 97.6%.
- PDF text came out with private-use glyphs (U+F087, U+F088) at the start of some rows, and with section headers out of reading order. The first parse silently dropped every 2012–16 and 2022–26 PGY-2 row. The totals for 2014 looked like 168 positions instead of 1,176. Caught by checking against NRMP's own Table 11A total (1,268 DR, 245 IR for 2026).
- The 2023 DR PGY-1 row carries an asterisk (143*, 100.0%*) that has no matching footnote on the page.

## 8. The "AI scared students away" dip came before the famous AI quote

DR's share filled by U.S. seniors bottomed in **2015** (55.9%, and all-applicant fill 86.9%, the lowest in the series). Hinton's "stop training radiologists" remark came in **late 2016**. By then the fill rate was already recovering: 2016 was 64.6% U.S. seniors and 95.4% overall, and 2017–2019 were near 100% overall. The literature we found ties the 2010–2015 slide to the post-2008 job market and reimbursement cuts (Sharafinski et al., Academic Radiology; Morey et al., JACR). The AI-deterrence surveys (Gong et al. 2019; Reader & Lee 2022, about one-sixth of would-be radiology applicants) measure attitudes, not Match outcomes. **The data can't credit the dip to AI fears.** It also can't show AI fear lastingly hurt the Match.

## 9. FDA's "radiology" label is the review panel, not the use

The FDA AI-enabled device list (1,614 devices, latest decision 2026-06-29) tags each device with the lead review panel. 1,230 (76%) are "Radiology". Some imaging AI sits under Cardiovascular or Neurology, so 76% is a floor for imaging AI. The 2026 count is a half year. The cumulative total at the end of 2016 was only 60 devices (26 radiology), so most of the AI "deployment" happened 2018–2025.

## 10. Medicare billing data is fee-for-service only

CMS Part B PUF counts cover traditional Medicare only. Medicare Advantage grew to roughly half of beneficiaries over 2013–2024 (widely reported; not sourced in this pass), so FFS **volume** trends understate total imaging. That's one reason we used the PUF for clinician counts, not exam volume. A per-beneficiary imaging series (for example the Neiman Institute's work, or the Smith-Bindman 2019 JAMA study) is still needed for the demand side.

## 11. The most famous quote in the story is usually misdated

Hinton's "people should stop training radiologists now" is widely dated to **November 2016**. He said it on **October 27, 2016**, at Creative Destruction Lab's "Machine Learning and the Market for Intelligence" conference in Toronto (CDL's own blog post of 2016-11-03 gives the date). The video, "Geoff Hinton: On Radiology", went up on YouTube on **2016-11-24**, four weeks later, and that upload date is the likely source of the November dating. It matters here because the hedge in the same breath ("It might be 10 years") puts the ten-year mark on **2026-10-27**, not in November. The research agents couldn't watch the video; the wording was finally checked against the transcript David captured in david-brain.

## 12. "Record residency slots" is true of almost every specialty

The headline everyone repeats (radiology residency positions at a record) holds for nearly all of medicine, because the whole Match grew 44% from 2016 to 2026 (30,750 → 44,344 positions). Indexed, diagnostic radiology's +8.6% ranks 19th of 21 large specialties. But much of the Match's growth is osteopathic programs joining the NRMP between 2015 and 2020. In 2021–2026, after the merger, radiology (diagnostic + interventional) grew 16.1% and the Match 16.4%. Choosing the window and whether to count interventional radiology moves the answer from "lagging badly" to "exactly on pace". Parsing it also meant stripping invisible arrow glyphs that NRMP prints before rows with large changes, and reconciling renamed specialties ("Orthopaedic"/"Orthopedic", "Psychiatry"/"Psychiatry (Categorical)").

## 13. "All Medicare billers" made radiology look like it was shrinking

The first pass compared radiologists billing Medicare (+13%, 2016–2024) with all Medicare billers (+36% over 2013–2024) and concluded radiology's share fell. But "all billers" is driven by non-physicians: nurse practitioners went from 98,293 to 203,212 billing NPIs (2016–2024, +107%) and physician assistants from 65,860 to 112,514 (+71%). Counting the full CMS files (about 1M to 1.2M individual NPIs a year) and keeping physician provider types only (39 non-physician types dropped), physicians grew 7.2% (602,317 → 645,633) and radiology (diagnostic + interventional) 12.8% (31,389 → 35,403). Radiology's share of Medicare-billing physicians *rose*, from 5.21% to 5.48%. (Oral and maxillofacial surgeons count as physicians only if they list an MD or DO, since the specialty is a dental one: 404 of 946 in 2016, 287 of 601 in 2024. David's call; it doesn't move the 7.2%.) Caveats: fee-for-service only (patients moving to Medicare Advantage push low-volume physicians under CMS's 11-beneficiary cutoff, which hits specialties with few Medicare patients, like OB/GYN and psychiatry, harder than radiology, where nearly everyone bills Medicare); and CMS split new specialties out over time (Hospitalist, 17,479 NPIs by 2021, mostly from Internal Medicine), which moves people between specialties but not in or out of the physician total.

## 14. Doximity's specialty pay tables don't add up to its own "overall growth" numbers

Doximity never prints an all-physician dollar average, only a yearly "overall growth" percentage. Chaining those percentages from the 2017 report to the 2026 report gives about **+19%** (+4%, then "less than one percent" down, then +1.5%, +3.8%, −2.4%, +5.9%, +3.7%, +2.0%). But the simple average of the 48 specialties listed in both the 2017 and 2026 tables rose from **$313,542 to $422,625, or +34.8%**. The biggest jump is between the 2019 and 2020 reports: the report says pay grew 1.5%, while neurosurgery's listed average went from $617K to $746,544 (+21%), thoracic surgery from $584K to $668,350 (+14%) and radiology from $429K to $485,460 (+13%). The report labels also skip a year. There's no "2022" report (the 2023 report covers 2022 pay), and the 2020 report pools 2019–2020 surveys, so no edition covers 2019 alone. **Comparing radiology's dollar figure against Doximity's headline growth rate would overstate radiology's lead.** Compare within each edition instead: radiology against the other specialties in the same table.

Reading the tables was a challenge too. The 2018 and 2019 specialty charts are images or vector art with no extractable text, so we read the numbers off rendered pages. In the 2023 PDF, text extraction puts "Radiology" next to **$468,509**, but the true value is **$496,667**. The labels and values come out in separate runs that drift apart, and the correct pairing only checks out against other rows printed elsewhere in the report (Plastic Surgery $571,373, Pulmonology $400,650).

Medscape's numbers get restated after publication. Its 2017 report gave the all-physician average as **$301,000**, and the 2018 report restated the same year as **$294,000**. Its 2025 report gave 2024 as **$376,000** (per Fierce Healthcare), and the 2026 report restated it as **$374,000**. Medscape's own pages return HTTP 402 (paywall), so most Medscape values here come from trade-press reprints.

## 15. Controlling for age shrinks every specialty, and Medicare's own patients keep leaving the data

The 65+ population grew 24.3% from 2016 to 2024 (49.2M → 61.2M, Census), much faster than any doctor count. Per 100,000 people aged 65+, radiologists (diagnostic + interventional) fell 9.3% (63.8 → 57.9) and physicians 13.8% (1,224 → 1,055). So the age control doesn't change radiology's lead over medicine, but it shows neither is keeping up with an aging country. The demand side is harder: traditional Medicare enrollment *fell* 12.2% (38.6M → 33.9M) as patients moved to Medicare Advantage, whose claims aren't in the CMS files. Per traditional enrollee, diagnostic radiology services rose 37.6% (4.67 → 6.43) vs 26.5% for all physician services. But the patients who stay in traditional Medicare may be older or sicker than those who leave, so per-enrollee intensity is overstated for everyone; compare radiology with all physicians, not with its own past.

## 16. "1,230 radiology AI tools" mostly don't read scans

The FDA's AI list has no description of what each device does, only a product code. Grouping the 1,230 radiology-panel devices by their 40 product codes, using FDA's own code names and definitions (foiclass.txt): 471 (38%) are image-processing and measurement software, 415 (34%) are AI inside the scanner itself (CT, MRI, ultrasound reconstruction and acquisition), 130 (11%) help detect or characterize disease, 126 (10%) triage the reading queue, and 87 (7%) plan radiation or ablation therapy. Every detection and triage code's legal definition says the device is "intended to aid" or "assist" a clinician; no radiology product code in FDA's classification file mentions autonomous use. Two codes (QIH, LLZ; 466 devices) are broad, so a name check flagged 13 that might detect findings; most of those turned out to be measurement or planning tools. Caveats: a device count is not usage, and a product code is the legal claim, not what the software could do.

## 17. One "radiologist" billed 1.9 million Medicare services in a year

While picking spot-checks, the highest-volume individual diagnostic radiologist in the 2024 CMS file showed 1,857,302 Medicare services. No person reads that many. Rows like this, almost certainly practices or labs billing under one physician's NPI, grew from 33 radiologists over 100,000 services (2.3% of all diagnostic radiology services) in 2016 to 124 (9.1%) in 2024. They inflated our "services per radiologist +10% vs +3.6% per physician" comparison, which used means. With the top 1% removed it's +3.1% vs −8.9%; at the median, −23% vs −31%. Radiology still beats physicians on every version, but the 10% figure was an outlier effect. Lesson: per-person averages from billing data need a median or trimmed check before they go on screen. The headline (a count of radiologists) isn't affected.

## 18. The Census changed its mind about 2020

The card 9 chart needed the 65+ population for every year, which spans two Census estimate series: 2010–2020 and 2020–2024 (rebased on the 2020 census). For 2020 they disagree, so the line uses the newer one, and the step from 2019 to 2020 looks flatter (+0.9 points) than its neighbors (about +3 points a year). Part of that is real (2020's pandemic deaths fell hardest on older Americans), part is the switch between series. The 2016 and 2024 endpoints, and the +24% headline, don't depend on that choice.

## 19. "How many radiologists bill Medicare?" has two right answers

The ACR's own workforce projection (Christensen et al., JACR, PMID 39952776) counts 37,482 radiologists enrolled to treat Medicare patients in 2023, from CMS's National Downloadable File. Our count is 35,403 for 2024, from CMS's billing file. The two measure different things: theirs counts everyone *enrolled* with Medicare; ours counts clinicians who actually *billed* traditional Medicare for at least 11 patients that year (CMS drops smaller billers for privacy). Both come from CMS and both rise, and our growth rates compare like with like (billers vs billers), so the headline doesn't change. But anyone checking "35,403 radiologists" against the ACR figure will find a 2,000-person gap, so the post should say which count it is.
