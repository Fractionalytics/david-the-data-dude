// The whole Reel as one timeline, keyed to absolute frames, so each card's clip starts exactly where
// the previous one ended. Card compositions (Root.tsx) render a window of it.
// Layouts follow scripts/mock_final_frames.py, moved down to clear David's collar and shoulders in
// the recorded footage (2026-11-03 stills: collar ~y 870 at center, shoulders ~y 900 at the sides,
// lav mic at ~x 458, y 960, so titles start below y 990).
import React from 'react';
import {Easing, interpolate, interpolateColors} from 'remotion';
import {VIDEO} from '@kit/zones';
import {barlow} from '@kit/fonts';
import {pencil} from './fonts';

const WHITE = '#FFFFFF';
const ORANGE = '#F28C38';
const TEAL = '#2EC4B6';
const GRAY = '#B9B4AA';
const PENCIL = '#E4E1DA';
const INK = '#0B0B0B';

const tc = (s: string) => {
	const [m, ss, ff] = s.split(':').map(Number);
	return (m * 60 + ss) * 30 + ff;
};

// David lengthened card 8 by 5 frames after the Sheet was last updated (2026-11-03), so every
// later card starts 5 frames after its Sheet time.
const CARD8_EXTRA = 5;

// The Sheet's Start column (Original Script tab, 2026-11-03, after David's 13-frame cut in card 5).
export const START = {
	c1: tc('0:00:00'),
	c2: tc('0:02:10'),
	c3: tc('0:07:13'),
	c4: tc('0:11:05'),
	c5: tc('0:16:13'),
	c6: tc('0:20:21'),
	c7: tc('0:26:00'),
	c8: tc('0:30:00'),
	c9: tc('0:38:00') + CARD8_EXTRA,
	c10: tc('0:46:02') + CARD8_EXTRA,
	c11: tc('0:47:07') + CARD8_EXTRA,
	c12: tc('0:52:13') + CARD8_EXTRA,
	c13: tc('0:56:10') + CARD8_EXTRA,
	c14: tc('1:01:05') + CARD8_EXTRA,
	c15: tc('1:08:17') + CARD8_EXTRA,
	c16: tc('1:17:07') + CARD8_EXTRA,
	c17: tc('1:20:27') + CARD8_EXTRA,
	c18: tc('1:23:10') + CARD8_EXTRA,
};
// Card 18 "Finishes at 1:24:09" in the Sheet, plus card 8's extra frames; the Reel's last frame is that one.
export const END = tc('1:24:09') + CARD8_EXTRA + 1;

// Cues inside cards. Cards 2, 4 and 16 are David's; the rest are estimated from where the words fall in the
// script and the card's length, so they may need nudging against the audio.
const CUE = {
	big316: tc('0:03:13'), // David: "At 03:13, I want to show the big number"
	big642: START.c4 + 50, // David: 50 frames into card 4
	under50: START.c9 + 100, // est.: "under $50K a year"
	twice: START.c9 + 140, // est.: "more than twice the rate as the next level up"
	scatterOut: START.c11 + 60, // est.: "something called"
	eitcWords: START.c11 + 100, // est.: "the earned income tax credit"
	povertyBars: START.c14 + 110, // est.: "America's biggest anti-poverty programs"
	sixPoint8: START.c15 + 150, // est.: "kept 6.8 million people"
	oddsNumbers: START.c16 + 45, // David: the "1 in N" labels start 45 frames into card 16
};

// data/reel_bands.csv (scripts/reel_bands.py): odds for 2021 returns, in-person share of audits
// closed FY2023-25.
const BANDS = [
	{band: '<$50K', rate: 0.3755, oneIn: 266, share: 4.9},
	{band: '$50K–$200K', rate: 0.1557, oneIn: 642, share: 21.7},
	{band: '$200K–$500K', rate: 0.2195, oneIn: 456, share: 23.0},
	{band: '$500K–$1M', rate: 0.5981, oneIn: 167, share: 25.4},
	{band: '$1M–$5M', rate: 0.9421, oneIn: 106, share: 46.3},
	{band: '$5M–$10M', rate: 3.856, oneIn: 26, share: 85.3},
	{band: '$10M+', rate: 6.5854, oneIn: 15, share: 86.0},
];

