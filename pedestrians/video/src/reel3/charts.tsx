// Reel 3's charts. Each draws from animation progress values (0-1), so a card can start from the previous
// card's end state. Titles and sign words are David's (Sheet: On-Screen Text, Script); gray subtitles and
// axis labels say what is measured. Numbers come from assets.json (scripts/prep_reel3_assets.py).
import React from 'react';
import {Img, staticFile} from 'remotion';
import data from '../data/data.json';
import assets from './assets.json';
import {C, clamp, H, Line, lerp, Plate, Pt, Sub, Svg, T, Title, W, partial} from './kit';

const N = assets.numbers;

// ---- Reused from Reel 1 (src/charts/Charts.tsx), redrawn for the taller plate ----

// Cards 1-2 and 5-7: pedestrian deaths per 100,000, US and Europe, 2000-2024.
// Card 34 adds `accentP` (Europe and the pre-2009 US line fade back, the 2009 low is marked) and `riseP`
// (the US line from 2009 on redrawn heavy, with its rise from the low).
export const RatesChart: React.FC<{title: string; usP: number; euP: number; accentP?: number; riseP?: number}> = ({title, usP, euP, accentP = 0, riseP = 0}) => {
	const us: Pt[] = data.rates.us.map((d) => ({x: d.year, v: d.rate}));
	const eu: Pt[] = data.rates.eu.map((d) => ({x: d.year, v: d.rate}));
	const L = 80, R = W - 170, TOP = 170, BOT = H - 80;
	const x = (yr: number) => L + ((yr - 2000) / 24) * (R - L);
	const y = (v: number) => BOT - (v / 2.5) * (BOT - TOP);
	const usEnd = partial(us, usP), euEnd = partial(eu, euP);
	const rise = us.filter((d) => d.x >= 2009);
	const low = rise[0], last = rise[rise.length - 1];
	return (
		<Plate>
			<Title text={title} size={54} />
			<Svg>
				{accentP > 0 && (
					<g opacity={accentP}>
						<rect x={x(2009)} y={TOP - 10} width={R - x(2009)} height={BOT - TOP + 10} fill={C.us} fillOpacity={0.06} />
						<line x1={x(2009)} x2={x(2009)} y1={TOP - 10} y2={BOT} stroke={C.muted} strokeWidth={4} strokeDasharray="10 10" />
					</g>
				)}
				<Sub text="Pedestrian deaths per 100,000 people" />
				<g opacity={1 - 0.75 * accentP}>
				<line x1={L} x2={R} y1={y(0)} y2={y(0)} stroke={C.grid} strokeWidth={2} />
				{[1, 2].map((v) => (
					<g key={v}>
						<line x1={L} x2={R} y1={y(v)} y2={y(v)} stroke={C.grid} strokeWidth={2} />
						<T x={L - 14} y={y(v) + 14} size={38} fill={C.muted} textAnchor="end">{v}</T>
					</g>
				))}
				{[2000, 2009, 2024].map((yr) => (
					<T key={yr} x={x(yr)} y={BOT + 50} size={40} fill={C.muted} textAnchor="middle">{yr}</T>
				))}
				{euP > 0 && <Line pts={eu} p={euP} x={x} y={y} color={C.eu} />}
				<Line pts={us} p={usP} x={x} y={y} color={C.us} />
				<T x={x(usEnd[usEnd.length - 1].x) + 18} y={y(usEnd[usEnd.length - 1].v) + 14} opacity={clamp(usP * 5 - 4) * (1 - accentP)}>US</T>
				{euP > 0 && <T x={x(euEnd[euEnd.length - 1].x) + 18} y={y(euEnd[euEnd.length - 1].v) + 14} opacity={clamp(euP * 5 - 4)}>Europe</T>}
				</g>
				{riseP > 0 && (
					<g>
						<Line pts={rise} p={riseP} x={x} y={y} color={C.us} width={14} />
						<circle cx={x(low.x)} cy={y(low.v)} r={14} fill={C.us} opacity={accentP} />
						<T x={x(low.x)} y={y(low.v) + 56} size={38} weight={800} textAnchor="middle" opacity={accentP}>2009: {low.v.toFixed(2)}</T>
						<T x={x(last.x) + 18} y={y(last.v) + 14} size={44} weight={800} fill={C.us} opacity={clamp(riseP * 5 - 4)}>US {last.v.toFixed(2)}</T>
					</g>
				)}
			</Svg>
		</Plate>
	);
};

