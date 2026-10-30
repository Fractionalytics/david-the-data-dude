// Card 6: Altman's 38,000 reproduced. The almond study's full water footprint per almond divided by
// Altman's water per query, starting from his own units (0.000085 gal, "roughly one fifteenth of a
// teaspoon"). A full-screen special case (David, 2026-10-30): no talking head, the two inputs above
// the caption band (1150-1230), the line and result below it, everything inside y 240-1690.
// The animation finishes at frame 30 and holds. Inputs: data/ladder.csv rung 0.
import React, {useMemo} from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {INK, Ink, MUTED, Page, Scrawl, ZONES, ink, ramp} from '../sharpie';

const CX = (ZONES.chart.left + ZONES.chart.right) / 2;
const RESULT = 38_190;

// Fades in while rising 20px.
const In: React.FC<{p: number; children: React.ReactNode}> = ({p, children}) => (
	<g opacity={p} transform={`translate(0 ${(1 - p) * 20})`}>{children}</g>
);

export const Card06: React.FC = () => {
	const frame = useCurrentFrame();
	const rule = useMemo(() => ink.line(170, 1290, 910, 1290, {seed: 6, strokeWidth: 10}), []);
	const count = interpolate(frame, [21, 30], [0, RESULT], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
		easing: Easing.out(Easing.cubic),
	});
	return (
		<Page>
			{/* Above the caption band */}
			<In p={ramp(frame, 0, 7)}>
				<Scrawl x={CX} y={285} size={48} color={MUTED} seed="l1">Water per almond</Scrawl>
				<Scrawl x={CX} y={400} size={160} seed="v1">12.29 L</Scrawl>
				<Scrawl x={CX} y={510} size={42} color={MUTED} seed="n1">University researchers, 2019</Scrawl>
			</In>
			<In p={ramp(frame, 6, 6)}>
				<Scrawl x={CX} y={630} size={48} color={MUTED} seed="l2">Water per ChatGPT query</Scrawl>
				<Scrawl x={CX} y={720} size={72} seed="g">0.000085 gallons</Scrawl>
			</In>
			<In p={ramp(frame, 10, 5)}>
				<Scrawl x={CX} y={805} size={60} seed="t">~1/15 teaspoon</Scrawl>
			</In>
			<In p={ramp(frame, 14, 5)}>
				<Scrawl x={CX} y={940} size={140} seed="v2">÷ 0.322 mL</Scrawl>
				<Scrawl x={CX} y={1060} size={42} color={MUTED} seed="n2">Altman's blog, June 2025</Scrawl>
			</In>
			{/* Below the caption band */}
			<Ink drawable={rule} progress={ramp(frame, 18, 4)} />
			{frame >= 21 && (
				<Scrawl x={CX} y={1470} size={230} color={INK.red} seed="result">
					{Math.round(count).toLocaleString('en-US')}
				</Scrawl>
			)}
			<Scrawl x={CX} y={1650} size={56} opacity={ramp(frame, 24, 6)} seed="unit">ChatGPT queries per almond</Scrawl>
		</Page>
	);
};