// Census P60-287, Table B-7 (printed p. 51): people kept out of poverty, SPM, 2024, in millions.
const POVERTY = [
	{label: 'Social Security', value: 28.7, color: GRAY},
	{label: 'Earned Income and Child Tax Credits', value: 6.8, color: TEAL},
	{label: 'SNAP', value: 3.6, color: GRAY},
];

const ease = Easing.out(Easing.cubic);
const inOut = Easing.inOut(Easing.cubic);
const ramp = (f: number, a: number, b: number, easing = (t: number) => t) =>
	interpolate(f, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing});
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// Deterministic jitter, so every render and every card agrees.
const rand = (i: number, salt: number) => {
	const x = Math.sin(i * 12.9898 + salt * 78.233) * 43758.5453;
	return x - Math.floor(x);
};

const Label: React.FC<{x: number; y: number; size?: number; color?: string; anchor?: 'start' | 'middle' | 'end'; opacity?: number; children: React.ReactNode}> = ({
	x,
	y,
	size = 52,
	color = WHITE,
	anchor = 'start',
	opacity = 1,
	children,
}) => (
	<text x={x} y={y} fontFamily={barlow} fontWeight={800} fontSize={size} fill={color} textAnchor={anchor} dominantBaseline="middle" opacity={opacity}>
		{children}
	</text>
);

// ---------------------------------------------------------------- cards 1-4: one dot per return

const CX = 510;
const CY = 1265;
const BIG = 360;
const PULSE_PERIOD = 30;

const circlePoints = (n: number) =>
	Array.from({length: n}, (_, i) => {
		const r = BIG * Math.sqrt((i + 0.5) / n);
		const theta = i * 2.399963;
		return {x: CX + r * Math.cos(theta), y: CY + r * Math.sin(theta)};
	});

// The audited dot sits near the top right edge whatever n is, so the arrow stays off the white dots.
const pickIndex = (pts: {x: number; y: number}[]) => {
	let best = 0;
	let bestD = Infinity;
	pts.forEach((p, i) => {
		const d = (p.x - CX - 197) ** 2 + (p.y - CY + 240) ** 2;
		if (d < bestD) {
			bestD = d;
			best = i;
		}
	});
	return best;
};

const P316 = circlePoints(316);
const P642 = circlePoints(642);
const PICK316 = pickIndex(P316);
const PICK642 = pickIndex(P642);
// Each of the 316 dots moves to its nearest free 642-dot slot, so the move stays small; the rest are new.
const TO642 = (() => {
	const used = new Set([PICK642]);
	return P316.map((p, i) => {
		if (i === PICK316) return PICK642;
		let best = -1;
		let bestD = Infinity;
		P642.forEach((q, j) => {
			const d = (p.x - q.x) ** 2 + (p.y - q.y) ** 2;
			if (!used.has(j) && d < bestD) {
				bestD = d;
				best = j;
			}
		});
		used.add(best);
		return best;
	});
})();
const NEW642 = (() => {
	const taken = new Set(TO642);
	return P642.map((_, j) => j).filter((j) => !taken.has(j));
})();

const FLY = {spread: 14, duration: 18};
const HIGHLIGHT = {from: 34, to: 42};
const NOTE = {from: 44, to: 62};
const MORPH = {from: START.c4 + 4, to: START.c4 + 40};
const ARRIVE = START.c4 + 14;

