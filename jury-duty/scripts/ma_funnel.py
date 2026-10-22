"""Massachusetts juror funnel, FY2012-FY2015, from the Office of Jury Commissioner annual reports.

Numbers in data/ma_ojc_annual.csv were transcribed from the PDFs' text (source_url per row),
read in the built-in browser on 2026-10-19 because mass.gov refuses automated fetches.
Summons counts cover trial and grand jurors; days served cover trial jurors only.
"Jurors served" in a year includes people summoned in other years, so the per-summons
odds below treat each year as a steady state.

Run from the repo root: python projects/jury-duty/scripts/ma_funnel.py
"""
from pathlib import Path

import pandas as pd

df = pd.read_csv(Path(__file__).resolve().parents[1] / "data" / "ma_ojc_annual.csv")
df["multi_day"] = df.served_2_days + df.served_3_days + df.served_4plus_days
out = pd.DataFrame({
    "FY": df.fiscal_year,
    "summoned": df.summoned,
    "served": df.jurors_served,
    "served/summoned": df.jurors_served / df.summoned,
    ">1 day/served": df.multi_day / df.jurors_served,
    "4+ days/served": df.served_4plus_days / df.jurors_served,
    ">1 day/summoned": df.multi_day / df.summoned,
    "4+ days/summoned": df.served_4plus_days / df.summoned,
})
pd.set_option("display.width", 200)
print(out.to_string(index=False, formatters={c: "{:.1%}".format for c in out.columns if "/" in c}))