// Card 32: RAND's best estimates of chronic meth users (4+ days a month) per 1,000 US residents, 2009 and
// 2012-2016 (no 2010-11 estimates; the line bridges the gap, dots mark real points).
export const RandChart: React.FC<{title: string; p: number}> = ({title, p}) => {
	const pts: Pt[] = N.rand.map((d) => ({x: d.year, v: d.v}));
	const L = 110, R = W - 150, TOP = 190, BOT = H - 100;
	const x = (yr: number) => L + ((yr - 2009) / 7) * (R - L);
	const y = (v: number) => BOT - (v / 12) * (BOT - TOP);
	const reach = (yr: number) => p >= (yr - 2009) / 7 - 1e-6;
	const first = pts[0], last = pts[pts.length - 1];
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				<Sub text="Heavy meth users per 1,000 people (RAND best estimates)" />
				{[0, 4, 8, 12].map((v) => (
					<g key={v}>
						<line x1={L} x2={R} y1={y(v)} y2={y(v)} stroke={v ? C.grid : C.ink} strokeWidth={v ? 2 : 3} />
						<T x={L - 14} y={y(v) + 12} size={34} fill={C.muted} textAnchor="end">{v}</T>
					</g>
				))}
				{[2009, 2012, 2016].map((yr) => <T key={yr} x={x(yr)} y={BOT + 46} size={38} fill={C.muted} textAnchor="middle">{yr}</T>)}
				<Line pts={pts} p={p} x={x} y={y} color={C.meth} />
				{pts.filter((d) => reach(d.x)).map((d) => <circle key={d.x} cx={x(d.x)} cy={y(d.v)} r={11} fill={C.meth} />)}
				<T x={x(first.x)} y={y(first.v) - 22} size={40} weight={800} textAnchor="middle">{first.v.toFixed(1)}</T>
				<T x={x(last.x) + 20} y={y(last.v) + 14} size={40} weight={800} opacity={clamp(p * 5 - 4)}>{last.v.toFixed(1)}</T>
				<T x={x(last.x) + 20} y={y(last.v) + 70} size={56} weight={800} fill={C.meth} opacity={clamp(p * 5 - 4)}>×{(last.v / first.v).toFixed(1)}</T>
				<T x={L} y={H - 22} size={28} fill={C.muted}>No RAND estimate for 2010–11. 2016 range: 4.0–16.3 per 1,000.</T>
			</Svg>
		</Plate>
	);
};

// Card 32: overdose deaths listing meth and no opioid, per 100,000 people, 2009-2024 (CDC WONDER; one
// definition throughout, see data/raw/cdc_wonder/SOURCE.md). Few casual users die of an overdose, so this
// tracks heavy use; leaving out opioid-involved deaths keeps fentanyl from inflating it after 2016.
export const MethOnlyChart: React.FC<{title: string; p: number}> = ({title, p}) => {
	const pts: Pt[] = N.methOnly.map((d) => ({x: d.year, v: d.v}));
	const L = 100, R = W - 170, TOP = 190, BOT = H - 110;
	const x = (yr: number) => L + ((yr - 2009) / 15) * (R - L);
	const y = (v: number) => BOT - (v / 4) * (BOT - TOP);
	const first = pts[0], last = pts[pts.length - 1];
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				<Sub text="Meth overdose deaths, no opioids, per 100,000 people" />
				{[0, 1, 2, 3, 4].map((v) => (
					<g key={v}>
						<line x1={L} x2={R} y1={y(v)} y2={y(v)} stroke={v ? C.grid : C.ink} strokeWidth={v ? 2 : 3} />
						<T x={L - 14} y={y(v) + 12} size={34} fill={C.muted} textAnchor="end">{v}</T>
					</g>
				))}
				{[2009, 2016, 2024].map((yr) => <T key={yr} x={x(yr)} y={BOT + 46} size={38} fill={C.muted} textAnchor="middle">{yr}</T>)}
				<Line pts={pts} p={p} x={x} y={y} color={C.meth} />
				<circle cx={x(first.x)} cy={y(first.v)} r={11} fill={C.meth} />
				<T x={x(first.x) + 6} y={y(first.v) - 22} size={40} weight={800}>{first.v.toFixed(1)}</T>
				<T x={x(last.x) + 20} y={y(last.v) + 20} size={60} weight={800} fill={C.meth} opacity={clamp(p * 5 - 4)}>×{Math.round(last.v / first.v)}</T>
				<T x={L} y={H - 22} size={28} fill={C.muted}>CDC WONDER. Deaths with any opioid listed are left out.</T>
			</Svg>
		</Plate>
	);
};

// Card 3: the stimulant-positive share and US pedestrian deaths, both indexed to 2009 = 100 (US only).
export const StimIndexChart: React.FC<{title: string; stimP: number; pedP: number}> = ({title, stimP, pedP}) => {
	const base = (arr: Pt[]) => arr.find((d) => d.x === 2009)!.v;
	const stimRaw: Pt[] = data.stimulant.map((d) => ({x: d.year, v: d.share}));
	const pedRaw: Pt[] = data.deaths.map((d) => ({x: d.year, v: d.deaths}));
	const sb = base(stimRaw), pb = base(pedRaw);
	const stim = stimRaw.map((d) => ({x: d.x, v: (d.v / sb) * 100}));
	const ped = pedRaw.map((d) => ({x: d.x, v: (d.v / pb) * 100}));
	const L = 110, R = W - 220, TOP = 180, BOT = H - 80;
	const x = (yr: number) => L + ((yr - 2000) / 24) * (R - L);
	const y = (v: number) => BOT - ((v - 50) / 310) * (BOT - TOP);
	const last = (s: Pt[]) => s[s.length - 1];
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				{[100, 200, 300].map((v) => (
					<g key={v}>
						<line x1={L} x2={R} y1={y(v)} y2={y(v)} stroke={C.grid} strokeWidth={2} />
						<T x={L - 14} y={y(v) + 14} size={38} fill={C.muted} textAnchor="end">{v}</T>
					</g>
				))}
				{[2000, 2009, 2015, 2024].map((yr) => (
					<T key={yr} x={x(yr)} y={BOT + 50} size={40} fill={C.muted} textAnchor="middle">{yr}</T>
				))}
				<Line pts={stim} p={stimP} x={x} y={y} color={C.meth} />
				<Line pts={ped} p={pedP} x={x} y={y} color={C.us} />
				<T x={x(2024) + 16} y={y(last(stim).v) + 14} size={38} opacity={clamp(stimP * 5 - 4)}>Stimulants</T>
				<T x={x(2024) + 16} y={y(last(ped).v) + 14} size={38} opacity={clamp(pedP * 5 - 4)}>Deaths</T>
				<T x={x(2000)} y={y(330)} size={34} fill={C.muted}>2009 = 100</T>
			</Svg>
		</Plate>
	);
};

