# ideabrowser video charts (Remotion)

Animated charts for the Instagram video. Each chart is a Remotion **composition**: a React component plus a size, frame rate and length. Rendering one turns it into an MP4. Read `docs/video-playbook.md` section 6 first.

## First time

Copy this template to `projects/<slug>/video/`, then replace `ideabrowser` in `package.json` and this README.

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

Refresh the numbers first with `python ../scripts/make_chart_data.py`, which writes `src/data/ideabrowser.json` (featured ideas only, Jev definitions v3).

| id | Storyboard card | What | Length |
|---|---|---|---|
| `services-by-era` | 2 and 7 | Share of featured ideas classified as services per era (2% → 3% → 41%); bars rise in turn, the newsletter era last and slowest | 4.9 s |
| `daily-strip` | 4 | One square per day, services in red: the 74 days before July 28 (2) fill first, a pause, then July 28 to the cut-off (30). Shows "Data through Oct 9, 2026" | 8.1 s |
| `conveyor` | 3 | Envelopes ride a belt through a Claude Code box (email becomes a card) and a Jev box (card gets a colored tag), then drop into Services / Software / Marketplace / Other bins. The 25 items are real newsletter-era ideas (Jul 28 on) sampled in proportion to that era's mix (10 services, 9 software, 4 marketplace, 2 other), so the bins fill in true proportions. A clock sweeps the 50 minutes from raw emails to all ideas classified. Plays 34:20–39:09 (SS:FF) in the edit. Logos (supplied by David) are in `public/logos/` and set in `LOGOS` in `src/charts/Conveyor.tsx` | 4.6 s |
| `seesaw` | 6 | Services vs Software as stacks of blocks on a seesaw, one block per featured idea; the tilt follows the gap between the stacks. August builds to 15 vs 8 (services sinks), then 7 blocks move and September settles at 8 vs 15 (software sinks) | 6.1 s |

Chart titles are editorial and stay off the charts until they come from the Sheet's On-Screen Text column. The visual style is the shared Sharpie look as a placeholder; the brief's style is still `[TBD: David]`.
