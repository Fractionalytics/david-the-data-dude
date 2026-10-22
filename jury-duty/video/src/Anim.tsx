// Animated Sankey for Jury Duty, one composition per storyboard card (Script v2 tab).
// Look (David, 2026-10-22, option B): fully transparent over his black shirt, teal for people still
// in the funnel, warm gray for people who drop out, gold only for the takeaway (14 on 4+ day trials);
// Barlow Condensed for numbers, Inter for labels. Laid out in ZONES_HEAD_TOP.chart.
// Each card starts from the previous card's end state, so the clips cut together seamlessly.
import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {loadFont as loadInter} from '@remotion/google-fonts/Inter';
import {loadFont as loadBarlow} from '@remotion/google-fonts/BarlowCondensed';
import {VIDEO, ZONES_HEAD_TOP} from '@kit/zones';
import {PATH} from './funnel';

const inter = loadInter('normal', {weights: ['400', '700'], subsets: ['latin']}).fontFamily;
const barlow = loadBarlow('normal', {weights: ['700', '800'], subsets: ['latin']}).fontFamily;

export const COLOR = {stay: '#2EC4B6', out: '#B9B4AA', key: '#F4C542'};
const DAY_FILLS = ['#A8EAE3', '#6FD9CE', '#2EC4B6', COLOR.key];

