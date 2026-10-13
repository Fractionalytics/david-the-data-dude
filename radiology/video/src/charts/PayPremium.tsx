// Card 9: radiologists' pay as a multiple of the average doctor's, 2017 vs 2025 (Doximity).
// The flat line at 1.0x is the average doctor; the radiologist line rises away from it, which
// productivity gains alone would have pushed the other way. Medscape shows the same (1.34x ->
// 1.48x) and is cited in the post text, not here. No footnote or source on the image: sources
// go in the post caption. The title is David's, word for word.
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import data from '../data/card9.json';
import {INK, Ink, Page, Plot, Scrawl, ZONES, ink, ramp, scaleY} from '../sharpie';

const SURVEY = data.surveys.find((s) => s.source === 'Doximity')!;
const [P0, P1] = SURVEY.points;
const PLOT: Plot = {left: ZONES.chart.left + 190, right: ZONES.chart.right - 190, top: ZONES.chart.top + 200, bottom: ZONES.chart.bottom - 190};
const Y_MIN = 1.0;
const Y_MAX = 1.5;
const y = (m: number) => scaleY(PLOT, m - Y_MIN, Y_MAX - Y_MIN);
const XS = [PLOT.left, PLOT.right];

const BASE_AT = 0;
const DOT_AT = 18;
const DRAW_START = 34;
const DRAW_FRAMES = 50;
const END_AT = DRAW_START + DRAW_FRAMES;
export const PAY_DURATION = END_AT + 66;

export const PayPremium: React.FC = () => {
	const frame = useCurrentFrame();
	const baseline = useMemo(() => ink.line(XS[0] - 70, y(1), XS[1] + 70, y(1), {seed: 5, stroke: INK.gray, strokeWidth: 8}), []);
	const line = useMemo(() => ink.line(XS[0], y(P0.multiple), XS[1], y(P1.multiple), {seed: 10, stroke: INK.blue, strokeWidth: 12}), []);
	const startDot = useMemo(() => ink.dot(XS[0], y(P0.multiple), 30, {seed: 20, stroke: INK.blue, fill: INK.blue, strokeWidth: 4}), []);
	const endDot = useMemo(() => ink.dot(XS[1], y(P1.multiple), 30, {seed: 30, stroke: INK.blue, fill: INK.blue, strokeWidth: 4}), []);
	const fmt = (m: number) => `${m.toFixed(2)}×`;

	return (
		<Page>
			{/* Title: David's On-Screen Text for card 9, word for word (2026-10-12). */}
			<Scrawl x={(ZONES.chart.left + ZONES.chart.right) / 2} y={ZONES.chart.top + 40} size={72} opacity={ramp(frame, BASE_AT, 10)} seed="title">
				RADIOLOGY PREMIUM
			</Scrawl>
			<g opacity={ramp(frame, BASE_AT, 12)}>
				<Ink drawable={baseline} progress={ramp(frame, BASE_AT, 14)} />
				<Scrawl x={(XS[0] + XS[1]) / 2} y={y(1) + 50} size={42} color={INK.gray} seed="base">
					Average doctor = 1.0×
				</Scrawl>
				{SURVEY.years.map((yr, i) => (
					<Scrawl key={yr} x={XS[i]} y={y(1) + 130} size={54} seed={`x${i}`}>
						{yr}
					</Scrawl>
				))}
			</g>
			<g opacity={ramp(frame, DOT_AT, 10)}>
				<Ink drawable={startDot} />
				<Scrawl x={XS[0]} y={y(P0.multiple) - 70} size={60} color={INK.blue} seed="s">
					{fmt(P0.multiple)}
				</Scrawl>
			</g>
			<Ink drawable={line} progress={ramp(frame, DRAW_START, DRAW_FRAMES)} />
			{/* The end value appears only when the line arrives, so no unmeasured in-between value
			    ever sits under 2025. */}
			<g opacity={ramp(frame, END_AT, 8)}>
				<Ink drawable={endDot} />
				<Scrawl x={XS[1]} y={y(P1.multiple) - 70} size={60} color={INK.blue} seed="e">
					{fmt(P1.multiple)}
				</Scrawl>
			</g>
			<Scrawl x={(XS[0] + XS[1]) / 2} y={(y(P0.multiple) + y(P1.multiple)) / 2 + 115} size={46} color={INK.blue} opacity={ramp(frame, END_AT, 12)} seed="n">
				Radiologists
			</Scrawl>
		</Page>
	);
};
