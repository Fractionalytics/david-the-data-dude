// The Reel's charts, drawn as functions of animation progress (0-1), so any card can start from the
// previous card's end state. Titles and callouts are David's words from the Sheet (On-Screen Text and
// Video columns); gray subtitles and axis labels say what is measured.
import React from 'react';
import data from '../data/data.json';
import {BAND_H, BAND_W, C, FONT, Plate, Title} from '../look';

const W = BAND_W;
const H = BAND_H;

type Pt = {x: number; v: number};

// A polyline drawn left to right up to progress p (by x), interpolating the last segment.
const partial = (pts: Pt[], p: number): Pt[] => {
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

const Svg: React.FC<{children: React.ReactNode}> = ({children}) => (
	<svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', left: 0, top: 0}}>
		{children}
	</svg>
);

const T: React.FC<React.SVGProps<SVGTextElement> & {size?: number; weight?: number}> = ({size = 44, weight = 700, children, ...rest}) => (
	<text fontFamily={FONT} fontSize={size} fontWeight={weight} fill={C.ink} {...rest}>
		{children}
	</text>
);

const Sub: React.FC<{text: string; opacity?: number}> = ({text, opacity = 1}) => (
	<T x={40} y={128} size={36} fill={C.muted} opacity={opacity}>{text}</T>
);

const Line: React.FC<{pts: Pt[]; p: number; x: (n: number) => number; y: (n: number) => number; color: string; dash?: string}> = ({pts, p, x, y, color, dash}) => {
	const shown = partial(pts, p);
	const end = shown[shown.length - 1];
	return (
		<g>
			<path d={pathOf(shown, x, y)} fill="none" stroke={color} strokeWidth={8} strokeLinejoin="round" strokeLinecap="round" strokeDasharray={dash} />
			{p > 0 && <circle cx={x(end.x)} cy={y(end.v)} r={9} fill={color} />}
		</g>
	);
};

const fade = (p: number) => Math.max(0, Math.min(1, p));

// Cards 1-5: pedestrian deaths per 100,000, 2000-2024. US first; Europe added on card 4.
export const RatesChart: React.FC<{title: string; titleSize?: number; titleOp: number; usP: number; euP: number}> = ({title, titleSize, titleOp, usP, euP}) => {
	const us: Pt[] = data.rates.us.map((d) => ({x: d.year, v: d.rate}));
	const eu: Pt[] = data.rates.eu.map((d) => ({x: d.year, v: d.rate}));
	const L = 80, R = W - 170, TOP = 160, BOT = H - 80;
	const x = (yr: number) => L + ((yr - 2000) / 24) * (R - L);
	const y = (v: number) => BOT - (v / 2.5) * (BOT - TOP);
	const usEnd = partial(us, usP), euEnd = partial(eu, euP);
	return (
		<Plate>
			<div style={{opacity: titleOp}}><Title text={title} size={titleSize} /></div>
			<Svg>
				<Sub text="Pedestrian deaths per 100,000 people" opacity={titleOp} />
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
				<T x={x(usEnd[usEnd.length - 1].x) + 18} y={y(usEnd[usEnd.length - 1].v) + 14} opacity={fade(usP * 5 - 4)}>US</T>
				{euP > 0 && <T x={x(euEnd[euEnd.length - 1].x) + 18} y={y(euEnd[euEnd.length - 1].v) + 14} opacity={fade(euP * 5 - 4)}>Europe</T>}
			</Svg>
		</Plate>
	);
};

// Card 8: share of new passenger vehicles. Europe (EU27): SUVs. US: all light trucks.
export const SuvChart: React.FC<{title: string; p: number}> = ({title, p}) => {
	const eu: Pt[] = data.suv.eu.map((d) => ({x: d.year, v: d.share}));
	const us: Pt[] = data.suv.us.map((d) => ({x: d.year, v: d.share}));
	const L = 110, R = W - 60, TOP = 160, BOT = H - 80;
	const x = (yr: number) => L + ((yr - 2000) / 24) * (R - L);
	const y = (v: number) => BOT - v * (BOT - TOP);
	const lab = fade(p * 5 - 4);
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				<Sub text="Share of new passenger vehicles sold" />
				{[0, 0.5, 1].map((v) => (
					<g key={v}>
						<line x1={L} x2={R} y1={y(v)} y2={y(v)} stroke={C.grid} strokeWidth={2} />
						<T x={L - 14} y={y(v) + 14} size={38} fill={C.muted} textAnchor="end">{v * 100}%</T>
					</g>
				))}
				{[2001, 2024].map((yr) => (
					<T key={yr} x={x(yr)} y={BOT + 50} size={40} fill={C.muted} textAnchor="middle">{yr}</T>
				))}
				<Line pts={us} p={p} x={x} y={y} color={C.us} />
				<Line pts={eu} p={p} x={x} y={y} color={C.eu} />
				<T x={x(2001)} y={y(0.62)} size={40} opacity={lab}>US: SUVs, pickups and vans</T>
				<T x={x(2014)} y={y(0.06)} size={40} opacity={lab}>Europe: SUVs</T>
			</Svg>
		</Plate>
	);
};

