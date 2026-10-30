# Data challenges

The inside look: data problems we hit along the way, with the numbers.

## 1. The only source for ChatGPT's water use is Sam Altman
The 0.32 mL per query (0.000085 gallons) appears in one place: a sentence in Altman's June 2025 blog post. It has no methodology, no definition of "average query", and no statement of which water it counts. PolitiFact asked OpenAI for data and got no answer. Everything on the AI side of the comparison rests on that one sentence.

## 2. "Water use" means three different things
An almond's 12.3 L "water footprint" includes rain (green water) and a theoretical amount for diluting fertilizer runoff (grey water). Only 6.35 L is irrigation (blue water). On the AI side, the narrowest measure is cooling water at the data center. Add the water evaporated at power plants to make the electricity and the figure is about 4.5 times larger (0.32 → 1.44 mL at Altman's own 0.34 Wh). Each side of the comparison uses a different definition.

## 3. How big is an almond?
Fulton et al. convert per-kilogram to per-almond at 1.2 g per kernel (an Almond Board summary said 23 per ounce, 1.23 g). USDA's 2025 field sample puts the average kernel at 1.60 g. That one choice moves the per-almond water from 12.3 L to 16.4 L, and Altman's ratio from 38,000 to 51,000. Secondhand sources had us at 12.6 L and 1.67 g until David downloaded the originals.

## 3b. Almost half of the almond's "water" is theoretical
The paper's 12.3 L per almond is 6.35 L of irrigation, 0.68 L of rain and 5.26 L (43%) of grey water: the volume of clean water that would be needed to dilute fertilizer runoff to the state nitrate standard. Nobody pumps that grey water. It's an impact measure that happens to be in liters.

## 4. The fact-checks left out the clause that matters
PolitiFact and CalMatters quoted the 38,000 line but not what Altman said next: "this is like the full-on, you know, total true water accounting, not just what's running in one data center." YouTube's transcript panel wouldn't load, so we got the wording by playing the clip with captions on and reading them as they appeared (the auto-captions spell ChatGPT "ChachiBT"). That clause changes the test: his 0.32 mL only works as onsite-only water, and he says it isn't.

## 4b. The "91%" that wasn't
Press coverage said training was 91% of Mistral's water. Mistral's own page gives no breakdown by stage. The 91% (from secondary coverage) is "training and inference" combined, over 18 months, with no query count, so it can't be turned into a per-query training share. We had repeated it before checking the primary page.

## 4c. Who owns the dam's evaporation?
Grid water factors swing almost 5× depending on one choice: whether evaporation from hydro reservoirs counts against the electricity. Li et al.'s US average (3.14 L/kWh) includes it. The same 2025 US mix without hydro is about 1.31 L/kWh, and Texas's gas-and-wind grid is about 0.9. That single choice moves "Altman is too high by" from about 9× to about 4× for inference alone.

## 4d. OpenAI doesn't say where it answers your question
OpenAI says it ran about 1.9 GW of compute in 2025, but not where. Known sites lean toward Texas, and the main ChatGPT fleet on Azure is undisclosed, so the grid is a range, not a measurement. Training compute is known only as dollar figures from leaked investor documents (via Epoch AI), so the training share assumes water scales with spending.

## 4d-2. Our own "gotcha" didn't survive the best case
We first concluded that Altman's 0.95 L of water per kWh, all-in, was below every grid's power-plant water, which would mean 0.32 mL couldn't be "total". Rechecked against Shaolei Ren's point that the data is too limited: on Texas's gas-and-wind grid, with closed-loop cooling and 0.34 Wh counted at the facility level, the all-in figure comes to 0.313 mL, matching Altman. So his number is reachable in the single most favorable case. It isn't reachable on the US average or with Microsoft's published cooling water (1.3–2× higher).

## 4e. What's an "average query"?
Altman's 0.34 Wh is for "the average query", with no reply length or model given. EcoLogits puts a 150-token reply on GPT-4o at 0.22–0.37 Wh, right on Altman's number. A 1,000-token reply on GPT-6 Astra is 11–27 Wh, up to 78 times more. Nobody outside OpenAI knows the average reply length or the mix of models, so the energy per query is a range, not a number.

## 4f. A fact-check that misquoted its own source
Tom's Hardware's "85 to 5,500 queries per almond" credits "Altman's own statements" for 1–50 mL per response. That range is actually from Li/Ren's 2023 GPT-3 paper. Its almond figure (1.1 gal) is the older estimate the California study replaced, and its low end converts 1 mL as 0.0002 gallons (really 0.76 mL). Its 5,500 happens to match our own result, and that's exactly why we can't use it as support.

## 5. Paywalls and dead links on the primary sources
The almond water study (sciencedirect.com, HTTP 403, then a bot-check page in the browser, which we didn't try to get past), the 2021 almond LCA (Springer, sign-in redirect), the MDPI AI water paper (403) and the 2025 NASS almond report (DNS failure, then 404) all failed to load. Their numbers come through PolitiFact, the Almond Board and trade press until we get the originals.

## 4g. The law changed between the analysis and the signature
California's new data-center water laws (AB 2619 and AB 2469, signed 2026-09-21) first looked like they made operators report power-plant water. The April committee analyses define "indirect water use," meaning water "withdrawn for the purpose of generating the electricity consumed by the data center," and require it at every license renewal. The chaptered text, on a site that blocked our fetcher (403) so we read it in a browser, cut it from both bills. AB 2619 now asks only for "total water use and direct water use," and the word "indirect" appears nowhere in AB 2469. Summaries written from the earlier versions describe a law that doesn't exist.

## 4h. The 2025 almond crop was a forecast, and it came in 10% light
The "850 billion almonds" came from USDA's July 2025 objective forecast: 3.00 billion meat pounds at 1.60 g per kernel. The Almond Board's June 2026 position report shows 2,692,744,085 lb of 2025/26 crop receipts with one month to go, about 2.69 billion lb and 0.7% below the year before. The final crop is about 10% under the forecast, so the 2025 crop was about 1.22 billion kg and 763 billion almonds, not 1.36 billion kg and 850 billion. The forecast was a real USDA number, but it wasn't the crop.
