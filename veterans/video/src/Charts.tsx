// Animated data cards (2026-11-04), timed to the Sheet's Start column.
// Layout: everything sits on one semi-transparent olive scrim below David's lapel mic.
// The mic measures y 932-982 in his frame (1080x1920), so the scrim starts at 1010. It stops at 1700 (Instagram's
// username starts at 1722) and at x 900 (the button rail starts at 927). The scrim counts as content.
// Look: "Field Stencil" from docs/visual-options.html (Saira Stencil numbers, Barlow Condensed labels).
//
// Runs of back-to-back cards (2-3-4-5, 9-10-11-12) are one continuous scene: each card opens on the previous card's
// last frame and morphs from it, and the scrim stays up. The scrim fades in only where a run starts (cards 2, 9, 15)
// and out only where it ends (cards 5, 12, 15), because the next card has no chart.
//
// Cues inside a card are frame offsets from the card's Start. David gave only card Starts, so these are ESTIMATES
// from where each phrase falls in his script (about 10-15 frames a word). Replace them with his timecodes if needed.
import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {loadFont} from '@remotion/google-fonts/SairaStencil';
import {barlow} from '@kit/fonts';

const {fontFamily: stencil} = loadFont('normal', {weights: ['700']});

export const ZONE = {left: 120, right: 900, top: 1010, bottom: 1700};
const PAD = 40;
export const INNER = {left: ZONE.left + PAD, right: ZONE.right - PAD, top: ZONE.top + PAD, bottom: ZONE.bottom - PAD};
const MID = (ZONE.left + ZONE.right) / 2;

export const C = {
	scrim: 'rgba(30, 36, 22, 0.82)',
	ink: '#ECE5CF',
	dim: '#B9B597',
	track: '#4D5839',
	vets: '#D8C690', // USAA 2023 survey: veterans and service members
	civ: '#8DB6CF', // YouGov 2025 survey: US adults
	civDeep: '#5F8FAE',
	alert: '#E8833A', // the one thing to look at
};

// --- timing helpers ---
const EASE = Easing.bezier(0.33, 0, 0.2, 1);
/** Eased tween of frame f from a..b, mapping to v0..v1, clamped. */
const tw = (f: number, a: number, b: number, v0 = 0, v1 = 1) =>
	interpolate(f, [a, b], [v0, v1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE});
const mix = (c0: string, c1: string, t: number) => {
	const p = (c: string) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16));
	const [a, b] = [p(c0), p(c1)];
	return `rgb(${a.map((v, i) => Math.round(v + (b[i] - v) * t)).join(',')})`;
};
const pct = (v: number, approx = false) => `${approx ? '~' : ''}${Math.round(v)}%`;

// --- primitives ---
type TextProps = {x: number; y: number; size?: number; color?: string; anchor?: 'start' | 'end' | 'middle'; opacity?: number; children: React.ReactNode};
const Label: React.FC<TextProps> = ({x, y, size = 48, color = C.ink, anchor = 'start', opacity = 1, children}) => (
	<text x={x} y={y} fontFamily={barlow} fontWeight={700} fontSize={size} fill={color} textAnchor={anchor} opacity={opacity}>
		{children}
	</text>
);
const Num: React.FC<TextProps> = ({x, y, size = 64, color = C.ink, anchor = 'start', opacity = 1, children}) => (
	<text x={x} y={y} fontFamily={stencil} fontWeight={700} fontSize={size} fill={color} textAnchor={anchor} opacity={opacity}>
		{children}
	</text>
);

/** The scrim plus a full-frame SVG in frame coordinates (see docs/solutions/ui-bugs/remotion-svg-...). */
export const Frame: React.FC<{fadeIn?: boolean; fadeOut?: boolean; children: React.ReactNode}> = ({fadeIn, fadeOut, children}) => {
	const f = useCurrentFrame();
	const {durationInFrames: n} = useVideoConfig();
	const o = (fadeIn ? tw(f, 0, 10) : 1) * (fadeOut ? tw(f, n - 12, n - 1, 1, 0) : 1);
	return (
		<AbsoluteFill style={{opacity: o}}>
			<svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0}}>
				<rect x={ZONE.left} y={ZONE.top} width={ZONE.right - ZONE.left} height={ZONE.bottom - ZONE.top} fill={C.scrim} />
				{children}
			</svg>
		</AbsoluteFill>
	);
};

