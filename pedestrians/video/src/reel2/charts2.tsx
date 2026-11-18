// Reel 2's charts for cards 4-45, in the lab-report look. Same conventions as charts.tsx: progress values
// 0-1 in, titles and subtitles from the Sheet, kickers, labels and source lines ours.
// Numbers: docs/reel2-visual-plan.md (number checks) and assets.json (scripts/prep_reel2_assets.py).
import React from 'react';
import {interpolate, interpolateColors} from 'remotion';
import reel3 from '../reel3/assets.json';
import assets from './assets.json';
import {C, clamp, FONT, H, headerBottom, lerp, Plate, Stamp, Svg, T, W} from './kit';

const METH = '#b8501a'; // card 12's meth palette
const FOOT = H - 60; // charts stay above the dotted source rule

const slideIn = (p: number) => ({opacity: clamp(p * 1.5), transform: `translateX(${(1 - clamp(p)) * -24}px)`});

// ---- Cards 4-5: past-year use, US vs. Europe, one pair of bars per drug ----
// US: NSDUH 2024 (12+); Europe: EUDA EDR 2025 (15-64). Amphetamines: meth only (US) vs. amphetamine + meth
// (Europe). Opioids are dependent or high-risk users, a different measure: US 1.2% (NSDUH 2025 opioid use
// disorder) to 2.3% (Keyes 2022 model), drawn as a bar with a whisker; Europe 0.19% (860,000 high-risk users).
// Each row is scaled to its own larger value.
type UseRow = {lab: string; note?: string; us: number; eu: number; usHi?: number; usTxt: string; euTxt: string};
const USE: UseRow[] = [
	{lab: 'Cocaine', us: 1.5, eu: 1.6, usTxt: '1.5%', euTxt: '1.6%'},
	{lab: 'Amphetamines', us: 0.8, eu: 0.8, usTxt: '0.8%', euTxt: '0.8%'},
	{lab: 'Opioids*', note: '*dependent or high-risk', us: 1.17, usHi: 2.3, eu: 0.19, usTxt: '1.2–2.3%', euTxt: '0.2%'},
	{lab: 'Cannabis', us: 22.3, eu: 8.4, usTxt: '22.3%', euTxt: '8.4%'},
];
export const UseBars: React.FC<{title: string; ps: number[]}> = ({title, ps}) => {
	const top = headerBottom(title) + 12, RH = 108, X0 = 300, BW = 360;
	return (
		<Plate title={title} kicker="Share of people who used in the past year" source="Sources: NSDUH 2024 (US, 12+) · EUDA 2025 (Europe, 15–64)">
			<Svg>
				<g>
					<rect x={W - 250} y={22} width={18} height={18} fill={C.us} />
					<T x={W - 226} y={39} size={20} fill={C.muted}>US</T>
					<rect x={W - 180} y={22} width={18} height={18} fill={C.eu} />
					<T x={W - 156} y={39} size={20} fill={C.muted}>Europe</T>
				</g>
				{USE.map((r, i) => {
					const p = ps[i] ?? 0;
					if (p <= 0) return null;
					const y = top + i * RH, max = Math.max(r.usHi ?? r.us, r.eu);
					const bw = (v: number) => (v / max) * BW * clamp(p);
					return (
						<g key={r.lab} opacity={clamp(p * 2)}>
							<T x={32} y={y + 44} size={34}>{r.lab}</T>
							{r.note && <T x={32} y={y + 74} size={18} fill={C.muted}>{r.note}</T>}
							<rect x={X0} y={y + 8} width={bw(r.us)} height={34} fill={C.us} />
							{r.usHi && (
								<g opacity={clamp(p * 3 - 2)}>
									<line x1={X0 + bw(r.us)} x2={X0 + bw(r.usHi)} y1={y + 25} y2={y + 25} stroke={C.us} strokeWidth={4} />
									<line x1={X0 + bw(r.usHi)} x2={X0 + bw(r.usHi)} y1={y + 12} y2={y + 38} stroke={C.us} strokeWidth={4} />
								</g>
							)}
							<T x={X0 + bw(r.usHi ?? r.us) + 10} y={y + 36} size={28} fill={C.us} opacity={clamp(p * 3 - 2)}>{r.usTxt}</T>
							<rect x={X0} y={y + 50} width={bw(r.eu)} height={34} fill={C.eu} />
							<T x={X0 + bw(r.eu) + 10} y={y + 78} size={28} fill={C.eu} opacity={clamp(p * 3 - 2)}>{r.euTxt}</T>
						</g>
					);
				})}
			</Svg>
		</Plate>
	);
};

