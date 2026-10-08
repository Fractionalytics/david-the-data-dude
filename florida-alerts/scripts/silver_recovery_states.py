"""Where state Silver Alert subjects were recovered, 2011-2020 (chart 5 candidate).

Input:  data/interim/silver_monthly_cases.csv (parse_silver_monthly.py)
Output: data/processed/silver_recovery_states.csv  recovered_state, people, share of all alerts

Rows with no recovery location (blank cell) or a "still active / remains missing / unknown" note are counted
separately so the denominator stays all 2,219 alerts.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1] / "data"
c = pd.read_csv(ROOT / "interim" / "silver_monthly_cases.csv")
state = c.recovered_state.fillna("blank recovery cell")
out = state.value_counts().rename_axis("recovered_state").reset_index(name="people")
out["share"] = (out.people / len(c)).round(4)
out.to_csv(ROOT / "processed" / "silver_recovery_states.csv", index=False)

outside = out[~out.recovered_state.isin(["FL", "not found", "blank recovery cell"])]
print(out.to_string(index=False))
print(f"\nRecovered outside Florida: {outside.people.sum()} of {len(c)} ({outside.people.sum() / len(c):.1%}), "
      f"in {len(outside)} states")
