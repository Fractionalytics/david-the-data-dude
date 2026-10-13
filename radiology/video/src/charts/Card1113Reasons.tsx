// Revised cards 11-13 (00:40:04 = 1204 frames): "TWO REASONS" (David's words), which moves up;
// then reason 1, a 100-square grid of a radiologist's working time that starts all blue (the
// assumption that reading scans is the whole job) and drains to 36% (VALUE study: Dhanoa et al.,
// J Am Coll Radiol 2013;10(10):764-769; observer followed 14 diagnostic radiologists at three
// Vancouver hospitals, fall 2012; 36.4% of time on image interpretation). Then reason 2, David's
// three On-Screen Text lines for card 13, word for word (numbers as on card8-facts: Census and
// CMS, data/processed/demand_controls.csv). Grid labels are descriptive; David may replace them.
//
// Cue ESTIMATES (David gave only the 40.1 s total; cards 11-13 = 94 words, ~12.8 frames/word):
//   card 12 starts ("First, it made...")        ~ word 13 -> frame 155: title up, "1."
//   "evaluating scans is all a radiologist does" ~ word 20 -> frame 256: grid, all blue
//   "about 36% of their time"                   ~ word 40 -> frame 510: drains to 36
//   "The rest includes"                         ~ word 46 -> frame 590: "64% everything else"
//   card 13 starts ("Second, it ignored...")    ~ word 56 -> frame 700: grid out, "2."
//   "Internal scans have become a bigger part"  ~ word 64 -> frame 820: imaging line
//   "the population over 65 ... risen 24%"      ~ word 73 -> frame 935: 65+ line
//   "the number of radiologists"                ~ word 88 -> frame 1110: radiologists line
// Lines sit in David's order; they appear in the order the script speaks them.
import React, {useMemo} from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Ink, Page, Scrawl, ZONES, ink, ramp} from '../sharpie';
import {CX, OTHER, RAD} from './parts';

export const CARD1113_DURATION = 1204;
const MOVE_AT = 155;
const ONE_AT = 170;
const GRID_AT = 256;
const DRAIN_AT = 510;
const REST_AT = 590;
const GRID_OUT = 700;
const TWO_AT = 715;

const READING = 36; // VALUE study, 36.4% rounded as in the script
const COLS = 10;
const ROWS = 10;
const CELL = 52;
const GRID_LEFT = CX - (COLS * CELL) / 2;
const GRID_TOP = ZONES.chart.top + 230;

const LINES = [
	{at: 935, text: ['65+ population up 24%']},
	{at: 820, text: ['Imaging services per Medicare patient', 'up 38% vs. 27% for doctor', 'services overall']},
	{at: 1110, text: ['Radiologists per 100k Americans 65+', 'down 9%.']},
];
const FACTS_TOP = ZONES.chart.top + 300;
const LINE_H = 62;
const GAP = 80;

export const Card1113Reasons: React.FC = () => {
	const frame = useCurrentFrame();
	const move = interpolate(frame, [MOVE_AT, MOVE_AT + 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const titleY = interpolate(move, [0, 1], [ZONES.chart.top + 420, ZONES.chart.top + 40]);
	// Same sizes as "1. CAPABILITY" and "2. PRESCRIPTION".
	const titleSize = interpolate(move, [0, 1], [96, 72]);
	const one = ramp(frame, ONE_AT, 10) * (1 - ramp(frame, GRID_OUT, 15));
	const gridIn = ramp(frame, GRID_AT, 10) * (1 - ramp(frame, GRID_OUT, 15));
	// Squares turn gray from the end, one at a time, until 36 blue are left.
	const blue = 100 - Math.round(ramp(frame, DRAIN_AT, 45) * (100 - READING));

	let y = FACTS_TOP;
	const blocks = LINES.map((l) => {
		const top = y;
		y += l.text.length * LINE_H + GAP;
		return {...l, top};
	});
	const dots = useMemo(() => blocks.map((b, i) => ink.dot(ZONES.chart.left + 20, b.top, 26, {seed: 130 + i, stroke: RAD, fill: RAD, strokeWidth: 4})), []);

	return (
		<Page>
			<Scrawl x={CX} y={titleY} size={titleSize} opacity={ramp(frame, 0, 10)} seed="two">
				TWO REASONS
			</Scrawl>
			<Scrawl x={CX} y={ZONES.chart.top + 140} size={80} opacity={one} seed="r1">
				1.
			</Scrawl>
			<g opacity={gridIn}>
				{Array.from({length: COLS * ROWS}, (_, i) => (
					<rect
						key={i}
						x={GRID_LEFT + (i % COLS) * CELL + 4}
						y={GRID_TOP + Math.floor(i / COLS) * CELL + 4}
						width={CELL - 8}
						height={CELL - 8}
						rx={5}
						fill={i < blue ? RAD : '#dcdcd8'}
					/>
				))}
				<Scrawl x={CX} y={GRID_TOP + ROWS * CELL + 60} size={60} color={RAD} opacity={ramp(frame, DRAIN_AT + 45, 10)} seed="read">
					{`${READING}% reading scans`}
				</Scrawl>
				<Scrawl x={CX} y={GRID_TOP + ROWS * CELL + 135} size={52} color={OTHER} opacity={ramp(frame, REST_AT, 10)} seed="rest">
					{`${100 - READING}% everything else`}
				</Scrawl>
			</g>
			<Scrawl x={CX} y={ZONES.chart.top + 140} size={80} opacity={ramp(frame, TWO_AT, 10)} seed="r2">
				2.
			</Scrawl>
			{blocks.map((b, i) => (
				<g key={i} opacity={ramp(frame, b.at, 10)}>
					<Ink drawable={dots[i]} />
					{b.text.map((t, j) => (
						<Scrawl key={j} x={ZONES.chart.left + 60} y={b.top + j * LINE_H} size={40} anchor="start" seed={`c13${i}${j}`}>
							{t}
						</Scrawl>
					))}
				</g>
			))}
		</Page>
	);
};
