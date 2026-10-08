// Card 5 (1:07:06–1:42:23). Two charts in one composition, timed to David's recording:
//   1. State Silver Alerts per year, 2011–2021, drawing in from the first frame.
//   2. At 1:20:02 the bars give way to 100 dots, one per Silver Alert.
//      At 1:30:14, 98 of them fill in: found. At 1:36:04, 11 of those turn red: found because of the alert.
// Each change finishes on David's cue frame (docs/video-playbook.md section 6).
import React, {useMemo} from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import data from '../data/silver.json';
import {Axes, COLOR, INK, Ink, Page, Scrawl, ScopeNote, ZONES, clamp, cue, ink, scaleY} from '../sharpie';

const TRANSITION = cue(5, 1, 20, 2); // dots fully in
const FOUND = cue(5, 1, 30, 14); // 98/100 reveal done
const DIRECT = cue(5, 1, 36, 4); // 11/100 reveal done
const SWAP = 20; // frames for the bars to fade and the dots to draw in, ending on TRANSITION
const FILL = 30; // frames for each reveal, ending on its cue

// --- Chart 1: alerts per year -------------------------------------------------------------
const PLOT = {left: ZONES.chart.left + 110, right: ZONES.chart.right - 10, top: ZONES.chart.top + 120, bottom: ZONES.chart.bottom - 230};
const Y_MAX = 300;
const YEARS = data.years;
const BAND = (PLOT.right - PLOT.left) / YEARS.length;
const BAR_W = BAND * 0.66;

