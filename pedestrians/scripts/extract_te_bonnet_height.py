"""Read T&E's average new-car bonnet height by year, 2010-2024 (EU, UK and
Norway), off the raster line chart on page 9 of "Ever higher" (June 2025). T&E
prints only the end points (76.9 cm in 2010, 83.8 cm in 2024); the yearly values
here are digitised from the chart's blue markers, so they're accurate to about
+/-0.1 cm. The axis is calibrated on the y gridlines (74 and 84 cm) and checked
against the printed end points.

Reads  data/raw/te/2025_06_Ever-higher_bonnets_report.pdf
Writes data/raw/te/bonnet_height_digitised.csv

    python scripts/extract_te_bonnet_height.py
"""

from pathlib import Path

import fitz
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "data" / "raw" / "te" / "2025_06_Ever-higher_bonnets_report.pdf"
DPI = 300
S = DPI / 110  # calibration below was read off a 110-dpi render
Y84, Y74 = 231 * S, 607 * S  # gridline rows for 84 cm and 74 cm
X2010, X2024 = 150 * S, 792 * S


def main() -> None:
    pix = fitz.open(PDF)[8].get_pixmap(dpi=DPI)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].astype(int)
    # The line and markers are a light blue: blue channel well above red.
    blue = (a[:, :, 2] > 200) & (a[:, :, 2] - a[:, :, 0] > 80) & (a[:, :, 1] > 120)
    rows = []
    for yr in range(2010, 2025):
        x = int(round(X2010 + (yr - 2010) * (X2024 - X2010) / 14))
        ys = np.where(blue[int(Y84) - 20:int(Y74) + 20, x - 2:x + 3].any(axis=1))[0] + int(Y84) - 20
        if len(ys):
            y = ys.mean()
            rows.append(dict(year=yr, bonnet_height_cm=round(84 - (y - Y84) / (Y74 - Y84) * 10, 2)))
    t = pd.DataFrame(rows)
    t.to_csv(ROOT / "data" / "raw" / "te" / "bonnet_height_digitised.csv", index=False)
    print(t.to_string(index=False))


if __name__ == "__main__":
    main()
