// Reel 2's lab-report kit (David picked it 2026-11-18 from charts/mockups/reel2/card-02_lab.png): a
// toxicology printout on off-white graph paper, monospace type, thin black rules, the headline ratio as a
// red rubber stamp. US red / Europe blue carry over from Reels 1 and 3.
// Layout: same as Reel 3. David's head tops are at y 1017 (glasses) and 1026 (cap) in the Reel 2 stills,
// the caption runs about y 937-1017, and the plate takes x 120-960, y 260-900.
// Font: Consolas, the Windows system monospace face the mockups used (renders on this machine only).
import React from 'react';
import {Easing, interpolate} from 'remotion';

export const BAND = {left: 120, right: 960, top: 260, bottom: 900};
export const W = BAND.right - BAND.left;
export const H = BAND.bottom - BAND.top;
export const FONT = 'Consolas, "Courier New", monospace';

export const C = {
	paper: '#F5F2EA',
	grid: '#E4DFD3',
	ink: '#1A1C1E',
	muted: '#5E6368',
	faint: '#9AA0A6',
	us: '#B3261E',
	eu: '#1F4E9C',
};

export const clamp = (v: number) => Math.max(0, Math.min(1, v));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const ease = Easing.inOut(Easing.cubic);
// Progress 0-1 between frames a and b.
export const prog = (g: number, a: number, b: number, e = ease) =>
	interpolate(g, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});

const PAD = 32;
// Title sizing: one line at up to 44px if it fits the plate, else two lines at 40px. Monospace, so width is
// about 0.55 em per character.
export const titleLayout = (text: string) => {
	const fit = (W - 2 * PAD) / (text.length * 0.55);
	if (fit >= 36) return {size: Math.min(44, fit), lines: 1};
	return {size: 40, lines: 2};
};
// Where a chart can start below the header (kicker + title + optional subtitle + rule).
export const headerBottom = (title: string, sub?: string) => {
	const {size, lines} = titleLayout(title);
	return 58 + size * 1.1 * lines + (sub ? 34 : 0) + 18;
};

// The paper: graph-paper grid, a thin black border, the kicker (what's measured; ours), David's title and
// subtitle, a rule, and a dotted rule over the source line. `headP` fades the header and footer (card 1 has
// none). An empty title leaves the paper bare.
export const Plate: React.FC<{title: string; kicker: string; source: string; sub?: string; headP?: number; children: React.ReactNode}> = ({title, kicker, source, sub, headP = 1, children}) => {
	const hb = headerBottom(title, sub);
	const {size, lines} = titleLayout(title);
	if (!title) headP = 0;
	return (
		<div style={{position: 'absolute', left: BAND.left, top: BAND.top, width: W, height: H, background: C.paper, boxShadow: `inset 0 0 0 3px ${C.ink}`, fontFamily: FONT, color: C.ink, overflow: 'hidden'}}>
			<svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
				{Array.from({length: Math.floor(W / 20)}, (_, i) => (
					<line key={`x${i}`} x1={(i + 1) * 20} x2={(i + 1) * 20} y1={3} y2={H - 3} stroke={C.grid} strokeWidth={1} />
				))}
				{Array.from({length: Math.floor(H / 20)}, (_, i) => (
					<line key={`y${i}`} x1={3} x2={W - 3} y1={(i + 1) * 20} y2={(i + 1) * 20} stroke={C.grid} strokeWidth={1} />
				))}
				<g opacity={headP}>
					<line x1={28} x2={W - 28} y1={hb - 8} y2={hb - 8} stroke={C.ink} strokeWidth={2.5} />
					<line x1={28} x2={W - 28} y1={H - 52} y2={H - 52} stroke={C.ink} strokeWidth={1.5} strokeDasharray="2 3" />
				</g>
			</svg>
			<div style={{opacity: headP}}>
				<div style={{position: 'absolute', left: PAD, top: 22, fontSize: 22, color: C.muted, textTransform: 'uppercase', letterSpacing: 1}}>{kicker}</div>
				<div style={{position: 'absolute', left: PAD, right: PAD, top: 52, fontSize: size, fontWeight: 700, lineHeight: 1.1}}>{title}</div>
				{sub && <div style={{position: 'absolute', left: PAD, right: PAD, top: 52 + size * 1.1 * lines + 4, fontSize: Math.min(24, (W - 2 * PAD) / (sub.length * 0.55)), color: C.ink, whiteSpace: 'nowrap'}}>{sub}</div>}
				<div style={{position: 'absolute', left: PAD, right: PAD, top: H - 38, fontSize: 18, color: C.muted, textTransform: 'uppercase', letterSpacing: 0.5, whiteSpace: 'nowrap'}}>{source}</div>
			</div>
			{children}
		</div>
	);
};

export const Svg: React.FC<{children: React.ReactNode}> = ({children}) => (
	<svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', left: 0, top: 0}}>
		{children}
	</svg>
);

export const T: React.FC<React.SVGProps<SVGTextElement> & {size?: number; weight?: number}> = ({size = 40, weight = 700, children, ...rest}) => (
	<text fontFamily={FONT} fontSize={size} fontWeight={weight} fill={C.ink} {...rest}>
		{children}
	</text>
);

// The rubber stamp: a red rounded box, tilted, that lands from slightly too big (p 0-1).
export const Stamp: React.FC<{x: number; y: number; text: string; sub?: string; p: number; size?: number; nowrap?: boolean}> = ({x, y, text, sub, p, size = 110, nowrap = false}) => {
	if (p <= 0) return null;
	const s = interpolate(p, [0, 0.7, 1], [1.7, 0.94, 1]);
	return (
		<div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, -50%) rotate(-6deg) scale(${s})`, opacity: clamp(p * 2.5), textAlign: 'center', color: C.us, fontFamily: FONT, fontWeight: 700}}>
			<div style={{fontSize: size, lineHeight: 1, padding: '6px 22px 10px', border: `7px solid ${C.us}`, borderRadius: 18, whiteSpace: nowrap ? 'nowrap' : undefined}}>{text}</div>
			{sub && <div style={{fontSize: 24, marginTop: 10, textTransform: 'uppercase', letterSpacing: 1}}>{sub}</div>}
		</div>
	);
};