// A 0-100% bar: label above, track for the full 100%, filled segments, value at the right.
const BAR_W = 540;
const BAR_H = 72;
type Seg = {share: number; color: string};
const Bar: React.FC<{y: number; labels: {text: string; o: number}[]; segs: Seg[]; value: string; opacity?: number; valueOpacity?: number}> = ({
	y,
	labels,
	segs,
	value,
	opacity = 1,
	valueOpacity = 1,
}) => {
	let x = INNER.left;
	return (
		<g opacity={opacity}>
			{labels.map((l) => (
				<Label key={l.text} x={INNER.left} y={y - 18} opacity={l.o}>
					{l.text}
				</Label>
			))}
			<rect x={INNER.left} y={y} width={BAR_W} height={BAR_H} fill={C.track} />
			{segs.map((s, i) => {
				const w = BAR_W * Math.max(0, s.share);
				const el = <rect key={i} x={x} y={y} width={w} height={BAR_H} fill={s.color} />;
				x += w;
				return el;
			})}
			<Num x={INNER.right} y={y + BAR_H - 8} anchor="end" opacity={valueOpacity}>
				{value}
			</Num>
		</g>
	);
};

// ---------- Card 2: USAA 2023, "half" uncomfortable ----------
const C2 = {fill: [45, 75]}; // "about half" (estimate)
const Card02Body: React.FC<{f: number}> = ({f}) => {
	const s = tw(f, C2.fill[0], C2.fill[1], 0, 0.5);
	return (
		<Bar
			y={1320}
			labels={[{text: 'Veterans & troops, 2023', o: tw(f, 6, 16)}]}
			segs={[{share: s, color: C.vets}]}
			value={pct(s * 100, true)}
			opacity={tw(f, 4, 14)}
			valueOpacity={tw(f, C2.fill[0], C2.fill[0] + 6)}
		/>
	);
};
export const Card02: React.FC = () => (
	<Frame fadeIn>
		<Card02Body f={useCurrentFrame()} />
	</Frame>
);

// ---------- Card 3: by age, under 30 ~70%, 65+ 24% ----------
const C3 = {older: 110}; // "older veterans less so" (estimate)
const Card03Body: React.FC<{f: number}> = ({f}) => {
	const y1 = tw(f, 0, 18, 1320, 1210);
	const s1 = tw(f, 6, 30, 0.5, 0.7);
	const s2 = tw(f, C3.older + 6, C3.older + 30, 0, 0.24);
	return (
		<>
			<Bar
				y={y1}
				labels={[
					{text: 'Veterans & troops, 2023', o: tw(f, 0, 9, 1, 0)},
					{text: 'Under 30', o: tw(f, 9, 18)},
				]}
				segs={[{share: s1, color: C.vets}]}
				value={pct(s1 * 100, true)}
			/>
			<Bar
				y={1460}
				labels={[{text: '65 and older', o: 1}]}
				segs={[{share: s2, color: C.vets}]}
				value={pct(s2 * 100)}
				opacity={tw(f, C3.older, C3.older + 10)}
			/>
		</>
	);
};
export const Card03: React.FC = () => (
	<Frame>
		<Card03Body f={useCurrentFrame()} />
	</Frame>
);