// Dots stream in from off the left edge; leftmost targets leave first.
const flyIn = (i: number, p: {x: number; y: number}, f: number, t0: number, minX: number, spanX: number) => {
	const delay = t0 + ((p.x - minX) / spanX) * (FLY.spread - 4) + rand(i, 1) * 4;
	const t = ramp(f, delay, delay + FLY.duration, ease);
	const x0 = -40 - rand(i, 2) * 220;
	const y0 = p.y + (rand(i, 3) - 0.5) * 180;
	// A slight arc, so the stream flows rather than slides.
	return {x: x0 + (p.x - x0) * t, y: y0 + (p.y - y0) * t - Math.sin(t * Math.PI) * 40 * (rand(i, 4) - 0.5)};
};

const PencilNote: React.FC<{pick: {x: number; y: number}; ring: number; t: number}> = ({pick, ring, t}) => {
	const label = {x: 800, y: 905};
	const start = {x: 812, y: 948};
	const bend = {x: 830, y: 1015};
	const gap = Math.hypot(start.x - pick.x, start.y - pick.y);
	const end = {x: pick.x + ((start.x - pick.x) / gap) * (ring + 12), y: pick.y + ((start.y - pick.y) / gap) * (ring + 12)};
	const heading = Math.atan2(end.y - bend.y, end.x - bend.x);
	const heads = [-0.55, 0.55].map((side) => ({x: end.x - 30 * Math.cos(heading + side), y: end.y - 30 * Math.sin(heading + side)}));
	// Two slightly different passes read as pencil rather than a vector stroke.
	const passes = [0, 1].map((k) => {
		const j = (n: number) => (rand(n, k + 3) - 0.5) * 2;
		return {
			curve: `M ${start.x + j(1)} ${start.y + j(2)} Q ${bend.x + j(3)} ${bend.y + j(4)} ${end.x} ${end.y}`,
			heads: heads.map((h, i) => `M ${h.x + j(5 + i)} ${h.y + j(7 + i)} L ${end.x} ${end.y}`),
		};
	});
	const word = ramp(t, 0, 0.45);
	const arrow = ramp(t, 0.35, 0.85);
	const tips = ramp(t, 0.85, 1);
	return (
		<g>
			<clipPath id="audit-wipe">
				<rect x={label.x - 90} y={label.y - 60} width={180 * word} height={120} />
			</clipPath>
			<text x={label.x} y={label.y} fontFamily={pencil} fontWeight={600} fontSize={60} fill={PENCIL} textAnchor="middle" dominantBaseline="middle" clipPath="url(#audit-wipe)">
				Audit
			</text>
			{passes.map((p, k) => (
				<g key={k} stroke={PENCIL} strokeWidth={6} strokeLinecap="round" fill="none" opacity={0.85}>
					<path d={p.curve} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - arrow} />
					{p.heads.map((d, i) => (
						<path key={i} d={d} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - tips} />
					))}
				</g>
			))}
		</g>
	);
};

// "1 in N" in orange over the dots, on a semi-opaque scrim (David's note on card 2).
const BigNumber: React.FC<{text: string; o: number}> = ({text, o}) =>
	o <= 0 ? null : (
		<g opacity={o} transform={`translate(${CX} ${CY}) scale(${0.92 + 0.08 * o}) translate(${-CX} ${-CY})`}>
			<rect x={CX - 300} y={CY - 125} width={600} height={250} rx={36} fill="rgba(11, 11, 13, 0.72)" />
			<Label x={CX} y={CY + 6} size={190} color={ORANGE} anchor="middle">
				{text}
			</Label>
		</g>
	);