// ---- Cards 7-8: the three explanations, numbered like a checklist ----
export const ListSign: React.FC<{title: string; items: string[]; shown: number[]}> = ({title, items, shown}) => {
	const top = headerBottom(title) + 40;
	return (
		<Plate title={title} kicker="Three factors" source="">
			{items.map((it, i) => (
				<div key={it} style={{position: 'absolute', left: 48, right: 40, top: top + i * 130, fontSize: 70, fontWeight: 700, whiteSpace: 'nowrap', ...slideIn(shown[i])}}>
					<span style={{color: C.us}}>{`${i + 1}.`}</span> {it}
				</div>
			))}
		</Plate>
	);
};

// ---- Cards 9-10: fentanyl's share of overdose deaths ----
// US 2024: 47,735 of 79,384 overdose deaths (60%). Europe: 208 of about 7,600 (2.7%); the 208 cover 15
// countries, the 7,600 the whole EU (plan, number check 9).
export const ShareBars: React.FC<{title: string; usP: number; euP: number}> = ({title, usP, euP}) => {
	const top = headerBottom(title) + 40, X0 = 40, BW = W - 80, BH = 90;
	const rows = [
		{lab: 'US', share: 47735 / 79384, txt: '60%', detail: '47,735 of 79,384 deaths', col: C.us, p: usP},
		{lab: 'Europe', share: 0.03, txt: 'about 3%', detail: '208 of about 7,600 deaths', col: C.eu, p: euP},
	];
	return (
		<Plate title={title} kicker="Overdose deaths involving fentanyl" source="Source: CDC WONDER (US, 2024) · EUDA (Europe; the 208 cover 15 countries)">
			<Svg>
				{rows.map((r, i) => {
					const y = top + i * 200;
					return (
						<g key={r.lab}>
							<T x={X0} y={y - 14} size={36}>{r.lab}</T>
							<T x={X0 + BW} y={y - 14} size={22} fill={C.muted} textAnchor="end" opacity={clamp(r.p * 2)}>{r.detail}</T>
							<rect x={X0} y={y} width={BW} height={BH} fill="none" stroke={C.ink} strokeWidth={2.5} />
							<rect x={X0} y={y} width={BW * r.share * clamp(r.p)} height={BH} fill={r.col} />
							<T x={X0 + Math.max(BW * r.share * clamp(r.p), 0) + 16} y={y + 64} size={56} fill={r.col} opacity={clamp(r.p * 3 - 2)}>{r.txt}</T>
						</g>
					);
				})}
			</Svg>
		</Plate>
	);
};

