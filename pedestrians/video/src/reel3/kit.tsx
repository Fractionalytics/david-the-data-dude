// Reel 3's road-sign kit: Reel 1's look (colors, font, plate) in Reel 3's layout. David framed his head lower
// this time (top of head about y 1000 in both speakers' stills, measured 2026-11-17 from public/reel3/), with
// the standard caption in the 80px above it (about y 920-1000). The plate takes the band above that:
// x 120-960, y 260-900, so it is 640 tall instead of Reel 1's 550.
import React from 'react';
import {Easing, interpolate} from 'remotion';
import {C, FONT} from '../look';

export {C, FONT};
export const BAND = {left: 120, right: 960, top: 260, bottom: 900};
export const W = BAND.right - BAND.left;
export const H = BAND.bottom - BAND.top;

export const clamp = (v: number) => Math.max(0, Math.min(1, v));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const ease = Easing.inOut(Easing.cubic);
// Progress 0-1 between frames a and b.
export const prog = (g: number, a: number, b: number, e = ease) =>
	interpolate(g, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});

export const Plate: React.FC<{children: React.ReactNode; opacity?: number}> = ({children, opacity = 1}) => (
	<div
		style={{
			position: 'absolute',
			left: BAND.left,
			top: BAND.top,
			width: W,
			height: H,
			background: C.plate,
			borderRadius: 30,
			boxShadow: `inset 0 0 0 7px ${C.border}`,
			fontFamily: FONT,
			color: C.ink,
			overflow: 'hidden',
			opacity,
		}}
	>
		{children}
	</div>
);

// Titles are David's words (Sheet, On-Screen Text), in caps.
export const Title: React.FC<{text: string; size?: number; opacity?: number}> = ({text, size = 58, opacity = 1}) => (
	<div style={{position: 'absolute', left: 40, right: 40, top: 26, fontSize: size, fontWeight: 800, lineHeight: 1.0, whiteSpace: 'pre-line', textTransform: 'uppercase', letterSpacing: 1, opacity, color: text.startsWith('[TBD') ? C.muted : C.ink}}>
		{text}
	</div>
);

export const Svg: React.FC<{children: React.ReactNode}> = ({children}) => (
	<svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', left: 0, top: 0}}>
		{children}
	</svg>
);

export const T: React.FC<React.SVGProps<SVGTextElement> & {size?: number; weight?: number}> = ({size = 44, weight = 700, children, ...rest}) => (
	<text fontFamily={FONT} fontSize={size} fontWeight={weight} fill={C.ink} {...rest}>
		{children}
	</text>
);

export const Sub: React.FC<{text: string; opacity?: number; y?: number}> = ({text, opacity = 1, y = 128}) => (
	<T x={40} y={y} size={36} fill={C.muted} opacity={opacity}>{text}</T>
);

export type Pt = {x: number; v: number};

// A polyline drawn left to right up to progress p (by x), interpolating the last segment.
export const partial = (pts: Pt[], p: number): Pt[] => {
	if (p >= 1) return pts;
	if (p <= 0) return [pts[0]];
	const x0 = pts[0].x, x1 = pts[pts.length - 1].x, cut = x0 + (x1 - x0) * p;
	const out: Pt[] = [];
	for (let i = 0; i < pts.length; i++) {
		if (pts[i].x <= cut) out.push(pts[i]);
		else {
			const a = pts[i - 1], b = pts[i], t = (cut - a.x) / (b.x - a.x);
			out.push({x: cut, v: a.v + (b.v - a.v) * t});
			break;
		}
	}
	return out;
};

const pathOf = (pts: Pt[], x: (n: number) => number, y: (n: number) => number) =>
	pts.map((p, i) => `${i ? 'L' : 'M'}${x(p.x).toFixed(1)},${y(p.v).toFixed(1)}`).join(' ');

export const Line: React.FC<{pts: Pt[]; p: number; x: (n: number) => number; y: (n: number) => number; color: string; dash?: string; width?: number}> = ({pts, p, x, y, color, dash, width = 8}) => {
	const shown = partial(pts, p);
	const end = shown[shown.length - 1];
	return (
		<g>
			<path d={pathOf(shown, x, y)} fill="none" stroke={color} strokeWidth={width} strokeLinejoin="round" strokeLinecap="round" strokeDasharray={dash} />
			{p > 0 && <circle cx={x(end.x)} cy={y(end.v)} r={9} fill={color} />}
		</g>
	);
};
