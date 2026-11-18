"""Animate the yearly stimulant maps into one GIF.

    python scripts/gif_stim_maps.py   (after scripts/chart_stim_map_years.py)
      reads  charts/stim_map_years/stim_map_<year>.png
      writes charts/stim_map_2009_2024.gif
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
files = sorted((ROOT / "charts" / "stim_map_years").glob("stim_map_*.png"))
imgs = [Image.open(f).convert("RGB") for f in files]
w, h = max(i.width for i in imgs), max(i.height for i in imgs)
scale = 1200 / w
frames = []
for im in imgs:  # pad to a common canvas (bbox_inches="tight" can differ by a few pixels), then shrink
    canvas = Image.new("RGB", (w, h), (252, 252, 251))
    canvas.paste(im, (0, 0))
    frames.append(canvas.resize((int(w * scale), int(h * scale)), Image.LANCZOS).quantize(colors=128))
durations = [900] * len(frames)
durations[0] = durations[-1] = 2500  # hold the first and last years
out = ROOT / "charts" / "stim_map_2009_2024.gif"
frames[0].save(out, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
print(out, len(frames), "frames", f"{out.stat().st_size / 1e6:.1f} MB")