// ---------- Card 4: YouGov 2025, US adults 53% = 22% definitely + 31% probably ----------
const C4 = {fill: [26, 56], definitely: 140, probably: 165}; // estimates
const Card04Body: React.FC<{f: number}> = ({f}) => {
	const y = tw(f, 0, 20, 1210, 1260);
	const drain = tw(f, 0, 16, 0.7, 0);
	const civ = tw(f, C4.fill[0], C4.fill[1], 0, 0.53);
	const deep = tw(f, C4.definitely, C4.definitely + 10); // the "definitely" part darkens
	const defShare = Math.min(civ, 0.22);
	const value = f < C4.fill[0] ? pct(drain * 100, true) : pct(civ * 100);
	return (
		<>
			<Bar
				y={y}
				labels={[
					{text: 'Under 30', o: tw(f, 0, 9, 1, 0)},
					{text: 'US adults, 2025', o: tw(f, 12, 22)},
				]}
				segs={[
					{share: drain, color: C.vets},
					{share: defShare, color: mix(C.civ, C.civDeep, deep)},
					{share: civ - defShare, color: C.civ},
				]}
				value={value}
				valueOpacity={f < C4.fill[0] ? tw(f, 0, 12, 1, 0) : tw(f, C4.fill[0], C4.fill[0] + 6)}
			/>
			{/* Card 3's 65+ bar leaves */}
			<Bar y={1460} labels={[{text: '65 and older', o: 1}]} segs={[{share: 0.24, color: C.vets}]} value="24%" opacity={tw(f, 0, 10, 1, 0)} />
			<g opacity={tw(f, C4.definitely, C4.definitely + 10)}>
				<rect x={INNER.left} y={1410} width={36} height={36} fill={C.civDeep} />
				<Label x={INNER.left + 52} y={1442} size={44}>
					22% definitely
				</Label>
			</g>
			<g opacity={tw(f, C4.probably, C4.probably + 10)}>
				<rect x={INNER.left} y={1480} width={36} height={36} fill={C.civ} />
				<Label x={INNER.left + 52} y={1512} size={44}>
					31% probably
				</Label>
			</g>
		</>
	);
};
export const Card04: React.FC = () => (
	<Frame>
		<Card04Body f={useCurrentFrame()} />
	</Frame>
);

