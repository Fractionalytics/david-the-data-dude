# voting video charts (Remotion)

Animated charts for the Instagram video. Each chart is a Remotion **composition**: a React component plus a size, frame rate and length. Rendering one turns it into an MP4. Read `docs/video-playbook.md` section 6 first.

## First time

Copy this template to `projects/<slug>/video/`, then replace `SLUG` in `package.json` and this README.

```bash
cd projects/<slug>/video
npm install
```

## Daily loop

1. **Preview** with `npm run studio`. Run `npm run studio:zones` instead to see the layout zones over every chart.
2. **Check frames**: `npx remotion still <id> out/frame.png --frame=N`. Look at mid-animation frames too, not just the last one.
3. **Render**:
   - `npm run render:all` writes every chart to `out/<id>.mp4`.
   - `npm run stills` writes each chart's last frame to `out/stills/<id>.png`.
   - `npm run cards` renders **one clip per storyboard card** (compositions named `card-NN`) as transparent ProRes 4444 to `out/cards/<id>.mov`, for overlaying on footage in CapCut. `npm run cards -- card-06` re-renders just that card, so a revision never means re-rendering the whole video. A `preview` composition, if the project has one, renders to `out/preview.mp4`.

## Shared kit

`@kit/...` imports from `shared/video-kit/src` (wired up in `remotion.config.ts` and `tsconfig.json`):
- `@kit/zones` holds `VIDEO`, `ZONES`, `HEAD` and `ZoneGuide`. Lay every chart out inside `ZONES.chart`.
- `@kit/sharpie` holds the Sharpie look (`Page`, `Ink`, `ink`, `Scrawl`, `Axes`, `INK`, ...), if the brief picks that style. Put project-specific colors and categories in this project's own `src/sharpie.tsx` (see `projects/triple-d/video/src/sharpie.tsx`).

Keep every `remotion` / `@remotion/*` package on the same exact version as the kit.

## Compositions (1080×1920, 30 fps)

| id | Storyboard card | What | Length |
|---|---|---|---|
| `card-01` | 1 | Unlabeled hook: a year counter runs through the midterms 1974 → 2022 while orchid figures fill to that year's voters 65+ per voter 18–24 (1.8 … 5.6 in 2014, 3.8 in 2018, 5.0 in 2022); ends on card 2's start state | 0:06:04 |
| `card-02` | 2 | Card 1's end state; "18–24" with a pulse on the gold figure at 0:08:03, "65+" with the five orchid figures pulsing at 0:09:28 (David's cues) | 0:06:11 |
| `card-04` | 4 | Adults, millions, 1972–2024: the gold 18–24 line (25M → 30M), then the orchid 65+ line (20M → 60M), then a dashed 2011 marker | 0:11:06 |
| `card-06` | 6 | Vertical 0–100 axis, "% of citizens who say they voted, 2020 → 2022". The 65+ bar rises to 74.5, then drains to 66.8, leaving a faint ghost; "−8 pts" (no raw percentages) | 0:09:10 |
| `card-07` | 7 | Card 6's end state, then the 18–24 bar: 51.4 drains to 27.6; "−24 pts" | 0:05:19 |
| `card-08` | 8 | Card 7's bars fade; the period line becomes "Midterms, 2014 → 2018"; the axis rescales so its top is 2018's 32.4 (ticks 0/10/20/30); one 18–24 bar rises from 17.1 (white line marks it) to the top; "+89%" beside it | 0:09:18 |
| `card-09` | 9 | Slopegraph, voters 65+ per voter 18–24: 5.6 (2014) → 3.8 (2018, labeled below its dot) | 0:05:26 |
| `card-10` | 10 | Card 9's end state, then 2022: back up to 5.0 | 0:08:00 |
| `animation` | all | The eight visual cards back to back on black, without David: the public repo's `videos/voting-animation.mp4` (rendered copy kept in `../videos/`) | 1:02:04 |
| `preview` | all | The whole timeline (talking-head cards 3, 5 and 11 blank) over `public/mock-bg.png`, a synthetic stand-in for David's frame (gitignored); review only | 1:17:14 |

Lengths run from each card's Start in the Sheet's Script v2 tab to the next card's Start (m:ss:ff at 30 fps); card 11 ends at 1:17:14. Card 2's cues are David's; every other in-card cue is an estimate from where its phrase falls in the line, set as a constant above each card in `src/Cards.tsx` (`C4`, `C6` ... `C10`) so it can be nudged without touching the drawing. Every number drawn comes from `src/data.ts`, which cites `data/processed/`.

**Look** (retuned 2026-10-23 on David's real footage; details at the top of `src/look.tsx`): fully transparent over his shirt, which reads on camera as slate gray-blue (~`#5A6973`). Gold `#FFD23F` = ages 18–24 (the viewer), orchid `#E9A6FF` = ages 65+ (teal failed at 2.6:1 contrast); white for text and empty figures. A narrow chart area, x 260–820 and y 880–1640, keeps everything on the shirt. Crisp over video: no text outlines (they rendered as a soft halo), every label bold (Inter 800, Barlow Condensed 800), no line under 6px, small labels 52–60px. No source fine print in the Reel. `public/mock-bg.png` is a synthetic frame built to his measured shirt color and outline.

**Render:** `npm run cards` writes transparent ProRes 4444 clips to `out/cards/<id>.mov` for CapCut, plus `out/preview.mp4`.
