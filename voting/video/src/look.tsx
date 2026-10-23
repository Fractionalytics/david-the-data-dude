// The Voting look: the Jury Duty look carried over, then retuned on David's real footage (2026-10-23).
// - His shirt reads on camera as slate gray-blue (~#5A6973, sampled from his screenshots), so both group
//   colors are light: gold #FFD23F = ages 18-24 (the viewer), orchid #E9A6FF = ages 65+. Both clear 3:1
//   against the shirt (dataviz validate_palette.js, --surface #5A6973); deutan dE 26, normal dE 28.
//   Teal failed at 2.6:1.
// - Crisp over video: no text outlines (they rendered as a soft halo), every label bold, no line under 6px.
// - A narrower chart area than ZONES_HEAD_TOP.chart, so everything sits on the shirt: x 260-820,
//   y 880-1640 (shirt measured at x ~215-870 below the arms, collar at ~750).
import React from 'react';
import {Easing, interpolate} from 'remotion';
import {loadFont as loadInter} from '@remotion/google-fonts/Inter';
import {loadFont as loadBarlow} from '@remotion/google-fonts/BarlowCondensed';

export const inter = loadInter('normal', {weights: ['700', '800'], subsets: ['latin']}).fontFamily;
export const barlow = loadBarlow('normal', {weights: ['700', '800'], subsets: ['latin']}).fontFamily;

export const COLOR = {young: '#FFD23F', old: '#E9A6FF', off: '#FFFFFF'};
export const Z = {left: 260, right: 820, top: 880, bottom: 1640};
export const CX = (Z.left + Z.right) / 2;

const ease = Easing.bezier(0.4, 0, 0.2, 1);
export const t = (f: number, a: number, b: number) =>
	interpolate(f, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
export const mix = (p: number, a: number, b: number) => a + (b - a) * p;

type TextProps = {x: number; y: number; size?: number; fill?: string; opacity?: number; anchor?: 'start' | 'middle' | 'end'; children: React.ReactNode};

export const Num: React.FC<TextProps> = ({x, y, size = 72, fill = 'white', opacity = 1, anchor = 'middle', children}) => (
	<text x={x} y={y} fontFamily={barlow} fontWeight={800} fontSize={size} textAnchor={anchor} fill={fill} opacity={opacity}>
		{children}
	</text>
);

export const Label: React.FC<TextProps> = ({x, y, size = 56, fill = 'white', opacity = 1, anchor = 'middle', children}) => (
	<text x={x} y={y} fontFamily={inter} fontWeight={800} fontSize={size} textAnchor={anchor} fill={fill} opacity={opacity}>
		{children}
	</text>
);

// A slim person: round head over a rounded body. (x, y) is the bottom center; h is the full height.
export const PERSON_W = 0.36; // body width as a share of height
export const Person: React.FC<{x: number; y: number; h: number; fill: string; scale?: number; opacity?: number}> = ({x, y, h, fill, scale = 1, opacity = 1}) => {
	const r = h * 0.15;
	const bw = h * PERSON_W;
	const bh = h * 0.6;
	return (
		<g transform={`translate(${x} ${y}) scale(${scale}) translate(${-x} ${-y})`} opacity={opacity}>
			<circle cx={x} cy={y - bh - h * 0.06 - r} r={r} fill={fill} />
			<rect x={x - bw / 2} y={y - bh} width={bw} height={bh} rx={bw * 0.4} fill={fill} />
		</g>
	);
};