const Dots: React.FC<{f: number}> = ({f}) => {
	const out = 1 - ramp(f, START.c5, START.c5 + 12, ease);
	if (out <= 0) return null;
	const morph = ramp(f, MORPH.from, MORPH.to, inOut);
	const radius = lerp(12.5, 8.5, morph);
	const xs316 = P316.map((p) => p.x);
	const min316 = Math.min(...xs316);
	const span316 = Math.max(...xs316) - min316;
	const xs642 = P642.map((p) => p.x);
	const min642 = Math.min(...xs642);
	const span642 = Math.max(...xs642) - min642;

	const pos316 = (i: number) => {
		const a = flyIn(i, P316[i], f, 0, min316, span316);
		const b = P642[TO642[i]];
		return {x: lerp(a.x, b.x, morph), y: lerp(a.y, b.y, morph)};
	};

	const lit = ramp(f, HIGHLIGHT.from, HIGHLIGHT.to, ease);
	const dot = lerp(19, 17, morph);
	const ring = dot + 13;
	const phase = Math.max(0, f - HIGHLIGHT.to) / PULSE_PERIOD;
	const pulse = 0.5 - 0.5 * Math.cos(phase * 2 * Math.PI);
	const pick = pos316(PICK316);

	const big316 = ramp(f, CUE.big316, CUE.big316 + 8, ease) * (1 - ramp(f, START.c4, START.c4 + 8));
	const big642 = ramp(f, CUE.big642, CUE.big642 + 8, ease) * (1 - ramp(f, START.c5, START.c5 + 8));

	return (
		<g opacity={out} transform={`translate(${CX} ${CY}) scale(${0.85 + 0.15 * out}) translate(${-CX} ${-CY})`}>
			{P316.map((_, i) => {
				if (i === PICK316) return null;
				const p = pos316(i);
				return <circle key={`o${i}`} cx={p.x} cy={p.y} r={radius} fill={WHITE} />;
			})}
			{f >= ARRIVE &&
				NEW642.map((j) => {
					const p = flyIn(j + 1000, P642[j], f, ARRIVE, min642, span642);
					return <circle key={`n${j}`} cx={p.x} cy={p.y} r={8.5} fill={WHITE} />;
				})}
			<BigNumber text="1 in 316" o={big316} />
			<BigNumber text="1 in 642" o={big642} />
			{/* The audited dot is drawn last, so its pulsing ring sits over its neighbours. */}
			<circle cx={pick.x} cy={pick.y} r={ring * (1 + 0.25 * pulse)} fill="none" stroke={ORANGE} strokeWidth={6} opacity={lit * (1 - 0.6 * pulse)} />
			<circle cx={pick.x} cy={pick.y} r={lerp(radius, dot, lit)} fill={interpolateColors(lit, [0, 1], [WHITE, ORANGE])} />
			<PencilNote pick={pick} ring={ring * 1.25} t={ramp(f, NOTE.from, NOTE.to)} />
		</g>
	);
};

// ---------------------------------------------------------------- card 5: mail vs. in person

const SPLIT_BAR = {left: 120, right: 900, top: 1130, height: 150};

const MailBar: React.FC<{f: number}> = ({f}) => {
	const out = 1 - ramp(f, START.c6, START.c6 + 12);
	if (f < START.c5 || out <= 0) return null;
	const share = BANDS[1].share;
	const {left, right, top, height} = SPLIT_BAR;
	const grow = ramp(f, START.c5 + 8, START.c5 + 30, ease);
	const split = left + ((right - left) * share) / 100;
	const labels = ramp(f, START.c5 + 22, START.c5 + 36);
	const w = (right - left) * grow;
	return (
		<g opacity={out}>
			<clipPath id="mail-grow">
				<rect x={left} y={top} width={w} height={height} />
			</clipPath>
			<g clipPath="url(#mail-grow)">
				<rect x={left} y={top} width={split - left - 3} height={height} fill={ORANGE} />
				<rect x={split + 3} y={top} width={right - split - 3} height={height} fill={TEAL} />
			</g>
			<g opacity={ramp(f, START.c5 + 4, START.c5 + 16)}>
				<Label x={510} y={985} size={60} anchor="middle">
					$50K–$200K
				</Label>
			</g>
			<g opacity={labels}>
				<Label x={left} y={top - 50} size={72}>{`${Math.round(share)}%`}</Label>
				<Label x={right} y={top - 50} size={72} anchor="end">{`${Math.round(100 - share)}%`}</Label>
				<Label x={left} y={top + height + 45}>In person</Label>
				<Label x={right} y={top + height + 45} anchor="end">
					Mail
				</Label>
			</g>
		</g>
	);
};