const Z = ZONES_HEAD_TOP.chart;
const CX = (Z.left + Z.right) / 2;
const W = 700;
const BAR = 52;
const PARENT_Y = Z.top + 250;
const CHILD_Y = Z.top + 560;
const ease = Easing.bezier(0.4, 0, 0.2, 1);
const t = (f: number, a: number, b: number) => interpolate(f, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
const mix = (p: number, a: number, b: number) => a + (b - a) * p;
const fmt = (n: number) => Math.round(n).toLocaleString('en-US');

type Rect = {x0: number; w: number};
type Kind = 'stay' | 'out' | 'days';
type Child = {value: number; label: string; kind: Kind};

// --- text ---------------------------------------------------------------------------------------
const Num: React.FC<{x: number; y: number; size: number; fill?: string; opacity?: number; anchor?: 'start' | 'middle' | 'end'; children: React.ReactNode}> = ({x, y, size, fill = 'white', opacity = 1, anchor = 'middle', children}) => (
	<text x={x} y={y} fontFamily={barlow} fontWeight={800} fontSize={size} textAnchor={anchor} fill={fill} opacity={opacity} stroke="rgba(0,0,0,0.6)" strokeWidth={size / 10} paintOrder="stroke">
		{children}
	</text>
);
const Label: React.FC<{x: number; y: number; size?: number; fill?: string; opacity?: number; weight?: number; anchor?: 'start' | 'middle' | 'end'; children: React.ReactNode}> = ({x, y, size = 28, fill = 'white', opacity = 1, weight = 400, anchor = 'middle', children}) => (
	<text x={x} y={y} fontFamily={inter} fontWeight={weight} fontSize={size} textAnchor={anchor} fill={fill} opacity={opacity} stroke="rgba(0,0,0,0.6)" strokeWidth={size / 9} paintOrder="stroke">
		{children}
	</text>
);

// 1,000 › 449 › 247 › 155 › 48 › 14 along the top, numbers only (David, 2026-10-22: the labels under them
// were too small to read). The last chip is the current parent. Six slots are reserved so nothing shifts
// when the 14 arrives: `final` brings it in, in gold, at frame `at` (card 11, on "4+ day trial").
const CRUMB_SLOTS = PATH.length + 1;
const CRUMB_Y = Z.top + 78;
const Breadcrumb: React.FC<{upto: number; f: number; final?: {value: number; at: number}}> = ({upto, f, final}) => {
	const w = (Z.right - Z.left - 40) / CRUMB_SLOTS;
	const xAt = (i: number) => Z.left + 20 + w * i + w / 2;
	const fin = final ? t(f, final.at, final.at + 12) : 0;
	return (
		<g>
			{PATH.slice(0, upto + 1).map((n, i) => {
				const isNew = i === upto;
				const o = isNew ? t(f, 10, 25) : 0.55;
				return (
					<g key={n.value} opacity={o}>
						<Num x={xAt(i)} y={CRUMB_Y} size={52}>{fmt(n.value)}</Num>
						{(i < upto || (isNew && fin > 0)) && (
							<Label x={xAt(i) + w / 2} y={CRUMB_Y - 4} size={30} opacity={i < upto ? 1 : fin / o}>›</Label>
						)}
					</g>
				);
			})}
			{final && fin > 0 && (
				<Num x={xAt(upto + 1)} y={CRUMB_Y} size={52} fill={COLOR.key} opacity={fin}>{fmt(final.value)}</Num>
			)}
		</g>
	);
};

// A vertical Sankey ribbon from a source span (bottom of a bar at y0) to a target span (top of a bar at y1).
const ribbon = (s0: number, s1: number, d0: number, d1: number, y0: number, y1: number) => {
	const m = (y0 + y1) / 2;
	return `M${s0} ${y0} C${s0} ${m} ${d0} ${m} ${d0} ${y1} L${d1} ${y1} C${d1} ${m} ${s1} ${m} ${s1} ${y0} Z`;
};

const wrap = (s: string): string[] => {
	if (s.length <= 18) return [s];
	const i = s.indexOf(', ') > 0 ? s.indexOf(', ') + 1 : s.lastIndexOf(' ', 18);
	return [s.slice(0, i).trim(), s.slice(i).trim()];
};

// Children laid out under a full-width parent: widths proportional, centered, with gaps.
export const layoutChildren = (parent: number, kids: Child[]) => {
	const gap = kids.length > 2 ? 20 : 40;
	const span = W + gap * (kids.length - 1);
	let x = CX - span / 2;
	let p = CX - W / 2;
	return kids.map((c) => {
		const w = (W * c.value) / parent;
		const r = {c, x0: x, w, p0: p};
		x += w + gap;
		p += w;
		return r;
	});
};

// --- one split: parent (zoomed in from the previous card's child) -> children ------------------------
// `cues`: optional frame (within the card) at which each child rolls out, one at a time, as David names it.
// Without cues, all children roll out together right after the zoom.
// `compare`: optional bars under the Sankey showing the sworn as a share of an earlier stage, each from
// its cue frame until the next one (card 9: 48 of 247 reported, then 48 of 1,000 summoned).
export type Compare = {at: number; part: number; total: number; label: string};

export const SplitCard: React.FC<{parent: {value: number; label: string}; kids: Child[]; from?: Rect; upto: number; cues?: number[]; compare?: Compare[]; crumbFinal?: {value: number; at: number}}> = ({
	parent,
	kids,
	from,
	upto,
	cues,
	compare = [],
	crumbFinal,
}) => {
	const f = useCurrentFrame();
	const zoom = t(f, 0, 20);
	const px = from ? mix(zoom, from.x0, CX - W / 2) : CX - W / 2;
	const pw = from ? mix(zoom, from.w, W) : W * t(f, 0, 20);
	const py = from ? mix(zoom, CHILD_Y, PARENT_Y) : PARENT_Y;
	const lay = layoutChildren(parent.value, kids);
	const yA = PARENT_Y + BAR;
	const start = (i: number) => (cues ? cues[i] : 25);
	return (
		<AbsoluteFill>
			<svg width={VIDEO.width} height={VIDEO.height} viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`}>
				<defs>
					{lay.map((_, i) => (
						<clipPath key={i} id={`grow-${i}`}>
							<rect x={0} y={yA} width={VIDEO.width} height={(CHILD_Y - yA) * t(f, start(i), start(i) + 30)} />
						</clipPath>
					))}
				</defs>
				<Breadcrumb upto={upto} f={f} final={crumbFinal} />
				<Num x={CX} y={PARENT_Y - 52} size={84} opacity={t(f, 10, 25)}>{fmt(parent.value)}</Num>
				<Label x={CX} y={PARENT_Y - 16} opacity={t(f, 10, 25)}>{parent.label}</Label>
				<rect x={px} y={py} width={pw} height={BAR} rx={6} fill={COLOR.stay} />
				{lay.map((k, i) => (
					<g key={i} clipPath={`url(#grow-${i})`}>
						<path d={ribbon(k.p0, k.p0 + k.w, k.x0, k.x0 + k.w, yA, CHILD_Y)} fill={k.c.kind === 'days' ? DAY_FILLS[i] : COLOR[k.c.kind]} opacity={k.c.kind === 'out' ? 0.3 : 0.45} />
					</g>
				))}
				{lay.map((k, i) => {
					const s = start(i);
					const fill = k.c.kind === 'days' ? DAY_FILLS[i] : COLOR[k.c.kind];
					const mid = k.x0 + k.w / 2;
					const key = k.c.kind === 'days' && i === lay.length - 1;
					return (
						<g key={`c${i}`} opacity={t(f, s + 23, s + 33)}>
							<rect x={k.x0} y={CHILD_Y} width={k.w} height={BAR} rx={6} fill={fill} />
							<Num x={mid} y={CHILD_Y + BAR + 84} size={key ? 96 : 78} fill={key ? COLOR.key : 'white'}>{fmt(k.c.value * t(f, s + 23, s + 50))}</Num>
							{wrap(k.c.label).map((l, j) => (
								<Label key={j} x={mid} y={CHILD_Y + BAR + 124 + j * 34} opacity={t(f, s + 33, s + 47)}>{l}</Label>
							))}
						</g>
					);
				})}
				{compare.map((c, i) => {
					const end = compare[i + 1]?.at ?? 1e6; // last bar stays to the end of the card
					const o = Math.min(t(f, c.at, c.at + 12), 1 - t(f, end, end + 8));
					if (o <= 0) return null;
					const y = CHILD_Y + 290;
					const partW = (W * c.part) / c.total;
					return (
						<g key={i} opacity={o}>
							<rect x={CX - W / 2} y={y} width={W} height={BAR} rx={6} fill={COLOR.out} opacity={0.35} />
							<rect x={CX - W / 2} y={y} width={partW * t(f, c.at + 6, c.at + 24)} height={BAR} rx={6} fill={COLOR.stay} />
							<Num x={CX - W / 2} y={y - 18} size={64} anchor="start">
								{fmt(c.part)}
								<tspan fontFamily={inter} fontWeight={400} fontSize={40} fill="white">{` of ${fmt(c.total)} ${c.label}`}</tspan>
							</Num>
						</g>
					);
				})}
			</svg>
		</AbsoluteFill>
	);
};

