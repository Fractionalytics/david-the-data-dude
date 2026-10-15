"""Draw each top-four team's logo as SVG and render transparent PNGs for the video.

Team names are David's (2026-10-11). Designs are original, built on generic baseball tropes:
- The Places: forest green and gold; a baseball rising like the sun over mountains and a river valley.
- The Nicknames: red, navy and cream; for Pete Crow-Armstrong, a crow perched on a flexed arm with
  "Nicknames" tattooed on the biceps in tailed script.
- The Sons of Somebody: navy and white; an old-timer in a top hat with a handlebar mustache.
- The Jobs: black and gold; hammer and wrench crossed like bats behind a baseball.

Fonts come from Google Fonts (all SIL Open Font License): Graduate, Yellowtail, Alfa Slab One, Rye.

Usage: python projects/world-series/design/make_logos.py [--chrome PATH]
Writes design/svg/<team>_logo.html and design/png/<team>_logo.png (1080x1080, transparent),
plus design/png/lineup.png (1920x1080 overview).
"""
import argparse
import math
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SVG_DIR, PNG_DIR = HERE / "svg", HERE / "png"
CHROME_REL = ("projects/triple-d/video/node_modules/.remotion/chrome-headless-shell/win64/"
              "chrome-headless-shell-win64/chrome-headless-shell.exe")
# Remotion's bundled Chrome lives in the main checkout (worktrees have no node_modules).
DEFAULT_CHROME = next((p / CHROME_REL for p in HERE.parents if (p / CHROME_REL).exists()), None)
FONTS = ("https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Graduate"
         "&family=Rye&family=Yellowtail&display=block")

TEAMS = {
    "places": dict(name="The Places", main="#1F4D3A", accent="#D9A520", light="#F3EBD8"),
    "nicknames": dict(name="The Nicknames", main="#B3272D", accent="#1B2A4A", light="#F4ECDC"),
    "sons": dict(name="The Sons of Somebody", main="#13294B", accent="#B3272D", light="#FFFFFF"),
    "jobs": dict(name="The Jobs", main="#151515", accent="#F2B705", light="#F2B705"),
}


# ---------- shared pieces ----------

def baseball(cx, cy, r, stitch="#C8102E"):
    """A ball with two seams of red stitching."""
    s = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#FBFAF5" stroke="#222" stroke-width="{r*0.06:.1f}"/>']
    for side in (-1, 1):
        x0 = cx + side * r * 0.62
        s.append(f'<path d="M{x0},{cy - r*0.78} Q{cx + side*r*0.28},{cy} {x0},{cy + r*0.78}" '
                 f'fill="none" stroke="{stitch}" stroke-width="{r*0.05:.1f}"/>')
        for i in range(-3, 4):
            y = cy + i * r * 0.2
            xm = cx + side * (r * 0.62 - (1 - (i / 4) ** 2) * r * 0.27)
            s.append(f'<line x1="{xm - r*0.07}" y1="{y - r*0.05}" x2="{xm + r*0.07}" y2="{y + r*0.05}" '
                     f'stroke="{stitch}" stroke-width="{r*0.04:.1f}" transform="rotate({side*35} {xm} {y})"/>')
    return "".join(s)


def ring_text(cx, cy, r, text, font, size, fill, pid, bottom=False):
    """Text around a circle: along the top arc, or along the bottom arc reading left to right."""
    sweep = 0 if bottom else 1
    d = f"M{cx - r},{cy} A{r},{r} 0 0 {sweep} {cx + r},{cy}"
    return (f'<path id="{pid}" d="{d}" fill="none"/>'
            f'<text font-family="{font}" font-size="{size}" fill="{fill}" letter-spacing="4">'
            f'<textPath href="#{pid}" startOffset="50%" text-anchor="middle">{text}</textPath></text>')


