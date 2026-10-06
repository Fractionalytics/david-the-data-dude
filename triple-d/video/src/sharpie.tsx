// The shared "Sharpie kit": marker colors, the handwriting font, hand-drawn strokes, and axes.
// Every chart builds from these pieces so they all share one look.
import React, {useMemo} from 'react';
import {AbsoluteFill, interpolate, random} from 'remotion';
import {evolvePath} from '@remotion/paths';
import {loadFont} from '@remotion/google-fonts/PermanentMarker';
import rough from 'roughjs';
import type {Drawable, Options} from 'roughjs/bin/core';

const markerFont = loadFont('normal', {weights: ['400'], subsets: ['latin']});
export const MARKER_FONT = markerFont.fontFamily;
// Resolves once the font is loaded, so text can be measured (e.g. for strike-throughs).
export const markerFontReady = () => markerFont.waitUntilDone();

// Classic Sharpie colors.
export const INK = {
	black: '#1d1d1f',
	red: '#d7263d',
	blue: '#1b5fbf',
	green: '#16924a',
	gray: '#8f8f8f',
};
export const CATEGORIES = ['Diner', 'Drive-In', 'Dive', 'Other'] as const;
export type Category = (typeof CATEGORIES)[number];
export const CATEGORY_INK: Record<Category, string> = {
	Diner: INK.red,
	'Drive-In': INK.blue,
	Dive: INK.green,
	Other: INK.gray,
};

// Vertical video (Instagram Reels) and the plot area inside it.
export const VIDEO = {width: 1080, height: 1920, fps: 30};
export type Plot = {left: number; right: number; top: number; bottom: number};

// Charts are top-justified so the bottom of the frame stays free for a talking head.
// The plot is always 800px tall; it starts lower when a title (and legend) sit above it.
export const TITLE_Y = 110;
export const LEGEND_Y = 205;
const PLOT_HEIGHT = 800;
const PLOT_TOP = {none: 150, title: 230, legend: 310};
export const plotFor = (header: keyof typeof PLOT_TOP, left = 250, right = 1000): Plot => ({
	left,
	right,
	top: PLOT_TOP[header],
	bottom: PLOT_TOP[header] + PLOT_HEIGHT,
});

const generator = rough.generator();

// Defaults that make rough.js look like a marker rather than a pencil: one confident
// stroke (no double-sketching), thick nib, a little wobble, dense scribble fills.
export const MARKER: Options = {
	roughness: 0.9,
	bowing: 0.6,
	strokeWidth: 8,
	disableMultiStroke: true,
	fillStyle: 'hachure',
	hachureGap: 9,
	fillWeight: 4,
	disableMultiStrokeFill: true,
};

export const ink = {
	line: (x1: number, y1: number, x2: number, y2: number, o: Options = {}) =>
		generator.line(x1, y1, x2, y2, {...MARKER, ...o}),
	path: (points: [number, number][], o: Options = {}) => generator.linearPath(points, {...MARKER, ...o}),
	rect: (x: number, y: number, w: number, h: number, o: Options = {}) =>
		generator.rectangle(x, y, w, h, {...MARKER, ...o}),
	dot: (x: number, y: number, d: number, o: Options = {}) =>
		generator.circle(x, y, d, {...MARKER, fillStyle: 'solid', ...o}),
};

// Renders a rough.js drawable. `progress` (0..1) draws the strokes in like a pen moving.
// rough.js draws a multi-point line as separate segments, and SVG restarts the dash pattern on
// every segment, so `connect` joins them into one stroke for the draw-in to work.
export const Ink: React.FC<{drawable: Drawable; progress?: number; connect?: boolean}> = ({drawable, progress = 1, connect = false}) => {
	const paths = useMemo(
		() => generator.toPaths(drawable).map((p) => (connect ? {...p, d: p.d.replace(/(?!^)M/g, 'L')} : p)),
		[drawable, connect],
	);
	if (progress <= 0) return null;
	return (
		<g filter="url(#marker-edge)">
			{paths.map((p, i) => {
				const evo = progress < 1 ? evolvePath(progress, p.d) : undefined;
				return (
					<path
						key={i}
						d={p.d}
						stroke={p.stroke}
						strokeWidth={p.strokeWidth}
						fill={p.fill ?? 'none'}
						strokeLinecap="round"
						strokeLinejoin="round"
						strokeDasharray={evo?.strokeDasharray}
						strokeDashoffset={evo?.strokeDashoffset}
					/>
				);
			})}
		</g>
	);
};

