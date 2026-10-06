// Chart 6: Jev's call, unpacked. Diner / Drive-In / Dive plus the 12 buckets that make up
// "Other", as horizontal bars (categories down the y-axis, counts along the x-axis).
// DDD bars keep their marker colors; the "Other" buckets are gray, like the Other bar.
import React, {useMemo} from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import data from '../data/triple-d.json';
import {Axes, CATEGORY_INK, INK, Ink, Page, Scrawl, Title, ink, plotFor, scaleX, type Category} from '../sharpie';

// The y title sits above the axis, so the plot gets extra headroom below the main title.
const PLOT = plotFor('legend', 470, 930);
// With no main title, the whole chart shifts up by the title's space (stays top-justified).
const UNTITLED_SHIFT = plotFor('legend').top - plotFor('title').top;
export const DETAILED_DURATION = 165;

type Row = {category: string; count: number};
const ROWS: Row[] = data.totals.detailed;
const X_MAX = Math.ceil(Math.max(...ROWS.map((r) => r.count)) / 50) * 50;
const BAND = (PLOT.bottom - PLOT.top) / ROWS.length;
const BAR_H = BAND * 0.66;
const rowY = (i: number) => PLOT.top + i * BAND + BAND / 2;
const colorOf = (c: string) => CATEGORY_INK[c as Category] ?? INK.gray;

export const DetailedBars: React.FC<{title: string}> = ({title}) => {
	const frame = useCurrentFrame();
	const bars = useMemo(
		() =>
			ROWS.map((r, i) =>
				ink.rect(PLOT.left, rowY(i) - BAR_H / 2, scaleX(PLOT, r.count, X_MAX) - PLOT.left, BAR_H, {
					seed: 500 + i,
					stroke: colorOf(r.category),
					fill: colorOf(r.category),
					strokeWidth: 5,
					hachureGap: 7,
					fillWeight: 3,
				}),
			),
		[],
	);
	const fadeIn = interpolate(frame, [0, 10], [0, 1], {extrapolateRight: 'clamp'});

	return (
		<Page>
			{title && <Title opacity={fadeIn}>{title}</Title>}
			<g transform={title ? undefined : `translate(0 ${-UNTITLED_SHIFT})`}>
			<Axes
				frame={frame}
				plot={PLOT}
				yTicks={ROWS.map((r, i) => ({at: rowY(i), label: r.category}))}
				yLabelSize={32}
				yTickMarks={false}
				yTitle="Kind of place"
				yTitleOnTop
				xTicks={[0, X_MAX / 2, X_MAX].map((v) => ({at: scaleX(PLOT, v, X_MAX), label: String(v)}))}
				xTitle="Restaurants"
			/>
			{ROWS.map((r, i) => {
				const start = 12 + i * 5;
				const grow = interpolate(frame, [start, start + 20], [0, 1], {
					extrapolateLeft: 'clamp',
					extrapolateRight: 'clamp',
					easing: Easing.out(Easing.cubic),
				});
				const end = scaleX(PLOT, r.count, X_MAX);
				const label = interpolate(frame, [start + 16, start + 24], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
				return (
					<g key={r.category}>
						<clipPath id={`hgrow-${i}`}>
							<rect x={PLOT.left - 10} y={rowY(i) - BAND / 2} width={(end - PLOT.left + 20) * grow} height={BAND} />
						</clipPath>
						<g clipPath={`url(#hgrow-${i})`}>
							<Ink drawable={bars[i]} />
						</g>
						<Scrawl x={end + 16} y={rowY(i)} size={34} anchor="start" opacity={label} seed={`hv${i}`}>
							{r.count}
						</Scrawl>
					</g>
				);
			})}
			</g>
		</Page>
	);
};