// ---- Card 11: meth in Europe's wastewater (EUDA 2025, 121 cities; Reel 3's map and dots) ----
// Dots are sized by meth residue (mg per 1,000 people a day); the cities above 150 (Czechia, Slovakia,
// eastern Germany, Kaunas in Lithuania) light up in meth orange with their countries tinted.
const dotR = (v: number) => Math.max(2.5, Math.sqrt(v / 600) * 20);
const HOT = ['CZE', 'SVK', 'LTU'];
// Labels for the exceptions, in map units (next to their dots).
const HOT_LABELS: Array<[string, number, number, 'start' | 'end']> = [
	['Lithuania', 332, 234, 'end'], ['Czechia', 232, 352, 'end'], ['Slovakia', 296, 362, 'start'], ['Germany', 208, 292, 'end'],
];
// View: central Europe and around it (map units), so the exceptions read at phone size.
const VIEW = {x: 40, y: 100, w: 400, h: 400};
export const EuropeMeth: React.FC<{title: string; sub: string; mapP: number; dotsP: number; hotP: number}> = ({title, sub, mapP, dotsP, hotP}) => {
	const M = reel3.map, WW = reel3.wastewater;
	const top = headerBottom(title, sub) + 4, s = Math.min((FOOT - top) / VIEW.h, 560 / VIEW.w);
	const ox = 30 - VIEW.x * s, oy = top - VIEW.y * s;
	const cities = [...WW.cities].sort((a, b) => a.v - b.v);
	const KX = 610;
	return (
		<Plate title={title} sub={sub} kicker="Meth in wastewater, 2025" source="Source: EUDA wastewater analysis, 2025 (121 European cities)">
			<Svg>
				<defs>
					<clipPath id="eu-clip"><rect x={30} y={top} width={VIEW.w * s} height={FOOT - top} /></clipPath>
				</defs>
				<g clipPath="url(#eu-clip)">
					<g transform={`translate(${ox},${oy}) scale(${s})`} opacity={mapP}>
						{M.countries.map((c, i) => (
							<path key={i} d={c.d} fill={HOT.includes(c.iso) ? interpolateColors(hotP, [0, 1], ['#DCD6CA', '#EFC39E']) : c.iso === 'DEU' ? interpolateColors(hotP, [0, 1], ['#DCD6CA', '#F3DCC6']) : c.europe ? '#DCD6CA' : '#ECE8DF'} stroke={C.paper} strokeWidth={1.2 / s} />
						))}
						{cities.map((c, i) => {
							const hot = c.v >= 150;
							const p = clamp(dotsP * 1.5 - (i / cities.length) * 0.5);
							return <circle key={i} cx={c.x} cy={c.y} r={(dotR(c.v) * p) / s} fill={hot && hotP > 0 ? METH : C.faint} fillOpacity={hot ? lerp(0.6, 0.9, hotP) : 0.6} stroke={C.paper} strokeWidth={1 / s} />;
						})}
					</g>
					<g opacity={hotP}>
						{HOT_LABELS.map(([lab, mx, my, anchor]) => (
							<T key={lab} x={ox + mx * s} y={oy + my * s} size={22} fill={METH} textAnchor={anchor} stroke={C.paper} strokeWidth={5} paintOrder="stroke">{lab}</T>
						))}
					</g>
				</g>
				<rect x={30} y={top} width={VIEW.w * s} height={FOOT - top} fill="none" stroke={C.ink} strokeWidth={2} opacity={mapP} />
				<g opacity={dotsP}>
					{[10, 100, 500].map((v, k) => (
						<g key={v}>
							<circle cx={KX + 20 + k * 60} cy={FOOT - 100 - dotR(v)} r={dotR(v)} fill={C.faint} fillOpacity={0.6} />
							<T x={KX + 20 + k * 60} y={FOOT - 70} size={20} fill={C.muted} textAnchor="middle">{v}</T>
						</g>
					))}
					<T x={KX + 80} y={FOOT - 40} size={18} fill={C.muted} textAnchor="middle">mg per 1,000</T>
					<T x={KX + 80} y={FOOT - 16} size={18} fill={C.muted} textAnchor="middle">people a day</T>
				</g>
			</Svg>
		</Plate>
	);
};

// ---- Cards 14-15: the supply mix, a 2x2 results table ----
export const MixGrid: React.FC<{title: string; ps: [number, number, number, number]}> = ({title, ps}) => {
	const top = headerBottom(title) + 64, X0 = 250, CW = 270, RH = 170;
	const cells: Array<[number, number, string, string]> = [
		[0, 0, 'Fentanyl', C.us], [0, 1, 'Meth', C.us], [1, 0, 'Heroin', C.eu], [1, 1, 'Cocaine', C.eu],
	];
	return (
		<Plate title={title} kicker="Main opioid and main stimulant" source="Sources: CDC WONDER (US) · EUDA European Drug Report 2025">
			<Svg>
				{['US', 'Europe'].map((c, i) => (
					<T key={c} x={X0 + CW * i + CW / 2} y={top - 18} size={34} textAnchor="middle" fill={i ? C.eu : C.us}>{c}</T>
				))}
				{['Opioid', 'Stimulant'].map((r, j) => (
					<T key={r} x={X0 - 22} y={top + RH * j + RH / 2 + 12} size={32} textAnchor="end">{r}</T>
				))}
				{[0, 1, 2].map((k) => (
					<g key={k}>
						<line x1={X0} x2={X0 + 2 * CW} y1={top + k * RH} y2={top + k * RH} stroke={C.ink} strokeWidth={2.5} />
						<line x1={X0 + k * CW} x2={X0 + k * CW} y1={top} y2={top + 2 * RH} stroke={C.ink} strokeWidth={2.5} />
					</g>
				))}
				{cells.map(([i, j, txt, col], k) => {
					const p = ps[k];
					return (
						<g key={txt} opacity={clamp(p * 2)}>
							<rect x={X0 + i * CW + 10} y={top + j * RH + 10} width={CW - 20} height={RH - 20} fill={col} fillOpacity={0.1 * clamp(p)} />
							<T x={X0 + i * CW + CW / 2} y={top + j * RH + RH / 2 + 18} size={52} textAnchor="middle" fill={col}>{txt}</T>
						</g>
					);
				})}
			</Svg>
		</Plate>
	);
};