// Handwritten text with a tiny, stable tilt so labels don't look typeset.
export const Scrawl: React.FC<{
	x: number;
	y: number;
	children: React.ReactNode;
	size?: number;
	color?: string;
	anchor?: 'start' | 'middle' | 'end';
	rotate?: number;
	opacity?: number;
	seed?: string;
}> = ({x, y, children, size = 44, color = INK.black, anchor = 'middle', rotate = 0, opacity = 1, seed = 's'}) => {
	const tilt = rotate + (random(seed) - 0.5) * 4;
	return (
		<text
			x={x}
			y={y}
			fontFamily={MARKER_FONT}
			fontSize={size}
			fill={color}
			textAnchor={anchor}
			dominantBaseline="middle"
			opacity={opacity}
			transform={`rotate(${tilt} ${x} ${y})`}
		>
			{children}
		</text>
	);
};

// White page plus a subtle displacement filter that roughens stroke edges like felt-tip ink.
export const Page: React.FC<{children: React.ReactNode}> = ({children}) => (
	<AbsoluteFill style={{backgroundColor: 'white'}}>
		<svg width={VIDEO.width} height={VIDEO.height} viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`}>
			<defs>
				{/* Filter region in canvas units: a bounding-box region clips straight horizontal and
				    vertical strokes (their box is 0px wide), which made axis lines hairline-thin. */}
				<filter id="marker-edge" filterUnits="userSpaceOnUse" x={0} y={0} width={VIDEO.width} height={VIDEO.height}>
					<feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves={1} seed={3} result="noise" />
					<feDisplacementMap in="SourceGraphic" in2="noise" scale={2.5} />
				</filter>
			</defs>
			{children}
		</svg>
	</AbsoluteFill>
);

export const scaleY = (plot: Plot, v: number, max: number) => plot.bottom - (v / max) * (plot.bottom - plot.top);
export const scaleX = (plot: Plot, v: number, max: number) => plot.left + (v / max) * (plot.right - plot.left);

type Tick = {at: number; label: string};

// Hand-drawn axes. Tick positions are in pixels. `yTitleOnTop` puts the y title above the
// axis instead of rotated beside it (for charts whose y labels are long category names).
export const Axes: React.FC<{
	frame: number;
	plot: Plot;
	start?: number;
	duration?: number;
	yTicks: Tick[];
	xTicks: Tick[];
	yTitle: string;
	xTitle: string;
	yLabelSize?: number;
	yTickMarks?: boolean;
	yTitleOnTop?: boolean;
	hideYAxis?: boolean;
}> = ({frame, plot: PLOT, start = 0, duration = 12, yTicks, xTicks, yTitle, xTitle, yLabelSize = 40, yTickMarks = true, yTitleOnTop = false, hideYAxis = false}) => {
	const p = interpolate(frame, [start, start + duration], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const labels = interpolate(frame, [start + duration * 0.5, start + duration * 1.2], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	const yAxis = useMemo(() => ink.line(PLOT.left, PLOT.bottom + 6, PLOT.left, PLOT.top - 30, {seed: 11}), [PLOT]);
	const xAxis = useMemo(() => ink.line(PLOT.left - 6, PLOT.bottom, PLOT.right + 20, PLOT.bottom, {seed: 12}), [PLOT]);
	const yMarks = useMemo(
		() => (yTickMarks ? yTicks.map((t, i) => ink.line(PLOT.left - 22, t.at, PLOT.left, t.at, {seed: 20 + i, strokeWidth: 6})) : []),
		[yTicks, yTickMarks, PLOT],
	);
	const xMarks = useMemo(
		() => xTicks.map((t, i) => ink.line(t.at, PLOT.bottom, t.at, PLOT.bottom + 22, {seed: 40 + i, strokeWidth: 6})),
		[xTicks, PLOT],
	);
	return (
		<g>
			{!hideYAxis && <Ink drawable={yAxis} progress={p} />}
			<Ink drawable={xAxis} progress={p} />
			{yMarks.map((d, i) => <Ink key={`y${i}`} drawable={d} progress={p} />)}
			{xMarks.map((d, i) => <Ink key={`x${i}`} drawable={d} progress={p} />)}
			{yTicks.map((t, i) => (
				<Scrawl key={`yl${i}`} x={PLOT.left - (yTickMarks ? 32 : 18)} y={t.at} size={yLabelSize} anchor="end" opacity={labels} seed={`yl${i}`}>
					{t.label}
				</Scrawl>
			))}
			{xTicks.map((t, i) => (
				<Scrawl key={`xl${i}`} x={t.at} y={PLOT.bottom + 62} opacity={labels} seed={`xl${i}`}>
					{t.label}
				</Scrawl>
			))}
			<Scrawl x={(PLOT.left + PLOT.right) / 2} y={PLOT.bottom + 150} size={54} opacity={labels} seed="xt">
				{xTitle}
			</Scrawl>
			{yTitleOnTop ? (
				<Scrawl x={PLOT.left - 18} y={PLOT.top - 62} size={46} anchor="end" opacity={labels} seed="yt">
					{yTitle}
				</Scrawl>
			) : (
				<Scrawl x={62} y={(PLOT.top + PLOT.bottom) / 2} size={50} rotate={-90} opacity={labels} seed="yt">
					{yTitle}
				</Scrawl>
			)}
		</g>
	);
};

// Small handwritten legend: a scribbled swatch and the category name.
const LEGEND_X = [90, 300, 560, 750]; // spaced by label length

export const Legend: React.FC<{opacity: number; y?: number}> = ({opacity, y = LEGEND_Y}) => {
	const swatches = useMemo(
		() => CATEGORIES.map((c, i) => ink.rect(LEGEND_X[i], y - 22, 44, 44, {seed: 70 + i, stroke: CATEGORY_INK[c], fill: CATEGORY_INK[c], strokeWidth: 5})),
		[y],
	);
	return (
		<g opacity={opacity}>
			{CATEGORIES.map((c, i) => (
				<g key={c}>
					<Ink drawable={swatches[i]} />
					<Scrawl x={LEGEND_X[i] + 58} y={y} size={36} anchor="start" seed={`lg${i}`}>
						{c}
					</Scrawl>
				</g>
			))}
		</g>
	);
};

export const Title: React.FC<{children: React.ReactNode; opacity: number}> = ({children, opacity}) => (
	<Scrawl x={VIDEO.width / 2} y={TITLE_Y} size={64} opacity={opacity} seed="title">
		{children}
	</Scrawl>
);

// The 12 "Other" buckets, largest first, each with its own Sharpie color. Short names are for
// legends; the full names match detailed_category in the data.
export const BUCKET_STYLES: {category: string; short: string; color: string}[] = [
	{category: 'Global kitchens', short: 'Global', color: '#6f3fa8'},
	{category: 'Mexican & Latin', short: 'Mexican/Latin', color: '#f07f13'},
	{category: 'Pizza & Italian', short: 'Pizza/Italian', color: '#c2187a'},
	{category: 'New American bistros', short: 'New American', color: '#0f9a9a'},
	{category: 'BBQ & smokehouses', short: 'BBQ', color: '#7a4a21'},
	{category: 'Sandwiches & delis', short: 'Sandwiches', color: '#d9a400'},
	{category: 'Brewpubs & bars', short: 'Brewpubs/bars', color: '#23336e'},
	{category: 'Southern, Cajun & soul', short: 'Southern', color: '#7fb800'},
	{category: 'Seafood', short: 'Seafood', color: '#3fb6e8'},
	{category: 'Bakeries, cafes & desserts', short: 'Bakeries', color: '#f06aa6'},
	{category: 'Butchers & markets', short: 'Butchers', color: '#8c1c2b'},
	{category: 'Breakfast & brunch', short: 'Breakfast', color: '#5d6d7e'},
];

// A legend laid out as a grid, for charts with more categories than fit on one line.
export const LegendGrid: React.FC<{
	items: {label: string; color: string}[];
	opacity: number;
	columns?: number;
	x0?: number;
	colWidth?: number;
	y0?: number;
	rowHeight?: number;
	size?: number;
}> = ({items, opacity, columns = 3, x0 = 70, colWidth = 330, y0 = 195, rowHeight = 48, size = 31}) => {
	const swatches = useMemo(
		() =>
			items.map((it, i) =>
				ink.rect(x0 + (i % columns) * colWidth, y0 + Math.floor(i / columns) * rowHeight - 17, 34, 34, {
					seed: 900 + i,
					stroke: it.color,
					fill: it.color,
					strokeWidth: 4,
					hachureGap: 6,
				}),
			),
		[items, columns, x0, colWidth, y0, rowHeight],
	);
	return (
		<g opacity={opacity}>
			{items.map((it, i) => (
				<g key={it.label}>
					<Ink drawable={swatches[i]} />
					<Scrawl
						x={x0 + (i % columns) * colWidth + 48}
						y={y0 + Math.floor(i / columns) * rowHeight}
						size={size}
						anchor="start"
						seed={`lgg${i}`}
					>
						{it.label}
					</Scrawl>
				</g>
			))}
		</g>
	);
};
