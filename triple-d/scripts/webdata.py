"""Load agent web-research results (data/interim/web/results/*.json), one record per restaurant id.

Later files override earlier ones (sorted: batch_ < retry_ < reverify_ < user_), but a
not-found retry never replaces an earlier found record. Records marked
"reverified": true always replace earlier ones, even if not found: they re-check
evidence that was gathered by fetching search-engine result pages.
"""

import json
from pathlib import Path

import pandas as pd

RESULTS = Path(__file__).resolve().parents[1] / "data" / "interim" / "web" / "results"


def load_web() -> pd.DataFrame:
    best: dict[str, dict] = {}
    for f in sorted(RESULTS.glob("*.json")):
        for rec in json.loads(f.read_text(encoding="utf-8")):
            prev = best.get(rec["id"])
            if prev is None or rec.get("reverified") or rec["found"] or not prev["found"]:
                best[rec["id"]] = rec
    cols = ["description", "format_tags", "found", "status"]
    return pd.DataFrame(best.values()).set_index("id") if best else pd.DataFrame(columns=cols)