// Card 4: share of tested pedestrians killed who were stimulant-positive, 2000-2024 (Reel 1's chart).
export const StimulantChart: React.FC<{title: string; p: number}> = ({title, p}) => {
	const pts: Pt[] = data.stimulant.map((d) => ({x: d.year, v: d.share}));
	const L = 120, R = W - 120, TOP = 190, BOT = H - 80;
	const x = (yr: number) => L + ((yr - 2000) / 24) * (R - L);
	const y = (v: number) => BOT - (v / 0.35) * (BOT - TOP);
	const at = (yr: number) => pts.find((d) => d.x === yr)!;
	const reach = (yr: number) => p >= (yr - 2000) / 24;
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				<line x1={L} x2={R} y1={y(0)} y2={y(0)} stroke={C.grid} strokeWidth={2} />
				{[0.1, 0.2, 0.3].map((v) => (
					<g key={v}>
						<line x1={L} x2={R} y1={y(v)} y2={y(v)} stroke={C.grid} strokeWidth={2} />
						<T x={L - 14} y={y(v) + 14} size={38} fill={C.muted} textAnchor="end">{Math.round(v * 100)}%</T>
					</g>
				))}
				{[2000, 2015, 2024].map((yr) => (
					<T key={yr} x={x(yr)} y={BOT + 50} size={40} fill={C.muted} textAnchor="middle">{yr}</T>
				))}
				{reach(2015) && <line x1={x(2015)} x2={x(2015)} y1={TOP} y2={BOT} stroke={C.muted} strokeWidth={4} strokeDasharray="10 10" />}
				<Line pts={pts} p={p} x={x} y={y} color={C.meth} />
				{reach(2014) && <T x={x(2014) - 16} y={y(at(2014).v) - 20} textAnchor="end">{Math.round(at(2014).v * 100)}%</T>}
				{p >= 1 && <T x={x(2024) + 16} y={y(at(2024).v) - 20}>{Math.round(at(2024).v * 100)}%</T>}
			</Svg>
		</Plate>
	);
};

// ---- New for Reel 3 ----

// Czech flag (white over red, blue wedge at the hoist), drawn at width w.
const Flag: React.FC<{x: number; y: number; w: number; opacity: number}> = ({x, y, w, opacity}) => {
	const h = (w * 2) / 3;
	return (
		<g transform={`translate(${x},${y})`} opacity={opacity}>
			<rect width={w} height={h / 2} fill="#FFFFFF" />
			<rect y={h / 2} width={w} height={h / 2} fill="#D7141A" />
			<path d={`M0,0 L${w / 2},${h / 2} L0,${h} Z`} fill="#11457E" />
			<rect width={w} height={h} fill="none" stroke={C.border} strokeWidth={4} />
		</g>
	);
};

