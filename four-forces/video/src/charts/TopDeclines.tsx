// Card 11: the four biggest job declines among very-high-AI-exposure occupations, May 2022 -> May 2025
// (BLS OEWS; loan processing excluded, as in the waterfall). All four are office & admin work;
// customer service tops the list at -9.9% ("a 1/10 clip"). Not a pie chart, per David. Not a split of
// the 870K: a by-group split doesn't hold up (see docs/data-challenges.md #12).
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import data from '../data/charts.json';
import {CUE} from '../cues';
import {INK, Ink, Page, Scrawl, ZONES, ink, ramp} from '../sharpie';
import {HOT, fmtJobs} from './parts';

const ROWS = data.breakdown;
const MAX = 300_000;
const NAME_Y0 = ZONES.chart.top + 90;
const ROW_H = 205;
const BAR_X = ZONES.chart.left + 10;
const BAR_W = 560;
export const TOP_DECLINES_DURATION = CUE.c11.dur;

export const TopDeclines: React.FC = () => {
	const frame = useCurrentFrame();
	const bars = useMemo(
		() => ROWS.map((r, i) => ink.rect(BAR_X, NAME_Y0 + 50 + i * ROW_H, (Math.abs(r.change) / MAX) * BAR_W, 70, {seed: 40 + i, stroke: HOT, fill: HOT, strokeWidth: 5, hachureGap: 8})),
		[],
	);
	return (
		<Page>
			{ROWS.map((r, i) => {
				const start = CUE.c11.rows[i];
				const top = NAME_Y0 + i * ROW_H;
				const w = (Math.abs(r.change) / MAX) * BAR_W;
				return (
					<g key={r.soc} opacity={ramp(frame, start, 8)}>
						<Scrawl x={BAR_X} y={top} size={44} anchor="start" seed={`n${i}`}>
							{r.label}
						</Scrawl>
						<clipPath id={`td-${i}`}>
							<rect x={BAR_X - 10} y={top + 30} width={(w + 20) * ramp(frame, start + 4, 24)} height={110} />
						</clipPath>
						<g clipPath={`url(#td-${i})`}>
							<Ink drawable={bars[i]} />
						</g>
						<Scrawl x={BAR_X + w + 24} y={top + 85} size={52} anchor="start" color={HOT} opacity={ramp(frame, start + 28, 8)} seed={`v${i}`}>
							{fmtJobs(r.change, true)}
						</Scrawl>
						<Scrawl x={BAR_X + w + 24} y={top + 140} size={34} anchor="start" color={INK.gray} opacity={ramp(frame, start + 28, 8)} seed={`p${i}`}>
							{`${r.pct}%`}
						</Scrawl>
					</g>
				);
			})}
		</Page>
	);
};