// --- card 6: 449 -> 247 + 202, and the 202 flows over to join the 551 as 753 -------------------------
export const MergeCard: React.FC<{from449: Rect; from551: Rect}> = ({from449, from551}) => {
	const f = useCurrentFrame();
	const up = t(f, 0, 20);
	const y = mix(up, CHILD_Y, PARENT_Y);
	const k = from449.w / 449; // keep card 5's scale so the bars don't jump
	const b247 = {x0: CX - (1000 * k + 60) / 2, w: 247 * k};
	const b753 = {x0: b247.x0 + b247.w + 60, w: 753 * k};
	const yA = PARENT_Y + BAR;
	const grow = t(f, 25, 60);
	const show = t(f, 55, 65);
	const merge = t(f, 65, 100);
	return (
		<AbsoluteFill>
			<svg width={VIDEO.width} height={VIDEO.height} viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`}>
				<defs>
					<clipPath id="grow6">
						<rect x={0} y={yA} width={VIDEO.width} height={(CHILD_Y - yA) * grow} />
					</clipPath>
				</defs>
				<Breadcrumb upto={1} f={f} />
				{/* the two bars from card 5, moved up into the parent row */}
				<rect x={from449.x0} y={y} width={from449.w} height={BAR} rx={6} fill={COLOR.stay} />
				<rect x={from551.x0} y={y} width={from551.w} height={BAR} rx={6} fill={COLOR.out} />
				<Num x={from449.x0 + from449.w / 2} y={y - 52} size={72} opacity={up}>449</Num>
				<Label x={from449.x0 + from449.w / 2} y={y - 16} opacity={up}>eligible</Label>
				<Num x={from551.x0 + from551.w / 2} y={y - 52} size={72} fill={COLOR.out} opacity={up}>551</Num>
				<Label x={from551.x0 + from551.w / 2} y={y - 16} opacity={up}>postponed, no reply…</Label>
				<g clipPath="url(#grow6)">
					<path d={ribbon(from449.x0, from449.x0 + 247 * k, b247.x0, b247.x0 + b247.w, yA, CHILD_Y)} fill={COLOR.stay} opacity={0.45} />
					<path d={ribbon(from449.x0 + 247 * k, from449.x0 + from449.w, b753.x0, b753.x0 + 202 * k, yA, CHILD_Y)} fill={COLOR.out} opacity={0.75} />
					<path d={ribbon(from551.x0, from551.x0 + from551.w, b753.x0 + 202 * k, b753.x0 + b753.w, yA, CHILD_Y)} fill={COLOR.out} opacity={0.3} />
				</g>
				<Label x={from449.x0 + from449.w + 70} y={(yA + CHILD_Y) / 2 + 10} size={30} weight={700} fill="white" opacity={t(f, 35, 50) * (1 - merge * 0.4)}>
					202 called off
				</Label>
				<g opacity={show}>
					<rect x={b247.x0} y={CHILD_Y} width={b247.w} height={BAR} rx={6} fill={COLOR.stay} />
					<rect x={b753.x0} y={CHILD_Y} width={b753.w} height={BAR} rx={6} fill={COLOR.out} />
					<Num x={b247.x0 + b247.w / 2} y={CHILD_Y + BAR + 84} size={78}>{fmt(247 * t(f, 55, 80))}</Num>
					<Label x={b247.x0 + b247.w / 2} y={CHILD_Y + BAR + 124} opacity={t(f, 60, 75)}>reported</Label>
					{/* 753 counts up from the 551 as the 202 land, then gets the emphasis */}
					<Num x={b753.x0 + b753.w / 2} y={CHILD_Y + BAR + 104} size={mix(t(f, 95, 110), 96, 120)}>{fmt(mix(merge, 551, 753))}</Num>
					<Label x={b753.x0 + b753.w / 2} y={CHILD_Y + BAR + 152} size={32} weight={700} opacity={t(f, 95, 110)}>never come to the courthouse</Label>
				</g>
			</svg>
		</AbsoluteFill>
	);
};

// --- card 1 (and card 15): the whole funnel at true scale, 1,000 down to the 14 ------------------------
// `onScreen` is the storyboard's On-Screen Text for the card, word for word.
export const FullFunnel: React.FC<{onScreen: string; hold?: boolean}> = ({onScreen, hold = false}) => {
	const frame = useCurrentFrame();
	const f = hold ? 9999 : frame;
	const rows = [...PATH, {value: 14, label: '4+ days on trial', kind: 'days' as const}];
	const scale = 0.7;
	const x0 = Z.left + 40;
	const top = Z.top + 175;
	const gapY = 145;
	const h = 30;
	const step = 14; // frames between rows: the whole funnel lands in ~3 seconds
	return (
		<AbsoluteFill>
			<svg width={VIDEO.width} height={VIDEO.height} viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`}>
				<Label x={CX} y={Z.top + 62} size={46} weight={700} fill={COLOR.key} opacity={t(f, rows.length * step + 10, rows.length * step + 25)}>
					{onScreen}
				</Label>
				{rows.map((r, i) => {
					const y = top + i * gapY;
					const a = i * step;
					const next = rows[i + 1];
					const isKey = i === rows.length - 1;
					const keepW = (next ? next.value : r.value) * scale;
					return (
						<g key={r.value} opacity={t(f, a, a + 8)}>
							{next && <rect x={x0} y={y + h} width={next.value * scale} height={(gapY - h) * t(f, a + 6, a + step + 2)} fill={COLOR.stay} opacity={0.3} />}
							<rect x={x0} y={y} width={Math.max(keepW, 4) * (next ? 1 : t(f, a, a + 10))} height={h} rx={4} fill={isKey ? COLOR.key : COLOR.stay} />
							{next && <rect x={x0 + keepW} y={y} width={(r.value - next.value) * scale} height={h} rx={4} fill={COLOR.out} opacity={0.55} />}
							<Num x={x0} y={y - 10} size={isKey ? 84 : 64} anchor="start" fill={isKey ? COLOR.key : 'white'}>
								{fmt(r.value)}
								<tspan fontFamily={inter} fontWeight={400} fontSize={40} fill="white">{'  ' + r.label}</tspan>
							</Num>
						</g>
					);
				})}
			</svg>
		</AbsoluteFill>
	);
};

// --- card 12: the three comparison lines from the storyboard's On-Screen Text ---------------------------
export const Comparisons: React.FC<{lines: string[]; at: number[]}> = ({lines, at}) => {
	const f = useCurrentFrame();
	return (
		<AbsoluteFill>
			<svg width={VIDEO.width} height={VIDEO.height} viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`}>
				{lines.map((l, i) => {
					const p = t(f, at[i], at[i] + 12);
					const [a, rest] = l.split(' > ');
					const y = Z.top + 260 + i * 210 + (1 - p) * 30;
					return (
						<g key={l} opacity={p}>
							<Num x={CX} y={y} size={84}>
								{a}
								<tspan fill={COLOR.stay}>{' > '}</tspan>
								{rest.replace(/ \(.*\)$/, '')}
							</Num>
							{/\(.*\)$/.test(rest) && <Label x={CX} y={y + 46} size={30}>{rest.match(/\(.*\)$/)![0]}</Label>}
						</g>
					);
				})}
			</svg>
		</AbsoluteFill>
	);
};
