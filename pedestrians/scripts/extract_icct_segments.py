"""Read EU-27 new passenger car registrations by segment, 2001-2024, out of the
vector chart Fig. 3-3 in the ICCT European Vehicle Market Statistics Pocketbook
2025/26 (a stacked area chart, in millions). The pocketbook prints no table, so
this recovers the plotted values from the PDF's drawing paths: each segment is a
filled polygon from the baseline to its cumulative top, so SUV = top of the
SUV/off-road layer minus top of the layer below it (van).

Reads  data/raw/icct/pocketbook_2025_26.pdf (page 7)
Writes data/raw/icct/fig3-3_segments_extracted.csv

    python scripts/extract_icct_segments.py
"""

from pathlib import Path

import fitz
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "data" / "raw" / "icct" / "pocketbook_2025_26.pdf"
CHART = fitz.Rect(125, 95, 300, 250)
# Axis calibration from the chart itself: baseline (0) at y=247.1, frame top (14 million) at y=96.8;
# 2001 at x=127.5, 2024 at x=297.5 (polygon extents). Checked against the tick labels.
Y0, Y14, X01, X24 = 247.1, 96.8, 127.5, 297.5
LAYERS = {(0.0, 0.444, 0.51): "suv_offroad_top", (0.489, 0.647, 0.693): "van_top",
          (0.672, 0.66, 0.661): "grey_top"}


def tops(pts: list[fitz.Point]) -> dict[int, float]:
    """Highest point (smallest y) of a polygon at each year's x position."""
    out = {}
    for yr in range(2001, 2025):
        x = X01 + (yr - 2001) * (X24 - X01) / 23
        near = [p.y for p in pts if abs(p.x - x) < 0.6]
        if near:
            out[yr] = round((Y0 - min(near)) / (Y0 - Y14) * 14, 3)
    return out


def main() -> None:
    pg = fitz.open(PDF)[6]
    cols = {}
    for d in pg.get_drawings():
        fill = tuple(round(c, 3) for c in d["fill"]) if d.get("fill") else None
        if d["rect"].intersects(CHART) and fill in LAYERS:
            pts = [p for it in d["items"] for p in it[1:] if isinstance(p, fitz.Point)]
            cols[LAYERS[fill]] = tops(pts)
    t = pd.DataFrame(cols).rename_axis("year").reset_index()
    t["total_m"] = t.suv_offroad_top
    t["suv_m"] = (t.suv_offroad_top - t.van_top).round(3)
    t["suv_share"] = (t.suv_m / t.total_m).round(3)
    t.to_csv(ROOT / "data" / "raw" / "icct" / "fig3-3_segments_extracted.csv", index=False)
    print(t.to_string())


if __name__ == "__main__":
    main()