// Cards 8-10: Europe (Natural Earth 1:50m), Czechia highlighted, the Czech flag top right. Card 10 adds
// EUDA's 2025 wastewater cities as dots, area proportional to meth residue (mg per 1,000 people a day),
// smallest first; the flag gives way to the size key.
const dotR = (v: number) => Math.max(3, Math.sqrt(v / 600) * 40);
export const EuropeMap: React.FC<{mapP: number; czP: number; flagP: number; citiesP?: number}> = ({mapP, czP, flagP, citiesP = 0}) => {
	const M = assets.map;
	const WW = assets.wastewater;
	const ox = (W - M.w) / 2 - 70, oy = (H - M.h) / 2;
	const czFill = (0.25 + 0.75 * czP) * (1 - 0.6 * citiesP);
	const KX = W - 120;
	const czC = WW.cities.filter((c) => c.cz);
	const czX = czC.reduce((a, c) => a + c.x, 0) / czC.length, czY = czC.reduce((a, c) => a + c.y, 0) / czC.length;
	return (
		<Plate>
			<Svg>
				<g transform={`translate(${ox},${oy})`} opacity={mapP}>
					{M.countries.filter((c) => c.iso !== 'CZE').map((c, i) => (
						<path key={i} d={c.d} fill={c.europe ? '#C9CDC4' : '#E2E4DE'} stroke="#FFFFFF" strokeWidth={1.5} />
					))}
					{M.countries.filter((c) => c.iso === 'CZE').map((c, i) => (
						<path key={i} d={c.d} fill={czP > 0 ? C.eu : '#C9CDC4'} fillOpacity={czFill} stroke={C.border} strokeWidth={czP * 3} />
					))}
					{WW.cities.map((c, i) => {
						const p = clamp(citiesP * 1.5 - (i / WW.cities.length) * 0.5);
						return <circle key={i} cx={c.x} cy={c.y} r={dotR(c.v) * p} fill={C.meth} fillOpacity={0.75} stroke="#FFFFFF" strokeWidth={1.5} opacity={p > 0 ? 1 : 0} />;
					})}
				</g>
				<Flag x={W - 224} y={40} w={180} opacity={flagP * (1 - citiesP)} />
				<g opacity={clamp(citiesP * 2 - 1)}>
					<T x={40} y={60} size={36} weight={800}>Meth in wastewater, 2025</T>
					<T x={40} y={98} size={30} fill={C.muted}>{WW.n} European cities (EUDA)</T>
					{[500, 100, 10].map((v) => (
						<g key={v}>
							<circle cx={KX - 30} cy={250 - dotR(v)} r={dotR(v)} fill="none" stroke={C.meth} strokeWidth={3} />
							<line x1={KX - 30} x2={KX + 22} y1={250 - 2 * dotR(v)} y2={250 - 2 * dotR(v)} stroke={C.muted} strokeWidth={1.5} />
							<T x={KX + 28} y={250 - 2 * dotR(v) + 9} size={26} fill={C.muted}>{v}</T>
						</g>
					))}
					<T x={KX - 10} y={290} size={26} fill={C.muted} textAnchor="middle">mg per 1,000</T>
					<T x={KX - 10} y={318} size={26} fill={C.muted} textAnchor="middle">people a day</T>
				</g>
				<g opacity={clamp(citiesP * 3 - 2)} transform={`translate(${ox},${oy})`}>
					<T x={czX + 100} y={czY + 4} size={40} weight={800} fill={C.eu}>Czechia</T>
					<line x1={czX + 94} y1={czY - 8} x2={czX + 55} y2={czY - 8} stroke={C.eu} strokeWidth={3} />
				</g>
			</Svg>
		</Plate>
	);
};

