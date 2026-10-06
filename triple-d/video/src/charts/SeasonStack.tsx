// Charts 4 and 5: every season's restaurants stacked by category (Jev's strict call),
// as counts or as 100%. A marker "sweep" reveals the seasons left to right.
import React, {useMemo} from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import data from '../data/triple-d.json';
import {Axes, CATEGORIES, CATEGORY_INK, Ink, Legend, Page, Title, ink, plotFor, scaleY} from '../sharpie';

const PLOT = plotFor('legend');

export const STACK_DURATION = 150;
const SWEEP_START = 12;
const SWEEP_FRAMES = 75;
const N = data.seasons.length;
const BAND = (PLOT.right - PLOT.left - 20) / N;
const BAR_W = BAND * 0.78;
const barX = (i: number) => PLOT.left + 14 + i * BAND + (BAND - BAR_W) / 2;

export type SeasonStackProps = {mode: 'count' | 'percent'; title: string};

export const SeasonStack: React.FC<SeasonStackProps> = ({mode, title}) => {
	const frame = useCurrentFrame();
	const yMax = mode === 'percent' ? 100 : 80;
	const segments = useMemo(
		() =>
			data.seasons.flatMap((s, i) => {
				let base = 0;
				return CATEGORIES.map((c, j) => {
					const n = (s.strict as Record<string, number>)[c];
					const v = mode === 'percent' ? (100 * n) / s.restaurants : n;
					const y0 = scaleY(PLOT, base, yMax);
					const y1 = scaleY(PLOT, base + v, yMax);
					base += v;
					if (n === 0) return null;
					return ink.rect(barX(i), y1, BAR_W, y0 - y1, {
						seed: 300 + i * 4 + j,
						stroke: CATEGORY_INK[c],
						fill: CATEGORY_INK[c],
						strokeWidth: 3,
						hachureGap: 5,
						fillWeight: 3,
						roughness: 0.6,
					});
				});
			}),
		[mode, yMax],
	);
	const sweep = interpolate(frame, [SWEEP_START, SWEEP_START + SWEEP_FRAMES], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	const fadeIn = interpolate(frame, [0, 10], [0, 1], {extrapolateRight: 'clamp'});
	const yTicks = mode === 'percent' ? [0, 50, 100].map((v) => ({at: scaleY(PLOT, v, yMax), label: `${v}%`}))
			: [0, 40, 80].map((v) => ({at: scaleY(PLOT, v, yMax), label: String(v)}));

	return (
		<Page>
			<Title opacity={fadeIn}>{title}</Title>
			<Legend opacity={fadeIn} />
			<Axes
				frame={frame}
				plot={PLOT}
				yTicks={yTicks}
				xTicks={[1, 10, 20, 30, 40].map((s) => ({at: barX(s - 1) + BAR_W / 2, label: String(s)}))}
				yTitle={mode === 'percent' ? 'Share of restaurants' : 'Restaurants'}
				xTitle="Season"
			/>
			<clipPath id="sweep">
				<rect x={PLOT.left} y={PLOT.top - 40} width={(PLOT.right - PLOT.left + 20) * sweep} height={PLOT.bottom - PLOT.top + 46} />
			</clipPath>
			<g clipPath="url(#sweep)">
				{segments.map((d, k) => (d ? <Ink key={k} drawable={d} /> : null))}
			</g>
		</Page>
	);
};
