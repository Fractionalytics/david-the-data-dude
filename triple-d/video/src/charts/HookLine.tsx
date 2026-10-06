// Chart 1 (the hook): % of each season's restaurants that Jev calls a Diner, Drive-In or Dive.
// The line draws itself from season 1 to season 43 in LINE_FRAMES frames (60 = 2 seconds).
import React, {useMemo} from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import data from '../data/triple-d.json';
import {Axes, INK, Ink, Page, Scrawl, ink, plotFor, scaleY} from '../sharpie';

const PLOT = plotFor('none');

const LINE_START = 8;
const LINE_FRAMES = 60;
export const HOOK_DURATION = LINE_START + LINE_FRAMES + 30;

const FIRST = 1;
const LAST = 43;
const sx = (season: number) => PLOT.left + 30 + ((season - FIRST) / (LAST - FIRST)) * (PLOT.right - PLOT.left - 40);

export const HookLine: React.FC = () => {
	const frame = useCurrentFrame();
	const points = useMemo(
		() => data.seasons.map((s) => [sx(s.season), scaleY(PLOT, s.pctDDD, 100)] as [number, number]),
		[],
	);
	const line = useMemo(() => ink.path(points, {seed: 5, stroke: INK.red, strokeWidth: 13, roughness: 0.7}), [points]);
	const progress = interpolate(frame, [LINE_START, LINE_START + LINE_FRAMES], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	const first = data.seasons[0];
	const last = data.seasons[data.seasons.length - 1];
	const startDot = useMemo(() => ink.dot(points[0][0], points[0][1], 26, {seed: 6, stroke: INK.red, fill: INK.red}), [points]);
	const endDot = useMemo(
		() => ink.dot(points[points.length - 1][0], points[points.length - 1][1], 26, {seed: 7, stroke: INK.red, fill: INK.red}),
		[points],
	);
	const endLabel = interpolate(frame, [LINE_START + LINE_FRAMES - 4, LINE_START + LINE_FRAMES + 6], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	return (
		<Page>
			<Axes
				frame={frame}
				duration={10}
				plot={PLOT}
				yTicks={[0, 50, 100].map((v) => ({at: scaleY(PLOT, v, 100), label: `${v}%`}))}
				xTicks={[1, 10, 20, 30, 40].map((s) => ({at: sx(s), label: String(s)}))}
				yTitle="Diners, Drive-Ins & Dives"
				xTitle="Season"
			/>
			<Ink drawable={line} progress={progress} connect />
			{progress > 0 && <Ink drawable={startDot} />}
			<Scrawl x={points[0][0] + 20} y={points[0][1] - 60} size={56} color={INK.red} anchor="start" opacity={progress > 0 ? 1 : 0} seed="p0">
				{`${Math.round(first.pctDDD)}%`}
			</Scrawl>
			{endLabel > 0 && <Ink drawable={endDot} />}
			<Scrawl x={points[points.length - 1][0]} y={points[points.length - 1][1] - 125} size={56} color={INK.red} opacity={endLabel} seed="p1">
				{`${Math.round(last.pctDDD)}%`}
			</Scrawl>
		</Page>
	);
};