const YearBars: React.FC<{frame: number}> = ({frame}) => {
	const bars = useMemo(
		() =>
			YEARS.map((y, i) => {
				const top = scaleY(PLOT, y.alerts, Y_MAX);
				return ink.rect(PLOT.left + i * BAND + (BAND - BAR_W) / 2, top, BAR_W, PLOT.bottom - top, {seed: 100 + i, stroke: INK.blue, fill: INK.blue, strokeWidth: 6, hachureGap: 8});
			}),
		[],
	);
	return (
		<g>
			<Axes
				frame={frame}
				plot={PLOT}
				yTicks={[0, 100, 200, 300].map((v) => ({at: scaleY(PLOT, v, Y_MAX), label: String(v)}))}
				xTicks={YEARS.map((_, i) => ({at: PLOT.left + i * BAND + BAND / 2, label: ''}))}
				yTitle=""
				xTitle=""
				yTitleOnTop
			/>
			{/* Year labels drawn here, smaller than the kit's default, so 11 of them fit side by side. */}
			{YEARS.map((y, i) => (
				<Scrawl key={`yr${i}`} x={PLOT.left + i * BAND + BAND / 2} y={PLOT.bottom + 56} size={32} opacity={interpolate(frame, [12, 20], [0, 1], clamp)} seed={`yr${i}`}>
					{`'${String(y.year).slice(2)}`}
				</Scrawl>
			))}
			<Scrawl x={ZONES.chart.left} y={PLOT.top - 70} size={44} anchor="start" opacity={interpolate(frame, [6, 16], [0, 1], clamp)} seed="yt">
				Silver Alerts
			</Scrawl>
			{YEARS.map((y, i) => {
				const start = 10 + i * 5;
				const grow = interpolate(frame, [start, start + 20], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
				const top = scaleY(PLOT, y.alerts, Y_MAX);
				const height = (PLOT.bottom - top) * grow;
				const cx = PLOT.left + i * BAND + BAND / 2;
				const label = interpolate(frame, [start + 16, start + 24], [0, 1], clamp);
				return (
					<g key={y.year}>
						<clipPath id={`yb-${i}`}>
							<rect x={cx - BAR_W} y={PLOT.bottom - height - 10} width={BAR_W * 2} height={height + 14} />
						</clipPath>
						<g clipPath={`url(#yb-${i})`}>
							<Ink drawable={bars[i]} />
						</g>
						<Scrawl x={cx} y={top - 26} size={30} opacity={label} seed={`yv${i}`}>
							{y.alerts}
						</Scrawl>
					</g>
				);
			})}
		</g>
	);
};

// --- Chart 2: 100 dots ----------------------------------------------------------------------
const GRID = 10;
const CELL = 58;
const GRID_LEFT = (ZONES.chart.left + ZONES.chart.right) / 2 - (GRID * CELL) / 2;
const GRID_TOP = ZONES.chart.top + 120;
const DOT = 42;
const dotCenter = (i: number): [number, number] => [GRID_LEFT + (i % GRID) * CELL + CELL / 2, GRID_TOP + Math.floor(i / GRID) * CELL + CELL / 2];

const Dots: React.FC<{frame: number}> = ({frame}) => {
	const {found, direct} = data.dots;
	const outlines = useMemo(() => Array.from({length: 100}, (_, i) => ink.dot(...dotCenter(i), DOT, {seed: 500 + i, fill: 'none', fillStyle: 'hachure', stroke: INK.gray, strokeWidth: 5})), []);
	const foundDots = useMemo(() => Array.from({length: 100}, (_, i) => ink.dot(...dotCenter(i), DOT, {seed: 500 + i, stroke: COLOR.found, fill: COLOR.found, strokeWidth: 5})), []);
	const directDots = useMemo(() => Array.from({length: 100}, (_, i) => ink.dot(...dotCenter(i), DOT, {seed: 500 + i, stroke: COLOR.alert, fill: COLOR.alert, strokeWidth: 5})), []);

	// Dots draw in row by row, finishing on the transition cue.
	const drawn = (i: number) => interpolate(frame, [TRANSITION - SWAP + (i / 100) * (SWAP - 6), TRANSITION - SWAP + (i / 100) * (SWAP - 6) + 6], [0, 1], clamp);
	// Reveals fill dot by dot, the last one landing on the cue.
	const filled = (i: number, n: number, end: number) => i < n && frame >= end - FILL + Math.floor((i / n) * FILL);
	const foundLabel = interpolate(frame, [FOUND - 8, FOUND], [0, 1], clamp);
	const directLabel = interpolate(frame, [DIRECT - 8, DIRECT], [0, 1], clamp);
	const legendY = GRID_TOP + GRID * CELL + 50;

	return (
		<g>
			{outlines.map((d, i) => (
				<Ink key={`o${i}`} drawable={d} progress={drawn(i)} />
			))}
			{foundDots.map((d, i) => (filled(i, found, FOUND) && !filled(i, direct, DIRECT) ? <Ink key={`f${i}`} drawable={d} /> : null))}
			{directDots.map((d, i) => (filled(i, direct, DIRECT) ? <Ink key={`d${i}`} drawable={d} /> : null))}
			{/* Counts above the grid; the legend below says what each color means. */}
			<Scrawl x={ZONES.chart.left + 20} y={GRID_TOP - 62} size={60} anchor="start" opacity={foundLabel} seed="n98">
				{`${found} / 100`}
			</Scrawl>
			<Scrawl x={ZONES.chart.right - 20} y={GRID_TOP - 62} size={60} anchor="end" color={COLOR.alert} opacity={directLabel} seed="n11">
				{`${direct} / 100`}
			</Scrawl>
			<g opacity={foundLabel}>
				<Ink drawable={ink.dot(ZONES.chart.left + 40, legendY, 30, {seed: 901, stroke: COLOR.found, fill: COLOR.found, strokeWidth: 4})} />
				<Scrawl x={ZONES.chart.left + 70} y={legendY} size={36} anchor="start" seed="lg1">
					found
				</Scrawl>
				<Ink drawable={ink.dot(ZONES.chart.left + 300, legendY, 30, {seed: 903, fill: 'none', fillStyle: 'hachure', stroke: INK.gray, strokeWidth: 4})} />
				<Scrawl x={ZONES.chart.left + 330} y={legendY} size={36} anchor="start" seed="lg3">
					not found
				</Scrawl>
			</g>
			<g opacity={directLabel}>
				<Ink drawable={ink.dot(ZONES.chart.left + 40, legendY + 58, 30, {seed: 902, stroke: COLOR.alert, fill: COLOR.alert, strokeWidth: 4})} />
				<Scrawl x={ZONES.chart.left + 70} y={legendY + 58} size={36} anchor="start" seed="lg2">
					found because of the alert
				</Scrawl>
			</g>
		</g>
	);
};

export const AlertsYearsDots: React.FC = () => {
	const frame = useCurrentFrame();
	const barsOut = interpolate(frame, [TRANSITION - SWAP, TRANSITION - SWAP / 2], [1, 0], clamp);
	return (
		<Page>
			{barsOut > 0 && (
				<g opacity={barsOut}>
					<YearBars frame={frame} />
					<ScopeNote opacity={1}>Florida state Silver Alerts · FDLE</ScopeNote>
				</g>
			)}
			{frame >= TRANSITION - SWAP && (
				<g>
					<Dots frame={frame} />
					<ScopeNote opacity={interpolate(frame, [FOUND - 8, FOUND], [0, 1], clamp)}>
						Source: FDLE monthly reports & newsletters
					</ScopeNote>
				</g>
			)}
		</Page>
	);
};
