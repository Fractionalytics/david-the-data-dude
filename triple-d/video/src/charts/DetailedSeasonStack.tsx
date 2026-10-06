// Charts 7-9: share of restaurants using detailed_category, so you can watch the "Other"
// buckets emerge as the diners fade.
//   layers  'full'   = Diner / Drive-In / Dive + all 12 buckets (15 colors)
//           'simple' = Diner / Drive-In / Dive + the top 3 buckets + gray "Everything else"
//   groupBy 'season' = one thin bar per season, revealed by a left-to-right marker sweep
//           'era'    = four wide bars (S1-10, S11-20, S21-30, S31-43) that grow up one by one,
//                      with percentages written on the bigger segments
// Diner / Drive-In / Dive always sit at the bottom in their usual colors. Plot height shrinks
// to fit the legend so every chart ends at the same height (bottom of frame stays free).
import React, {useMemo} from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import data from '../data/triple-d.json';
import {Axes, BUCKET_STYLES, CATEGORY_INK, INK, Ink, LegendGrid, Page, Scrawl, Title, ink, scaleY, type Plot} from '../sharpie';

export const DETAILED_STACK_DURATION = 165;
const PLOT_BOTTOM = 1110;
const LEGEND_Y0 = 195;
const LEGEND_ROW = 48;
const ERA_LABEL_MIN = 7; // only write a % on segments at least this big

type Layer = {categories: string[]; short: string; color: string};
const DDD: Layer[] = [
	{categories: ['Diner'], short: 'Diner', color: CATEGORY_INK.Diner},
	{categories: ['Drive-In'], short: 'Drive-In', color: CATEGORY_INK['Drive-In']},
	{categories: ['Dive'], short: 'Dive', color: CATEGORY_INK.Dive},
];
const TOP_BUCKETS = 3;
const LAYERS: Record<'full' | 'simple', Layer[]> = {
	full: [...DDD, ...BUCKET_STYLES.map((b) => ({categories: [b.category], short: b.short, color: b.color}))],
	simple: [
		...DDD,
		...BUCKET_STYLES.slice(0, TOP_BUCKETS).map((b) => ({categories: [b.category], short: b.short, color: b.color})),
		{categories: BUCKET_STYLES.slice(TOP_BUCKETS).map((b) => b.category), short: 'Everything else', color: INK.gray},
	],
};

type Bar = {label: string; total: number; counts: Record<string, number>};
const BARS: Record<'season' | 'era', Bar[]> = {
	season: data.seasons.map((s) => ({label: String(s.season), total: s.restaurants, counts: s.detailed as Record<string, number>})),
	era: data.eras.map((e) => ({label: e.label, total: e.restaurants, counts: e.detailed as Record<string, number>})),
};

export type DetailedSeasonStackProps = {title: string; layers: 'full' | 'simple'; groupBy: 'season' | 'era'};

export const DetailedSeasonStack: React.FC<DetailedSeasonStackProps> = ({title, layers: layerSet, groupBy}) => {
	const frame = useCurrentFrame();
	const layers = LAYERS[layerSet];
	const bars = BARS[groupBy];
	const legendRows = Math.ceil(layers.length / 3);
	const plot: Plot = useMemo(
		() => ({left: 250, right: 1000, top: LEGEND_Y0 + (legendRows - 1) * LEGEND_ROW + 80, bottom: PLOT_BOTTOM}),
		[legendRows],
	);

	const band = (plot.right - plot.left - 20) / bars.length;
	const barW = band * (groupBy === 'era' ? 0.66 : 0.8);
	const barX = (i: number) => plot.left + 14 + i * band + (band - barW) / 2;

	// One rough rectangle per (bar, layer), plus its share for labeling.
	const segments = useMemo(
		() =>
			bars.map((b, i) => {
				let base = 0;
				return layers.map((layer, j) => {
					const n = layer.categories.reduce((sum, c) => sum + (b.counts[c] ?? 0), 0);
					const share = (100 * n) / b.total;
					const y0 = scaleY(plot, base, 100);
					const y1 = scaleY(plot, base + share, 100);
					base += share;
					const drawable =
						n === 0
							? null
							: ink.rect(barX(i), y1, barW, y0 - y1, {
									seed: 1000 + i * 16 + j,
									stroke: layer.color,
									fill: layer.color,
									strokeWidth: groupBy === 'era' ? 4 : 2.5,
									hachureGap: groupBy === 'era' ? 7 : 4,
									fillWeight: groupBy === 'era' ? 3 : 2.5,
									roughness: 0.5,
								});
					return {drawable, share, mid: (y0 + y1) / 2};
				});
			}),
		// eslint-disable-next-line react-hooks/exhaustive-deps
		[bars, layers, plot],
	);

	const fadeIn = interpolate(frame, [0, 10], [0, 1], {extrapolateRight: 'clamp'});
	const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
	const sweep = interpolate(frame, [14, 94], [0, 1], clamp);

	const xTicks =
		groupBy === 'season'
			? [1, 10, 20, 30, 40].map((s) => ({at: barX(s - 1) + barW / 2, label: String(s)}))
			: bars.map((b, i) => ({at: barX(i) + barW / 2, label: b.label}));

	return (
		<Page>
			<Title opacity={fadeIn}>{title}</Title>
			<LegendGrid items={layers.map((l) => ({label: l.short, color: l.color}))} opacity={fadeIn} y0={LEGEND_Y0} rowHeight={LEGEND_ROW} />
			<Axes
				frame={frame}
				plot={plot}
				yTicks={[0, 50, 100].map((v) => ({at: scaleY(plot, v, 100), label: `${v}%`}))}
				xTicks={xTicks}
				yTitle="Share of restaurants"
				xTitle={groupBy === 'season' ? 'Season' : 'Seasons'}
			/>
			{groupBy === 'season' ? (
				<>
					<clipPath id={`sweep-${layerSet}`}>
						<rect x={plot.left} y={plot.top - 40} width={(plot.right - plot.left + 20) * sweep} height={plot.bottom - plot.top + 46} />
					</clipPath>
					<g clipPath={`url(#sweep-${layerSet})`}>
						{segments.flat().map((s, k) => (s.drawable ? <Ink key={k} drawable={s.drawable} /> : null))}
					</g>
				</>
			) : (
				segments.map((barSegs, i) => {
					const start = 14 + i * 18;
					const grow = interpolate(frame, [start, start + 26], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
					const labels = interpolate(frame, [start + 24, start + 34], [0, 1], clamp);
					const h = (plot.bottom - plot.top + 10) * grow;
					return (
						<g key={i}>
							<clipPath id={`era-grow-${i}`}>
								<rect x={barX(i) - 10} y={plot.bottom - h} width={barW + 20} height={h + 8} />
							</clipPath>
							<g clipPath={`url(#era-grow-${i})`}>
								{barSegs.map((s, j) => (s.drawable ? <Ink key={j} drawable={s.drawable} /> : null))}
							</g>
							{barSegs.map((s, j) =>
								s.share >= ERA_LABEL_MIN ? (
									<g key={`l${j}`} opacity={labels}>
										<rect x={barX(i) + barW / 2 - 46} y={s.mid - 22} width={92} height={44} rx={10} fill="white" opacity={0.85} />
										<Scrawl x={barX(i) + barW / 2} y={s.mid} size={32} seed={`el${i}-${j}`}>
											{`${Math.round(s.share)}%`}
										</Scrawl>
									</g>
								) : null,
							)}
						</g>
					);
				})
			)}
		</Page>
	);
};