// Cards 15-19: heavy users × risk per user = stimulant-positive dead pedestrians, US as a multiple of
// Czechia, drawn as a rectangle: width = users, height = risk per user, area = dead pedestrians. Czechia
// is the 1×1 square. Build order follows the words: users (15), the 13× area (16), the 4× height (17).
// Cards 18-19 zoom out and add RAND's low and high ends: 1.3 × 9.8 and 5.5 × 2.4, both still 13× in area,
// on the curve users × risk = 13.
export const AreaChart: React.FC<{title: string; czP: number; usersP: number; areaP: number; riskP: number; zoomP: number; rangeP: number; focusP?: number}> = ({title, czP, usersP, areaP, riskP, zoomP, rangeP, focusP = 0}) => {
	const dim = 1 - 0.7 * focusP; // card 30: everything but the risk side fades back
	const E = N.chartE;
	const X0 = 110, Y0 = H - 90;
	const u = lerp(92, 38, zoomP);
	const px = (v: number) => X0 + v * u, py = (v: number) => Y0 - v * u;
	const w = lerp(1, E.users.best, usersP);
	const h = lerp(1, E.risk.best, areaP);
	const maxX = lerp(4.2, 6.2, zoomP), maxY = lerp(4.6, 10.6, zoomP);
	const step = zoomP > 0.5 ? 2 : 1;
	const ticksX = Array.from({length: Math.floor(maxX / step)}, (_, i) => (i + 1) * step);
	const ticksY = Array.from({length: Math.floor(maxY / step)}, (_, i) => (i + 1) * step);
	const curve = Array.from({length: 60}, (_, i) => 1.22 + (i / 59) * (6.0 - 1.22)).map((x) => ({x, v: E.floor / x}));
	const curveD = curve.slice(0, Math.max(2, Math.round(curve.length * rangeP))).map((p, i) => `${i ? 'L' : 'M'}${px(p.x).toFixed(1)},${py(p.v).toFixed(1)}`).join(' ');
	const RX = 470; // the equation column
	const row = (y: number, op: number, num: string, label: string, color: string, sign = '') => (
		<g opacity={op}>
			<T x={RX} y={y} size={36} fill={C.muted} weight={800}>{sign}</T>
			<T x={RX + 34} y={y} size={58} weight={800} fill={color}>{num}</T>
			<T x={RX + 34} y={y + 38} size={32} fill={C.ink}>{label}</T>
		</g>
	);
	const f1 = (v: number) => v.toFixed(1);
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				<Sub text="US as a multiple of Czechia (1×1)" />
				<defs>
					<clipPath id="area-clip"><rect x={X0} y={150} width={RX - X0 - 10} height={Y0 - 150} /></clipPath>
				</defs>
				<g clipPath="url(#area-clip)">
					{ticksX.map((v) => <line key={`gx${v}`} x1={px(v)} x2={px(v)} y1={Y0} y2={py(maxY)} stroke={C.grid} strokeWidth={2} />)}
					{ticksY.map((v) => <line key={`gy${v}`} x1={X0} x2={px(maxX)} y1={py(v)} y2={py(v)} stroke={C.grid} strokeWidth={2} />)}
					{/* US rectangle: users wide, risk tall */}
					<rect x={X0} y={py(h)} width={(w) * u} height={h * u} fill={areaP > 0 ? C.us : C.meth} fillOpacity={usersP > 0 ? 0.9 * (1 - 0.5 * focusP) : 0} />
					{/* RAND's ends, same area */}
					<g opacity={rangeP}>
						<rect x={X0} y={py(E.risk.hi)} width={E.users.lo * u} height={E.risk.hi * u} fill="none" stroke={C.ink} strokeWidth={4} strokeDasharray="10 7" />
						<rect x={X0} y={py(E.risk.lo)} width={E.users.hi * u} height={E.risk.lo * u} fill="none" stroke={C.ink} strokeWidth={4} strokeDasharray="10 7" />
					</g>
					{rangeP > 0 && <path d={curveD} fill="none" stroke={C.muted} strokeWidth={3} />}
					{/* Czechia's unit square */}
					<rect x={X0} y={py(1)} width={u} height={u} fill={C.eu} opacity={czP} stroke="#FFFFFF" strokeWidth={3} />
				</g>
				<line x1={X0} x2={X0} y1={Y0} y2={155} stroke={C.ink} strokeWidth={3} />
				<line x1={X0} x2={RX - 10} y1={Y0} y2={Y0} stroke={C.ink} strokeWidth={3} />
				{ticksX.filter((v) => px(v) < RX - 20).map((v) => <T key={`tx${v}`} x={px(v)} y={Y0 + 36} size={30} fill={C.muted} textAnchor="middle">{v}×</T>)}
				{ticksY.filter((v) => py(v) > 165).map((v) => <T key={`ty${v}`} x={X0 - 10} y={py(v) + 10} size={30} fill={C.muted} textAnchor="end">{v}×</T>)}
				<T x={X0 + 2} y={Y0 + 72} size={30} fill={C.meth} weight={800}>Heavy meth users per person →</T>
				<T x={-Y0 + 2} y={X0 - 62} size={30} fill={C.muted} weight={800} transform="rotate(-90)" opacity={riskP}>Risk per heavy user →</T>
				{areaP > 0.6 && zoomP < 0.5 && <T x={X0 + (w * u) / 2} y={py(h / 2) + 26} size={78} weight={800} fill="#FFFFFF" textAnchor="middle" opacity={clamp((areaP - 0.6) / 0.4) * (1 - zoomP * 2)}>13×</T>}
				{rangeP > 0 && (
					<g opacity={rangeP}>
						<T x={px(E.users.lo) + 10} y={py(E.risk.hi) + 30} size={30} weight={800}>{f1(E.users.lo)} × {f1(E.risk.hi)}</T>
						<T x={px(E.users.hi) + 8} y={py(E.risk.lo) + 30} size={30} weight={800}>{f1(E.users.hi)} × {f1(E.risk.lo)}</T>
					</g>
				)}
				{row(240, clamp(usersP * 2) * dim, rangeP > 0.5 ? `${f1(E.users.lo)}–${f1(E.users.hi)}×` : `${f1(E.users.best)}×`, 'heavy meth users', C.meth)}
				{row(345, riskP, rangeP > 0.5 ? `${f1(E.risk.lo)}–${f1(E.risk.hi)}×` : `${f1(E.risk.best)}×`, 'risk per heavy user', C.muted, '×')}
				{row(450, clamp((areaP - 0.3) / 0.7) * dim, `${Math.round(E.floor)}×`, 'stimulant-positive dead', C.us, '=')}
				<T x={RX + 34} y={526} size={32} opacity={clamp((areaP - 0.3) / 0.7) * dim}>pedestrians per person</T>
				{focusP > 0 && (
					<g opacity={focusP}>
						<path d={`M${X0 + w * u + 14},${py(h)} h14 V${Y0} h-14`} fill="none" stroke={C.ink} strokeWidth={5} />
						<rect x={RX - 8} y={296} width={W - RX - 20} height={102} rx={10} fill="none" stroke={C.ink} strokeWidth={4} />
					</g>
				)}
			</Svg>
		</Plate>
	);
};