// ---------------------------------------------------------------- cards 6-10: odds vs. in-person share

const PLOT = {left: 415, right: 890, top: 905, bottom: 1515};
const ODDS_MIN = 1 / 1000;
const ODDS_MAX = 1 / 10;
const yOf = (rate: number) => {
	const span = Math.log10(ODDS_MAX) - Math.log10(ODDS_MIN);
	return PLOT.bottom - ((Math.log10(rate) - Math.log10(ODDS_MIN)) / span) * (PLOT.bottom - PLOT.top);
};
const xOf = (share: number) => PLOT.left + (share / 100) * (PLOT.right - PLOT.left);
const NO_X = PLOT.left + 80;
const leftLabel = (share: number) => share > 60;

const Scatter: React.FC<{f: number}> = ({f}) => {
	if (f < START.c6) return null;
	const out = 1 - ramp(f, CUE.scatterOut, CUE.scatterOut + 20);
	if (out <= 0) return null;
	const yAxis = ramp(f, START.c6 + 6, START.c6 + 26, ease);
	const yTicks = ramp(f, START.c6 + 16, START.c6 + 30);
	const xAxis = ramp(f, START.c7, START.c7 + 20, ease);
	const xTicks = ramp(f, START.c7 + 10, START.c7 + 25);
	const slide = ramp(f, START.c7 + 15, START.c7 + 55, inOut);
	const base = BANDS[1];
	const y50200 = yOf(base.rate / 100);

	const point = (b: (typeof BANDS)[number], k: number) => {
		// Card 6: the $50K-$200K dot appears where the bar was; the higher bands rise out of it in turn.
		// Card 9: the under-$50K band is plotted last.
		let appear: number;
		let rise = 1;
		if (b.band === '<$50K') {
			appear = ramp(f, CUE.under50, CUE.under50 + 10, ease);
		} else if (k === 1) {
			appear = ramp(f, START.c6 + 10, START.c6 + 22);
		} else {
			const t0 = START.c6 + 30 + 12 * (k - 2);
			appear = ramp(f, t0, t0 + 6);
			rise = ramp(f, t0, t0 + 24, inOut);
		}
		const x = b.band === '<$50K' ? xOf(b.share) : lerp(NO_X, xOf(b.share), slide);
		const y = lerp(y50200, yOf(b.rate / 100), rise);
		return {x, y, appear};
	};

	const flashing = f >= START.c8 && f < START.c8 + 220;
	const flashOn = !flashing || Math.floor((f - START.c8) / 10) % 2 === 0;

	const low = point(BANDS[0], 0);
	const mid = point(BANDS[1], 1);
	const across = ramp(f, CUE.twice, CUE.twice + 18, inOut);
	const down = ramp(f, CUE.twice + 18, CUE.twice + 45, inOut);

	return (
		<g opacity={out}>
			{/* Axes */}
			<line x1={PLOT.left} y1={PLOT.bottom} x2={PLOT.left} y2={lerp(PLOT.bottom, PLOT.top, yAxis)} stroke={GRAY} strokeWidth={6} strokeLinecap="round" />
			<g opacity={yTicks}>
				{[1000, 100, 10].map((t) => (
					<Label key={t} x={PLOT.left - 20} y={yOf(1 / t)} color={GRAY} anchor="end">{`1 in ${t.toLocaleString('en-US')}`}</Label>
				))}
				<g transform={`translate(148 ${(PLOT.top + PLOT.bottom) / 2}) rotate(-90)`}>
					<Label x={0} y={0} color={GRAY} anchor="middle">
						Odds of Audit
					</Label>
				</g>
			</g>
			{xAxis > 0 && (
				<line x1={PLOT.left} y1={PLOT.bottom} x2={lerp(PLOT.left, PLOT.right, xAxis)} y2={PLOT.bottom} stroke={GRAY} strokeWidth={6} strokeLinecap="round" />
			)}
			<g opacity={xTicks}>
				<Label x={xOf(0)} y={PLOT.bottom + 45} color={GRAY} anchor="middle">
					0%
				</Label>
				<Label x={xOf(50)} y={PLOT.bottom + 45} color={GRAY} anchor="middle">
					50%
				</Label>
				<Label x={xOf(100)} y={PLOT.bottom + 45} color={GRAY} anchor="end">
					100%
				</Label>
				<Label x={PLOT.right} y={PLOT.bottom + 115} color={GRAY} anchor="end">
					Share In Person
				</Label>
			</g>

			{/* Card 9: how much higher the under-$50K odds are than the next band up. */}
			{across > 0 && (
				<line x1={mid.x} y1={mid.y} x2={lerp(mid.x, low.x, across)} y2={mid.y} stroke={GRAY} strokeWidth={6} strokeLinecap="round" strokeDasharray="0.1 16" />
			)}
			{down > 0 && (
				<line x1={low.x} y1={mid.y} x2={low.x} y2={lerp(mid.y, low.y, down)} stroke={WHITE} strokeWidth={7} strokeLinecap="round" strokeDasharray="0.1 15" />
			)}

			{BANDS.map((b, k) => {
				const p = point(b, k);
				if (p.appear <= 0) return null;
				const isLow = b.band === '<$50K';
				const isTop = b.band === '$10M+';
				// Labels that end up left of their dot swap sides halfway through the slide.
				const goesLeft = leftLabel(b.share) && !isLow;
				const swapped = goesLeft && slide >= 0.5;
				const labelO = goesLeft ? Math.abs(1 - 2 * slide) : 1;
				const dotO = isTop && !flashOn ? 0.15 : 1;
				return (
					<g key={b.band} opacity={p.appear}>
						{isTop && flashing && flashOn && <circle cx={p.x} cy={p.y} r={30} fill="none" stroke={TEAL} strokeWidth={6} />}
						<circle cx={p.x} cy={p.y} r={17 * (isLow ? lerp(1.6, 1, p.appear) : 1)} fill={isLow ? ORANGE : TEAL} opacity={dotO} />
						<Label x={p.x + (swapped ? -30 : 30)} y={p.y + 2} anchor={swapped ? 'end' : 'start'} opacity={labelO}>
							{b.band}
						</Label>
					</g>
				);
			})}
		</g>
	);
};

