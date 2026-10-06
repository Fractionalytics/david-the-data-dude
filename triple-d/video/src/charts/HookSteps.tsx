// Chart 1b (the hook, slowed down): the DDD% line drawn step by step.
//   Season 1 is labeled, pause, the line falls to season 2 (labeled), pause, to season 3
//   (labeled), pause, then the rest of the line draws to season 43 in 2 s and is labeled.
// Same axes, scale and position as hook-line, so the two can be cut together.
import React, {useMemo} from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import data from '../data/triple-d.json';
import {Axes, INK, Ink, Page, Scrawl, ink, plotFor, scaleY} from '../sharpie';

const PLOT = plotFor('none');
const FPS = 30;
const AXES_FRAMES = 12;
const LABEL_FRAMES = 8; // fade-in for each label
const PAUSE = 2 * FPS; // hold after each early label
const STEP_FRAMES = FPS; // draw time for each of the first two drops
const REST_FRAMES = 2 * FPS; // draw time for seasons 3 -> 43
const HOLD = FPS; // hold at the end

// Timeline (frames): label S1, pause, draw S1->S2, label, pause, draw S2->S3, label, pause, rest, label.
const T_S1 = AXES_FRAMES;
const T_DRAW12 = T_S1 + LABEL_FRAMES + PAUSE;
const T_S2 = T_DRAW12 + STEP_FRAMES;
const T_DRAW23 = T_S2 + LABEL_FRAMES + PAUSE;
const T_S3 = T_DRAW23 + STEP_FRAMES;
const T_REST = T_S3 + LABEL_FRAMES + PAUSE;
const T_END = T_REST + REST_FRAMES;
export const HOOK_STEPS_DURATION = T_END + LABEL_FRAMES + HOLD;

const FIRST = 1;
const LAST = 43;
const sx = (season: number) => PLOT.left + 30 + ((season - FIRST) / (LAST - FIRST)) * (PLOT.right - PLOT.left - 40);
const POINTS = data.seasons.map((s) => [sx(s.season), scaleY(PLOT, s.pctDDD, 100)] as [number, number]);
const STYLE = {stroke: INK.red, strokeWidth: 13, roughness: 0.7};

export const HookSteps: React.FC = () => {
	const frame = useCurrentFrame();
	const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
	// The two early drops ease in and out (deliberate); the long run to season 43 is linear, like hook-line.
	const drawn = (start: number, frames: number, eased = true) =>
		interpolate(frame, [start, start + frames], [0, 1], eased ? {...clamp, easing: Easing.inOut(Easing.quad)} : clamp);
	const shown = (start: number) => interpolate(frame, [start, start + LABEL_FRAMES], [0, 1], clamp);

	const segments = useMemo(
		() => [
			ink.path(POINTS.slice(0, 2), {...STYLE, seed: 21}),
			ink.path(POINTS.slice(1, 3), {...STYLE, seed: 22}),
			ink.path(POINTS.slice(2), {...STYLE, seed: 23}),
		],
		[],
	);
	const dots = useMemo(
		() => [0, 1, 2, POINTS.length - 1].map((i, k) => ink.dot(POINTS[i][0], POINTS[i][1], 24, {seed: 30 + k, stroke: INK.red, fill: INK.red})),
		[],
	);
	const progress = [drawn(T_DRAW12, STEP_FRAMES), drawn(T_DRAW23, STEP_FRAMES), drawn(T_REST, REST_FRAMES, false)];
	const labelAt = [T_S1, T_S2, T_S3, T_END];
	const pct = (i: number) => `${Math.round(data.seasons[i].pctDDD)}%`;

	return (
		<Page>
			<Axes
				frame={frame}
				plot={PLOT}
				duration={10}
				yTicks={[0, 50, 100].map((v) => ({at: scaleY(PLOT, v, 100), label: `${v}%`}))}
				xTicks={[1, 10, 20, 30, 40].map((s) => ({at: sx(s), label: String(s)}))}
				yTitle="Diners, Drive-Ins & Dives"
				xTitle="Season"
			/>
			{segments.map((d, k) => (
				<Ink key={k} drawable={d} progress={progress[k]} connect />
			))}
			{[0, 1, 2].map((k) => (
				// The first three points sit ~17px apart, so their labels go to the right, at each point's height.
				<g key={k} opacity={shown(labelAt[k])}>
					<Ink drawable={dots[k]} />
					<Scrawl x={POINTS[k][0] + 34} y={POINTS[k][1]} size={52} color={INK.red} anchor="start" seed={`s${k}`}>
						{pct(k)}
					</Scrawl>
				</g>
			))}
			<g opacity={shown(T_END)}>
				<Ink drawable={dots[3]} />
				<Scrawl x={POINTS[POINTS.length - 1][0]} y={POINTS[POINTS.length - 1][1] - 125} size={56} color={INK.red} seed="s43">
					{pct(POINTS.length - 1)}
				</Scrawl>
			</g>
		</Page>
	);
};
