# florida-alerts video charts (Remotion)

Animated charts for the Instagram video. Each chart is a Remotion **composition**: a React component plus a size, frame rate and length. Rendering one turns it into an MP4. Read `docs/video-playbook.md` section 6 first.

## First time

Already set up. In a new worktree, run `npm install` here first. The chart data comes from the pipeline: run `python ../scripts/export_video_data.py` to refresh `src/data/silver.json` after any change to the data.

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
| `card5-years-dots` | 5 (1:07:06–1:42:23) | State Silver Alerts per year, 2011–2021, drawing in from frame 0. Gives way to 100 dots, done by 1:20:02. 98 fill black ("found") by 1:30:14. 11 of them turn red ("found because of the alert") by 1:36:04 | 35.6 s |
| `card6-found-by` | 6 (1:42:23–1:52:19) | Who spotted them, in FDLE's 197 success stories: citizen 107, police 84, the person themself 3, unclear 2, family 1 | 9.9 s |
| `card7-channels` | 7 (1:52:19–2:00:20) | How they knew, public vs. police: "Public alerts" stacked from highway signs 49 + lottery 14 = 63, against the police BOLO's 54. Stories that don't name a channel (79, mostly citizen finds) aren't shown | 8.0 s |
| `card8-map` | 8 (2:00:20–2:16:21) | Where people were found, 2011–2020. Opens on Florida (2,035), pans to Georgia (82) by 2:07:16, zooms out fast so the whole country and Puyallup, WA land on 2:11:21. 22 states filled orange | 16.0 s |
| `card9-takeaways` | 9 (2:16:21–2:44:02) | David's five lines (four from the Video column, plus "Public > police" added 2026-10-08), written in one by one, one shared font size so none wraps. Line cues are estimates at the top of `src/charts/Takeaways.tsx` | 27.4 s |

Each composition is exactly as long as its card, so it drops onto the timeline at the card's start. All cue times live in `src/sharpie.tsx` (`CARD`) and at the top of each chart file, as David's MM:SS:FF timecodes at 30 fps.

Colors mean the same thing on every card: green = the public, blue = police, red = found because of the alert, orange (map) = a state where someone was found.

Check frames with `node render-checks.mjs [id ...]`, which writes the cue frames and mid-animation frames to `out/checks/`.
