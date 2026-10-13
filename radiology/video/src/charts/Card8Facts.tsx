// Card 8: David's three On-Screen Text lines, word for word, one per cue. Line 2 is wrapped
// to fit the phone width; no words changed. Numbers verified: 65+ +24.3% (Census), imaging
// services per traditional-Medicare enrollee +37.6% vs +26.5% (CMS), radiologists per 100k
// people 65+ -9.3% (CMS + Census).
//
// Cue ESTIMATES (~175 words/min over card 8's 28 words, adjust in edit):
//   line 1 at "an aging population"            ~ word 13 -> 4.5 s
//   line 2 at "increasing reliance on imaging" ~ word 19 -> 6.5 s
//   line 3 at "supply didn't keep up"          ~ word 25 -> 8.5 s
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {Ink, Page, Scrawl, ZONES, ink, ramp} from '../sharpie';
import {RAD} from './parts';

const LINES = [
	{at: 135, text: ['65+ population up 24%']},
	{at: 195, text: ['Imaging services per Medicare patient', 'up 38% vs. 27% for doctor', 'services overall']},
	{at: 255, text: ['Radiologists per 100k Americans 65+', 'down 9%.']},
];
const TOP = ZONES.chart.top + 110;
const LINE_H = 62;
const GAP = 70;
export const CARD8_DURATION = 330;

export const Card8Facts: React.FC = () => {
	const frame = useCurrentFrame();
	let y = TOP;
	const blocks = LINES.map((l) => {
		const top = y;
		y += l.text.length * LINE_H + GAP;
		return {...l, top};
	});
	const dots = useMemo(() => blocks.map((b, i) => ink.dot(ZONES.chart.left + 20, b.top, 26, {seed: 80 + i, stroke: RAD, fill: RAD, strokeWidth: 4})), []);
	return (
		<Page>
			{blocks.map((b, i) => (
				<g key={i} opacity={ramp(frame, b.at, 10)}>
					<Ink drawable={dots[i]} />
					{b.text.map((t, j) => (
						<Scrawl key={j} x={ZONES.chart.left + 60} y={b.top + j * LINE_H} size={40} anchor="start" seed={`c8${i}${j}`}>
							{t}
						</Scrawl>
					))}
				</g>
			))}
		</Page>
	);
};
