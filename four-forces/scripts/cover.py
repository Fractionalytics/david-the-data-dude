"""SUPERSEDED (2026-10-16): covers are 1080x1920 from now on (docs/video-playbook.md section 6); David's
shipped thumbnail is projects/amara/cover.jpg. Kept for the record.

4:5 cover image (1080x1350) from the final four-forces frame, with empty room at the bottom for
David to add text in Instagram Edits.

    python scripts/cover.py   (run from projects/amara/, after rendering video/out/stills/c17c-forces-slow.png)

Unlike shared/video-kit/carousel_frame.py (which centers the chart), this pins the chart to the top
so the bottom ~460px stay white.
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "video/out/stills/c17c-forces-slow.png"
OUT = ROOT / "video/out/cover-4x5.png"
W, H = 1080, 1350
CROP_TOP, CROP_BOTTOM = 230, 1060  # the title through the last table row, plus a little air
TOP_MARGIN = 60

src = Image.open(SRC).convert("RGB")
assert src.size == (1080, 1920), src.size
chart = src.crop((0, CROP_TOP, W, CROP_BOTTOM))
cover = Image.new("RGB", (W, H), "white")
cover.paste(chart, (0, TOP_MARGIN))
cover.save(OUT)
print(f"{OUT}: {W}x{H}; free space at the bottom: {H - TOP_MARGIN - chart.height}px")