def star(cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx + rr*math.cos(a):.1f},{cy - rr*math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'


# ---------- The Places ----------

def places(t):
    g, gold, cream = t["main"], t["accent"], t["light"]
    return (f'<circle cx="300" cy="300" r="280" fill="{g}" stroke="{gold}" stroke-width="10"/>'
            f'<circle cx="300" cy="300" r="200" fill="{cream}" stroke="{gold}" stroke-width="6"/>'
            '<defs><clipPath id="in"><circle cx="300" cy="300" r="197"/></clipPath></defs>'
            '<g clip-path="url(#in)">'
            + baseball(262, 262, 50)
            + f'<polygon points="90,420 190,250 250,330 330,200 420,320 470,270 520,420" fill="{g}"/>'
            f'<polygon points="190,250 212,288 168,288" fill="{cream}"/><polygon points="330,200 356,244 304,244" fill="{cream}"/>'
            f'<path d="M100,470 Q250,380 300,420 Q360,470 520,400 L520,520 L100,520 Z" fill="#6FA8C7"/>'
            f'<path d="M100,500 Q260,420 300,450 Q360,490 520,440 L520,520 L100,520 Z" fill="{g}"/>'
            '</g>'
            + ring_text(300, 300, 222, "THE PLACES", "Graduate", 48, gold, "pt")
            + star(85, 300, 18, gold) + star(515, 300, 18, gold)
            + ring_text(300, 300, 252, "★ ★ ★", "Graduate", 34, gold, "pb", bottom=True))


# ---------- The Nicknames ----------

ARM = ("M-140,480 C40,430 188,312 262,300 C336,288 396,328 420,384 L428,212 L508,212 L514,408 "
       "C522,470 500,512 452,524 C360,548 190,548 -140,546 Z")


def flexed_arm(skin, ink):
    """A flexed arm entering from the left: biceps up top, forearm raised, fist at the top right."""
    return (f'<path d="{ARM}" fill="{skin}" stroke="{ink}" stroke-width="7" stroke-linejoin="round"/>'
            f'<path d="M418,384 C430,420 440,452 466,470" fill="none" stroke="{ink}" stroke-width="5" '
            f'stroke-linecap="round" opacity=".6"/>'                       # elbow crease
            f'<path d="M330,318 C352,330 368,348 376,366" fill="none" stroke="#fff" stroke-width="8" '
            f'stroke-linecap="round" opacity=".45"/>'                     # biceps highlight
            f'<path d="M402,226 L402,146 Q402,114 428,112 Q441,98 456,110 Q471,98 486,110 Q501,98 514,112 '
            f'Q528,118 528,146 L528,196 Q528,226 494,226 Z" fill="{skin}" stroke="{ink}" stroke-width="7" '
            f'stroke-linejoin="round"/>'
            + "".join(f'<path d="M{x},116 L{x},146" stroke="{ink}" stroke-width="5" stroke-linecap="round" opacity=".6"/>'
                      for x in (442, 471, 500))                           # fingers
            + f'<path d="M404,178 C430,166 462,170 478,190" fill="none" stroke="{ink}" stroke-width="6" '
              f'stroke-linecap="round"/>')                                 # thumb


def crow_perched(ink, beak="#D9A520"):
    """A crow facing left, feet at (0, 0)."""
    return (f'<g transform="scale(-1,1) translate(-320,-376)"><g fill="{ink}">'
            '<path d="M250,350 Q228,262 300,230 Q368,206 392,250 Q404,292 360,330 Q320,362 250,350 Z"/>'
            '<path d="M262,346 L170,372 L196,346 L150,348 L246,322 Z"/>'
            '<circle cx="388" cy="236" r="40"/>'
            f'<path d="M420,226 L470,238 L420,250 Z" fill="{beak}"/>'
            '<path d="M300,300 Q330,270 372,276 Q340,300 300,312 Z" fill="#000" opacity=".35"/>'
            f'<rect x="300" y="344" width="8" height="32" fill="{beak}"/><rect x="330" y="340" width="8" height="36" fill="{beak}"/>'
            '</g><circle cx="398" cy="228" r="8" fill="#fff"/><circle cx="400" cy="228" r="4" fill="#000"/></g>')


def nicknames(t):
    red, navy, cream = t["main"], t["accent"], t["light"]
    script = (f'<text x="258" y="448" text-anchor="middle" font-family="Yellowtail" font-size="74" fill="{red}" '
              f'stroke="{navy}" stroke-width="4" paint-order="stroke" transform="rotate(-8 258 448)">Nicknames</text>')
    tail = "".join(f'<path d="M170,468 Q265,508 360,448" fill="none" stroke="{c}" stroke-width="{w}" '
                   f'stroke-linecap="round"/>' for c, w in ((navy, 16), (red, 8)))
    # Pete Crow-Armstrong: a crow perched on a flexed arm, "Nicknames" tattooed on the biceps.
    art = flexed_arm("#E2AE84", navy) + f'<g transform="translate(262,304)">{crow_perched(navy)}</g>' + script + tail
    return (f'<circle cx="300" cy="300" r="282" fill="{cream}" stroke="{navy}" stroke-width="12"/>'
            f'<circle cx="300" cy="300" r="262" fill="none" stroke="{red}" stroke-width="5"/>'
            '<defs><clipPath id="nk"><circle cx="300" cy="300" r="258"/></clipPath></defs>'
            f'<g clip-path="url(#nk)"><g transform="translate(300,300) scale(0.84) translate(-322,-322)">{art}</g></g>')


# ---------- The Sons of Somebody ----------

def top_hat_mustache(ink, band):
    return (f'<rect x="215" y="120" width="170" height="170" rx="10" fill="{ink}"/>'
            f'<rect x="215" y="240" width="170" height="26" fill="{band}"/>'
            f'<ellipse cx="300" cy="292" rx="140" ry="22" fill="{ink}"/>'
            f'<circle cx="300" cy="372" r="74" fill="#F1D3B3" stroke="{ink}" stroke-width="6"/>'
            f'<circle cx="274" cy="356" r="7" fill="{ink}"/><circle cx="326" cy="356" r="7" fill="{ink}"/>'
            f'<path d="M300,392 C270,372 236,380 216,404 C208,414 196,408 196,396 C186,428 236,436 300,404 '
            f'C364,436 414,428 404,396 C404,408 392,414 384,404 C364,380 330,372 300,392 Z" fill="{ink}"/>')


def sons(t):
    navy, red, white = t["main"], t["accent"], t["light"]
    return (f'<circle cx="300" cy="300" r="282" fill="{white}" stroke="{navy}" stroke-width="12"/>'
            f'<circle cx="300" cy="300" r="214" fill="none" stroke="{navy}" stroke-width="5"/>'
            + top_hat_mustache(navy, red)
            + ring_text(300, 300, 226, "SONS OF", "Rye", 44, navy, "st")
            + ring_text(300, 300, 258, "SOMEBODY", "Rye", 44, navy, "sb", bottom=True)
            + star(62, 300, 16, red) + star(538, 300, 16, red))


# ---------- The Jobs ----------

def hammer_wrench(ink):
    hammer = (f'<g transform="rotate(-40 300 300)"><rect x="285" y="120" width="30" height="330" rx="8" fill="#C89B5A" '
              f'stroke="{ink}" stroke-width="4"/><path d="M220,100 L380,100 L380,150 L240,150 L220,130 Z" fill="#9AA0A6" '
              f'stroke="{ink}" stroke-width="4"/></g>')
    wrench = (f'<g transform="rotate(40 300 300)"><rect x="286" y="150" width="28" height="300" rx="10" fill="#9AA0A6" '
              f'stroke="{ink}" stroke-width="4"/><path d="M262,92 A50,50 0 1 0 338,92 L338,138 L318,154 L282,154 L262,138 Z" '
              f'fill="#9AA0A6" stroke="{ink}" stroke-width="4"/></g>')
    return hammer + wrench


def jobs(t):
    black, gold = t["main"], t["accent"]
    slab = "".join(f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Alfa Slab One" font-size="64" '
                   f'fill="{c}">THE JOBS</text>' for x, y, c in ((303, 495, "#8a6a00"), (300, 492, black)))
    return (f'<path d="M300,30 L560,170 L520,470 L300,575 L80,470 L40,170 Z" fill="{black}" stroke="{gold}" stroke-width="12"/>'
            + hammer_wrench(black) + baseball(300, 300, 78)
            + f'<path d="M70,410 L530,410 L500,470 L530,530 L70,530 L100,470 Z" fill="{gold}" stroke="{black}" stroke-width="6"/>'
            + slab)


DRAW = {"places": places, "nicknames": nicknames, "sons": sons, "jobs": jobs}


def page(svg_body, bg="transparent"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONTS}">'
            f'<style>html,body{{margin:0;background:{bg};}}svg{{display:block}}</style></head>'
            f'<body>{svg_body}</body></html>')