// Cards 18-24: one sign per fact, the number and bar filling to the share. `pop` adds the population bar (card 24).
export const StatSign: React.FC<{pct: number; label: string; p: number; pop?: number; popP?: number}> = ({pct, label, p, pop, popP = 0}) => {
	const L = 50, R = W - 50, BAR_Y = pop ? 335 : 360, BAR_H = pop ? 56 : 70;
	const shown = Math.round(pct * p);
	return (
		<Plate>
			<div style={{position: 'absolute', left: 50, top: 30, fontSize: 210, fontWeight: 800, lineHeight: 1, color: C.us}}>{shown}%</div>
			<div style={{position: 'absolute', left: 54, top: 245, fontSize: 60, fontWeight: 800, textTransform: 'uppercase', letterSpacing: 1, whiteSpace: 'nowrap'}}>{label}</div>
			<Svg>
				<rect x={L} y={BAR_Y} width={R - L} height={BAR_H} rx={10} fill={C.track} />
				<rect x={L} y={BAR_Y} width={(R - L) * (pct / 100) * p} height={BAR_H} rx={10} fill={C.us} />
				{pop ? (
					<g opacity={fade(popP * 3)}>
						<rect x={L} y={BAR_Y + BAR_H + 16} width={R - L} height={BAR_H} rx={10} fill={C.track} />
						<rect x={L} y={BAR_Y + BAR_H + 16} width={(R - L) * (pop / 100) * popP} height={BAR_H} rx={10} fill={C.muted} />
						<T x={L + 16} y={BAR_Y + BAR_H * 2 + 16 - 14} size={36} fill="#FFFFFF">{pop}% of the population</T>
					</g>
				) : (
					<T x={L} y={BAR_Y + BAR_H + 52} size={38} fill={C.muted}>of the rise in US pedestrian deaths, 2009–2022</T>
				)}
				{pop ? <T x={L} y={H - 30} size={34} fill={C.muted}>Share of the rise in pedestrian deaths, 2009–2022</T> : null}
			</Svg>
		</Plate>
	);
};

// Card 25: % change in pedestrian death rate by neighborhood poverty, fifths of the population.
export const PovertyBars: React.FC<{title: string; p: number}> = ({title, p}) => {
	const rows = [...data.poverty].sort((a, b) => b.q - a.q); // poorest first
	const L = 250, R = W - 130, TOP = 160, RH = 64;
	const max = 90;
	const name = (q: number) => (q === 5 ? 'Poorest fifth' : q === 1 ? 'Richest fifth' : '');
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				{rows.map((r, i) => {
					const yy = TOP + i * RH;
					const hi = r.q === 5 || r.q === 1;
					const w = ((R - L) * r.pct) / max * p;
					return (
						<g key={r.q}>
							<T x={L - 18} y={yy + 40} size={38} fill={hi ? C.ink : C.muted} textAnchor="end">{name(r.q)}</T>
							<rect x={L} y={yy + 8} width={w} height={RH - 22} rx={8} fill={r.q === 5 ? C.us : hi ? C.ink : C.track} />
							<T x={L + w + 14} y={yy + 42} size={40} weight={800} opacity={fade(p * 4 - 3)} fill={hi ? C.ink : C.muted}>+{Math.round(r.pct)}%</T>
						</g>
					);
				})}
				<T x={40} y={H - 30} size={34} fill={C.muted}>Rise in death rate by neighborhood income, 2009–11 to 2020–22</T>
			</Svg>
		</Plate>
	);
};

