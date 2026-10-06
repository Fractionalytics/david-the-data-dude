// Chart: "Jev's call" morphing into "Jev's call, unpacked".
//   1. Horizontal bars Diner / Drive-In / Dive / Other grow in (scale 0-1,200).
//   2. Other cracks into its 12 buckets (largest first), with gaps opening between pieces.
//   3. Diner / Drive-In / Dive slide to their final rows (rows narrow from 4 to 15), then the
//      pieces peel up from the bottom one by one into their own rows.
//   4. Zoom: the x scale goes 0-1,200 -> 0-300 so every bar stretches and small buckets are legible;
//      bucket names and counts fade in.
// The final frame matches category-bars-detailed (untitled), so the two can be cut together.
// Bars are regenerated with rough.js every frame (fixed seeds) because their geometry changes.
import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import data from '../data/triple-d.json';
import {Axes, CATEGORY_INK, INK, Ink, Page, Scrawl, ink, plotFor, type Category, type Plot} from '../sharpie';

// Same box as the untitled category-bars-detailed chart.
const BASE = plotFor('legend', 470, 930);
const SHIFT = plotFor('legend').top - plotFor('title').top;
const PLOT: Plot = {...BASE, top: BASE.top - SHIFT, bottom: BASE.bottom - SHIFT};
const W = PLOT.right - PLOT.left;
const H = PLOT.bottom - PLOT.top;

// Timeline (frames at 30 fps).
const GROW0 = 10; // initial bars grow, 8 frames apart, 24 frames each
const SPLIT0 = 120; // Other cracks into pieces
const SPLIT1 = 150;
const MOVE0 = 150; // Diner / Drive-In / Dive slide to their final rows first...
const MOVE1 = 195;
const PIECES0 = 185; // ...then the pieces peel up from the bottom, one at a time
const STAGGER = 8;
const PIECE = 45;
const ZOOM0 = 320; // x scale 1,200 -> 300
const ZOOM1 = 362;
const LABELS0 = 348;
const LABELS1 = 378;
export const CATEGORY_MORPH_DURATION = 438; // ends with a 2 s hold

const DDD = ['Diner', 'Drive-In', 'Dive'] as const;
const FINAL: {category: string; count: number}[] = data.totals.detailed;
const BUCKETS = FINAL.filter((r) => !(DDD as readonly string[]).includes(r.category)); // largest first
const OTHER = (data.totals.strict as Record<string, number>).Other;
const SCALE0 = 1200;
const SCALE1 = Math.ceil(Math.max(...FINAL.map((r) => r.count)) / 50) * 50; // 300, as in the detailed chart
const GAP = 7; // px between Other's pieces once cracked

// Row geometry: 4 rows at the start, 15 at the end.
const BAND0 = H / 4;
const BAND1 = H / FINAL.length;
const rowY0 = (i: number) => PLOT.top + i * BAND0 + BAND0 / 2;
const rowY1 = (j: number) => PLOT.top + j * BAND1 + BAND1 / 2;
const BAR_H0 = BAND0 * 0.55;
const BAR_H1 = BAND1 * 0.66;

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const ease = Easing.inOut(Easing.cubic);
const colorOf = (c: string) => CATEGORY_INK[c as Category] ?? INK.gray;

