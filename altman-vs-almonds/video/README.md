# altman-vs-almonds video charts (Remotion)

Animated charts for the Instagram video. Each chart is a Remotion **composition**: a React component plus a size, frame rate and length. Rendering one turns it into an MP4. Read `docs/video-playbook.md` section 6 first.

## First time

Copy this template to `projects/<slug>/video/`, then replace `altman-vs-almonds` in `package.json` and this README.

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
| `card-06` | 6 | Full-screen special case: 12.29 L ÷ 0.322 mL (from 0.000085 gal, ~1/15 tsp) above the caption band, the line and 38,190 below it, y 240–1690. Opaque off-white. Animation ends at frame 30, then holds | 87 frames (02:27) |
| `card-08` | 8 | PNG only, 840 × 410, for the band above David's head (y 250–660): EcoLogits energy per 150-token reply for GPT-4o, GPT-5.5 and GPT-6 Astra against Altman's 0.34 Wh, on an 85% off-white panel. `npx remotion still card-08 out/cards-v2/card-08.png` | still |
| `card-15` | 15 + 16 | Scorecard frame (headers, row labels) and Altman's 38,190; done by frame 70, holds through card 16 | 417 frames (254 + 163) |
| `card-17` | 17 | Fills each row's adjustment from the On-Screen Chart tab, recounts the total to 5,823 and adds 6.6x; done by frame 232 | 271 frames |
| `card-18` | 18, 19, 20 | 38,000 / 5,800 = 6.6x: the denominator counts down while the ratio counts up; done by frame 105. Its last frame is the still for cards 19 (135 frames) and 20 (155 frames) | 274 frames |

Cards 15–18 use the traditional layout: off-white from the top to y 1150, transparent below for the caption and David's face; content measured inside x 121–958, y 269–1126.
