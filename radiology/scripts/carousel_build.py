"""Rebuild the whole carousel after a caption edit: one command.

    python scripts/carousel_build.py              # the drawn chest
    python scripts/carousel_build.py --real-scan  # the real chest scan, as a separate version

1. Copies the captions from carousel/slides.md to video/src/data/carousel.json, word for word.
2. Renders the 11 slides at 2x, 2160x2880, to video/out/carousel/2x/ (sharp text in the LinkedIn PDF).
3. Downscales them to exactly 1080x1440 (3:4) for Instagram: to carousel/instagram/ (tracked).
4. Prints carousel/radiology-carousel.pdf from the 2x slides through a headless browser, not Pillow,
   because LinkedIn's converter rejects stitched image PDFs
   (docs/solutions/best-practices/carousel-pdf-browser-printed-at-2x.md).
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

import pypdf
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
VIDEO = ROOT / "video"
REAL = "--real-scan" in sys.argv
SUFFIX = "-real-scan" if REAL else ""
OUT2X = VIDEO / "out" / "carousel" / f"2x{SUFFIX}"
TRACKED = ROOT / "carousel" / f"instagram{SUFFIX}"
PDF = ROOT / "carousel" / f"radiology-carousel{SUFFIX}.pdf"
N = 11
BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]
OUT2X.mkdir(parents=True, exist_ok=True)
TRACKED.mkdir(parents=True, exist_ok=True)

# Captions: the last cell of each slide row; " // " separates paragraphs; *(...)* notes are dropped.
captions = {}
table = (ROOT / "carousel" / "slides.md").read_text(encoding="utf-8").split("## Post text")[0]
for line in table.splitlines():
    m = re.match(r"\| ([\d.]+) \|", line)
    if m:
        cell = re.sub(r"\*\([^)]*\)\*", "", line.rstrip().rstrip("|").rsplit("|", 1)[1]).strip()
        if "TBD: David" in cell:
            raise SystemExit(f"Slide {m.group(1)} still has [TBD: David]")
        captions[m.group(1)] = [p.strip() for p in cell.split(" // ") if p.strip()]
(VIDEO / "src" / "data" / "carousel.json").write_text(json.dumps(captions, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

props = ""
if REAL:
    props_file = VIDEO / "out" / "carousel" / "real-scan-props.json"
    props_file.write_text(json.dumps({"scan": "real"}), encoding="utf-8")
    props = f"--props={props_file}"

files = []
for i in range(1, N + 1):
    big_path = OUT2X / f"{i:02d}.png"
    # shell=True so Windows finds npx.cmd
    subprocess.run(f"npx remotion still carousel-{i:02d} out/carousel/2x{SUFFIX}/{i:02d}.png --scale=2 --log=error {props}", cwd=VIDEO, shell=True, check=True)
    big = Image.open(big_path)
    assert big.size == (2160, 2880), big.size
    big.resize((1080, 1440), Image.LANCZOS).save(TRACKED / f"{i:02d}.png")
    # JPEGs for the PDF: the film grain makes 2x PNGs too heavy for a LinkedIn document.
    jpg_path = OUT2X / f"{i:02d}.jpg"
    big.convert("RGB").save(jpg_path, quality=90)
    files.append(jpg_path)
    print(f"slide {i}: done")

pages = "\n".join(f'<div class="p"><img src="{f.as_uri()}"></div>' for f in files)
html = OUT2X / "carousel.html"
html.write_text(
    "<!doctype html><html><head><meta charset='utf-8'><style>"
    "@page{size:1080px 1440px;margin:0}html,body{margin:0}"
    ".p{width:1080px;height:1440px;page-break-after:always;overflow:hidden}"
    ".p img{width:1080px;height:1440px;display:block}"
    f"</style></head><body>{pages}</body></html>",
    encoding="utf-8",
)
browser = next((b for b in BROWSERS if Path(b).exists()), None)
if not browser:
    raise SystemExit("No Edge or Chrome found")
PDF.unlink(missing_ok=True)
subprocess.run([browser, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}", html.as_uri()], check=True, capture_output=True)
# Edge can return before the file is written, so wait until its size stops changing.
last = -1
for _ in range(60):
    time.sleep(1)
    size = PDF.stat().st_size if PDF.exists() else 0
    if size and size == last:
        break
    last = size

r = pypdf.PdfReader(PDF)
sizes = {(round(float(p.mediabox.width)), round(float(p.mediabox.height))) for p in r.pages}
if len(r.pages) != N or len(sizes) != 1:
    raise SystemExit(f"Bad PDF: {len(r.pages)} pages, sizes {sizes}")
w, h = sizes.pop()
if abs(h / w - 4 / 3) > 0.01:
    raise SystemExit(f"Pages are {w}x{h}, not 3:4")
print(f"{PDF}: {len(r.pages)} pages, {w}x{h} pt, {PDF.stat().st_size / 1e6:.1f} MB, producer={r.metadata.get('/Producer')}")