// ---- Cards 16-17: fentanyl about 50x heroin (DEA and CDC rule of thumb), as two bars across the full width
// of the chart zone. No 50x callout: the bars show it (David, 2026-11-18) ----
export const Potency: React.FC<{title: string; heroinP: number; fentP: number}> = ({title, heroinP, fentP}) => {
	const top = headerBottom(title) + 20, X0 = 32, BW = W - 64, BH = 120;
	const hy = top + 44, fy = top + 250;
	const fw = BW * lerp(1 / 50, 1, fentP);
	return (
		<Plate title={title} kicker="Strength per milligram" source="Rule of thumb: DEA, CDC">
			<Svg>
				<g opacity={clamp(heroinP * 2)}>
					<T x={X0} y={hy - 14} size={34} fill={C.eu}>Heroin</T>
					<rect x={X0} y={hy} width={(BW / 50) * clamp(heroinP)} height={BH} fill={C.eu} />
					<T x={X0 + BW / 50 + 14} y={hy + BH / 2 + 18} size={52} fill={C.eu}>1</T>
				</g>
				{fentP > 0 && (
					<g>
						<T x={X0} y={fy - 14} size={34} fill={C.us}>Fentanyl</T>
						<rect x={X0} y={fy} width={fw} height={BH} fill={C.us} />
						<T x={X0 + fw - 24} y={fy + BH / 2 + 20} size={56} textAnchor="end" fill="#FFFFFF" opacity={clamp(fentP * 3 - 2)}>about 50</T>
					</g>
				)}
			</Svg>
		</Plate>
	);
};

// ---- Cards 22-23: "Fentanyl & a Stimulant: / The Deadly Pair" (Sheet, Video column; David's words) ----
// The first line types out; the second lands as a stamp.
export const DeadlyPairSign: React.FC<{typeP: number; stampP: number}> = ({typeP, stampP}) => {
	const line1 = 'Fentanyl & a Stimulant:';
	const n = Math.round(line1.length * clamp(typeP));
	return (
		<Plate title="" kicker="" source="">
			<div style={{position: 'absolute', left: 60, top: 170, fontSize: 58, fontWeight: 700, whiteSpace: 'pre'}}>
				{line1.slice(0, n)}
				<span style={{opacity: typeP > 0 && typeP < 1 ? 1 : 0}}>▍</span>
			</div>
			<Stamp x={W / 2} y={390} text="The Deadly Pair" p={stampP} size={66} nowrap />
		</Plate>
	);
};