// Cards 29-31 and 40-41: stimulant-positive share of tested pedestrians killed, 2000-2024.
export const StimulantChart: React.FC<{title: string; p: number}> = ({title, p}) => {
	const pts: Pt[] = data.stimulant.map((d) => ({x: d.year, v: d.share}));
	const L = 120, R = W - 120, TOP = 175, BOT = H - 80;
	const x = (yr: number) => L + ((yr - 2000) / 24) * (R - L);
	const y = (v: number) => BOT - (v / 0.35) * (BOT - TOP);
	const at = (yr: number) => pts.find((d) => d.x === yr)!;
	const two = title.includes('\n');
	const reach = (yr: number) => p >= (yr - 2000) / 24;
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				{!two && <Sub text="Share of tested pedestrians killed positive for stimulants" />}
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

// Cards 42-43: the stimulant share and US pedestrian deaths, both indexed to 2009 = 100.
export const StimIndexChart: React.FC<{title: string; pedP: number}> = ({title, pedP}) => {
	const base = (arr: Pt[]) => arr.find((d) => d.x === 2009)!.v;
	const stimRaw: Pt[] = data.stimulant.map((d) => ({x: d.year, v: d.share}));
	const pedRaw: Pt[] = data.deaths.map((d) => ({x: d.year, v: d.deaths}));
	const sb = base(stimRaw), pb = base(pedRaw);
	const stim = stimRaw.map((d) => ({x: d.x, v: (d.v / sb) * 100}));
	const ped = pedRaw.map((d) => ({x: d.x, v: (d.v / pb) * 100}));
	const L = 110, R = W - 220, TOP = 160, BOT = H - 80;
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
				<line x1={x(2015)} x2={x(2015)} y1={TOP} y2={BOT} stroke={C.muted} strokeWidth={4} strokeDasharray="10 10" />
				<Line pts={stim} p={1} x={x} y={y} color={C.meth} />
				<Line pts={ped} p={pedP} x={x} y={y} color={C.us} />
				<T x={x(2024) + 16} y={y(last(stim).v) + 14} size={38}>Stimulants</T>
				<T x={x(2024) + 16} y={y(last(ped).v) + 14} size={38} opacity={fade(pedP * 5 - 4)}>Deaths</T>
				<T x={x(2000)} y={y(330)} size={34} fill={C.muted}>2009 = 100</T>
			</Svg>
		</Plate>
	);
};