// Card 22: tested dead pedestrians per million a year, 2016-21, US vs. Czechia, by test result. `focusP`
// fades the stimulant-positive pair back so the no-stimulant pair (the card's question) stands out.
export const BucketBars: React.FC<{title: string; barsP: number; focusP: number}> = ({title, barsP, focusP}) => {
	const B = N.buckets;
	const groups = [
		{label: 'Stimulant-positive', us: B.stim.us, cz: B.stim.cz, stim: true},
		{label: 'No stimulants found', us: B.noStim.us, cz: B.noStim.cz, stim: false},
	];
	const L = 120, R = W - 50, TOP = 200, BOT = H - 100;
	const y = (v: number) => BOT - (v / 10.5) * (BOT - TOP);
	const gw = (R - L) / 2, bw = 120;
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				<Sub text="Tested dead pedestrians per million people a year, 2016–21" />
				{[0, 5, 10].map((v) => <g key={v}><line x1={L} x2={R} y1={y(v)} y2={y(v)} stroke={C.grid} strokeWidth={2} /><T x={L - 14} y={y(v) + 12} size={34} fill={C.muted} textAnchor="end">{v}</T></g>)}
				{groups.map((gr, i) => {
					const cx = L + gw * i + gw / 2;
					const us = gr.us * barsP, cz = gr.cz * barsP;
					const usLab = gr.us.toFixed(1), czLab = gr.cz.toFixed(1);
					const labOp = clamp(barsP * 3 - 2);
					return (
						<g key={gr.label} opacity={gr.stim ? 1 - 0.75 * focusP : 1}>
							<rect x={cx - bw - 6} y={y(us)} width={bw} height={BOT - y(us)} fill={C.us} />
							<rect x={cx + 6} y={y(cz)} width={bw} height={BOT - y(cz)} fill={C.eu} />
							<T x={cx - bw / 2 - 6} y={y(us) - 14} size={46} weight={800} fill={C.us} textAnchor="middle" opacity={labOp}>{usLab}</T>
							<T x={cx + bw / 2 + 6} y={y(cz) - 14} size={46} weight={800} fill={C.eu} textAnchor="middle" opacity={labOp}>{czLab}</T>
							<T x={cx} y={BOT + 46} size={38} weight={800} textAnchor="middle">{gr.label}</T>
						</g>
					);
				})}
				<line x1={L} x2={R} y1={BOT} y2={BOT} stroke={C.ink} strokeWidth={3} />
				<T x={W - 50} y={190} size={40} weight={800} fill={C.us} textAnchor="end">US</T>
				<T x={W - 50} y={234} size={40} weight={800} fill={C.eu} textAnchor="end">Czechia</T>
			</Svg>
		</Plate>
	);
};

// Cards 24 and 32: a sign whose words are David's On-Screen Text, the number set large.
export const WordSign: React.FC<{before: string; num: string; after: string; color: string; p: number; sub?: string; range?: [number, number]}> = ({before, num, after, color, p, sub, range}) => {
	const L = 50, R = W - 50;
	return (
		<Plate>
			{sub && <div style={{position: 'absolute', left: 54, top: 34, fontSize: 36, fontWeight: 700, color: C.muted}}>{sub}</div>}
			<div style={{position: 'absolute', left: 50, top: sub ? 90 : 60, fontSize: 64, fontWeight: 800, textTransform: 'uppercase', letterSpacing: 1}}>{before}</div>
			<div style={{position: 'absolute', left: 44, top: sub ? 160 : 130, fontSize: 220, fontWeight: 800, lineHeight: 1, color, opacity: clamp(p * 2), transform: `scale(${0.85 + 0.15 * clamp(p)})`, transformOrigin: 'left center'}}>{num}</div>
			<div style={{position: 'absolute', left: 50, top: sub ? 390 : 360, fontSize: 64, fontWeight: 800, textTransform: 'uppercase', letterSpacing: 1, opacity: clamp(p * 2 - 0.5)}}>{after}</div>
			{range && (
				<Svg>
					<rect x={L} y={490} width={R - L} height={60} rx={10} fill={C.track} />
					<rect x={L} y={490} width={(R - L) * (range[1] / 100) * clamp(p)} height={60} rx={10} fill={color} />
					<line x1={L + (R - L) * (range[0] / 100)} x2={L + (R - L) * (range[0] / 100)} y1={490} y2={550} stroke="#FFFFFF" strokeWidth={3} opacity={range[0] > 0 ? clamp(p * 3 - 2) : 0} />
					<T x={L + (R - L) * (range[0] / 100)} y={476} size={30} fill={C.muted} textAnchor="middle" opacity={range[0] > 0 ? clamp(p * 3 - 2) : 0}>{range[0]}%</T>
					<T x={L + (R - L) * (range[1] / 100) + 6} y={476} size={30} weight={800} fill={color} opacity={clamp(p * 3 - 2)}>{range[1]}%</T>
					<T x={L} y={590} size={32} fill={C.muted}>0%</T>
					<T x={R} y={590} size={32} fill={C.muted} textAnchor="end">100% of the rise</T>
				</Svg>
			)}
		</Plate>
	);
};

