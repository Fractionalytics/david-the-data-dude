# Degree-of-difficulty rubric

Score every analysis in this repo out of 10 and record it in the project's README under **Degree of difficulty**. There are five dimensions, each scored 0, 1 or 2. Score the work as it actually happened, not as you expected it to go.

| Dimension | 0 (easy) | 1 | 2 (hard) |
|---|---|---|---|
| **1. Acquisition:** where the data lives | Download, API or a ready-made table | Scrape structured web pages; polite rate limits | PDFs, scans, images, video; paywalls, logins, records requests, manual data entry |
| **2. Coverage:** is any one source complete? | One source has everything | Sources must be stitched; small gaps filled by targeted research | Big gaps that need primary research or estimation; the answer depends on what's missing |
| **3. Entity resolution:** knowing two records are the same thing | Shared IDs, or nothing to join | Fuzzy name/location matching; a handful of manual fixes | Ambiguous identities at scale; many-to-many; manual review dominates |
| **4. Judgment:** how subjective the measure is | Objective fields (counts, dates, prices) | Classification with clear, defensible definitions | Constructs we had to define ourselves; definitions and policy choices change the answer |
| **5. Verification:** can we check the result? | Ground truth exists | Spot-checkable by hand; no full answer key | No ground truth; claims rest on the method |

**Reading the total:** 0–3 is easy, 4–6 is moderate, 7–8 is hard, and 9–10 is a slog.

In each README, list the five scores with a one-line reason for each, then the total. Note where the difficulty is concentrated: "easy to get, hard to label" is a different story from "hard to get, easy to label".