// ---- Cards 24-25: drug-checking samples with fentanyl (Wagner et al. 2023): powder meth 1 in 8, crystal 2 in 276 ----
export const DotGrids: React.FC<{title: string; powderP: number; crystalP: number}> = ({title, powderP, crystalP}) => {
	const top = headerBottom(title) + 26;
	const crystal = Array.from({length: 276}, (_, i) => i);
	const COLS = 23, SP = 21;
	const lit = new Set([95, 210]);
	return (
		<Plate title={title} kicker="Meth samples that tested positive for fentanyl" source="Source: Wagner et al. 2023, community drug-checking samples">
			<Svg>
				<g opacity={clamp(powderP * 2)}>
					<T x={32} y={top + 30} size={30}>Powder meth</T>
					<T x={32} y={top + 66} size={30} fill={C.us}>1 in 8</T>
					{Array.from({length: 8}, (_, i) => (
						<circle key={i} cx={300 + i * 62} cy={top + 30} r={22 * clamp(powderP * 8 - i)} fill={i === 3 ? C.us : C.faint} />
					))}
				</g>
				<g opacity={clamp(crystalP * 2)}>
					<T x={32} y={top + 170} size={30}>Crystal meth</T>
					<T x={32} y={top + 206} size={30} fill={C.us}>2 in 276</T>
					{crystal.map((i) => {
						const p = clamp(crystalP * 1.6 - (i / 276) * 0.6);
						return <circle key={i} cx={300 + (i % COLS) * SP} cy={top + 150 + Math.floor(i / COLS) * SP} r={7.5 * p} fill={lit.has(i) ? C.us : C.faint} />;
					})}
				</g>
			</Svg>
		</Plate>
	);
};

// ---- Card 26: 88% of syringe-program clients whose main drug is fentanyl also used a stimulant
// (UW ADAI 2023 Washington State syringe services program survey) ----
export const StatWaffle: React.FC<{title: string; sub: string; p: number}> = ({title, sub, p}) => {
	const top = headerBottom(title, sub) + 24, SP = 38, X0 = 440;
	const shown = Math.round(88 * clamp(p * 1.25));
	return (
		<Plate title={title} sub={sub} kicker="Washington State syringe services programs" source="Source: UW Addictions, Drug & Alcohol Institute, 2023 survey">
			<Svg>
				<T x={40} y={top + 150} size={150} fill={C.us}>{`${shown}%`}</T>
				<T x={44} y={top + 210} size={26} fill={C.ink} opacity={clamp(p * 2 - 1)}>of clients whose main</T>
				<T x={44} y={top + 244} size={26} fill={C.ink} opacity={clamp(p * 2 - 1)}>drug is fentanyl also</T>
				<T x={44} y={top + 278} size={26} fill={C.ink} opacity={clamp(p * 2 - 1)}>used a stimulant</T>
				{Array.from({length: 100}, (_, i) => (
					<rect key={i} x={X0 + (i % 10) * SP} y={top + Math.floor(i / 10) * SP} width={SP - 6} height={SP - 6} fill={i < shown ? C.us : C.grid} />
				))}
			</Svg>
		</Plate>
	);
};

// ---- Cards 30-32: the upper/downer seesaw. Fentanyl alone tips it down; meth on the other end levels it ----
export const Seesaw: React.FC<{title: string; downP: number; upP: number; levelP: number}> = ({title, downP, upP, levelP}) => {
	const cx = W / 2, cy = 470, L = 300;
	// The beam starts level. Fentanyl lands on the left and weighs that end down (the beam turns
	// counterclockwise, so SVG's rotate is negative); meth lands on the right and brings it back to level.
	const tilt = 12 * clamp(downP) * (1 - clamp(levelP));
	// Boxes ride on the beam (they're drawn in its rotated frame) and drop in from above as they appear.
	const Box: React.FC<{x: number; label: string; drug: string; col: string; p: number}> = ({x, label, drug, col, p}) => (
		<g opacity={clamp(p * 2)} transform={`translate(${x},${-6 - (1 - clamp(p)) * 80})`}>
			<rect x={-105} y={-110} width={210} height={110} fill={col} />
			<T x={0} y={-66} size={30} textAnchor="middle" fill="#FFFFFF">{label}</T>
			<T x={0} y={-24} size={36} textAnchor="middle" fill="#FFFFFF">{drug}</T>
		</g>
	);
	return (
		<Plate title={title} kicker="Why people combine them" source="Source: UW ADAI interviews (2018); Friedman & Shover 2023">
			<Svg>
				<polygon points={`${cx - 50},${cy + 100} ${cx + 50},${cy + 100} ${cx},${cy + 6}`} fill={C.ink} />
				<g transform={`translate(${cx},${cy}) rotate(${-tilt})`}>
					<line x1={-L} y1={0} x2={L} y2={0} stroke={C.ink} strokeWidth={12} strokeLinecap="round" />
					<Box x={-L + 115} label="Downer" drug="fentanyl" col={C.us} p={downP} />
					<Box x={L - 115} label="Upper" drug="meth" col={METH} p={upP} />
				</g>
			</Svg>
		</Plate>
	);
};

