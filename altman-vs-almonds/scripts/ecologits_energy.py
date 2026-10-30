"""Independent check on Altman's 0.34 Wh per query: EcoLogits' estimated energy per reply
for OpenAI models at several reply lengths. Training is outside EcoLogits' scope.

Needs `pip install ecologits==0.11.3`. Run from the repo root:
python projects/altman-vs-almonds/scripts/ecologits_energy.py
Writes data/ecologits_energy.csv.
"""
from pathlib import Path

import pandas as pd
from ecologits.tracers.utils import llm_impacts

OUT = Path(__file__).resolve().parents[1] / "data"

# gpt-4o was ChatGPT's default when Altman posted 0.34 Wh (June 2025); the rest are later models.
MODELS = ["gpt-4o", "gpt-5", "gpt-5.5", "chat-latest", "gpt-6-sol", "gpt-6-astra"]
TOKENS = [150, 300, 500, 1000]
LATENCY_S = 1000.0  # an upper bound, so EcoLogits uses its own modeled generation time


def bounds(v):
    v = v.value
    return (v.min, v.max) if hasattr(v, "min") else (v, v)


rows = []
for m in MODELS:
    for t in TOKENS:
        r = llm_impacts("openai", m, t, LATENCY_S)
        lo, hi = bounds(r.usage.energy)
        wlo, whi = bounds(r.usage.wcf)
        rows.append({"model": m, "output_tokens": t, "energy_Wh_min": lo * 1000, "energy_Wh_max": hi * 1000,
                     "x_altman_min": lo * 1000 / 0.34, "x_altman_max": hi * 1000 / 0.34,
                     "water_mL_min": wlo * 1000, "water_mL_max": whi * 1000})
df = pd.DataFrame(rows)
df.round(3).to_csv(OUT / "ecologits_energy.csv", index=False)
print(df.round(2).to_string(index=False))
