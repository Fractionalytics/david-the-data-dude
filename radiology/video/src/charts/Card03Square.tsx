// Revised card 3 (00:06:05 = 185 frames): a square headline chart for a small corner inset
// while David's face fills the screen. Radiologists billing traditional Medicare +12.8% (blue)
// vs all doctors +7.2% (gray), 2016-2024. Text is large because the inset is small.
// Title: the descriptive label used on the other headline charts; card 3's On-Screen Text is
// empty, so David can replace it with his own wording.
import React, {useMemo} from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import data from '../data/cards.json';
import {Ink, Scrawl, ink, ramp} from '../sharpie';
import {OTHER, RAD} from './parts';

export const SQUARE = {width: 1080, height: 1080, fps: 30};
export const CARD03_DURATION = 185;

const BASE = 850;
const TOP_H = 520; // height of the taller (radiologists) bar
const W = 260;
const BARS = [
	{x: 170, value: data.medicare.radiologists, color: RAD, name: 'Radiologists', seed: 31},
	{x: 650, value: data.medicare.physicians, color: OTHER, name: 'All doctors', seed: 32},
];

export const Card03Square: React.FC = () => {
	const frame = useCurrentFrame();
	const max = data.medicare.radiologists;
	const h = (v: number) => (v / max) * TOP_H;
	const bars = useMemo(
		() => BARS.map((b) => ink.rect(b.x, BASE - h(b.value), W, h(b.value), {seed: b.seed, stroke: b.color, fill: b.color, strokeWidth: 7, hachureGap: 9})),
		[max],
	);
	const baseline = useMemo(() => ink.line(110, BASE, 970, BASE, {seed: 33, strokeWidth: 8}), []);
	const grow = ramp(frame, 15, 45);
	const values = ramp(frame, 60, 10); // values appear once the bars have finished growing
	return (
		<AbsoluteFill style={{backgroundColor: 'white'}}>
			<svg width={1080} height={1080} viewBox="0 0 1080 1080">
				<defs>
					<filter id="marker-edge" filterUnits="userSpaceOnUse" x={0} y={0} width={1080} height={1080}>
						<feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves={1} seed={3} result="noise" />
						<feDisplacementMap in="SourceGraphic" in2="noise" scale={2.5} />
					</filter>
					{/* Bars rise from the baseline: clip from the bottom up. */}
					<clipPath id="rise">
						<rect x={0} y={BASE + 20 - (TOP_H + 40) * grow} width={1080} height={(TOP_H + 40) * grow} />
					</clipPath>
				</defs>
				<Scrawl x={540} y={95} size={66} opacity={ramp(frame, 0, 10)} seed="t1">
					Doctors billing Medicare
				</Scrawl>
				<Scrawl x={540} y={170} size={56} opacity={ramp(frame, 0, 10)} seed="t2">
					2016–2024
				</Scrawl>
				<g clipPath="url(#rise)">
					{bars.map((d, i) => (
						<Ink key={i} drawable={d} />
					))}
				</g>
				<Ink drawable={baseline} progress={ramp(frame, 0, 12)} />
				{BARS.map((b) => (
					<g key={b.name}>
						<Scrawl x={b.x + W / 2} y={BASE - h(b.value) - 50} size={78} color={b.color} opacity={values} seed={`v${b.seed}`}>
							{`+${b.value.toFixed(1)}%`}
						</Scrawl>
						<Scrawl x={b.x + W / 2} y={BASE + 70} size={58} color={b.color} opacity={ramp(frame, 0, 10)} seed={`n${b.seed}`}>
							{b.name}
						</Scrawl>
					</g>
				))}
			</svg>
		</AbsoluteFill>
	);
};
