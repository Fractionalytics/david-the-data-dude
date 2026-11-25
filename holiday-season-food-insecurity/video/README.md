# thanksgiving-food-insecurity video charts (Remotion)

Animated charts for the Instagram video. Each chart is a Remotion **composition**: a React component plus a size, frame rate and length. Rendering one turns it into an MP4. Read `docs/video-playbook.md` section 6 first.

## First time

Copy this template to `projects/<slug>/video/`, then replace `thanksgiving-food-insecurity` in `package.json` and this README.

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

`card-NN` renders one transparent ProRes 4444 clip per storyboard card to `out/cards/card-NN.mov`, timed to the Sheet's Start column (`src/cards.tsx`, read 2026-11-24). `preview-NN` is the same card over this Reel's footage, for review stills (`node render-previews.mjs` → `out/previews/`).

Layout (measured 2026-11-24 on `public/speaker-a.png` and `speaker-b.png`): head tops at y 1045 (A) and 1073 (B). Captions go in y 985–1045 (David: 60px above the heads). The receipt panel fills x 160–920, y 260–980. Measured on the rendered alpha channel of card-11 and card-54: bounding box (160, 260, 920, 980).

| Cards | Chart (src/charts.tsx) |
|---|---|
| 1–3, 7–9, 29–30, 58–59 | `HookChart`: USDA rate 2001–2024, then empty 2025–26 slots and question marks |
| 5–6 | `Surveys`: the other government surveys, then each one's status |
| 11–15 | `DinnerChart`: AFBF dinner price each year, 2019–2026 |
| 16, 19–25, 31–32 | `Bills`: one line per bill, then low-end pay |
| 27 | `Definition` |
| 28 | `BigNumber`: 47.9M |
| 33 | `Employment` (David's lines) |
| 34 | `Acronym` |
| 36, 50, 51–52 | `Slope` |
| 38, 40 | `IneligibleBar` |
| 42 | `MealRatio` |
| 43 | `Tefap` |
| 44–45 | `Donations` |
| 46 | `Demand` |
| 47–48 | `PaidWith` |
| 49 | `UtilityDebt` |
| 54–57, 60–61 | `Factors`: red = bad news, green = good news, arrow = direction |

No clip for card 4 (David's screenshot), card 10 (his photos) or cards 62–67.
