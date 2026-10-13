# radiology video charts (Remotion)

Animated charts for the Instagram video. Each chart is a Remotion **composition**: a React component plus a size, frame rate and length. Rendering one turns it into an MP4. Read `docs/video-playbook.md` section 6 first.

## First time

Copy this template to `projects/<slug>/video/`, then replace `radiology` in `package.json` and this README.

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
**"Revised Script" tab (2026-10-13), lengths from David's edit:**

| `rev03-headline-square` | 3 | 1080×1080 corner inset: "Doctors billing Medicare 2016–2024" (descriptive title, David may replace), radiologists +12.8% (blue) vs all doctors +7.2% (gray), large labels for small display | 185 frames (00:06:05) |
| `rev06-07-capability` | 6–7 | "1. CAPABILITY" → moves up → 76% of 1,614 FDA AI tools grid → "5 years" crossed out → "15 years". Cue estimates in the file | 720 frames (00:24:00) |
| `rev08-amara` | 8 | "AMARA'S LAW" + concept sketch (no data): what we expect vs what happens, short run / long run | 257 frames (00:08:17) |
| `rev09-10-prescription` | 9–10 | "2. PRESCRIPTION" → moves up → fields "AI" and "labor economics", trail over the fence, "EPISTEMIC TRESPASSING". Cue estimates in the file | 680 frames (00:22:20) |
| `rev11-13-reasons` | 11–13 | "TWO REASONS" → moves up → "1." grid of a radiologist's time, all blue, draining to 36% reading scans (VALUE study, 2012) → "2." David's three card 13 lines. Cue estimates in the file | 1204 frames (00:40:04) |
| `rev14-pay-premium` | 14 | The `card9-pay-premium` chart, unchanged, held to David's length | 645 frames (00:21:15) |
| `rev16-takeaway-square` | 16 | 1080×1080, card 3's format: the card 14 "RADIOLOGY PREMIUM" chart itself (PayPremium, scaled into the square), 1.30× (2017) → 1.44× (2025) | 228 frames (00:07:18) |

**Earlier "Sheet1" card numbers (superseded where the revised script differs):**

| id | Storyboard card | What | Length |
|---|---|---|---|
| `card4-growth` | 4 | Radiologists vs all doctors: billing Medicare +12.8% vs +7.2% (2016–2024), then pay +49% vs +35% (Doximity 2017 vs 2026). Cue estimates in the file | 420 frames (14 s) |
| `card5-ai-arrived` | 5 | 1,614 FDA AI tools as 100 squares, 76 radiology; then Medicare services per doctor +10% vs +3.6% (means). Cue estimates in the file | 520 frames (17 s) |
| `card6-venn` | 6 | DRAFT final frame: AI / Radiologist Venn with David's labels. Animation after layout approval | 30 frames |
| `card8-facts` | 8 | David's three On-Screen Text lines, one per cue (estimates in the file) | 330 frames (11 s) |
| `card9-pay-premium` | 9 | "RADIOLOGY PREMIUM": radiologist pay as a multiple of the average doctor's, Doximity 1.30× (2017) → 1.44× (2025); 1.0× baseline | 150 frames (5 s) |
| `card11-takeaway` | 11 | Radiologists +12.8% vs all doctors +7.2% billing Medicare, 2016–2024 | 240 frames (8 s) |

All chart numbers come from `scripts/build_video_data.py` → `src/data/cards.json` and `card9.json`.
