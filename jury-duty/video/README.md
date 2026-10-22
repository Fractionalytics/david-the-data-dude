# jury-duty video charts (Remotion)

Animated charts for the Instagram video. Each chart is a Remotion **composition**: a React component plus a size, frame rate and length. Rendering one turns it into an MP4. Read `docs/video-playbook.md` section 6 first.

## First time

Copy this template to `projects/<slug>/video/`, then replace `jury-duty` in `package.json` and this README.

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

## Shared kit

`@kit/...` imports from `shared/video-kit/src` (wired up in `remotion.config.ts` and `tsconfig.json`):
- `@kit/zones` holds `VIDEO`, `ZONES`, `HEAD` and `ZoneGuide`. Lay every chart out inside `ZONES.chart`.
- `@kit/sharpie` holds the Sharpie look (`Page`, `Ink`, `ink`, `Scrawl`, `Axes`, `INK`, ...), if the brief picks that style. Put project-specific colors and categories in this project's own `src/sharpie.tsx` (see `projects/triple-d/video/src/sharpie.tsx`).

Keep every `remotion` / `@remotion/*` package on the same exact version as the kit.

## Compositions (1080×1920, 30 fps)

| id | Storyboard card | What | Length |
|---|---|---|---|
| `card-01` | 1 | Whole funnel at true scale, 1,000 → 14 (gold), then the on-screen "1-in-70 serve on 4+ day trial" | 0:05:09 |
| `card-05` | 5 | 1,000 → 449 eligible + 551 postponed, no reply or excused | 0:11:25 |
| `card-06` | 6 | 449 → 247 reported + 202 called off; the 202 flow over to join the 551 as 753 who never come | 0:15:08 |
| `card-08` | 8 | Zoom into 247 → 155 sent to a courtroom + 92 sent home | 0:11:04 |
| `card-09` | 9 | Zoom into 155 → 48 sworn + 107 not chosen; below it, "48 of 247 reported" from 0:51:03, then "48 of 1,000 summoned" from 0:55:03 | 0:16:10 |
| `card-11` | 11 | Zoom into 48; the 8 / 19 / 7 / 14 (gold) day buckets roll out one at a time at 1:08:02, 1:12:12, 1:14:21, 1:17:04 | 0:20:13 |
| `card-12` | 12 | The three comparison lines from the On-Screen Text column, at 1:22:08, 1:25:11, 1:27:03 | 0:12:08 |
| `card-15` | 15 | Card 1's end state, held | 0:08:00 |
| `preview` | all | Every card in order over a still of David's frame (`public/mock-bg.png`, gitignored); review only | 1:40:17 |

Lengths run from each card's Start in the Sheet's Script v2 tab to the next card's Start (m:ss:ff at 30 fps).

**Look** (chosen 2026-10-22): fully transparent over David's black shirt; teal `#2EC4B6` for people still in the funnel, warm gray `#B9B4AA` for people who drop out, gold `#F4C542` only for the takeaway (the 14); Barlow Condensed for numbers, Inter for labels; layout in `ZONES_HEAD_TOP.chart` from the shared kit. No source fine print in the Reel; the credit goes in the caption and the public README.

**Render:** `node render-cards.mjs` writes transparent ProRes 4444 clips to `out/cards/<id>.mov` for CapCut and `out/preview.mp4`. `node render-checks.mjs [frame ...]` writes review frames from the preview to `out/check/`.
