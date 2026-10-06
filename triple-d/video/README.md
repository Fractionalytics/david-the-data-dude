# triple-d video charts (Remotion)

Animated, Sharpie-style charts for the Instagram video. Each chart is a Remotion **composition**: a React component plus a size, frame rate and length. Rendering one turns it into an MP4.

## First time

```bash
cd projects/triple-d/video
npm install
```

## Daily loop

1. **Refresh the data** after any analysis change: `python ../scripts/make_chart_data.py` writes `src/data/triple-d.json`.
2. **Preview** with `npm run studio`, which opens Remotion Studio at http://localhost:3000. Pick a composition on the left and scrub the timeline. Code edits hot-reload.
3. **Render**: `npm run render:all` writes every chart to `out/<id>.mp4`. `npm run stills` writes the **last frame** of every video to `out/stills/<id>.png`. To render one, run `npx remotion render hook-line out/hook-line.mp4`. To check a single frame, run `npx remotion still hook-line out/frame.png --frame=40`.

## Compositions (1080×1920, 30 fps)

| id | What | Length |
|---|---|---|
| `hook-line` | % of each season's restaurants Jev calls a Diner, Drive-In or Dive; the line draws from season 1 to 43 in 2 s | 3.3 s |
| `hook-line-steps` | Same chart, slowed: season 1 labeled, 2 s pause, line falls to season 2 (labeled), 2 s pause, to season 3 (labeled), 2 s pause, then seasons 3-43 draw in 2 s and season 43 is labeled | 12.5 s |
| `ddd-strike` | Title card, no chart: DINERS / DRIVE-INS / DIVES written out one per line, then each struck through in red. Timing follows editor timecodes (HH:MM:SS:FF at 30 fps) set in `src/charts/DddStrike.tsx` | 10.1 s |
| `d-words` | "D-WORDS" scoreboard: DAVID vs. TRIPLE-D columns fill with words at set timecodes, red scores tick up; TRIPLE-D's first three words (incl. the intentional "DIVE-INS") are erased and re-written. Timing in `src/charts/DWords.tsx` (SS:FF at 30 fps) | 10.8 s |
| `category-bars-jev` | Unique restaurants per category, Jev's strict call | 5 s |
| `category-bars-forced` | Same, "if Guy had to pick" | 5 s |
| `category-bars-detailed` | (No title) Jev's call, unpacked: Diner/Drive-In/Dive plus the 12 "Other" buckets, horizontal | 5.5 s |
| `category-morph` | Horizontal Jev's call (Diner, Drive-In, Dive, Other) morphs into the detailed chart: Other cracks into its 12 buckets, DDD bars slide to their rows, pieces peel up one by one, then the x-axis zooms 0-1,200 -> 0-300. Ends identical to `category-bars-detailed` | 14.6 s |
| `season-stack` | Restaurants per season, stacked by category (counts) | 5 s |
| `season-stack-100` | Same as 100% stacked | 5 s |
| `season-stack-100-detailed` | 100% stacked using `detailed_category`: Diner/Drive-In/Dive plus the 12 "Other" buckets, 15-color legend (shorter plot so it ends at the same height) | 5.5 s |
| `season-stack-100-simple` | Same, simplified to 7 categories: DDD + top 3 buckets (Global, Mexican/Latin, Pizza/Italian) + gray "Everything else" | 5.5 s |
| `era-stack-100-simple` | "Then vs. now": the 7 simplified categories for four season groups (S1-10, S11-20, S21-30, S31-43), with % labels | 5.5 s |
| `then-now-slope` | "Diners out, global in": slope chart, First 10 vs Last 10 seasons; Diner and Global cross, Drive-In & BBQ stay flat; "5.5x more Diners" / "3.2x more Global" | 4.5 s |
| `then-now-slope-combined` | First 10 vs Last 10: Diner (35% → 4%), Dive (19% → 6%), Drive-In (7% → 6%, thin: the flat one) against Global kitchens + Mexican & Latin summed into one "Global & Latin" line (13% → 32%); "2.6x more Diners" / "7.7x more Global & Latin" | 4.5 s |
| `then-now-seasons` | Same four lines through all 43 seasons | 4.5 s |
| `then-now-endpoints` | "Season 1 vs. season 43": Diners (22 → 1) vs. Global (1 → 8) and Mexican/Latin (0 → 6), BBQ flat (2 → 3); counts, not %; "22 to 1" / "8 to 1". Drive-In left out (season 1 was unusually drive-in heavy) | 4.5 s |

All charts use **US restaurants only** (states, DC, Puerto Rico: 1,560 of 1,634); `src/data/triple-d-all.json` has every country if you need it. Slope charts compare the **First 10** seasons (1-10) with the **Last 10** (34-43).

All charts are top-justified (`plotFor` in `src/sharpie.tsx`), and the bottom ~600px of the frame is left empty for a talking head.

## Where to change things

- **Look** (colors, marker thickness, wobble, font, plot area) lives in `src/sharpie.tsx`. `MARKER` holds the rough.js settings; `INK` holds the colors.
- **Timing** is set per chart with the frame constants at the top of each file in `src/charts/`. At 30 fps, 30 frames is 1 second.
- **Lengths and titles** are set in `src/Root.tsx`.

The hand-drawn strokes come from [rough.js](https://roughjs.com), and the draw-in animation from `@remotion/paths`' `evolvePath`. The font is Permanent Marker, from Google Fonts.

Remotion is free for individuals and companies with up to 3 employees; larger companies need a [company license](https://remotion.pro). Keep all `remotion` / `@remotion/*` packages on the **same exact version**, since a mismatch breaks rendering.
