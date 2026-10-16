# amara video charts (Remotion)

Animated charts for the Instagram video. Each chart is a Remotion **composition**: a React component plus a size, frame rate and length. Rendering one turns it into an MP4. Read `docs/video-playbook.md` section 6 first.

## First time

Copy this template to `projects/<slug>/video/`, then replace `amara` in `package.json` and this README.

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

| id | Storyboard card | What | Length (frames) |
|---|---|---|---|
| `c07-waterfall-ceiling` | 7 | Dashed ceiling, then the 1.8M bar (lands on "1.8M", est.) | 706 |
| `c08-waterfall-pretrend` | 8 | −670K pre-2022 decline drops out | 245 |
| `c09-waterfall-loans` | 9 | −260K loan processing drops out | 271 |
| `c10-waterfall-remaining` | 10 | 870K remaining, labelled | 218 |
| `c11-top-declines` | 11 | Four biggest declines among very-high-exposure jobs, May 2022 → May 2025, customer service first | 534 |
| `c13-forces-title` | 13 | "FOUR FORCES" | 71 |
| `c14-forces-list` | 14 | Each force fully on screen at David's timecode (1:41:25, 1:47:13, 1:53:18, 1:58:17) | 862 |
| `c15-forces-table` | 15 | List shrinks into the FORCE / FAST / SLOW table; FAST and SLOW appear as named (est.) | 284 |
| `c16a-office-vs-rest` | 16, first beat | Office & admin vs. other jobs, May 2019 = 100 | 195 |
| `c16b-forces-fast` | 16, second beat | FAST meters fill (all weak) | 89 |
| `c17a-radiology-grid` | 17, first beat | Radiology's 100-square grid drains to 36% reading scans | 175 |
| `c17b-paralegals` | 17, second beat | Paralegals +13.8% vs other jobs +6.6% | 135 |
| `c17c-forces-slow` | 17, third beat | SLOW meters fill (all strong) | 123 |
| `c19-call-centers-square` | 19 | White 1080×1080 overlay: slopegraph 440K → 303K, −31% | 334 |

Each composition runs from its card's Start timecode to the next card's, so the clips drop straight onto David's timeline. Cue estimates within cards are listed in `src/cues.ts`. Data: every number comes from `src/data/charts.json`, written by `scripts/video_data.py` (run from `projects/amara/`). Mid-animation checks: `node render-checks.mjs`.