def render(chrome, html_path, png_path, w, h):
    subprocess.run([str(chrome), "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--default-background-color=00000000", "--virtual-time-budget=8000",
                    f"--window-size={w},{h}", f"--screenshot={png_path}", html_path.as_uri()],
                   check=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chrome", default=str(DEFAULT_CHROME))
    args = ap.parse_args()
    SVG_DIR.mkdir(exist_ok=True)
    PNG_DIR.mkdir(exist_ok=True)

    logos = {}
    for key, t in TEAMS.items():
        inner = DRAW[key](t)
        logos[key] = inner
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="1080" height="1080">{inner}</svg>'
        html = SVG_DIR / f"{key}_logo.html"
        html.write_text(page(svg), encoding="utf-8")
        render(args.chrome, html, PNG_DIR / f"{key}_logo.png", 1080, 1080)

    # Overview: the four logos in a row, team name under each.
    cells = []
    for c, (key, t) in enumerate(TEAMS.items()):
        inner = logos[key]
        for i in ("in", "pt", "pb", "st", "sb", "nk"):  # ids must be unique on one page
            inner = (inner.replace(f'id="{i}"', f'id="{key}{i}"').replace(f'#{i}"', f'#{key}{i}"')
                     .replace(f"url(#{i})", f"url(#{key}{i})"))
        x = 60 + c * 460
        cells.append(f'<svg x="{x}" y="250" width="420" height="420" viewBox="0 0 600 600">{inner}</svg>'
                     f'<text x="{x + 210}" y="740" text-anchor="middle" font-family="Graduate" font-size="34" '
                     f'fill="#F3EBD8">{t["name"]}</text>')
    sheet = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080">{"".join(cells)}</svg>'
    html = SVG_DIR / "lineup.html"
    html.write_text(page(sheet, bg="#20262b"), encoding="utf-8")
    render(args.chrome, html, PNG_DIR / "lineup.png", 1920, 1080)
    print(f"wrote {len(logos)} logos + lineup.png to {PNG_DIR}")


if __name__ == "__main__":
    main()
