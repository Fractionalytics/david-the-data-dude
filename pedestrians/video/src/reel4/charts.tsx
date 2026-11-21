// Reel 4's two charts. Data: src/reel4/data.json (scripts/export_reel4_video_data.py, from
// data/final/reel4_four_waves.csv; CDC WONDER, 2025 provisional).
import React from 'react';
import data from './data.json';
import {C, clamp, lerp, LineKey, LINES, PANEL, T} from './kit';

// ---- Plot geometry: the axes take as little as possible ----
// x: 2000 at 175, 2025 at 945. y: 0 at 905, 42,000 at 175 (wave 4's 41,583 peak lands at y ~182).
export const X0 = 175, X1 = 945, Y0 = 905, YTOP = 175, VMAX = 42000;
export const xOf = (yr: number) => X0 + ((yr - 2000) / 25) * (X1 - X0);
export const yOf = (v: number) => Y0 - (v / VMAX) * (Y0 - YTOP);
const YEARS = data.years;
const S = data.series as Record<LineKey, number[]>;
export const valueAt = (k: LineKey, yr: number) => {
	const i = Math.max(0, Math.min(YEARS.length - 2, Math.floor(yr - 2000)));
	return lerp(S[k][i], S[k][i + 1], clamp(yr - 2000 - i));
};

const pathTo = (k: LineKey, yr: number) => {
	const pts: string[] = [];
	for (let y = 2000; y <= Math.floor(yr); y++) pts.push(`${xOf(y)},${yOf(S[k][y - 2000])}`);
	if (yr % 1 > 0.001) pts.push(`${xOf(yr)},${yOf(valueAt(k, yr))}`);
	return pts.join(' ');
};

export type Marker = {yr: number; label: string; labelY: number; anchor: 'start' | 'end'; p: number; dots?: LineKey[]; lineTop?: number};

// The waves chart. `reach` is the year each line has been drawn to (2000 = not drawn); `drawing` puts a pen
// dot on lines still moving. `axesP` fades the frame (axes, years, source); `legendP` the key.
export const Waves: React.FC<{reach: Record<LineKey, number>; drawing: Record<LineKey, boolean>; axesP: number; markers?: Marker[]; children?: React.ReactNode}> = ({reach, drawing, axesP, markers = [], children}) => (
	<>
		<svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
			<g opacity={axesP}>
				{[10000, 20000, 30000, 40000].map((v) => (
					<g key={v}>
						<line x1={X0} x2={X1} y1={yOf(v)} y2={yOf(v)} stroke={C.ink} strokeOpacity={0.16} strokeWidth={1.5} />
						<T x={X0 - 10} y={yOf(v) + 6} size={18} fill={C.muted} textAnchor="end" weight={400}>{`${v / 1000}K`}</T>
					</g>
				))}
				<line x1={X0} x2={X1} y1={Y0} y2={Y0} stroke={C.rule} strokeWidth={2} />
				{[2000, 2005, 2010, 2015, 2020, 2025].map((yr) => (
					<T key={yr} x={xOf(yr)} y={Y0 + 28} size={19} fill={C.muted} textAnchor="middle" weight={400}>{yr}</T>
				))}
				<line x1={PANEL.left + 22} x2={PANEL.right - 22} y1={Y0 + 42} y2={Y0 + 42} stroke={C.rule} strokeWidth={1.2} strokeDasharray="2 3" />
				<T x={PANEL.left + 24} y={Y0 + 62} size={14} fill={C.muted} weight={400} letterSpacing={0.5}>
					SOURCE: CDC WONDER · 2025 PROVISIONAL · WAVES DEFINED BY FRIEDMAN, CICCARONE ET AL. 2026
				</T>
			</g>
			{markers.map((m) =>
				m.p > 0 ? (
					<g key={m.label} opacity={clamp(m.p)}>
						<line x1={xOf(m.yr)} x2={xOf(m.yr)} y1={Y0} y2={m.lineTop ?? m.labelY + 14} stroke={C.ink} strokeOpacity={0.7} strokeWidth={2} strokeDasharray="6 6" />
						<T x={xOf(m.yr) + (m.anchor === 'start' ? 8 : -8)} y={m.labelY} size={21} textAnchor={m.anchor}>{m.label}</T>
					</g>
				) : null,
			)}
			{LINES.map((l) =>
				reach[l.key] > 2000.001 ? (
					<g key={l.key}>
						<polyline points={pathTo(l.key, reach[l.key])} fill="none" stroke="rgba(0,0,0,0.45)" strokeWidth={11} strokeLinejoin="round" strokeLinecap="round" />
						<polyline points={pathTo(l.key, reach[l.key])} fill="none" stroke={l.color} strokeWidth={7} strokeLinejoin="round" strokeLinecap="round" strokeDasharray={'dash' in l ? l.dash : undefined} />
						{drawing[l.key] && <circle cx={xOf(reach[l.key])} cy={yOf(valueAt(l.key, reach[l.key]))} r={9} fill={l.color} />}
					</g>
				) : null,
			)}
			{markers.flatMap((m) =>
				(m.dots ?? []).map((k) => {
					const col = LINES.find((l) => l.key === k)!.color;
					return m.p > 0 ? <circle key={m.label + k} cx={xOf(m.yr)} cy={yOf(valueAt(k, m.yr))} r={11} fill={col} stroke="#0B0D0C" strokeWidth={3} opacity={clamp(m.p)} /> : null;
				}),
			)}
		</svg>
		{children}
	</>
);