// Cards 32-37: by state, change in meth overdose deaths vs. change in pedestrian deaths (per 100,000).
// West Virginia is left out (David, 2026-11-09). The pre-registered test (P10) required the link to hold
// both with it (r = 0.35) and without it (r = 0.65); this chart shows the second check, and the first
// comment says so.
export const MethScatter: React.FC<{title: string; dotsP: number; fitP: number}> = ({title, dotsP, fitP}) => {
	const s = data.states.filter((d) => d.state !== 'WV');
	const L = 90, R = W - 40, TOP = 170, BOT = H - 100;
	const xMax = 25, yMin = -0.5, yMax = 3;
	const x = (v: number) => L + (v / xMax) * (R - L);
	const y = (v: number) => BOT - ((v - yMin) / (yMax - yMin)) * (BOT - TOP);
	const n = s.length;
	const mx = s.reduce((a, d) => a + d.meth, 0) / n, my = s.reduce((a, d) => a + d.ped, 0) / n;
	const b = s.reduce((a, d) => a + (d.meth - mx) * (d.ped - my), 0) / s.reduce((a, d) => a + (d.meth - mx) ** 2, 0);
	const a0 = my - b * mx;
	const call = new Set(['NM', 'AZ', 'NY']);
	const order = [...s].sort((p, q) => p.meth - q.meth);
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				<Sub text="Change per 100,000 people by state, 2009–11 to 2020–22" />
				<line x1={L} x2={R} y1={y(0)} y2={y(0)} stroke={C.grid} strokeWidth={2} />
				<line x1={L} x2={L} y1={TOP} y2={BOT} stroke={C.grid} strokeWidth={2} />
				{fitP > 0 && (
					<line x1={x(0)} x2={x(xMax * fitP)} y1={y(a0)} y2={y(a0 + b * xMax * fitP)} stroke={C.ink} strokeWidth={5} strokeDasharray="14 10" />
				)}
				{order.map((d, i) => {
					const t = fade(dotsP * n - i);
					return <circle key={d.state} cx={x(d.meth)} cy={y(d.ped)} r={11 * t} fill={C.meth} stroke={C.plate} strokeWidth={3} />;
				})}
				{s.filter((d) => call.has(d.state)).map((d) => (
					<T key={d.state} x={x(d.meth) + (d.state === 'AZ' ? -16 : 16)} y={y(d.ped) + (d.state === 'AZ' ? -18 : 14)} size={38}
						textAnchor={d.state === 'AZ' ? 'end' : 'start'} opacity={fade(dotsP * 3 - 2)}>{d.state}</T>
				))}
				<T x={(L + R) / 2} y={BOT + 56} size={38} fill={C.muted} textAnchor="middle">Rise in meth overdose deaths →</T>
				<T x={L + 14} y={TOP + 24} size={38} fill={C.muted}>↑ Rise in pedestrian deaths</T>
			</Svg>
		</Plate>
	);
};

// Cards 48-50: US overdose deaths involving meth (psychostimulants, T43.6), CDC provisional, 2015-2025.
export const MethChart: React.FC<{title: string; p: number}> = ({title, p}) => {
	const pts: Pt[] = data.meth.map((d) => ({x: d.year, v: d.deaths / 1000}));
	const L = 110, R = W - 150, TOP = 170, BOT = H - 80;
	const x = (yr: number) => L + ((yr - 2015) / 10) * (R - L);
	const y = (v: number) => BOT - (v / 40) * (BOT - TOP);
	const pk = pts.find((d) => d.x === 2023)!, last = pts[pts.length - 1];
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				<Sub text="US overdose deaths involving meth, thousands" />
				{[0, 20, 40].map((v) => (
					<g key={v}>
						<line x1={L} x2={R} y1={y(v)} y2={y(v)} stroke={C.grid} strokeWidth={2} />
						<T x={L - 14} y={y(v) + 14} size={38} fill={C.muted} textAnchor="end">{v}</T>
					</g>
				))}
				{[2015, 2023, 2025].map((yr) => (
					<T key={yr} x={x(yr)} y={BOT + 50} size={40} fill={C.muted} textAnchor="middle">{yr}</T>
				))}
				<Line pts={pts} p={p} x={x} y={y} color={C.meth} />
				{p >= 0.8 && <T x={x(2023)} y={y(pk.v) - 22} textAnchor="middle">{pk.v.toFixed(1)}k</T>}
				{p >= 1 && <T x={x(2025) + 16} y={y(last.v) + 14}>{last.v.toFixed(1)}k</T>}
			</Svg>
		</Plate>
	);
};

