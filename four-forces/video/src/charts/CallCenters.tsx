// Card 19: slopegraph of call-center industry employment (BLS CES, NAICS 56142, not seasonally
// adjusted, so same month at both ends): Aug 2022 439.8K -> Aug 2026 303.3K (preliminary), -31%.
// David's Video note: "a slopegraph with the absolute numbers and a big 31% drop from 2022 to today.
// Render this as an animated white square that I can overlay." So: 1080x1080, white, no zones.
// Text is large because the overlay may be shown small. Timing: ../cues.ts.
import React, {useMemo} from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import data from '../data/charts.json';
import {CUE} from '../cues';
import {INK, Ink, Scrawl, ink, ramp} from '../sharpie';
import {HOT} from './parts';

export const SQUARE = {width: 1080, height: 1080, fps: 30};
export const CALL_DURATION = CUE.c19.dur;

const C = data.callCenters;
const XL = 260;
const XR = 820;
const TOP = 150;
const BOT = 870;
const VMAX = 460;
const y = (k: number) => BOT - (k / VMAX) * (BOT - TOP);
const PCT_AT = CUE.c19.pct; // "-31%" lands on "31%"
const LINE_AT = PCT_AT - 70;
const fmt = (k: number) => `${Math.round(k)}K`;

export const CallCenters: React.FC = () => {
	const frame = useCurrentFrame();
	const line = useMemo(() => ink.line(XL, y(C.from_k), XR, y(C.to_k), {seed: 11, stroke: HOT, strokeWidth: 14}), []);
	const dots = useMemo(() => [ink.dot(XL, y(C.from_k), 36, {seed: 12, stroke: HOT, fill: HOT}), ink.dot(XR, y(C.to_k), 36, {seed: 13, stroke: HOT, fill: HOT})], []);
	const axes = useMemo(() => [XL, XR].map((x, i) => ink.line(x, TOP - 40, x, BOT, {seed: 14 + i, stroke: INK.gray, strokeWidth: 4})), []);
	return (
		<AbsoluteFill style={{backgroundColor: 'white'}}>
			<svg width={1080} height={1080} viewBox="0 0 1080 1080">
				<defs>
					<filter id="marker-edge" filterUnits="userSpaceOnUse" x={0} y={0} width={1080} height={1080}>
						<feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves={1} seed={3} result="noise" />
						<feDisplacementMap in="SourceGraphic" in2="noise" scale={2.5} />
					</filter>
				</defs>
				<g opacity={ramp(frame, 0, 10)}>
					{axes.map((a, i) => (
						<Ink key={i} drawable={a} />
					))}
					{[C.from, C.to].map((t, i) => (
						<Scrawl key={t} x={i ? XR : XL} y={BOT + 70} size={60} seed={`t${i}`}>
							{t}
						</Scrawl>
					))}
					<Ink drawable={dots[0]} />
					<Scrawl x={XL} y={y(C.from_k) - 75} size={80} color={HOT} seed="a">
						{fmt(C.from_k)}
					</Scrawl>
				</g>
				<Ink drawable={line} progress={ramp(frame, LINE_AT, 45)} />
				<g opacity={ramp(frame, LINE_AT + 45, 8)}>
					<Ink drawable={dots[1]} />
					<Scrawl x={XR} y={y(C.to_k) - 75} size={80} color={HOT} seed="b">
						{fmt(C.to_k)}
					</Scrawl>
				</g>
				<Scrawl x={540} y={(y(C.from_k) + y(C.to_k)) / 2 + 230} size={210} color={HOT} opacity={ramp(frame, PCT_AT - 12, 12)} seed="pct">
					{`${C.pct}%`}
				</Scrawl>
			</svg>
		</AbsoluteFill>
	);
};