// ---- Card 33: strength per milligram, morphine = 1 (CDC opioid dose tables, DEA): heroin ~2, methadone 4.7,
// fentanyl ~100. Buprenorphine left off (David, 2026-11-18) ----
export const Strengths: React.FC<{title: string; ps: number[]}> = ({title, ps}) => {
	const top = headerBottom(title) + 40, X0 = 290, WMAX = 400, h = 60;
	const rows: Array<[string, number, string, string]> = [['Heroin', 2, '~2', C.eu], ['Methadone', 4.7, '4.7', C.faint], ['Fentanyl', 100, '~100', C.us]];
	return (
		<Plate title={title} kicker="Strength per milligram (morphine = 1)" source="Rough conversions: CDC opioid dose tables; DEA">
			<Svg>
				{rows.map(([lab, v, txt, col], i) => {
					const p = ps[i] ?? 0, y = top + i * 120, w = Math.max((v / 100) * WMAX * clamp(p), p > 0 ? 4 : 0);
					return (
						<g key={lab} opacity={clamp(p * 3)}>
							<T x={X0 - 18} y={y + 42} size={36} textAnchor="end" fill={col === C.faint ? C.muted : C.ink}>{lab}</T>
							<rect x={X0} y={y} width={w} height={h} fill={col} />
							<T x={X0 + w + 12} y={y + 44} size={40} fill={col === C.faint ? C.muted : col}>{txt}</T>
							{lab === 'Fentanyl' && <T x={X0} y={y + h + 36} size={28} fill={C.us} opacity={clamp(p * 2 - 1)}>about 50× heroin</T>}
						</g>
					);
				})}
			</Svg>
		</Plate>
	);
};

// ---- Cards 35-36, 43: the 13x as pieces. US bar = 13.1 Europe bars; each slice lights with its label
// (Sheet, On-Screen Text) inside its part of the bar ----
const SLICE_LABELS = [['The Deadly Pair'], ['Fentanyl,', 'no stimulant'], ['Stimulant,', 'no fentanyl'], ['Everything', 'else']];
const SLICE_COLS = [C.us, '#C9453B', '#DC7A70', '#B99C96'];
export const SplitBar: React.FC<{title: string; ps: number[]}> = ({title, ps}) => {
	const S = assets.split;
	// Europe's 1x bar is as tall as the US bar, so the slices compare to it by length alone (David, 2026-11-18).
	// The narrow "everything else" slice is labeled up in the Europe row's empty right side.
	const top = headerBottom(title) + 14, X0 = 40, BW = W - 80, k = BW / S.us;
	const euW = S.europe * k, BH = 150, ey = top + 36, by = ey + BH + 46;
	let x = X0;
	return (
		<Plate title={title} kicker="Drug-induced death rates, as multiples of Europe's" source="Source: CDC WONDER (US, 2024, on Europe's definition) · EUDA (Europe)">
			<Svg>
				<T x={X0} y={ey - 12} size={26} fill={C.eu}>Europe = 1×</T>
				<rect x={X0} y={ey} width={euW} height={BH} fill={C.eu} />
				<T x={X0} y={by - 12} size={26} fill={C.us}>{`US = ${S.x.toFixed(0)}×`}</T>
				<rect x={X0} y={by} width={BW} height={BH} fill="#EFDCD8" />
				{S.slices.map((s, i) => {
					const w = s.per_million * k, x0 = x;
					x += w;
					const p = clamp(ps[i] ?? 0);
					const narrow = w < 120;
					const lines = SLICE_LABELS[i];
					return (
						<g key={s.slice}>
							<rect x={x0} y={by} width={w * p} height={BH} fill={SLICE_COLS[i]} />
							<line x1={x0 + w} x2={x0 + w} y1={by} y2={by + BH} stroke={C.paper} strokeWidth={3} />
							<g opacity={clamp(p * 2 - 1)}>
								{narrow ? (
									<g>
										<line x1={x0 + w / 2} x2={x0 + w / 2} y1={by} y2={ey + BH - 6} stroke={C.ink} strokeWidth={2} />
										<T x={x0 + w} y={ey + BH - 66} size={24} textAnchor="end">{lines.join(' ')}</T>
										<T x={x0 + w} y={ey + BH - 22} size={36} textAnchor="end" fill={SLICE_COLS[i]}>{`${s.x_europe.toFixed(1)}×`}</T>
									</g>
								) : (
									<g>
										{lines.map((ln, j) => (
											<T key={ln} x={x0 + 12} y={by + 36 + j * 28} size={i === 0 ? 26 : 22} fill="#FFFFFF">{ln}</T>
										))}
										<T x={x0 + 12} y={by + BH - 22} size={i === 0 ? 72 : 52} fill="#FFFFFF">{i === 0 ? '5×' : `${s.x_europe.toFixed(1)}×`}</T>
									</g>
								)}
							</g>
						</g>
					);
				})}
			</Svg>
		</Plate>
	);
};

