// Card 4: one square per day, featured idea classified as a service in red. Two equal
// windows: the N days before July 28 fill first (2 red), a pause, then the N days since (30 red).
// The cut-off date is shown under the grid, so every "since" in the script has a fixed end.
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import data from '../data/ideabrowser.json';
import {INK, Ink, Page, Scrawl, TYPE_INK, ZONES, ink, ramp} from '../sharpie';

const COLS = 15;
const CELL = (ZONES.chart.right - ZONES.chart.left) / COLS;
const SQUARE = CELL - 10;
// Panel label row, then the grid 50px below it. Two panels plus the legend fit inside ZONES.chart.
const PANEL_TOP = [ZONES.chart.top + 30, ZONES.chart.top + 400];
const GRID_OFFSET = 50;
const FILL_FRAMES = [60, 90]; // frames to fill each panel, one day at a time
const START = [12, 12 + 60 + 30];
export const STRIP_DURATION = START[1] + FILL_FRAMES[1] + 50;

const fmt = (iso: string) => new Date(iso + 'T12:00').toLocaleDateString('en-US', {month: 'short', day: 'numeric'});

export const DailyStrip: React.FC = () => {
	const frame = useCurrentFrame();
	const before = data.strip.filter((d) => d.date < data.switch);
	const after = data.strip.filter((d) => d.date >= data.switch);
	const panels = [before, after];
	const reds = useMemo(
		() =>
			panels.map((days, p) =>
				days.map((d, i) =>
					d.type === 'Service'
						? ink.rect(
								ZONES.chart.left + (i % COLS) * CELL + 5,
								PANEL_TOP[p] + GRID_OFFSET + Math.floor(i / COLS) * CELL + 5,
								SQUARE,
								SQUARE,
								{seed: 100 * p + i, stroke: TYPE_INK.service, fill: TYPE_INK.service, strokeWidth: 5, hachureGap: 7},
						  )
						: null,
				),
			),
		[],
	);
	const labels = [`${data.window_days} days before ${fmt(data.switch)}`, `${fmt(data.switch)} – ${fmt(data.cutoff)}`];

	return (
		<Page>
			{panels.map((days, p) => {
				const shown = Math.floor(ramp(frame, START[p], FILL_FRAMES[p]) * days.length);
				const count = days.slice(0, shown).filter((d) => d.type === 'Service').length;
				const head = ramp(frame, START[p] - 10, 10);
				return (
					<g key={p}>
						<Scrawl x={ZONES.chart.left} y={PANEL_TOP[p] + 20} size={40} anchor="start" opacity={head} seed={`l${p}`}>
							{labels[p]}
						</Scrawl>
						<Scrawl x={ZONES.chart.right} y={PANEL_TOP[p] + 14} size={64} anchor="end" color={TYPE_INK.service} opacity={head} seed={`c${p}`}>
							{String(count)}
						</Scrawl>
						{days.slice(0, shown).map((d, i) => {
							const x = ZONES.chart.left + (i % COLS) * CELL + 5;
							const yy = PANEL_TOP[p] + GRID_OFFSET + Math.floor(i / COLS) * CELL + 5;
							const red = reds[p][i];
							return red ? (
								<Ink key={i} drawable={red} />
							) : (
								<rect key={i} x={x} y={yy} width={SQUARE} height={SQUARE} rx={6} fill={TYPE_INK.other} />
							);
						})}
					</g>
				);
			})}
			<g opacity={ramp(frame, START[1] + FILL_FRAMES[1], 15)}>
				<rect x={ZONES.chart.left} y={ZONES.chart.bottom - 118} width={34} height={34} rx={6} fill={TYPE_INK.service} />
				<Scrawl x={ZONES.chart.left + 50} y={ZONES.chart.bottom - 100} size={34} anchor="start" seed="lg1">
					service idea
				</Scrawl>
				<rect x={ZONES.chart.left + 330} y={ZONES.chart.bottom - 118} width={34} height={34} rx={6} fill={TYPE_INK.other} />
				<Scrawl x={ZONES.chart.left + 380} y={ZONES.chart.bottom - 100} size={34} anchor="start" seed="lg2">
					any other idea
				</Scrawl>
				<Scrawl x={ZONES.chart.left} y={ZONES.chart.bottom - 40} size={30} anchor="start" color={INK.gray} seed="cut">
					{`One featured idea per day. Data through ${fmt(data.cutoff)}, 2026`}
				</Scrawl>
			</g>
		</Page>
	);
};