// ---------------------------------------------------------------- cards 11-13: the credit's name

const EitcWords: React.FC<{f: number}> = ({f}) => {
	const out = 1 - ramp(f, CUE.povertyBars, CUE.povertyBars + 12);
	if (f < CUE.eitcWords || out <= 0) return null;
	return (
		<g opacity={out}>
			{['Earned', 'Income', 'Tax', 'Credit'].map((word, i) => {
				const t = ramp(f, CUE.eitcWords + 10 * i, CUE.eitcWords + 10 * i + 10, ease);
				return (
					<g key={word} opacity={t} transform={`translate(0 ${(1 - t) * 30})`}>
						<Label x={510} y={985 + i * 190} size={130} anchor="middle">
							{word}
						</Label>
					</g>
				);
			})}
		</g>
	);
};

// ---------------------------------------------------------------- cards 14-15: people kept out of poverty

const POV = {left: 120, title: 1015, row0: 1110, rowGap: 200, barOffset: 50, barH: 85, longest: 580};
const ZOOM = {labelY: 1075, barY: 1130, barH: 190, width: 780, titleY: 1375};

const Poverty: React.FC<{f: number}> = ({f}) => {
	const out = 1 - ramp(f, START.c16, START.c16 + 12);
	if (f < CUE.povertyBars + 8 || out <= 0) return null;
	const zoom = ramp(f, START.c15 + 5, START.c15 + 40, inOut);
	const others = 1 - ramp(f, START.c15, START.c15 + 15);
	return (
		<g opacity={out}>
			<g opacity={ramp(f, CUE.povertyBars + 8, CUE.povertyBars + 20)}>
				<Label x={POV.left} y={lerp(POV.title, ZOOM.titleY, zoom)} color={GRAY}>
					People kept out of poverty, 2024
				</Label>
			</g>
			{POVERTY.map((p, i) => {
				const t0 = CUE.povertyBars + 12 + 10 * i;
				const grow = ramp(f, t0, t0 + 25, ease);
				const isCredit = i === 1;
				const top = POV.row0 + i * POV.rowGap;
				const width = (POV.longest * p.value) / POVERTY[0].value;
				const o = ramp(f, t0, t0 + 8) * (isCredit ? 1 : others);
				if (o <= 0) return null;
				const labelY = isCredit ? lerp(top, ZOOM.labelY, zoom) : top;
				const barY = isCredit ? lerp(top + POV.barOffset, ZOOM.barY, zoom) : top + POV.barOffset;
				const barH = isCredit ? lerp(POV.barH, ZOOM.barH, zoom) : POV.barH;
				const barW = isCredit ? lerp(width, ZOOM.width, zoom) : width;
				const six = ramp(f, CUE.sixPoint8, CUE.sixPoint8 + 10, ease);
				return (
					<g key={p.label} opacity={o}>
						<Label x={POV.left} y={labelY}>
							{p.label}
						</Label>
						<rect x={POV.left} y={barY} width={barW * grow} height={barH} fill={p.color} />
						<g opacity={isCredit ? 1 - zoom : 1}>
							<Label x={POV.left + width * grow + 18} y={barY + barH / 2 + 2} opacity={ramp(f, t0 + 18, t0 + 26)}>{`${p.value}M`}</Label>
						</g>
						{isCredit && six > 0 && (
							<g opacity={six}>
								<Label x={POV.left + ZOOM.width / 2} y={ZOOM.barY + ZOOM.barH / 2 + 4} size={96} color={INK} anchor="middle">
									6.8 million
								</Label>
							</g>
						)}
					</g>
				);
			})}
		</g>
	);
};