// Cards 25-26: two study periods, 2003-05 and 2016-21, per million people a year. Card 25: tested victims by
// group (no stimulants found solid, stimulant-positive dashed). Card 26: all pedestrian deaths.
// A series can carry its own progress `p` (card 25 draws the dashed pair onto card 23's chart) and a `change` note.
type SlopeSeries = {label: string; v: number[]; color: string; dash?: string; nudge?: number; p?: number; change?: string};
// `x1` sets where the right-hand points sit: 380 leaves room for long labels (cards 23, 25); card 26's short
// labels let it spread wider.
export const SlopeChart: React.FC<{title: string; sub: string; series: SlopeSeries[]; max: number; ticks: number[]; p: number; x1?: number}> = ({title, sub, series, max, ticks, p, x1 = 380}) => {
	const X0 = 150, X1 = x1, TOP = 190, BOT = H - 100;
	const y = (v: number) => BOT - (v / max) * (BOT - TOP);
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				<Sub text={sub} />
				{ticks.map((v) => <line key={v} x1={X0 - 40} x2={W - 40} y1={y(v)} y2={y(v)} stroke={C.grid} strokeWidth={2} />)}
				{series.map((s) => {
					const [a, b] = s.v, n = s.nudge ?? 0, sp = s.p ?? p;
					const yb = lerp(y(a), y(b), clamp(sp));
					return (
						<g key={s.label} opacity={sp > 0 ? 1 : 0}>
							<line x1={X0} y1={y(a)} x2={lerp(X0, X1, clamp(sp))} y2={yb} stroke={s.color} strokeWidth={8} strokeDasharray={s.dash} strokeLinecap="round" />
							<circle cx={X0} cy={y(a)} r={11} fill={s.color} />
							{sp >= 1 && <circle cx={X1} cy={y(b)} r={11} fill={s.color} />}
							<T x={X0 - 22} y={y(a) + 13 + n} size={40} weight={800} fill={s.color} textAnchor="end">{a.toFixed(1)}</T>
							<T x={X1 + 22} y={y(b) + 13 + n} size={38} weight={800} fill={s.color} opacity={clamp(sp * 5 - 4)}>{b.toFixed(1)}  {s.label}</T>
							{s.change && <T x={X1 + 22} y={y(b) + 56 + n} size={40} weight={800} fill={s.color} opacity={clamp(sp * 5 - 4)}>{s.change}</T>}
						</g>
					);
				})}
				<T x={X0} y={BOT + 56} size={40} fill={C.muted} textAnchor="middle">2003–05</T>
				<T x={X1} y={BOT + 56} size={40} fill={C.muted} textAnchor="middle">2016–21</T>
			</Svg>
		</Plate>
	);
};

// Cards 37-42: pages of Brumbelow's report, panned and zoomed to the passage being discussed, with a
// highlighter sweeping across it. `view` is the page and the region shown (page pixels at 2x).
export type View = {page: number; cx: number; cy: number; w: number};
type HlKey = keyof typeof assets.highlights;
export const ReportPage: React.FC<{view: View; marks: Array<[HlKey, number]>; credit: string; opacity?: number}> = ({view, marks, credit, opacity = 1}) => {
	const BOX = {x: 30, y: 30, w: W - 60, h: H - 150};
	const s = BOX.w / view.w;
	const left = BOX.x - (view.cx - view.w / 2) * s;
	const top = BOX.y + BOX.h / 2 - view.cy * s;
	return (
		<Plate>
			<div style={{position: 'absolute', left: BOX.x, top: BOX.y, width: BOX.w, height: BOX.h, overflow: 'hidden', borderRadius: 8, background: '#FFFFFF', boxShadow: `0 0 0 2px ${C.grid}`, opacity}}>
				<div style={{position: 'absolute', left: left - BOX.x, top: top - BOX.y, width: assets.page.w * s, height: assets.page.h * s}}>
					<Img src={staticFile(`reel3/pages/p${view.page}.png`)} style={{position: 'absolute', width: '100%', height: '100%'}} />
					{marks.map(([k, p]) => {
						const hl = assets.highlights[k];
						if (hl.page !== view.page || p <= 0) return null;
						const n = hl.rects.length;
						return hl.rects.map((r, i) => {
							const lp = clamp(p * n - i);
							return <div key={`${k}${i}`} style={{position: 'absolute', left: (r[0] - 4) * s, top: (r[1] - 3) * s, width: (r[2] - r[0] + 8) * s * lp, height: (r[3] - r[1] + 6) * s, background: 'rgba(253,185,19,0.45)', mixBlendMode: 'multiply'}} />;
						});
					})}
				</div>
			</div>
			<div style={{position: 'absolute', left: 40, right: 40, bottom: 20, fontSize: 32, fontWeight: 700, lineHeight: 1.1, color: C.muted, whiteSpace: 'pre-line'}}>{credit}</div>
		</Plate>
	);
};

// Cards 44 and 48-49: working in tandem. Per person, 2009 = 1, through 2016 (RAND's last year): heavy meth
// users (RAND) and meth-positive dead pedestrians (FARS, tested and positive). Labels are David's words.
export const TandemChart: React.FC<{usersP: number; methP: number; labels: [string, string]}> = ({usersP, methP, labels}) => {
	const users: Pt[] = N.tandem.users.map((d) => ({x: d.year, v: d.v}));
	const meth: Pt[] = N.tandem.meth.map((d) => ({x: d.year, v: d.v}));
	const L = 100, R = W - 60, TOP = 150, BOT = H - 90;
	const x = (yr: number) => L + ((yr - 2009) / 7) * (R - L);
	const y = (v: number) => BOT - (v / 7) * (BOT - TOP);
	const um = users[users.length - 1].v, mm = meth[meth.length - 1].v;
	return (
		<Plate>
			<Svg>
				<Sub text="Per person, 2009 = 1" y={60} />
				{[1, 3, 5, 7].map((v) => (
					<g key={v}>
						<line x1={L} x2={R} y1={y(v)} y2={y(v)} stroke={C.grid} strokeWidth={2} />
						<T x={L - 14} y={y(v) + 12} size={34} fill={C.muted} textAnchor="end">{v}</T>
					</g>
				))}
				<line x1={L} x2={R} y1={y(0)} y2={y(0)} stroke={C.ink} strokeWidth={3} />
				{[2009, 2012, 2016].map((yr) => <T key={yr} x={x(yr)} y={BOT + 46} size={38} fill={C.muted} textAnchor="middle">{yr}</T>)}
				<Line pts={users} p={usersP} x={x} y={y} color={C.meth} />
				<Line pts={meth} p={methP} x={x} y={y} color={C.us} />
				<T x={x(2016)} y={y(um) + 62} size={36} weight={800} fill={C.meth} textAnchor="end" opacity={clamp(usersP * 5 - 4)}>{labels[0]}</T>
				<T x={x(2016) - 30} y={y(mm) + 10} size={36} weight={800} fill={C.us} textAnchor="end" opacity={clamp(methP * 5 - 4)}>{labels[1]}</T>
			</Svg>
		</Plate>
	);
};