export const CategoryMorph: React.FC = () => {
	const frame = useCurrentFrame();
	const scale = interpolate(frame, [ZOOM0, ZOOM1], [SCALE0, SCALE1], {...clamp, easing: ease});
	const px = (count: number) => (count / scale) * W;
	const split = interpolate(frame, [SPLIT0, SPLIT1], [0, 1], {...clamp, easing: ease});
	const dddMove = interpolate(frame, [MOVE0, MOVE1], [0, 1], {...clamp, easing: ease});
	const grow = (i: number) => interpolate(frame, [GROW0 + i * 8, GROW0 + i * 8 + 24], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	const labelsIn = interpolate(frame, [LABELS0, LABELS1], [0, 1], clamp);

	// Each bar has a white backing so a bar moving over another covers it cleanly.
	const rect = (x: number, y: number, w: number, h: number, c: string, seed: number) =>
		w < 2 ? null : (
			<>
				<rect x={x} y={y - h / 2} width={w} height={h} fill="white" />
				<Ink drawable={ink.rect(x, y - h / 2, w, h, {seed, stroke: colorOf(c), fill: colorOf(c), strokeWidth: 5, hachureGap: 7, fillWeight: 3})} />
			</>
		);

	// Diner / Drive-In / Dive: one bar each, sliding from its 4-row slot to its final row.
	const dddBars = DDD.map((c, i) => {
		const finalRow = FINAL.findIndex((r) => r.category === c);
		const count = FINAL[finalRow].count;
		const y = lerp(rowY0(i), rowY1(finalRow), dddMove);
		const h = lerp(BAR_H0, BAR_H1, dddMove);
		const w = px(count) * grow(i);
		const size = lerp(46, 32, dddMove);
		return (
			<g key={c}>
				{rect(PLOT.left, y, w, h, c, 500 + finalRow)}
				<Scrawl x={PLOT.left - 18} y={y} size={size} anchor="end" seed={`m${c}`}>
					{c}
				</Scrawl>
				<Scrawl x={PLOT.left + w + 16} y={y} size={lerp(46, 34, dddMove)} anchor="start" opacity={grow(i) >= 1 ? 1 : 0} seed={`mc${c}`}>
					{count}
				</Scrawl>
			</g>
		);
	});

	// Other: a single bar until it cracks, then 12 pieces that peel off to their rows.
	const otherGrow = grow(3);
	const other =
		frame < SPLIT0 ? (
			<g>
				{rect(PLOT.left, rowY0(3), px(OTHER) * otherGrow, BAR_H0, 'Other', 520)}
				<Scrawl x={PLOT.left + px(OTHER) * otherGrow + 16} y={rowY0(3)} size={46} anchor="start" opacity={otherGrow >= 1 ? 1 : 0} seed="mcOther">
					{OTHER.toLocaleString('en-US')}
				</Scrawl>
			</g>
		) : (
			(() => {
				let offset = 0;
				return BUCKETS.map((b, k) => {
					const finalRow = FINAL.findIndex((r) => r.category === b.category);
					const start = PIECES0 + k * STAGGER;
					const p = interpolate(frame, [start, start + PIECE], [0, 1], {...clamp, easing: ease});
					const x = PLOT.left + (px(offset) + k * GAP * split) * (1 - p);
					offset += b.count;
					const y = lerp(rowY0(3), rowY1(finalRow), p);
					const h = lerp(BAR_H0, BAR_H1, p);
					return <g key={b.category}>{rect(x, y, px(b.count), h, b.category, 500 + finalRow)}</g>;
				});
			})()
		);

	const otherLabel = interpolate(frame, [SPLIT0, SPLIT1], [1, 0], clamp);
	const tickVals = (frame < (ZOOM0 + ZOOM1) / 2 ? [0, SCALE0 / 2, SCALE0] : [0, SCALE1 / 2, SCALE1]).map((v) => v.toLocaleString('en-US'));
	const tickFade = interpolate(Math.abs(frame - (ZOOM0 + ZOOM1) / 2), [0, (ZOOM1 - ZOOM0) / 2], [0, 1], clamp);

	return (
		<Page>
			<Axes
				frame={frame}
				plot={PLOT}
				yTicks={[]}
				yTickMarks={false}
				yTitle="Kind of place"
				yTitleOnTop
				xTicks={[0, 0.5, 1].map((f) => ({at: PLOT.left + f * W, label: ''}))}
				xTitle="Restaurants"
			/>
			{[0, 0.5, 1].map((f, i) => (
				<Scrawl key={i} x={PLOT.left + f * W} y={PLOT.bottom + 62} opacity={frame < 12 ? 0 : tickFade} seed={`xt${i}`}>
					{tickVals[i]}
				</Scrawl>
			))}
			<Scrawl x={PLOT.left - 18} y={rowY0(3)} size={46} anchor="end" opacity={otherLabel} seed="mOther">
				Other
			</Scrawl>
			{dddBars}
			{other}
			{BUCKETS.map((b) => {
				const finalRow = FINAL.findIndex((r) => r.category === b.category);
				return (
					<g key={b.category} opacity={labelsIn}>
						<Scrawl x={PLOT.left - 18} y={rowY1(finalRow)} size={32} anchor="end" seed={`b${finalRow}`}>
							{b.category}
						</Scrawl>
						<Scrawl x={PLOT.left + px(b.count) + 16} y={rowY1(finalRow)} size={34} anchor="start" seed={`bc${finalRow}`}>
							{b.count}
						</Scrawl>
					</g>
				);
			})}
		</Page>
	);
};