// ---------- Card 5: the two surveys crossed as a mosaic ----------
// Different people, so the cells assume a random civilian meets a random veteran (independence).
// Card 4's bar unfolds into the mosaic's two columns, then the veterans' split cuts across and the overlap lights up.
const C5 = {morph: [0, 26], split: 80, highlight: 130}; // "half the civilians" / "half the veterans" / "not ... comfortable" (estimates)
const M = (() => {
	const px = INNER.left + 110;
	const pw = INNER.right - px;
	const py = 1200;
	const ph = INNER.bottom - py;
	return {px, pw, py, ph, cw: pw * 0.53, rh: ph * 0.5, gap: 6};
})();
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const Card05Body: React.FC<{f: number}> = ({f}) => {
	const t = tw(f, C5.morph[0], C5.morph[1]);
	const {px, pw, py, ph, cw, rh, gap} = M;
	// Card 4's bar: fill x 160..446, track 446..700, y 1260..1332.
	const barFillW = BAR_W * 0.53;
	const L = {x: lerp(INNER.left, px, t), y: lerp(1260, py, t), w: lerp(barFillW, cw - gap / 2, t), h: lerp(BAR_H, ph, t)};
	const R = {x: lerp(INNER.left + barFillW, px + cw + gap / 2, t), y: L.y, w: lerp(BAR_W - barFillW, pw - cw - gap / 2, t), h: L.h};
	const deepFade = tw(f, 0, 12, 1, 0); // card 4's darker "definitely" segment blends away
	const split = tw(f, C5.split, C5.split + 16); // the veterans' line sweeps across
	const hi = tw(f, C5.highlight, C5.highlight + 12);
	const old = tw(f, 0, 10, 1, 0);
	return (
		<>
			{/* card 4's labels leave */}
			<g opacity={old}>
				<Label x={INNER.left} y={1242}>
					US adults, 2025
				</Label>
				<Num x={INNER.right} y={1260 + BAR_H - 8} anchor="end">
					53%
				</Num>
				<rect x={INNER.left} y={1410} width={36} height={36} fill={C.civDeep} />
				<Label x={INNER.left + 52} y={1442} size={44}>
					22% definitely
				</Label>
				<rect x={INNER.left} y={1480} width={36} height={36} fill={C.civ} />
				<Label x={INNER.left + 52} y={1512} size={44}>
					31% probably
				</Label>
			</g>
			{/* columns: would thank (blue) vs. not or unsure (track) */}
			<rect x={L.x} y={L.y} width={L.w} height={L.h} fill={mix(C.civ, C.track, hi)} />
			<rect x={L.x} y={L.y} width={(L.w * 0.22) / 0.53} height={L.h} fill={C.civDeep} opacity={deepFade} />
			<rect x={R.x} y={R.y} width={R.w} height={R.h} fill={C.track} />
			{/* the overlap cell */}
			<rect x={px} y={py} width={cw - gap / 2} height={rh - gap / 2} fill={C.alert} opacity={hi} />
			{/* the veterans' split: a scrim-colored gap sweeping left to right */}
			<rect x={px} y={py + rh - gap / 2} width={pw * split} height={gap} fill="rgb(37,43,28)" />
			<g opacity={tw(f, C5.morph[1] - 8, C5.morph[1] + 6)}>
				<Label x={px} y={1080} size={40} color={C.civ}>
					CIVILIANS
				</Label>
				<Num x={px} y={1150} size={52} color={C.civ}>
					53%
				</Num>
				<Label x={px + 112} y={1150} size={40}>
					would thank
				</Label>
				<Num x={px + cw + gap} y={1150} size={52} color={C.dim}>
					47%
				</Num>
				<Label x={px + cw + gap + 112} y={1150} size={40} color={C.dim}>
					no / unsure
				</Label>
			</g>
			<g opacity={tw(f, C5.split + 4, C5.split + 16)}>
				<g transform={`translate(${INNER.left + 30}, ${py + ph / 2}) rotate(-90)`}>
					<Label x={0} y={0} size={40} color={C.vets} anchor="middle">
						VETERANS
					</Label>
				</g>
				<g transform={`translate(${INNER.left + 88}, ${py + rh / 2}) rotate(-90)`}>
					<Label x={0} y={0} size={36} anchor="middle">
						uncomfortable
					</Label>
				</g>
				<g transform={`translate(${INNER.left + 88}, ${py + rh + rh / 2}) rotate(-90)`}>
					<Label x={0} y={0} size={36} color={C.dim} anchor="middle">
						not
					</Label>
				</g>
			</g>
		</>
	);
};
export const Card05: React.FC = () => (
	<Frame fadeOut>
		<Card05Body f={useCurrentFrame()} />
	</Frame>
);

// ---------- Cards 9 and 10: 17.2M living veterans, about 6% of US adults ----------
const C9 = {big: [8, 44], six: 135}; // "About 6% of US adults" (estimate)
const BigNumbersBody: React.FC<{f: number; opacity?: number}> = ({f, opacity = 1}) => {
	const m = tw(f, C9.big[0], C9.big[1], 0, 17.2);
	const six = tw(f, C9.six, C9.six + 20, 0, 6);
	return (
		<g opacity={opacity}>
			<Num x={MID} y={1235} size={190} anchor="middle" color={C.vets} opacity={tw(f, C9.big[0], C9.big[0] + 6)}>
				{m.toFixed(1)}M
			</Num>
			<Label x={MID} y={1300} size={52} anchor="middle" opacity={tw(f, 22, 34)}>
				living US veterans
			</Label>
			<Num x={MID} y={1550} size={190} anchor="middle" color={C.vets} opacity={tw(f, C9.six, C9.six + 6)}>
				{Math.round(six)}%
			</Num>
			<Label x={MID} y={1615} size={52} anchor="middle" opacity={tw(f, C9.six + 10, C9.six + 22)}>
				of US adults
			</Label>
		</g>
	);
};
const DONE = 10_000; // a frame past every cue: the card's end state
export const Card09: React.FC = () => (
	<Frame fadeIn>
		<BigNumbersBody f={useCurrentFrame()} />
	</Frame>
);
export const Card10: React.FC = () => (
	<Frame>
		<BigNumbersBody f={DONE} />
	</Frame>
);

