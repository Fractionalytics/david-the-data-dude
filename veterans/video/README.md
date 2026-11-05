# veterans video charts (Remotion)

Animated charts for the Instagram video. Each chart is a Remotion **composition**: a React component plus a size, frame rate and length. Rendering one turns it into an MP4. Read `docs/video-playbook.md` section 6 first.

## First time

Copy this template to `projects/<slug>/video/`, then replace `veterans` in `package.json` and this README.

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

## Compositions (1080x1920, 30 fps): animated, 2026-11-04

All cards sit on one olive scrim (82% opaque) at x 120-900, y 1010-1700: below David's lapel mic (y 932-982), left of the button rail, above the username. Measured from the rendered alpha channel. Look: Field Stencil (Saira Stencil numbers, Barlow Condensed labels).

| id | Card | What | Source |
|---|---|---|---|
| card-02 | 2 | One bar, veterans and troops uncomfortable, ~50% | USAA/YouGov 2023 |
| card-03 | 3 | Under 30 ~70%, 65+ 24% | USAA 2023 |
| card-04 | 4 | US adults 53% (22% definitely + 31% probably), new color | YouGov 10 Nov 2025 |
| card-05 | 5 | Mosaic: civilians 53/47 by veterans 50/50, overlap cell highlighted | both surveys, assumes random pairing |
| card-09, card-10 | 9-10 | 17.2M living veterans, 6% of US adults | VetPop FY2026; ACS 2024 |
| card-11 | 11 | Deployed 61%, married on active duty 47%, combat zone 36% | Pew 2019 |
| card-12 | 12 | Six most common rated conditions, PTSD highlighted | VA ABR FY2025 |
| card-15 | 15 | 17.2M | VetPop FY2026 |

`card-NN-over` puts a card over `public/mock-bg.png` (David's frame, gitignored) for review: `npx remotion still card-05-over out/stills/card-05.png --frame=0`.

**Transitions.** Cards 2-3-4-5 and 9-10-11-12 are two continuous scenes. Each card opens on the previous card's last frame and morphs from it: card 2's bar rises and grows into card 3's under-30 bar; card 3's bars drain into card 4's blue civilian bar; card 4's bar unfolds into card 5's mosaic columns; card 10's numbers lift away as card 11's bars arrive; card 11's bars clear as card 12's conditions grow. The scrim fades in only at cards 2, 9 and 15, and out only at the end of cards 5, 12 and 15. Checked on `out/preview.mp4` frames either side of every cut.

**Cue estimates.** David's Sheet gives card Starts only, so cues inside a card (card 3's 65+ bar, card 4's definitely/probably, card 5's split and highlight, card 9's 6%, card 11's three bars) are estimated from where the phrase falls in the script. They're constants at the top of each card in `src/Charts.tsx`.

**Render:** `node render-cards.mjs` writes transparent ProRes 4444 clips to `out/cards/card-NN.mov` and `out/preview.mp4` (every card at its real Start over David's frame).
