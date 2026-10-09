// Cards 2 and 7: share of featured ideas classified as services, per era (2% -> 3% -> 41%).
// Each bar rises in turn; the newsletter era's bar rises last and slowest.
import React, {useMemo} from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import data from '../data/ideabrowser.json';
import {INK, Ink, Page, Scrawl, TYPE_INK, ZONES, ink, ramp} from '../sharpie';

const PLOT = {left: ZONES.chart.left + 110, right: ZONES.chart.right - 20, top: ZONES.chart.top + 120, bottom: ZONES.chart.bottom - 190};
const MAX = 50; // % at the top of the y axis
const BAR_W = 150;
const ERA_LABELS = [
	['Era 1', "Jul '25–Jan '26"],
	['Era 2', "Jan–Jul '26"],
	['Newsletter', `Jul 28–${new Date(data.cutoff + 'T12:00').toLocaleDateString('en-US', {month: 'short', day: 'numeric'})} '26`],
];
// [start frame, frames to grow] per bar
const GROW = [[14, 18], [36, 18], [62, 40]];
export const ERA_DURATION = 62 + 40 + 45;

const y = (pct: number) => PLOT.bottom - (pct / MAX) * (PLOT.bottom - PLOT.top);
const cx = (i: number) => PLOT.left + ((i + 0.5) / 3) * (PLOT.right - PLOT.left);

export const ServicesByEra: React.FC = () => {
	const frame = useCurrentFrame();
	const eras = data.eras.map((e) => ({...e, pct: (100 * e.service) / e.total}));
	const axes = useMemo(
		() => [
			ink.line(PLOT.left, PLOT.bottom + 6, PLOT.left, PLOT.top - 20, {seed: 11}),
			ink.line(PLOT.left - 6, PLOT.bottom, PLOT.right, PLOT.bottom, {seed: 12}),
			...[0, 25, 50].map((v, i) => ink.line(PLOT.left - 22, y(v), PLOT.left, y(v), {seed: 20 + i, strokeWidth: 6})),
		],
		[],
	);
	const bars = useMemo(
		() =>
			eras.map((e, i) =>
				ink.rect(cx(i) - BAR_W / 2, y(e.pct), BAR_W, PLOT.bottom - y(e.pct), {
					seed: 30 + i,
					stroke: TYPE_INK.service,
					fill: TYPE_INK.service,
				}),
			),
		[],
	);
	const axisIn = ramp(frame, 0, 12);

	return (
		<Page>
			{axes.map((a, i) => (
				<Ink key={i} drawable={a} progress={axisIn} />
			))}
			{[0, 25, 50].map((v) => (
				<Scrawl key={v} x={PLOT.left - 34} y={y(v)} size={40} anchor="end" opacity={axisIn} seed={`y${v}`}>
					{`${v}%`}
				</Scrawl>
			))}
			<Scrawl x={PLOT.left - 10} y={PLOT.top - 60} size={40} anchor="start" opacity={axisIn} seed="yt">
				Service ideas, % of featured
			</Scrawl>
			{eras.map((e, i) => {
				const [start, frames] = GROW[i];
				const grow = interpolate(frame, [start, start + frames], [0, 1], {
					extrapolateLeft: 'clamp',
					extrapolateRight: 'clamp',
					easing: Easing.out(Easing.cubic),
				});
				const top = PLOT.bottom - grow * (PLOT.bottom - y(e.pct));
				const shown = (grow * e.pct).toFixed(0);
				return (
					<g key={i}>
						<defs>
							<clipPath id={`bar${i}`}>
								<rect x={cx(i) - BAR_W} y={top - 20} width={BAR_W * 2} height={PLOT.bottom - top + 40} />
							</clipPath>
						</defs>
						{grow > 0 && (
							<g clipPath={`url(#bar${i})`}>
								<Ink drawable={bars[i]} />
							</g>
						)}
						<Scrawl x={cx(i)} y={top - 60} size={i === 2 ? 76 : 56} color={TYPE_INK.service} opacity={grow > 0 ? 1 : 0} seed={`p${i}`}>
							{`${shown}%`}
						</Scrawl>
						<Scrawl x={cx(i)} y={PLOT.bottom + 55} size={42} opacity={axisIn} seed={`x${i}`}>
							{ERA_LABELS[i][0]}
						</Scrawl>
						<Scrawl x={cx(i)} y={PLOT.bottom + 105} size={27} color={INK.gray} opacity={axisIn} seed={`d${i}`}>
							{ERA_LABELS[i][1]}
						</Scrawl>
						<Scrawl x={cx(i)} y={PLOT.bottom + 148} size={28} color={INK.gray} opacity={ramp(frame, start + frames, 8)} seed={`n${i}`}>
							{`${e.service} of ${e.total}`}
						</Scrawl>
					</g>
				);
			})}
		</Page>
	);
};
