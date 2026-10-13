// Revised cards 6-7 (00:24:00 = 720 frames): "1. CAPABILITY" (David's words), which then moves
// to the top while the FDA grid fills (76% of 1,614 AI tools are radiology), then "5 years"
// is crossed out and "15 years" written in (Hinton, Dec 2023: off by a factor of three).
//
// Cue ESTIMATES (David gave only the 24 s total; cards 6+7 = 67 words, so ~2.8 words/s):
//   "76% of FDA-cleared AI tools"        ~ word 30 -> 10.7 s -> grid at frame 315
//   "off by a factor of three"           ~ word 51 -> 18.3 s -> grid out, "5 years" at 545
//   "Instead of 5 years"                 ~ word 57 -> 20.4 s -> cross-out at 600
//   "it would probably take 15"          ~ word 66 -> 23.6 s -> "15 years" at 655
import React, {useMemo} from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import data from '../data/cards.json';
import {INK, Ink, Page, Scrawl, ZONES, ink, ramp} from '../sharpie';
import {CX, RAD} from './parts';

export const CARD0607_DURATION = 720;
const MOVE_AT = 290; // title moves up
const GRID_AT = 315;
const GRID_OUT = 520;
const FIVE_AT = 545;
const CROSS_AT = 600;
const FIFTEEN_AT = 655;

const COLS = 10;
const ROWS = 10;
const CELL = 62;
const GRID_LEFT = CX - (COLS * CELL) / 2;
const GRID_TOP = ZONES.chart.top + 190;
const SHARE = Math.round((100 * data.fda.radiology) / data.fda.all); // 76

export const Card0607Capability: React.FC = () => {
	const frame = useCurrentFrame();
	const move = interpolate(frame, [MOVE_AT, MOVE_AT + 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const titleY = interpolate(move, [0, 1], [ZONES.chart.top + 420, ZONES.chart.top + 40]);
	// Same starting size as "2. PRESCRIPTION" (cards 9-10), so the two section titles match.
	const titleSize = interpolate(move, [0, 1], [96, 72]);
	const gridIn = ramp(frame, GRID_AT, 10) * (1 - ramp(frame, GRID_OUT, 15));
	const filled = Math.round(ramp(frame, GRID_AT + 10, 60) * SHARE);
	const cross = useMemo(() => ink.line(CX - 210, ZONES.chart.top + 420, CX + 210, ZONES.chart.top + 330, {seed: 71, stroke: INK.red, strokeWidth: 14}), []);
	return (
		<Page>
			<Scrawl x={CX} y={titleY} size={titleSize} opacity={ramp(frame, 0, 10)} seed="cap">
				1. CAPABILITY
			</Scrawl>
			<g opacity={gridIn}>
				<Scrawl x={CX} y={GRID_TOP - 60} size={44} seed="fda">
					{`FDA-cleared AI tools: ${data.fda.all.toLocaleString('en-US')}`}
				</Scrawl>
				{Array.from({length: COLS * ROWS}, (_, i) => (
					<rect
						key={i}
						x={GRID_LEFT + (i % COLS) * CELL + 4}
						y={GRID_TOP + Math.floor(i / COLS) * CELL + 4}
						width={CELL - 8}
						height={CELL - 8}
						rx={6}
						fill={i < filled ? RAD : '#dcdcd8'}
					/>
				))}
				<Scrawl x={CX} y={GRID_TOP + ROWS * CELL + 60} size={64} color={RAD} opacity={ramp(frame, GRID_AT + 70, 10)} seed="pct">
					{`${SHARE}% radiology`}
				</Scrawl>
			</g>
			<g opacity={ramp(frame, FIVE_AT, 10)}>
				<Scrawl x={CX} y={ZONES.chart.top + 375} size={140} seed="five">
					5 years
				</Scrawl>
				<Ink drawable={cross} progress={ramp(frame, CROSS_AT, 12)} />
			</g>
			<Scrawl x={CX} y={ZONES.chart.top + 620} size={170} color={RAD} opacity={ramp(frame, FIFTEEN_AT, 10)} seed="fifteen">
				15 years
			</Scrawl>
		</Page>
	);
};
