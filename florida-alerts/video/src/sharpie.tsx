// Florida Alerts' chart kit: the shared Sharpie look (shared/video-kit) plus this project's colors,
// David's timecodes, and the horizontal bar chart cards 6 and 7 share. Charts import from here.
import React, {useMemo} from 'react';
import {Easing, interpolate} from 'remotion';
import {INK, Ink, Scrawl, ink} from '@kit/sharpie';
import {ZONES} from '@kit/zones';

export * from '@kit/sharpie';
export {VIDEO, ZONES} from '@kit/zones';

// One meaning per color across every card: the public (citizens, highway signs, lottery) is green,
// police are blue, "found because of the alert" is red, everything else is gray.
export const COLOR = {
	public: INK.green,
	police: INK.blue,
	alert: INK.red,
	found: INK.black,
	other: INK.gray,
};

// David's timecodes are MM:SS:FF at 30 fps (docs/video-playbook.md section 6).
export const tc = (mm: number, ss: number, ff: number) => (mm * 60 + ss) * 30 + ff;

// Each card's window in the recording. A composition's frame 0 is its card's start.
export const CARD = {
	5: {start: tc(1, 7, 6), end: tc(1, 42, 23)},
	6: {start: tc(1, 42, 23), end: tc(1, 52, 19)},
	7: {start: tc(1, 52, 19), end: tc(2, 0, 20)},
	8: {start: tc(2, 0, 20), end: tc(2, 16, 21)},
	9: {start: tc(2, 16, 21), end: tc(2, 44, 2)},
} as const;
export type CardNo = keyof typeof CARD;
export const durationOf = (card: CardNo) => CARD[card].end - CARD[card].start;
// An absolute timecode as a frame within its card.
export const cue = (card: CardNo, mm: number, ss: number, ff: number) => tc(mm, ss, ff) - CARD[card].start;

export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Small handwritten note at the bottom of the chart zone saying what the data covers.
export const ScopeNote: React.FC<{children: React.ReactNode; opacity: number}> = ({children, opacity}) => (
	<Scrawl x={(ZONES.chart.left + ZONES.chart.right) / 2} y={ZONES.chart.bottom - 40} size={34} color={INK.gray} opacity={opacity} seed="scope">
		{children}
	</Scrawl>
);

// Horizontal bars, largest first, each scribbled in and grown left to right one after another.
// Labels sit above each bar so long names never squeeze the bars.
export type HBarRow = {label: string; value: number; color: string};
export const HBars: React.FC<{frame: number; rows: HBarRow[]; max: number; top: number; bottom: number}> = ({frame, rows, max, top, bottom}) => {
	const left = ZONES.chart.left + 10;
	const right = ZONES.chart.right - 110; // room for the value label
	const step = (bottom - top) / rows.length;
	const barH = Math.min(70, step * 0.42);
	const bars = useMemo(
		() =>
			rows.map((r, i) => {
				const y = top + i * step + step * 0.42;
				return ink.rect(left, y, Math.max(6, ((right - left) * r.value) / max), barH, {seed: 300 + i, stroke: r.color, fill: r.color});
			}),
		// eslint-disable-next-line react-hooks/exhaustive-deps
		[rows, max, top, bottom],
	);
	return (
		<g>
			{rows.map((r, i) => {
				const start = 6 + i * 10;
				const grow = interpolate(frame, [start, start + 24], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
				const shown = interpolate(frame, [start, start + 8], [0, 1], clamp);
				const value = interpolate(frame, [start + 18, start + 26], [0, 1], clamp);
				const y = top + i * step + step * 0.42;
				const w = Math.max(6, ((right - left) * r.value) / max);
				return (
					<g key={r.label}>
						<Scrawl x={left} y={y - 34} size={46} anchor="start" opacity={shown} seed={`hl${i}`}>
							{r.label}
						</Scrawl>
						<clipPath id={`hb-${i}`}>
							<rect x={left - 20} y={y - 20} width={(w + 40) * grow} height={barH + 40} />
						</clipPath>
						<g clipPath={`url(#hb-${i})`}>
							<Ink drawable={bars[i]} />
						</g>
						<Scrawl x={left + w + 24} y={y + barH / 2} size={50} anchor="start" opacity={value} seed={`hv${i}`}>
							{r.value}
						</Scrawl>
					</g>
				);
			})}
		</g>
	);
};
