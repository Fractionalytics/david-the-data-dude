// Card 8: energy per 150-token ChatGPT reply, EcoLogits low-high estimates, against Altman's 0.34 Wh.
// A PNG for the head-middle frame (David, 2026-10-30): exactly the band above his head, x 120-960 by
// y 250-660 (840 x 410), on a semi-transparent off-white panel. David positions it himself.
// Data: data/ecologits_energy.csv, output_tokens 150.
import React, {useMemo} from 'react';
import {AbsoluteFill} from 'remotion';
import {INK, Ink, MUTED, Scrawl, ink} from '../sharpie';

export const CARD08 = {width: 840, height: 410};

const ROWS: {label: string; min: number; max: number; text: string}[] = [
	{label: 'GPT-4o', min: 0.222, max: 0.366, text: '0.22–0.37'},
	{label: 'GPT-5.5', min: 0.668, max: 1.357, text: '0.67–1.36'},
	{label: 'GPT-6 Astra', min: 1.807, max: 4.103, text: '1.8–4.1'},
];
const ALTMAN_WH = 0.34;

const X0 = 320; // zero line
const X1 = 770; // 5.2 Wh
const MAX = 5.2;
const x = (wh: number) => X0 + (wh / MAX) * (X1 - X0);
const ROW_Y = [185, 270, 355];

export const Card08: React.FC = () => {
	const bars = useMemo(
		() => ROWS.map((r, i) => ink.line(x(r.min), ROW_Y[i], x(r.max), ROW_Y[i], {seed: 80 + i, strokeWidth: 30, roughness: 0.5, stroke: INK.red})),
		[],
	);
	const axis = useMemo(() => ink.line(X0, 140, X0, 395, {seed: 79, strokeWidth: 6}), []);
	const altman = useMemo(() => ink.line(x(ALTMAN_WH), 128, x(ALTMAN_WH), 395, {seed: 78, strokeWidth: 5, strokeLineDash: [14, 12], stroke: INK.blue}), []);
	return (
		<AbsoluteFill>
			<svg width={CARD08.width} height={CARD08.height} viewBox={`0 0 ${CARD08.width} ${CARD08.height}`}>
				<defs>
					<filter id="marker-edge" filterUnits="userSpaceOnUse" x={0} y={0} width={CARD08.width} height={CARD08.height}>
						<feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves={1} seed={3} result="noise" />
						<feDisplacementMap in="SourceGraphic" in2="noise" scale={2.5} />
					</filter>
				</defs>
				<rect x={0} y={0} width={CARD08.width} height={CARD08.height} rx={28} fill="rgba(243, 236, 220, 0.85)" />
				<Scrawl x={CARD08.width / 2} y={48} size={44} seed="t">Energy per ChatGPT reply</Scrawl>
				<Scrawl x={CARD08.width / 2} y={95} size={30} color={MUTED} seed="st">Watt-hours per 150-token reply (EcoLogits)</Scrawl>
				<Ink drawable={axis} />
				<Ink drawable={altman} />
				<Scrawl x={x(ALTMAN_WH) + 12} y={138} size={30} color={INK.blue} anchor="start" seed="al">Altman: 0.34</Scrawl>
				{ROWS.map((r, i) => (
					<g key={r.label}>
						<Scrawl x={X0 - 18} y={ROW_Y[i]} size={36} anchor="end" seed={`l${i}`}>{r.label}</Scrawl>
						<Ink drawable={bars[i]} />
						<Scrawl x={x(r.max) + 28} y={ROW_Y[i]} size={34} anchor="start" seed={`v${i}`}>{r.text}</Scrawl>
					</g>
				))}
			</svg>
		</AbsoluteFill>
	);
};