// ---------------------------------------------------------------- cards 16-18: odds for every band

const ODDS = {title: 1015, row0: 1100, rowGap: 90, barLeft: 420, longest: 280, barH: 58};

const OddsBars: React.FC<{f: number}> = ({f}) => {
	const t0 = START.c16 + 8;
	if (f < t0) return null;
	const topRate = Math.max(...BANDS.map((b) => b.rate));
	return (
		<g>
			<g opacity={ramp(f, t0, t0 + 12)}>
				<Label x={120} y={ODDS.title} color={GRAY}>
					Odds of an audit, 2021 returns
				</Label>
			</g>
			{BANDS.map((b, i) => {
				const s = t0 + 6 + 6 * i;
				const y = ODDS.row0 + i * ODDS.rowGap;
				const width = Math.max(6, (ODDS.longest * b.rate) / topRate) * ramp(f, s, s + 20, ease);
				return (
					<g key={b.band} opacity={ramp(f, s, s + 8)}>
						<Label x={120} y={y + 2}>
							{b.band}
						</Label>
						<rect x={ODDS.barLeft} y={y - ODDS.barH / 2} width={width} height={ODDS.barH} fill={b.band === '<$50K' ? ORANGE : TEAL} />
						<Label x={ODDS.barLeft + width + 16} y={y + 2} opacity={ramp(f, CUE.oddsNumbers + 6 * i, CUE.oddsNumbers + 6 * i + 8)}>{`1 in ${b.oneIn}`}</Label>
					</g>
				);
			})}
		</g>
	);
};

export const Reel: React.FC<{f: number}> = ({f}) => (
	<svg width={VIDEO.width} height={VIDEO.height} viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`} style={{position: 'absolute', inset: 0}}>
		<Dots f={f} />
		<MailBar f={f} />
		<Scatter f={f} />
		<EitcWords f={f} />
		<Poverty f={f} />
		<OddsBars f={f} />
	</svg>
);
