# sedans-to-suvs video charts (Remotion)

Animated charts for the Instagram video. Each chart is a Remotion **composition**: a React component plus a size, frame rate and length. Rendering one turns it into an MP4. Read `docs/video-playbook.md` section 6 first.

## First time

Copy this template to `projects/<slug>/video/`, then replace `sedans-to-suvs` in `package.json` and this README.

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
| `card-NN` (38 clips) | 1–6, 8, 15–26, 29–37, 40–43, 46, 48–51, 56 | Each card's slice of the whole-Reel timeline (`src/timeline.tsx`), timed from the Sheet's Start column (`src/cues.ts`) | to the next card's start |
| `still-NN` | same | The card over a still of its speaker, for review (`node render-checks.mjs 30:mid`) | same |
| `preview` | all graphic cards | Every card over its speaker still, back to back | sum of the cards |

Data: `python ../scripts/export_video_data.py` writes `src/data/data.json` from `data/final/` (and CDC's provisional meth file). Estimated in-card cues (no word timecodes) are marked `EST` in `src/cues.ts`.