// ---------- Card 11: Pew 2019. Deployed 61%, married while on active duty 47%, combat zone 36% ----------
// "Personal hardship" has no clean measure, so it has no bar.
const C11 = [35, 65, 228]; // "deployments overseas" / "separation from loved ones" / "combat conditions" (estimates)
const C11_BARS = [
	{y: 1150, label: 'Deployed at least once', share: 0.61, color: C.vets},
	{y: 1360, label: 'Married while on active duty', share: 0.47, color: C.vets},
	{y: 1570, label: 'Served in a combat zone', share: 0.36, color: C.alert},
];
const Card11Body: React.FC<{f: number}> = ({f}) => (
	<>
		{C11_BARS.map((b, i) => {
			const s = tw(f, C11[i] + 6, C11[i] + 28, 0, b.share);
			return <Bar key={b.label} y={b.y} labels={[{text: b.label, o: 1}]} segs={[{share: s, color: b.color}]} value={pct(s * 100)} opacity={tw(f, C11[i], C11[i] + 10)} />;
		})}
	</>
);
export const Card11: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<Frame>
			{/* card 10's numbers lift away as the first bar arrives */}
			<g transform={`translate(0, ${tw(f, 0, 16, 0, -40)})`}>
				<BigNumbersBody f={DONE} opacity={tw(f, 0, 14, 1, 0)} />
			</g>
			<Card11Body f={f} />
		</Frame>
	);
};

// ---------- Card 12: VA FY2025, the six most common service-connected conditions ----------
const CONDITIONS = [
	{label: 'Tinnitus', v: 3.583295},
	{label: 'Knee, limited motion', v: 2.312985},
	{label: 'Sciatic nerve', v: 2.026583},
	{label: 'Back or neck strain', v: 1.791869},
	{label: 'PTSD', v: 1.760497, hi: true},
	{label: 'Hearing loss', v: 1.690837},
];
const Card12Body: React.FC<{f: number}> = ({f}) => {
	const top = 1110;
	const row = 92;
	const max = 3.583295;
	const bw = 520;
	return (
		<>
			<Label x={INNER.left} y={1088} size={40} color={C.dim} opacity={tw(f, 6, 16)}>
				Veterans compensated by VA
			</Label>
			{CONDITIONS.map((c, i) => {
				const a = 8 + i * 6;
				const g = tw(f, a, a + 18);
				const y = top + i * row;
				const color = c.hi ? C.alert : C.vets;
				const w = ((bw * c.v) / max) * g;
				return (
					<g key={c.label} opacity={tw(f, a, a + 8)}>
						<Label x={INNER.left} y={y + 40} size={40} color={c.hi ? C.alert : C.ink}>
							{c.label}
						</Label>
						<rect x={INNER.left} y={y + 50} width={w} height={32} fill={color} />
						<Num x={INNER.left + w + 14} y={y + 80} size={40} color={c.hi ? C.alert : C.ink}>
							{(c.v * g).toFixed(2)}M
						</Num>
					</g>
				);
			})}
		</>
	);
};
export const Card12: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<Frame fadeOut>
			{/* card 11's bars clear out as the conditions grow in */}
			<g opacity={tw(f, 0, 10, 1, 0)}>
				<Card11Body f={DONE} />
			</g>
			<Card12Body f={f} />
		</Frame>
	);
};

// ---------- Card 15: the headline number alone ----------
export const Card15: React.FC = () => {
	const f = useCurrentFrame();
	const s = tw(f, 4, 20, 1.15, 1);
	return (
		<Frame fadeIn fadeOut>
			<g transform={`translate(${MID}, 1340) scale(${s}) translate(${-MID}, -1340)`} opacity={tw(f, 4, 14)}>
				<Num x={MID} y={1420} size={230} anchor="middle" color={C.vets}>
					17.2M
				</Num>
			</g>
		</Frame>
	);
};