// Card 44: P25's four state groups, 2018-24 (docs/hypothesis-test.md, round 12). Columns: states below/above
// the median meth overdose rate; rows: below/above the median rate of pedestrians killed with no stimulants
// found. Each square's area is the group's meth-positive dead pedestrians per million a year. `ps` = progress
// for [low/low, one-factor pair, high/high].
export const StateGrid: React.FC<{title: string; ps: [number, number, number]}> = ({title, ps}) => {
	const cells = N.stateGrid;
	const max = Math.max(...cells.map((c) => c.Y));
	const LX = 200, CW = (W - LX - 30) / 2, TOP = 250, RH = (H - TOP - 20) / 2, SMAX = Math.min(CW, RH) - 62;
	const p = (c: (typeof cells)[number]) => (c.hiM && c.hiR ? ps[2] : !c.hiM && !c.hiR ? ps[0] : ps[1]);
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				<Sub text="Meth-positive dead pedestrians per million a year, 2018–24" />
				<Sub text={`${cells.reduce((a, c) => a + c.n, 0)} US states, split at the median on each`} y={168} />
				<T x={LX + CW / 2} y={TOP - 18} size={36} weight={800} fill={C.muted} textAnchor="middle">Less meth</T>
				<T x={LX + CW * 1.5} y={TOP - 18} size={36} weight={800} fill={C.meth} textAnchor="middle">More meth</T>
				<T x={LX - 20} y={TOP + RH / 2 - 4} size={36} weight={800} fill={C.us} textAnchor="end">Deadlier</T>
				<T x={LX - 20} y={TOP + RH / 2 + 34} size={36} weight={800} fill={C.us} textAnchor="end">roads</T>
				<T x={LX - 20} y={TOP + RH * 1.5 - 4} size={36} weight={800} fill={C.muted} textAnchor="end">Safer</T>
				<T x={LX - 20} y={TOP + RH * 1.5 + 34} size={36} weight={800} fill={C.muted} textAnchor="end">roads</T>
				<line x1={LX} x2={W - 30} y1={TOP + RH} y2={TOP + RH} stroke={C.grid} strokeWidth={2} />
				<line x1={LX + CW} x2={LX + CW} y1={TOP} y2={H - 20} stroke={C.grid} strokeWidth={2} />
				{cells.map((c) => {
					const cx = LX + CW * (c.hiM ? 1.5 : 0.5), cy = TOP + RH * (c.hiR ? 0.5 : 1.5) - 16;
					const side = SMAX * Math.sqrt(c.Y / max) * clamp(p(c));
					const big = c.Y / max > 0.3;
					return (
						<g key={`${c.hiM}${c.hiR}`} opacity={p(c) > 0 ? 1 : 0}>
							<rect x={cx - side / 2} y={cy - side / 2} width={side} height={side} fill={C.us} />
							<T x={big ? cx : cx + side / 2 + 12} y={cy + (big ? 20 : 16)} size={big ? (c.hiM && c.hiR ? 76 : 54) : 48} weight={800} fill={big ? '#FFFFFF' : C.us} textAnchor={big ? 'middle' : 'start'} opacity={clamp(p(c) * 3 - 2)}>{c.Y.toFixed(1)}</T>
							<T x={cx} y={cy + RH / 2 - 8} size={28} weight={700} fill={C.muted} textAnchor="middle" opacity={clamp(p(c) * 3 - 2)}>{c.n} states</T>
						</g>
					);
				})}
			</Svg>
		</Plate>
	);
};

// Card 46: a list sign, words from the Script.
export const ListSign: React.FC<{items: string[]; shown: number[]}> = ({items, shown}) => (
	<Plate>
		{items.map((it, i) => (
			<div key={it} style={{position: 'absolute', left: 50, right: 40, top: 80 + i * 180, fontSize: 84, fontWeight: 800, textTransform: 'uppercase', letterSpacing: 1, lineHeight: 1, whiteSpace: 'nowrap', opacity: clamp(shown[i]), transform: `translateX(${(1 - clamp(shown[i])) * -30}px)`}}>
				{it}
			</div>
		))}
	</Plate>
);
