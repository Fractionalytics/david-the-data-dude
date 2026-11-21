// Reel 4's look: Reel 2's lab report (monospace type, graph-paper grid, thin rules, a dotted source rule,
// a rubber stamp), re-cut for a semi-transparent scrim over David's green-hedge footage (David, 2026-11-21).
// The paper becomes smoked glass: a dark, 64%-opaque panel, so the type and rules flip to off-white, and the
// five lines take bright colours that stay clear of the hedge's greens.
// Layout, measured on David's hedge still (public/reel4/speaker.png): the top of his head is at y ~1005 and
// his chin at ~1530, so his caption runs below the chin (~y 1550-1630, clear of Instagram's username at
// 1722) and the panel takes everything above his head, y 140-980. Only the peaks of waves 3 and 4 reach
// into Instagram's header band (y 168-220); David allowed that.
import React from 'react';
import {Easing, interpolate} from 'remotion';

export const FONT = 'Consolas, "Courier New", monospace';
export const PANEL = {left: 104, right: 976, top: 140, bottom: 980};

export const C = {
	glass: 'rgba(14, 17, 16, 0.64)',
	grid: 'rgba(255, 255, 255, 0.07)',
	rule: 'rgba(242, 239, 230, 0.55)',
	ink: '#F2EFE6',
	muted: '#B4BAB4',
	stamp: '#FF5A50',
};

// One colour per line. Wave 1 amber (pills, and OxyContin's sales on cards 4-6), wave 2 sky blue, wave 3
// coral, wave 4 orchid, stimulants without fentanyl off-white and dashed.
export const LINES = [
	{key: 'w1', label: 'WAVE 1  RX PILLS', color: '#FFB547'},
	{key: 'w2', label: 'WAVE 2  HEROIN', color: '#5EC8FF'},
	{key: 'w3', label: 'WAVE 3  FENTANYL', color: '#FF6B6B'},
	{key: 'w4', label: 'WAVE 4  FENTANYL + STIMULANT', color: '#D98BFF'},
	{key: 'stim', label: 'STIMULANTS, NO FENTANYL', color: '#F2EFE6', dash: '14 10'},
] as const;
export type LineKey = (typeof LINES)[number]['key'];

export const clamp = (v: number) => Math.max(0, Math.min(1, v));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const ease = Easing.inOut(Easing.cubic);
export const prog = (g: number, a: number, b: number, e = ease) =>
	interpolate(g, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});

// The smoked-glass panel with graph-paper grid and a thin border. Children draw in full-frame coordinates.
export const Panel: React.FC<{opacity?: number; children?: React.ReactNode}> = ({opacity = 1, children}) => {
	const {left, right, top, bottom} = PANEL;
	const w = right - left, h = bottom - top;
	return (
		<div style={{position: 'absolute', inset: 0, opacity}}>
			<div style={{position: 'absolute', left, top, width: w, height: h, background: C.glass, borderRadius: 6, boxShadow: `inset 0 0 0 2px ${C.rule}`}} />
			<svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
				{Array.from({length: Math.floor(w / 24) - 1}, (_, i) => (
					<line key={`x${i}`} x1={left + (i + 1) * 24} x2={left + (i + 1) * 24} y1={top + 3} y2={bottom - 3} stroke={C.grid} strokeWidth={1} />
				))}
				{Array.from({length: Math.floor(h / 24) - 1}, (_, i) => (
					<line key={`y${i}`} x1={left + 3} x2={right - 3} y1={top + (i + 1) * 24} y2={top + (i + 1) * 24} stroke={C.grid} strokeWidth={1} />
				))}
			</svg>
			{children}
		</div>
	);
};

export const T: React.FC<React.SVGProps<SVGTextElement> & {size?: number; weight?: number}> = ({size = 22, weight = 700, children, ...rest}) => (
	<text fontFamily={FONT} fontSize={size} fontWeight={weight} fill={C.ink} {...rest}>
		{children}
	</text>
);

// A typed note card (the lab report's annotation slip): a darker box with a kicker, body lines and an
// optional source line. Body text is David's On-Screen Text; kickers and source lines are ours.
export const Note: React.FC<{x: number; y: number; w: number; p: number; kicker?: string; lines: string[]; size?: number; source?: string; fine?: string}> = ({x, y, w, p, kicker, lines, size = 26, source, fine}) => {
	if (p <= 0) return null;
	return (
		<div style={{position: 'absolute', left: x, top: y, width: w, opacity: clamp(p * 1.4), transform: `translateY(${(1 - clamp(p)) * 14}px)`, background: 'rgba(8, 10, 9, 0.72)', boxShadow: `inset 0 0 0 1.5px ${C.rule}`, borderRadius: 4, padding: '16px 20px 14px', fontFamily: FONT, color: C.ink, boxSizing: 'border-box'}}>
			{kicker && <div style={{fontSize: 17, color: C.muted, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 8}}>{kicker}</div>}
			{lines.map((l, i) => (
				<div key={i} style={{fontSize: size, fontWeight: 700, lineHeight: 1.22, marginTop: i ? 8 : 0}}>{l}</div>
			))}
			{fine && <div style={{fontSize: 20, lineHeight: 1.32, marginTop: 14, color: C.ink, opacity: 0.88}}>{fine}</div>}
			{source &&<div style={{fontSize: 15, color: C.muted, letterSpacing: 0.5, textTransform: 'uppercase', marginTop: 12, borderTop: `1.5px dotted ${C.rule}`, paddingTop: 8}}>{source}</div>}
		</div>
	);
};

// The rubber stamp: a red rounded box, tilted, that lands from slightly too big (p 0-1).
export const Stamp: React.FC<{x: number; y: number; text: string; sub?: string; p: number; size?: number}> = ({x, y, text, sub, p, size = 120}) => {
	if (p <= 0) return null;
	const s = interpolate(p, [0, 0.7, 1], [1.7, 0.94, 1]);
	return (
		<div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, -50%) rotate(-6deg) scale(${s})`, opacity: clamp(p * 2.5), textAlign: 'center', color: C.stamp, fontFamily: FONT, fontWeight: 700}}>
			<div style={{fontSize: size, lineHeight: 1, padding: '6px 24px 12px', border: `8px solid ${C.stamp}`, borderRadius: 18, whiteSpace: 'nowrap', background: 'rgba(8,10,9,0.55)'}}>{text}</div>
			{sub && <div style={{fontSize: 20, marginTop: 10, textTransform: 'uppercase', letterSpacing: 1}}>{sub}</div>}
		</div>
	);
};
