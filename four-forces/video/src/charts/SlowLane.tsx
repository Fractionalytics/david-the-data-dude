// Card 17, second beat: the slow lane. Paralegals grew +13.8% from May 2022 to May 2025, faster than
// all jobs outside office work (+6.6%, the Reel's one benchmark). BLS OEWS. The radiology grid is
// the beat before (RadiologyGrid.tsx); the SLOW meters are the beat after (Forces, mode "slow").
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import data from '../data/charts.json';
import {INK, Ink, Page, Scrawl, ZONES, ink, ramp} from '../sharpie';
import {CUE} from '../cues';
import {COOL, OTHER} from './parts';

const ROWS = [
	{name: 'Paralegals', value: data.slowLane.paralegals_pct_2022_25, color: COOL},
	{name: 'Other jobs', value: data.benchmark.outside_office_pct_2022_25, color: OTHER},
];
const MAX = 16;
const X0 = ZONES.chart.left + 10;
const W = 600;
const Y0 = ZONES.chart.top + 230;
const ROW_H = 260;
export const SLOW_DURATION = CUE.c17b.dur;
// Paralegals' bar and value land on "14%"; the benchmark follows.
const STARTS = [CUE.c17b.paralegals - 36, CUE.c17b.paralegals - 8];

export const SlowLane: React.FC = () => {
	const frame = useCurrentFrame();
	const bars = useMemo(() => ROWS.map((r, i) => ink.rect(X0, Y0 + 50 + i * ROW_H, (r.value / MAX) * W, 80, {seed: 70 + i, stroke: r.color, fill: r.color, strokeWidth: 5, hachureGap: 8})), []);
	return (
		<Page>
			<Scrawl x={X0} y={ZONES.chart.top + 80} size={40} anchor="start" color={INK.gray} seed="scope">
				May 2022 → May 2025
			</Scrawl>
			{ROWS.map((r, i) => {
				const start = STARTS[i];
				const w = (r.value / MAX) * W;
				return (
					<g key={r.name} opacity={ramp(frame, start, 8)}>
						<Scrawl x={X0} y={Y0 + i * ROW_H} size={52} anchor="start" color={r.color} seed={`n${i}`}>
							{r.name}
						</Scrawl>
						<clipPath id={`sl-${i}`}>
							<rect x={X0 - 10} y={Y0 + 30 + i * ROW_H} width={(w + 20) * ramp(frame, start + 4, 24)} height={120} />
						</clipPath>
						<g clipPath={`url(#sl-${i})`}>
							<Ink drawable={bars[i]} />
						</g>
						<Scrawl x={X0 + w + 26} y={Y0 + 90 + i * ROW_H} size={60} anchor="start" color={r.color} opacity={ramp(frame, start + 28, 8)} seed={`v${i}`}>
							{`+${r.value}%`}
						</Scrawl>
					</g>
				);
			})}
		</Page>
	);
};
