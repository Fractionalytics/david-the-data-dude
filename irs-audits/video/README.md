# irs-audits video charts (Remotion)

Animated charts for the Instagram video. Each chart is a Remotion **composition**: a React component plus a size, frame rate and length. Rendering one turns it into an MP4. Read `docs/video-playbook.md` section 6 first.

## First time

Copy this template to `projects/<slug>/video/`, then replace `irs-audits` in `package.json` and this README.

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

| id | Storyboard card | What | Frames |
|---|---|---|---|
| `card-01` | 1 | 316 dots stream in from the left and settle in a circle on the shirt; one turns orange and pulses; pencil "Audit" label and arrow draw in | 70 |
| `card-02` | 2 | At 0:03:13 (David's cue), "1 in 316" in orange on a semi-opaque scrim over the dots | 153 |
| `card-03` | 3 | Card 2's end state | 112 |
| `card-04` | 4 | The number clears; the 316 dots shrink to their nearest of 642 slots and 326 more stream in; "1 in 642" on the scrim 50 frames in (David's cue) | 158 |
| `card-05` | 5 | Dots clear; $50K–$200K bar: 22% in person, 78% mail | 128 |
| `card-06` | 6 | Bar clears; y-axis (Odds of Audit); the $50K–$200K dot appears and the higher bands rise out of it one by one | 159 |
| `card-07` | 7 | x-axis (Share In Person) draws; dots slide to their in-person share | 120 |
| `card-08` | 8 | $10M+ flashes on and off with a ring, ending steady | 245 (5 frames longer than the Sheet) |
| `card-09` | 9 | <$50K plotted in orange (est. cue 0:41:15); dotted guides show its gap above $50K–$200K (est. 0:42:25) | 242 |
| `card-10` | 10 | Card 9's end state | 35 |
| `card-11` | 11 | Scatter fades (est. 0:49:12); "Earned / Income / Tax / Credit" word by word (est. 0:50:22) | 156 |
| `card-12`, `card-13` | 12–13 | Card 11's end state | 117, 145 |
| `card-14` | 14 | Words clear; people kept out of poverty, 2024: Social Security 28.7M, Earned Income and Child Tax Credits 6.8M, SNAP 3.6M (est. cue 1:05:00) | 222 |
| `card-15` | 15 | Zoom to the credits bar; "6.8 million" inside it (est. cue 1:13:22) | 260 |
| `card-16` | 16 | Odds of an audit for every band as horizontal bars, <$50K in orange; the "1 in N" labels start 45 frames in (David's cue) | 110 |
| `card-17`, `card-18` | 17–18 | Card 16's end state, through 1:24:14 | 73, 30 |
| `preview` | all | The whole timeline over a still of David's frame (`public/mock-bg.png`, gitignored); review only | 2,535 |

Every card is a window of one timeline (`src/Reel.tsx`), keyed to the Sheet's Start column (Original Script tab) at 30 fps, with cards 9 onward 5 frames later than the Sheet because David lengthened card 8 afterward, so each clip starts where the previous one ended. Cues marked "est." are estimated from where the words fall in the script; they're listed at the top of `src/Reel.tsx` (`CUE`) and can be nudged against the audio.

**Look:** fully transparent over David's black shirt (sampled `#191A1F` on the 2026-11-03 stills); white dots, orange `#F28C38` for the audited return, pencil `#E4E1DA` for the hand label in Caveat (a stand-in until David picks the pencil font; `fonts/Caveat-600.woff2`, SIL OFL). Teal `#2EC4B6` for the other bands and the credits, warm gray `#B9B4AA` for axes and comparison bars; Barlow Condensed 800, 52px or larger. Layout inside `ZONES_HEAD_TOP.chart`, below David's lav mic (~y 960).

**Check frames:** `node render-checks.mjs [frame ...]` writes preview frames to `out/check/`.
