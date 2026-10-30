// Cards 15-17: the cost accounting scorecard from the Sheet's On-Screen Chart tab (cell text is
// David's, 2026-10-30). Traditional layout: off-white background down to the caption band, the
// table filling y 240-1150. Card 15 draws the empty card and Altman's 38,190 and holds through
// card 16; card 17 starts from that state, fills in each row's adjustments and recounts the total.
// Card 18 (in this file because it carries the total forward): 38,000 / 5,800 = 7x.
import React, {useMemo} from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {INK, Ink, MUTED, Page, Scrawl, ZONES, ink, ramp} from '../sharpie';

const CAPTION_TOP = ZONES.caption.top; // 1150

// Columns: row label (left-aligned), Altman, Almonds (centered).
const COL = {label: 130, altman: 555, almonds: 852};
const HEADER_Y = 290;
const ROW_Y = (i: number) => 425 + i * 112; // 425 ... 873
const TOTAL_Y = 1030;

// [row label, Altman cell, Almonds cell], from the On-Screen Chart tab.
const ROWS: [string, string, string][] = [
	['Direct', 'Keep', 'Keep'],
	['Power', 'Best case only', '<1%'],
	['Rain', '', 'Remove'],
	['Grey', 'Not included', 'Remove'],
	['Training', 'Add', 'Partial'],
];

// Actions in color, notes in blue.
const cellColor = (text: string) =>
	text === 'Keep' ? INK.black : text === 'Remove' ? INK.red : text === 'Add' ? INK.green : INK.blue;

const ALTMAN_TOTAL = 38_190;
const OUR_TOTAL = 5_823; // data/ladder.csv rung 3, 0.34 Wh incl. PUE

// The card's frame: headers, rules and row labels. `p` 0..1 draws it in.
const Frame: React.FC<{frame: number; start: number}> = ({frame, start}) => {
	const top = useMemo(() => ink.line(125, 345, 955, 345, {seed: 151, strokeWidth: 7}), []);
	const bottom = useMemo(() => ink.line(125, 945, 955, 945, {seed: 152, strokeWidth: 7}), []);
	return (
		<g>
			{[['Water type', COL.label, 'start'], ['Altman', COL.altman, 'middle'], ['Almonds', COL.almonds, 'middle']].map(([t, x, a], i) => (
				<Scrawl key={t as string} x={x as number} y={HEADER_Y} size={48} color={MUTED} anchor={a as 'start' | 'middle'} opacity={ramp(frame, start + i * 3, 8)} seed={`h${i}`}>
					{t}
				</Scrawl>
			))}
			<Ink drawable={top} progress={ramp(frame, start + 6, 10)} />
			{ROWS.map(([label], i) => (
				<Scrawl key={label} x={COL.label} y={ROW_Y(i)} size={64} anchor="start" opacity={ramp(frame, start + 14 + i * 6, 8)} seed={`r${i}`}>
					{label}
				</Scrawl>
			))}
			<Ink drawable={bottom} progress={ramp(frame, start + 42, 10)} />
			<Scrawl x={COL.label} y={TOTAL_Y} size={64} anchor="start" opacity={ramp(frame, start + 48, 8)} seed="tl">Total</Scrawl>
		</g>
	);
};

// The total row: "38,190" alone at first; card 17 counts it to 5,823 and adds "= 6.6x".
const Total: React.FC<{value: number; ratio: number}> = ({value, ratio}) => (
	<g>
		<Scrawl x={COL.altman + 85} y={TOTAL_Y} size={90} color={INK.red} anchor="end" seed="tv">
			{Math.round(value).toLocaleString('en-US')}
		</Scrawl>
		{ratio > 0 && (
			<Scrawl x={COL.altman + 125} y={TOTAL_Y} size={90} color={INK.red} anchor="start" opacity={ratio} seed="tr">
				= 6.6x
			</Scrawl>
		)}
		<Scrawl x={540} y={TOTAL_Y + 82} size={40} color={MUTED} seed="tu">ChatGPT queries per almond</Scrawl>
	</g>
);

// Card 15 (and 16, held): 417 frames. Drawn in by frame 70.
export const Card15: React.FC = () => {
	const frame = useCurrentFrame();
	return (
		<Page bgBottom={CAPTION_TOP}>
			<Frame frame={frame} start={0} />
			<g opacity={ramp(frame, 58, 10)}>
				<Total value={ALTMAN_TOTAL} ratio={0} />
			</g>
		</Page>
	);
};

// Card 17: 271 frames. Starts where card 15 ends; one row every 28 frames from frame 8, then the
// total recounts (152-212) and the ratio lands at 222. Holds from frame 232.
export const Card17: React.FC = () => {
	const frame = useCurrentFrame();
	const total = interpolate(frame, [152, 212], [ALTMAN_TOTAL, OUR_TOTAL], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
		easing: Easing.inOut(Easing.cubic),
	});
	return (
		<Page bgBottom={CAPTION_TOP}>
			<Frame frame={frame} start={-100} />
			{ROWS.map(([, altman, almonds], i) => {
				const t = 8 + i * 28;
				return (
					<g key={i}>
						<Scrawl x={COL.altman} y={ROW_Y(i)} size={56} color={cellColor(altman)} opacity={ramp(frame, t, 8)} seed={`a${i}`}>{altman}</Scrawl>
						<Scrawl x={COL.almonds} y={ROW_Y(i)} size={56} color={cellColor(almonds)} opacity={ramp(frame, t + 8, 8)} seed={`b${i}`}>{almonds}</Scrawl>
					</g>
				);
			})}
			<Total value={total} ratio={ramp(frame, 222, 10)} />
		</Page>
	);
};

// Card 18: 274 frames. 38,000 / 5,800 = 6.6x (David chose one decimal over 7x, 2026-10-30, to match the scorecard). The denominator counts down
// from 38,000 (frames 15-105) while the ratio counts up with it; done by 105, then holds.
// Its last frame is the still for cards 19 and 20.
export const Card18: React.FC = () => {
	const frame = useCurrentFrame();
	const denom = interpolate(frame, [15, 105], [38_000, 5_800], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
		easing: Easing.inOut(Easing.cubic),
	});
	const rule = useMemo(() => ink.line(190, 525, 890, 525, {seed: 18, strokeWidth: 10}), []);
	const shown = Math.round(denom / 100) * 100; // counts in hundreds, so it lands exactly on 5,800
	return (
		<Page bgBottom={CAPTION_TOP}>
			<g opacity={ramp(frame, 0, 8)}>
				<Scrawl x={540} y={380} size={210} seed="num">38,000</Scrawl>
				<Ink drawable={rule} progress={ramp(frame, 2, 8)} />
				<Scrawl x={540} y={680} size={210} seed="den">{shown.toLocaleString('en-US')}</Scrawl>
				<Scrawl x={540} y={1010} size={270} color={INK.red} seed="ratio">
					= {(38_000 / shown).toFixed(1)}x
				</Scrawl>
			</g>
		</Page>
	);
};
