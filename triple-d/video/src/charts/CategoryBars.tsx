// Charts 2 and 3: total unique restaurants per category, either Jev's strict call or the
// "if Guy had to pick" forced call. Bars are scribbled in, then grow up one after another.
import React, {useMemo} from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import data from '../data/triple-d.json';
import {Axes, CATEGORIES, CATEGORY_INK, INK, Ink, Page, Scrawl, Title, ink, plotFor, scaleY} from '../sharpie';

// With no title, the chart moves up to the top of the frame (still top-justified).
const PLOTS = {titled: plotFor('title'), untitled: plotFor('none')};

export const BARS_DURATION = 150;
const Y_MAX = 1200;

export type CategoryBarsProps = {policy: 'strict' | 'forced'; title: string; xTitle: string};

export const CategoryBars: React.FC<CategoryBarsProps> = ({policy, title, xTitle}) => {
	const frame = useCurrentFrame();
	const totals = data.totals[policy] as Record<string, number>;
	const PLOT = title ? PLOTS.titled : PLOTS.untitled;
	const BAND = (PLOT.right - PLOT.left) / CATEGORIES.length;
	const BAR_W = BAND * 0.62;
	const bars = useMemo(
		() =>
			CATEGORIES.map((c, i) => {
				const x = PLOT.left + i * BAND + (BAND - BAR_W) / 2;
				const top = scaleY(PLOT, totals[c], Y_MAX);
				return ink.rect(x, top, BAR_W, PLOT.bottom - top, {seed: 100 + i, stroke: CATEGORY_INK[c], fill: CATEGORY_INK[c]});
			}),
		// eslint-disable-next-line react-hooks/exhaustive-deps
		[totals, PLOT],
	);
	const fadeIn = interpolate(frame, [0, 10], [0, 1], {extrapolateRight: 'clamp'});

	return (
		<Page>
			{title && <Title opacity={fadeIn}>{title}</Title>}
			<Axes
				frame={frame}
				plot={PLOT}
				yTicks={[0, 400, 800, 1200].map((v) => ({at: scaleY(PLOT, v, Y_MAX), label: v.toLocaleString('en-US')}))}
				xTicks={CATEGORIES.map((c, i) => ({at: PLOT.left + i * BAND + BAND / 2, label: c}))}
				yTitle="Restaurants"
				xTitle={xTitle}
			/>
			{CATEGORIES.map((c, i) => {
				const start = 14 + i * 12;
				const grow = interpolate(frame, [start, start + 24], [0, 1], {
					extrapolateLeft: 'clamp',
					extrapolateRight: 'clamp',
					easing: Easing.out(Easing.cubic),
				});
				const top = scaleY(PLOT, totals[c], Y_MAX);
				const height = (PLOT.bottom - top) * grow;
				const label = interpolate(frame, [start + 20, start + 28], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
				const cx = PLOT.left + i * BAND + BAND / 2;
				return (
					<g key={c}>
						<clipPath id={`grow-${i}`}>
							<rect x={cx - BAR_W} y={PLOT.bottom - height - 10} width={BAR_W * 2} height={height + 14} />
						</clipPath>
						<g clipPath={`url(#grow-${i})`}>
							<Ink drawable={bars[i]} />
						</g>
						<Scrawl x={cx} y={top - 48} size={50} color={INK.black} opacity={label} seed={`v${i}`}>
							{totals[c].toLocaleString('en-US')}
						</Scrawl>
					</g>
				);
			})}
		</Page>
	);
};
