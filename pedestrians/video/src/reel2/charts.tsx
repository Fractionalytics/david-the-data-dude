// Reel 2's charts, in the lab-report look. Each draws from animation progress values (0-1), so a card can
// start from the previous card's end state. Titles are David's (Sheet: On-Screen Text); kickers, labels and
// source lines are ours and say what is measured.
import React from 'react';
import {interpolateColors} from 'remotion';
import assets from './assets.json';
import {C, clamp, headerBottom, Plate, Stamp, Svg, T, W} from './kit';

// Cards 1-3 (and the repeats on 6, 34, 46): US 218.6 vs. Europe 16.7 drug-induced deaths per million, 13.1x.
// US on Europe's definition, 2024 (data/raw/cdc_wonder/SOURCE.md); Europe from EUDA.
// Card 1 draws the bars bare (David: "Leave off titles and labels intentionally"); `headP` brings in the
// title, labels and numbers, `stampP` the 13x. `focusP` (cards 6 and 46) fades the bars back and enlarges
// the stamp.
export const GapBars: React.FC<{title: string; usP: number; euP: number; headP: number; stampP: number; focusP?: number}> = ({title, usP, euP, headP, stampP, focusP = 0}) => {
	const X0 = 200, WMAX = 470, XMAX = 230, top = 180;
	const rows = [
		{lab: 'US', v: 218.6, col: C.us, txt: '219', p: usP},
		{lab: 'EUROPE', v: 16.7, col: C.eu, txt: '17', p: euP},
	];
	return (
		<Plate title={title} kicker="Drug-induced deaths per million people" source="Source: CDC WONDER (US, 2024, on Europe's definition) · EUDA (Europe)" headP={headP}>
			<Svg>
				<g opacity={1 - 0.6 * focusP}>
				{rows.map((r, i) => {
					const y = top + i * 150, w = (r.v / XMAX) * WMAX * r.p;
					return (
						<g key={r.lab}>
							<rect x={X0} y={y} width={Math.max(w, 0)} height={70} fill={r.col} />
							<T x={X0 - 20} y={y + 50} size={40} textAnchor="end" opacity={headP}>{r.lab}</T>
							<T x={X0 + w + 14} y={y + 63} size={80} fill={r.col} opacity={headP}>{r.txt}</T>
						</g>
					);
				})}
				</g>
			</Svg>
			<Stamp x={620} y={470 - 30 * focusP} text="13×" sub="US ÷ Europe" p={stampP} size={110 + 60 * focusP} />
		</Plate>
	);
};

// Card 12: meth overdose deaths per million by state, 2009 -> 2016 -> 2024 (CDC WONDER, T43.6).
// `t` runs 0-2: 0 = 2009, 1 = 2016, 2 = 2024; between whole values the tiles blend. `mapP` fades it in.
const BINS: Array<[number, string]> = [[100, '#7a2e0b'], [50, '#b8501a'], [25, '#e08a3c'], [10, '#f3c48a'], [0, '#fbe8cf']];
const SUPPRESSED = '#d9d9d6';
const fill = (v: number | null) => (v === null ? SUPPRESSED : BINS.find(([lo]) => v >= lo)![1]);
const LEGEND: Array<[string, string]> = [['0', BINS[4][1]], ['10', BINS[3][1]], ['25', BINS[2][1]], ['50', BINS[1][1]], ['100+', BINS[0][1]]];

export const MethMap: React.FC<{title: string; t: number; mapP: number}> = ({title, t, mapP}) => {
	const M = assets.methMap;
	const i = Math.min(Math.floor(t), 1), f = clamp(t - i);
	// 12 x 8 grid; rows 0-1 are nearly empty, so the year and the legend sit there.
	const TILE = 50, GAP = 4, X0 = (W - 12 * (TILE + GAP)) / 2, Y0 = headerBottom(title) + 14;
	const LX = X0 + 5 * (TILE + GAP), LY = Y0 + 4;
	const year = M.years[Math.round(t)];
	return (
		<Plate title={title} kicker="Meth overdose deaths per million people" source="Source: CDC WONDER, multiple cause of death (meth, T43.6)">
			<Svg>
				<g opacity={mapP}>
					{M.tiles.map((s) => {
						const a = fill(s.v[i]), b = fill(s.v[i + 1]);
						const x = X0 + s.col * (TILE + GAP), y = Y0 + s.row * (TILE + GAP);
						const col = interpolateColors(f, [0, 1], [a, b]);
						const dark = (s.v[Math.round(t)] ?? 0) >= 50;
						return (
							<g key={s.abbr}>
								<rect x={x} y={y} width={TILE} height={TILE} rx={5} fill={col} stroke="#CBBFA8" strokeWidth={1.5} />
								<T x={x + TILE / 2} y={y + TILE / 2 + 7} size={20} textAnchor="middle" fill={dark ? '#FFFFFF' : C.ink}>{s.abbr}</T>
							</g>
						);
					})}
					{/* Year in the empty top-left of the grid */}
					<T x={X0 + TILE + GAP} y={Y0 + 62} size={72} fill={C.us}>{year}</T>
					<T x={X0 + TILE + GAP} y={Y0 + 98} size={22} fill={C.muted}>{`US overall: ${M.national[Math.round(t)].toFixed(0)}`}</T>
					{/* Legend in the empty top-right */}
					{LEGEND.map(([lab, col], k) => (
						<g key={lab}>
							<rect x={LX + k * 54} y={LY} width={50} height={20} fill={col} />
							<T x={LX + k * 54} y={LY + 44} size={20} fill={C.muted}>{lab}</T>
						</g>
					))}
					<rect x={LX} y={LY + 64} width={20} height={20} fill={SUPPRESSED} />
					<T x={LX + 28} y={LY + 81} size={20} fill={C.muted}>under 10 deaths</T>
				</g>
			</Svg>
		</Plate>
	);
};

export {W};
