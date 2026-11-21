# Release 2026-11-21: Reel 4, the four waves of the opioid epidemic

Frozen when the Reel was posted ([Instagram](https://www.instagram.com/reel/DgBD8DnSr7N/), DDD17). Later iterations add new releases; this one never changes.

- `reel4_four_waves.csv`: US overdose deaths by year, 1999–2025, from CDC WONDER Multiple Cause of Death. Underlying cause is drug poisoning (X40–X44, X60–X64, X85, Y10–Y14). 1999–2017 come from the 1999–2020 database, 2018–2024 from the 2018–2024 Single Race database, and 2025 from the provisional database (deaths through Nov 7, 2026, exported Nov 19, 2026). Written by `scripts/reel4_four_waves.py`.
  - Raw query counts: `od_all`, `rx` (T40.2), `rx_and_fent` (T40.2 and T40.4), `heroin` (T40.1), `heroin_and_fent`, `fent` (T40.4), `fent_and_stim` (T40.4 and T40.5 or T43.6), `stim` (T40.5 or T43.6). Age-adjusted rates (`*_aadj`) exist for the unsubtracted queries only.
  - The waves, as defined by Friedman, Palamar, Ciccarone et al. (medRxiv 2026):
    - `wave1_rx_no_fent` = rx − rx_and_fent
    - `wave2_heroin_no_fent` = heroin − heroin_and_fent
    - `wave3_fent_no_stim` = fent − fent_and_stim
    - `wave4_fent_and_stim` = fent_and_stim
    - `stim_no_fent` = stim − fent_and_stim
  - `*_crude` columns are deaths per 100,000, computed from WONDER's population. 2025 uses the 2024 population.
- **Checks** (asserted in the script):
  - 2017: 70,237 overdose deaths, 28,466 fentanyl, 15,482 heroin, 14,495 Rx (NCHS Data Brief 329).
  - Fentanyl plus a stimulant: 235 in 2010 and 34,429 in 2021 (Friedman & Shover 2023).
  - 2023: 31,193 fentanyl without a stimulant and 41,583 with one (the 2026 preprint).
  - The provisional database's 2024 matches the final data exactly.
- **The Reel's "at least 700K":** the four waves sum to 704,808 for 2000–2025 at minimum. A death involving both pills and heroin counts in both waves 1 and 2, so the plain sum (805,857) is an upper bound.
