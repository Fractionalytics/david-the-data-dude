// Card 5: "AI did arrive." Panel 1: the FDA's 1,614 AI-enabled devices (through 2026-06-29) as
// 100 squares, one per 1%; the 76 radiology squares fill in blue. Panel 2: average Medicare
// services per clinician, 2016-2024: radiologists +10% vs all doctors +3.6% (means, David's
// choice; the median/trimmed caveat is in data-challenges §17). No source line on the image.
//
// Cue ESTIMATES (~175 words/min over card 5's 50 words, adjust in edit):
//   panel 1 at "Out of 1,600+ FDA-cleared AI tools..."           ~ word 8  -> 2.7 s
//   panel 2 at "Medicare services billed per radiologist..."     ~ word 38 -> 13 s
import React from 'react';
import {useCurrentFrame} from 'remotion';
import data from '../data/cards.json';
import {Page, Scrawl, ZONES, ramp} from '../sharpie';
import {BarPair, OTHER, RAD} from './parts';

const GRID_AT = 80;
const FILL_FRAMES = 60;
const BARS_AT = 390;
export const CARD5_DURATION = 520;

const COLS = 20;
const ROWS = 5;
const CELL = (ZONES.chart.right - ZONES.chart.left) / COLS;
const SQ = CELL - 8;
const GRID_TOP = ZONES.chart.top + 90;
const SHARE = Math.round((100 * data.fda.radiology) / data.fda.all); // 76

export const Card5Arrived: React.FC = () => {
	const frame = useCurrentFrame();
	const filled = Math.round(ramp(frame, GRID_AT + 10, FILL_FRAMES) * SHARE);
	return (
		<Page>
			<g opacity={ramp(frame, GRID_AT, 8)}>
				<Scrawl x={ZONES.chart.left} y={ZONES.chart.top + 30} size={42} anchor="start" seed="g1">
					{`FDA-cleared AI tools: ${data.fda.all.toLocaleString('en-US')}`}
				</Scrawl>
				{Array.from({length: COLS * ROWS}, (_, i) => (
					<rect
						key={i}
						x={ZONES.chart.left + (i % COLS) * CELL + 4}
						y={GRID_TOP + Math.floor(i / COLS) * CELL + 4}
						width={SQ}
						height={SQ}
						rx={5}
						fill={i < filled ? RAD : '#dcdcd8'}
					/>
				))}
				<Scrawl x={ZONES.chart.left} y={GRID_TOP + ROWS * CELL + 50} size={52} anchor="start" color={RAD} opacity={ramp(frame, GRID_AT + 10 + FILL_FRAMES, 10)} seed="g2">
					{`${SHARE}% radiology`}
				</Scrawl>
			</g>
			<BarPair
				frame={frame}
				start={BARS_AT}
				top={ZONES.chart.top + 520}
				label="Medicare services per doctor, 2016–2024"
				rows={[
					{name: 'Radiologists', value: data.services.radiologists, color: RAD},
					{name: 'All doctors', value: data.services.physicians, color: OTHER},
				]}
				max={11}
				fmt={(v) => `+${Number.isInteger(v) ? v : v.toFixed(1)}%`}
				seed={500}
			/>
		</Page>
	);
};
