// Pieces shared by Radiology's charts. Colors: radiologists blue, everyone else gray, the
// same on every card. Text is level (setScrawlTilt(0) in ../sharpie).
import React, {useMemo} from 'react';
import {INK, Ink, Scrawl, ZONES, ink, ramp} from '../sharpie';

export const RAD = INK.blue;
export const OTHER = INK.gray;
export const CX = (ZONES.chart.left + ZONES.chart.right) / 2;

export type Row = {name: string; value: number; color: string};

// A labelled pair of horizontal bars that grow from zero. Each row: name on the left, bar,
// value at the bar's end once it has fully grown (no in-between values on screen).
// `top` is the label's y; `max` is the value that fills BAR_W.
const NAME_W = 300;
const BAR_X = ZONES.chart.left + NAME_W;
const BAR_W = ZONES.chart.right - BAR_X - 150;
const ROW_H = 120;

export const BarPair: React.FC<{
	frame: number;
	start: number;
	top: number;
	label?: string;
	rows: Row[];
	max: number;
	fmt: (v: number) => string;
	seed: number;
	nameSize?: number;
}> = ({frame, start, top, label, rows, max, fmt, seed, nameSize = 40}) => {
	const bars = useMemo(
		() =>
			rows.map((r, i) =>
				ink.rect(BAR_X, top + 70 + i * ROW_H, Math.max(8, (r.value / max) * BAR_W), 70, {
					seed: seed + i,
					stroke: r.color,
					fill: r.color,
					strokeWidth: 5,
					hachureGap: 7,
				}),
			),
		[rows, max, top, seed],
	);
	const grow = ramp(frame, start + 8, 30);
	return (
		<g>
			{label && (
				<Scrawl x={ZONES.chart.left} y={top + 10} size={40} anchor="start" opacity={ramp(frame, start, 8)} seed={`bl${seed}`}>
					{label}
				</Scrawl>
			)}
			{rows.map((r, i) => {
				const y = top + 70 + i * ROW_H;
				const w = Math.max(8, (r.value / max) * BAR_W);
				const clipId = `clip-${seed}-${i}`;
				return (
					<g key={r.name} opacity={ramp(frame, start, 8)}>
						<Scrawl x={BAR_X - 24} y={y + 35} size={nameSize} anchor="end" color={r.color} seed={`bn${seed}${i}`}>
							{r.name}
						</Scrawl>
						<clipPath id={clipId}>
							<rect x={BAR_X - 10} y={y - 20} width={(w + 20) * grow} height={110} />
						</clipPath>
						<g clipPath={`url(#${clipId})`}>
							<Ink drawable={bars[i]} />
						</g>
						<Scrawl x={BAR_X + w + 20} y={y + 35} size={52} anchor="start" color={r.color} opacity={ramp(frame, start + 38, 8)} seed={`bv${seed}${i}`}>
							{fmt(r.value)}
						</Scrawl>
					</g>
				);
			})}
		</g>
	);
};
