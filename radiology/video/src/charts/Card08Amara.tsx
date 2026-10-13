// Revised card 8 (00:08:17 = 257 frames): "AMARA'S LAW" at the top middle (David's words),
// then a CONCEPT sketch of the law, not data: what we expect from a technology (gray) races
// ahead early and flattens; what actually happens (blue) starts slow and overtakes it later.
// No numbers on the axes, on purpose: nothing here is measured. Axis words "short run" /
// "long run" come from the quote David reads.
//
// Cue ESTIMATES (8.6 s total): title 0 s, "expected" curve 1-3.7 s, "actual" curve 3.7-6.7 s,
// "short run" / "long run" labels after each curve.
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {INK, Ink, Page, Plot, Scrawl, ZONES, ink, ramp} from '../sharpie';
import {CX, RAD} from './parts';

export const CARD08_DURATION = 257;
const PLOT: Plot = {left: ZONES.chart.left + 40, right: ZONES.chart.right - 40, top: ZONES.chart.top + 200, bottom: ZONES.chart.bottom - 200};
const N = 40;
const px = (t: number) => PLOT.left + t * (PLOT.right - PLOT.left);
const py = (v: number) => PLOT.bottom - v * (PLOT.bottom - PLOT.top);
// Shapes only: expectation jumps then plateaus; reality is slow, then overtakes (cross ~70% along).
const expected = (t: number) => 0.72 * (1 - Math.exp(-6 * t)) + 0.08 * t;
const actual = (t: number) => 0.97 * t ** 3;
const curve = (f: (t: number) => number) => Array.from({length: N + 1}, (_, i) => [px(i / N), py(f(i / N))] as [number, number]);

const EXP_AT = 30;
const ACT_AT = 110;
export const Card08Amara: React.FC = () => {
	const frame = useCurrentFrame();
	const axes = useMemo(
		() => [ink.line(PLOT.left, PLOT.bottom, PLOT.right + 20, PLOT.bottom, {seed: 81}), ink.line(PLOT.left, PLOT.bottom, PLOT.left, PLOT.top - 20, {seed: 82})],
		[],
	);
	const exp = useMemo(() => ink.path(curve(expected), {seed: 83, stroke: INK.gray, strokeWidth: 10}), []);
	const act = useMemo(() => ink.path(curve(actual), {seed: 84, stroke: RAD, strokeWidth: 10}), []);
	return (
		<Page>
			<Scrawl x={CX} y={ZONES.chart.top + 40} size={90} opacity={ramp(frame, 0, 10)} seed="amara">
				AMARA'S LAW
			</Scrawl>
			{axes.map((a, i) => (
				<Ink key={i} drawable={a} progress={ramp(frame, 12, 15)} />
			))}
			<Ink drawable={exp} progress={ramp(frame, EXP_AT, 80)} connect />
			<Scrawl x={px(0.42)} y={py(expected(0.42)) - 55} size={42} color={INK.gray} opacity={ramp(frame, EXP_AT + 60, 10)} seed="exp">
				what we expect
			</Scrawl>
			<Scrawl x={px(0.2)} y={PLOT.bottom + 55} size={42} opacity={ramp(frame, EXP_AT + 60, 10)} seed="sr">
				short run
			</Scrawl>
			<Ink drawable={act} progress={ramp(frame, ACT_AT, 90)} connect />
			<Scrawl x={px(0.88)} y={py(actual(0.97)) - 10} size={42} color={RAD} anchor="end" opacity={ramp(frame, ACT_AT + 85, 10)} seed="act">
				what happens
			</Scrawl>
			<Scrawl x={px(0.85)} y={PLOT.bottom + 55} size={42} opacity={ramp(frame, ACT_AT + 85, 10)} seed="lr">
				long run
			</Scrawl>
		</Page>
	);
};