// ---- Cards 44-45: Deadly Pair deaths 2010-2024 (CDC WONDER); the 2024 drop drawn last, then -33% ----
export const Trend: React.FC<{title: string; p: number; dropP: number; stampP: number}> = ({title, p, dropP, stampP}) => {
	const D = assets.deadlyPair;
	const top = headerBottom(title) + 40, L = 110, R = W - 120, BOT = FOOT - 50;
	const x = (yr: number) => L + ((yr - 2010) / 14) * (R - L);
	const y = (v: number) => BOT - (v / 45000) * (BOT - top);
	const upTo = D.filter((d) => d.year <= 2023);
	const n = (upTo.length - 1) * clamp(p);
	const pts = upTo.slice(0, Math.floor(n) + 1).map((d) => [x(d.year), y(d.deaths)]);
	const i = Math.floor(n), f = n - i;
	if (i < upTo.length - 1) pts.push([lerp(x(upTo[i].year), x(upTo[i + 1].year), f), lerp(y(upTo[i].deaths), y(upTo[i + 1].deaths), f)]);
	const a = D[D.length - 2], b = D[D.length - 1];
	const dx = lerp(x(a.year), x(b.year), clamp(dropP)), dy = lerp(y(a.deaths), y(b.deaths), clamp(dropP));
	return (
		<Plate title={title} kicker="US overdose deaths involving fentanyl and a stimulant" source="Source: CDC WONDER, multiple cause of death (T40.4 with T40.5 or T43.6)">
			<Svg>
				{[0, 20000, 40000].map((v) => (
					<g key={v}>
						<line x1={L} x2={R} y1={y(v)} y2={y(v)} stroke={C.ink} strokeOpacity={0.25} strokeWidth={1.5} />
						<T x={L - 12} y={y(v) + 8} size={24} fill={C.muted} textAnchor="end">{v ? `${v / 1000}k` : '0'}</T>
					</g>
				))}
				{[2010, 2015, 2020, 2024].map((yr) => (
					<T key={yr} x={x(yr)} y={BOT + 34} size={24} fill={C.muted} textAnchor="middle">{yr}</T>
				))}
				<polyline points={pts.map((q) => q.join(',')).join(' ')} fill="none" stroke={C.us} strokeWidth={7} strokeLinejoin="round" strokeLinecap="round" />
				{p >= 1 && (
					<g>
						<circle cx={x(a.year)} cy={y(a.deaths)} r={9} fill={C.us} />
						<T x={x(a.year) - 14} y={y(a.deaths) - 18} size={26} textAnchor="end" fill={C.us}>2023: 41,583</T>
					</g>
				)}
				{dropP > 0 && (
					<g>
						<line x1={x(a.year)} y1={y(a.deaths)} x2={dx} y2={dy} stroke={C.us} strokeWidth={7} strokeLinecap="round" />
						<circle cx={dx} cy={dy} r={9} fill={C.us} />
						<T x={x(b.year) + 16} y={y(b.deaths) + 9} size={26} fill={C.us} opacity={clamp(dropP * 3 - 2)}>28,063</T>
					</g>
				)}
			</Svg>
			<Stamp x={R - 60} y={BOT - 80} text="−33%" sub="2023 to 2024" p={stampP} size={56} />
		</Plate>
	);
};

export {FONT};