// The key, top-left: one row per line, each fading in as its line first appears.
export const Legend: React.FC<{show: Record<LineKey, number>; p: number}> = ({show, p}) => (
	<svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0, opacity: p}}>
		<T x={190} y={290} size={38} letterSpacing={1}>US OVERDOSE DEATHS PER YEAR</T>
		{LINES.map((l, i) => (
			<g key={l.key} opacity={clamp(show[l.key])}>
				<line x1={190} x2={226} y1={326 + i * 30} y2={326 + i * 30} stroke={l.color} strokeWidth={7} strokeLinecap="round" strokeDasharray={'dash' in l ? '10 7' : undefined} />
				<T x={240} y={333 + i * 30} size={20}>{l.label}</T>
			</g>
		))}
	</svg>
);

// ---- Cards 4-6: OxyContin sales, 1996 vs. 2000 (Van Zee 2009) ----
// `p` draws the slope from 1996 to 2000; `refP` adds the dashed $1B line (card 6).
export const Slopegraph: React.FC<{p: number; refP: number}> = ({p, refP}) => {
	const [a, b] = data.oxycontin;
	const XA = 330, XB = 750, B0 = 860, BT = 330, MAX = 1.2e9;
	const y = (v: number) => B0 - (v / MAX) * (B0 - BT);
	const col = LINES[0].color;
	const ex = lerp(XA, XB, clamp(p)), ey = lerp(y(a.sales), y(b.sales), clamp(p));
	return (
		<svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
			<T x={190} y={290} size={42} letterSpacing={1}>OXYCONTIN SALES PER YEAR</T>
			<line x1={XA} x2={XA} y1={B0} y2={BT - 20} stroke={C.ink} strokeOpacity={0.35} strokeWidth={2} />
			<line x1={XB} x2={XB} y1={B0} y2={BT - 20} stroke={C.ink} strokeOpacity={0.35} strokeWidth={2} />
			<T x={XA} y={B0 + 40} size={30} textAnchor="middle">{a.year}</T>
			<T x={XB} y={B0 + 40} size={30} textAnchor="middle">{b.year}</T>
			<g opacity={clamp(refP)}>
				<line x1={XA - 60} x2={XB + 60} y1={y(1e9)} y2={y(1e9)} stroke={C.ink} strokeOpacity={0.7} strokeWidth={2} strokeDasharray="8 8" />
				<T x={XA - 66} y={y(1e9) + 7} size={22} fill={C.muted} textAnchor="end">$1B</T>
			</g>
			{p > 0 && (
				<>
					<line x1={XA} y1={y(a.sales)} x2={ex} y2={ey} stroke={col} strokeWidth={9} strokeLinecap="round" />
					<circle cx={XA} cy={y(a.sales)} r={13} fill={col} />
					<T x={XA - 26} y={y(a.sales) + 13} size={40} textAnchor="end" fill={col}>$48M</T>
					<circle cx={ex} cy={ey} r={13} fill={col} />
					<T x={XB + 28} y={y(b.sales) + 15} size={56} fill={col} opacity={clamp(p * 4 - 3)}>$1.1B</T>
				</>
			)}
			<line x1={PANEL.left + 22} x2={PANEL.right - 22} y1={Y0 + 42} y2={Y0 + 42} stroke={C.rule} strokeWidth={1.2} strokeDasharray="2 3" />
			<T x={PANEL.left + 24} y={Y0 + 62} size={14} fill={C.muted} weight={400} letterSpacing={0.5}>SOURCE: VAN ZEE, AMERICAN JOURNAL OF PUBLIC HEALTH, 2009</T>
		</svg>
	);
};
