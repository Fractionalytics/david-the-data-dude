// Cards 7-10: the job gap in the most AI-exposed occupations (BLS "very high"), May 2022 -> May 2025.
// One composition per card, each picking up where the last left off:
//   card 7  - a dashed ceiling, then the 1.8M bar
//   card 8  - the pre-2022 decline drops out (-670K)
//   card 9  - loan processing drops out (-260K)
//   card 10 - the 870K that's left grows and gets its label
// Numbers: data/charts.json (scripts/video_data.py), rounded to 10K as in the script. No title: the
// On-Screen Text column is empty. Bar labels are data labels. Timing: ../cues.ts.
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import data from '../data/charts.json';
import {CUE} from '../cues';
import {INK, Ink, Page, Scrawl, ZONES, ink, ramp} from '../sharpie';
import {HOT, OTHER, dashedLine, fmtJobs} from './parts';

const W = data.waterfall;
const MAX = 2_000_000;
const TOP = ZONES.chart.top + 120;
const BASE = ZONES.chart.bottom - 190;
const y = (v: number) => BASE - (v / MAX) * (BASE - TOP);
const LEFT = ZONES.chart.left + 30;
const RIGHT = ZONES.chart.right - 30;
const SLOT = (RIGHT - LEFT) / 4;
const BAR_W = 150;
const x = (i: number) => LEFT + SLOT * i + (SLOT - BAR_W) / 2;

const BARS = [
	{lo: 0, hi: W.raw, color: HOT, value: fmtJobs(W.raw, false, 10), label: ['Gap vs.', 'other jobs']},
	{lo: W.raw - W.pretrend, hi: W.raw, color: OTHER, value: fmtJobs(-W.pretrend, true, 10), label: ['Pre-2022', 'decline']},
	{lo: W.final, hi: W.raw - W.pretrend, color: OTHER, value: fmtJobs(-W.loans, true, 10), label: ['Loan', 'processing']},
	{lo: 0, hi: W.final, color: HOT, value: fmtJobs(W.final, false, 10), label: ['Remaining', '']},
];

// Card -> which bar it animates, and when.
export const STAGES = {
	7: {bar: 0, at: CUE.c07.bar, frames: CUE.c07.barFrames, dur: CUE.c07.dur},
	8: {bar: 1, at: CUE.c08.bar, frames: CUE.c08.barFrames, dur: CUE.c08.dur},
	9: {bar: 2, at: CUE.c09.bar, frames: CUE.c09.barFrames, dur: CUE.c09.dur},
	10: {bar: 3, at: CUE.c10.bar, frames: CUE.c10.barFrames, dur: CUE.c10.dur},
} as const;
export type WaterfallCard = keyof typeof STAGES;

export const Waterfall: React.FC<{card: WaterfallCard}> = ({card}) => {
	const frame = useCurrentFrame();
	const stage = STAGES[card];
	const ceiling = useMemo(() => dashedLine(LEFT - 10, y(W.raw), RIGHT + 10, y(W.raw), 26, 18, {seed: 300, stroke: INK.black, strokeWidth: 5}), []);
	const base = useMemo(() => ink.line(LEFT - 10, BASE, RIGHT + 10, BASE, {seed: 4, stroke: INK.black, strokeWidth: 6}), []);
	const rects = useMemo(
		() => BARS.map((b, i) => ink.rect(x(i), y(b.hi), BAR_W, y(b.lo) - y(b.hi), {seed: 10 + i, stroke: b.color, fill: b.color, strokeWidth: 5, hachureGap: 8})),
		[],
	);
	// Thin connectors carry each bar's top or bottom across to the next one.
	const links = useMemo(
		() => [W.raw, W.raw - W.pretrend, W.final].map((v, i) => ink.line(x(i) + BAR_W, y(v), x(i + 1), y(v), {seed: 30 + i, stroke: INK.gray, strokeWidth: 3})),
		[],
	);
	return (
		<Page>
			{ceiling.map((d, i) => (
				// Card 7 draws the ceiling dash by dash; later cards start with it in place.
				<g key={i} opacity={card === 7 ? ramp(frame, CUE.c07.ceiling + i * 0.8, 4) : 1}>
					<Ink drawable={d} />
				</g>
			))}
			<Ink drawable={base} />
			{BARS.slice(0, stage.bar + 1).map((b, i) => {
				const t = i < stage.bar ? 1 : ramp(frame, stage.at, stage.frames);
				const labelOn = i < stage.bar ? 1 : ramp(frame, stage.at + stage.frames - 4, 6);
				const h = y(b.lo) - y(b.hi);
				const clipId = `wf-${card}-${i}`;
				const removed = b.color === OTHER;
				return (
					<g key={i}>
						<clipPath id={clipId}>
							{/* Totals grow up from the baseline; removed chunks drop down from the bar above. */}
							{removed ? (
								<rect x={x(i) - 12} y={y(b.hi) - 12} width={BAR_W + 24} height={(h + 24) * t} />
							) : (
								<rect x={x(i) - 12} y={y(b.lo) + 12 - (h + 24) * t} width={BAR_W + 24} height={(h + 24) * t} />
							)}
						</clipPath>
						{t > 0 && (
							<g clipPath={`url(#${clipId})`}>
								<Ink drawable={rects[i]} />
							</g>
						)}
						{i > 0 && <Ink drawable={links[i - 1]} progress={t} />}
						<Scrawl x={x(i) + BAR_W / 2} y={removed ? y(b.lo) + 50 : y(b.hi) - 45} size={removed ? 44 : 58} color={b.color} opacity={labelOn} seed={`v${i}`}>
							{b.value}
						</Scrawl>
						{b.label.map((line, k) => (
							<Scrawl key={k} x={x(i) + BAR_W / 2} y={BASE + 50 + k * 46} size={36} color={removed ? INK.gray : INK.black} opacity={i < stage.bar ? 1 : ramp(frame, stage.at, 8)} seed={`l${i}${k}`}>
								{line}
							</Scrawl>
						))}
					</g>
				);
			})}
		</Page>
	);
};