// Card 51: pedestrians vs. everyone else killed on US roads, indexed to 2022 = 100. 2025 = early
// estimates (pedestrians GHSA, all deaths NHTSA), drawn dashed.
export const RoadChart: React.FC<{title: string; p: number}> = ({title, p}) => {
	const r = data.road;
	const b = r.find((d) => d.year === 2022)!;
	const ped: Pt[] = r.map((d) => ({x: d.year, v: (d.ped / b.ped) * 100}));
	const oth: Pt[] = r.map((d) => ({x: d.year, v: (d.other / b.other) * 100}));
	const L = 110, R = W - 220, TOP = 170, BOT = H - 80;
	const x = (yr: number) => L + ((yr - 2015) / 10) * (R - L);
	const y = (v: number) => BOT - ((v - 60) / 50) * (BOT - TOP);
	const upTo = (s: Pt[], yr: number) => s.filter((d) => d.x <= yr);
	const from = (s: Pt[], yr: number) => s.filter((d) => d.x >= yr);
	const solid = Math.min(1, p / 0.9), dash = fade((p - 0.9) / 0.1);
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				<Sub text="US road deaths, 2022 = 100" />
				{[80, 100].map((v) => (
					<g key={v}>
						<line x1={L} x2={R} y1={y(v)} y2={y(v)} stroke={C.grid} strokeWidth={2} />
						<T x={L - 14} y={y(v) + 14} size={38} fill={C.muted} textAnchor="end">{v}</T>
					</g>
				))}
				{[2015, 2022, 2025].map((yr) => (
					<T key={yr} x={x(yr)} y={BOT + 50} size={40} fill={C.muted} textAnchor="middle">{yr}</T>
				))}
				<Line pts={upTo(oth, 2024)} p={solid} x={x} y={y} color={C.muted} />
				<Line pts={upTo(ped, 2024)} p={solid} x={x} y={y} color={C.us} />
				{dash > 0 && <Line pts={from(oth, 2024)} p={dash} x={x} y={y} color={C.muted} dash="2 16" />}
				{dash > 0 && <Line pts={from(ped, 2024)} p={dash} x={x} y={y} color={C.us} dash="2 16" />}
				<T x={x(2025) + 16} y={y(ped[ped.length - 1].v) - 10} size={38} opacity={fade(dash * 2 - 1)}>Pedestrians</T>
				<T x={x(2025) + 16} y={y(oth[oth.length - 1].v) + 34} size={38} opacity={fade(dash * 2 - 1)}>Everyone else</T>
				<T x={x(2025)} y={y(108)} size={30} fill={C.muted} textAnchor="middle" opacity={dash}>2025 estimate</T>
			</Svg>
		</Plate>
	);
};

// Card 56: slopegraph, 2009 vs. 2024, per 100,000.
export const Slope: React.FC<{title: string; leftNote: string; rightNote: string; p: number}> = ({title, leftNote, rightNote, p}) => {
	const get = (k: 'us' | 'eu', yr: number) => data.rates[k].find((d) => d.year === yr)!.rate;
	const X0 = 190, X1 = W - 300, TOP = 210, BOT = H - 90;
	const y = (v: number) => BOT - (v / 2.4) * (BOT - TOP);
	const rows: Array<[string, 'us' | 'eu', string]> = [['US', 'us', C.us], ['Europe', 'eu', C.eu]];
	const lp = Math.min(1, p / 0.7), np = fade((p - 0.7) / 0.3);
	return (
		<Plate>
			<Title text={title} />
			<Svg>
				<Sub text="Pedestrian deaths per 100,000 people" />
				{rows.map(([name, k, col]) => {
					const y0 = y(get(k, 2009)), y1 = y(get(k, 2024));
					return (
						<g key={k}>
							<line x1={X0} x2={X0 + (X1 - X0) * lp} y1={y0} y2={y0 + (y1 - y0) * lp} stroke={col} strokeWidth={8} strokeLinecap="round" />
							<circle cx={X0} cy={y0} r={11} fill={col} />
							{lp >= 1 && <circle cx={X1} cy={y1} r={11} fill={col} />}
							<T x={X1 + 22} y={y1 + 14} opacity={fade(lp * 5 - 4)}>{name} {get(k, 2024).toFixed(2)}</T>
						</g>
					);
				})}
				<T x={X0 - 22} y={y(get('us', 2009)) - 4} textAnchor="end">{get('eu', 2009).toFixed(2)}</T>
				<T x={X0 - 22} y={y(get('us', 2009)) + 40} textAnchor="end">{get('us', 2009).toFixed(2)}</T>
				<T x={X0} y={BOT + 56} size={42} fill={C.muted} textAnchor="middle">2009</T>
				<T x={X1} y={BOT + 56} size={42} fill={C.muted} textAnchor="middle">2024</T>
				<T x={X0} y={TOP - 20} size={64} weight={800} textAnchor="middle">{leftNote}</T>
				<T x={X1} y={TOP - 20} size={64} weight={800} textAnchor="middle" fill={C.us} opacity={np}>{rightNote}</T>
			</Svg>
		</Plate>
	);
};
