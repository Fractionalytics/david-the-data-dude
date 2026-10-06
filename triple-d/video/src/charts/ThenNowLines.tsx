// Charts 10-12: what came in as the diners went out. Each version is declared in VARIANTS:
//   'slope'     = first 10 seasons (1-10) vs. last 10 (34-43); Diner vs. Global, Drive-In & BBQ flat; "5.5x / 3.2x"
//   'season'    = the same four lines through every season 1-43
//   'combined'  = first 10 vs. last 10: Diner, Dive and Drive-In (in their DDD colors; Drive-In
//                 thin, as the flat one) against Global kitchens + Mexican & Latin summed into one
//                 "Global & Latin" line, since the two overlap. No BBQ: it's an Other bucket, not a D.
//   'endpoints' = season 1 vs. season 43 only; Diner vs. Global and Mexican & Latin, BBQ flat.
//                 Labeled with restaurant counts: single seasons are ~36 restaurants, so counts
//                 are more honest than percentages. Drive-In is left out because season 1 was
//                 unusually drive-in heavy (8 of 37), which would contradict the flat era trend.
// Gray (flat) lines draw first, then the colored lines, then the callouts appear. Two-point
// versions have no y-axis (every point carries its value). Lines are labeled at their ends
// instead of with a legend; gray lines whose values nearly coincide share one label.
import React, {useMemo} from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import data from '../data/triple-d.json';
import {Axes, BUCKET_STYLES, CATEGORY_INK, INK, Ink, Page, Scrawl, Title, ink, plotFor, scaleY} from '../sharpie';

export const THEN_NOW_DURATION = 135;
const PLOT = plotFor('title');
const GRAY_START = 10;
const HERO_START = 34;
const HERO_FRAMES = 45;
const CALLOUT_START = HERO_START + HERO_FRAMES;
const LABEL_GAP = 46; // minimum vertical space between end labels

const bucketColor = (c: string) => BUCKET_STYLES.find((b) => b.category === c)!.color;

type Point = {total: number; counts: Record<string, number>};
const share = (p: Point, c: string) => (100 * (p.counts[c] ?? 0)) / p.total;
const count = (p: Point, c: string) => p.counts[c] ?? 0;

const SEASONS: Point[] = data.seasons.map((s) => ({total: s.restaurants, counts: s.detailed as Record<string, number>}));
// Slope charts compare the first ten seasons (1-10) with the last ten (34-43).
const SLOPE = data.slopeEras as {label: string; restaurants: number; detailed: Record<string, number>}[];
const ERA_POINTS: Point[] = SLOPE.map((e) => ({total: e.restaurants, counts: e.detailed}));

type Line = {category: string; color: string; hero: boolean; sumOf?: string[]};
// A label covers one or more lines (its value is their average) and appears when its lines do.
type Label = {name: string; categories: string[]; color: string; singular?: string; sum?: boolean};
type Callout = {at: 0 | 1; text: string; name: string; color: string};
type Variant = {
	points: Point[];
	lines: Line[];
	labels: Label[];
	units: 'percent' | 'count';
	yMax: number;
	x: [number, number];
	twoPoint: boolean;
	xTicks: (xAt: (i: number) => number) => {at: number; label: string}[];
	xTitle: string;
	callouts: (first: Point, last: Point) => Callout[];
};

const DINER: Line = {category: 'Diner', color: CATEGORY_INK.Diner, hero: true};
const GLOBAL: Line = {category: 'Global kitchens', color: bucketColor('Global kitchens'), hero: true};
const LATIN: Line = {category: 'Mexican & Latin', color: bucketColor('Mexican & Latin'), hero: true};
const gray = (category: string): Line => ({category, color: INK.gray, hero: false});
const labelFor = (l: Line, name: string): Label => ({name, categories: [l.category], color: l.color});
const ratio = (a: number, b: number) => (a / b).toFixed(1).replace(/\.0$/, '');
const DIVE: Line = {category: 'Dive', color: CATEGORY_INK.Dive, hero: true};
const DRIVE_IN_FLAT: Line = {category: 'Drive-In', color: CATEGORY_INK['Drive-In'], hero: false};
const GLOBAL_LATIN: Line = {category: 'Global & Latin', color: bucketColor('Global kitchens'), hero: true, sumOf: ['Global kitchens', 'Mexican & Latin']};
const GRAY_PAIR: Label = {name: 'Drive-In & BBQ', categories: ['Drive-In', 'BBQ & smokehouses'], color: INK.gray};

const VARIANTS: Record<'slope' | 'combined' | 'season' | 'endpoints', Variant> = {
	slope: {
		points: ERA_POINTS,
		lines: [gray('Drive-In'), gray('BBQ & smokehouses'), DINER, GLOBAL],
		labels: [GRAY_PAIR, labelFor(DINER, 'Diner'), labelFor(GLOBAL, 'Global')],
		units: 'percent',
		yMax: 40,
		x: [420, 720],
		twoPoint: true,
		xTicks: (xAt) => [
			{at: xAt(0), label: SLOPE[0].label},
			{at: xAt(1), label: SLOPE[1].label},
		],
		xTitle: 'Seasons',
		callouts: (f, l) => [
			{at: 0, text: `${ratio(share(f, 'Diner'), share(f, 'Global kitchens'))}x more`, name: 'Diners', color: DINER.color},
			{at: 1, text: `${ratio(share(l, 'Global kitchens'), share(l, 'Diner'))}x more`, name: 'Global', color: GLOBAL.color},
		],
	},
	combined: {
		points: ERA_POINTS,
		lines: [DRIVE_IN_FLAT, DINER, DIVE, GLOBAL_LATIN],
		labels: [
			labelFor(DRIVE_IN_FLAT, 'Drive-In'),
			labelFor(DINER, 'Diner'),
			labelFor(DIVE, 'Dive'),
			{name: 'Global & Latin', categories: GLOBAL_LATIN.sumOf!, color: GLOBAL_LATIN.color, sum: true},
		],
		units: 'percent',
		yMax: 40,
		x: [420, 690], // room for the long right label
		twoPoint: true,
		xTicks: (xAt) => [
			{at: xAt(0), label: SLOPE[0].label},
			{at: xAt(1), label: SLOPE[1].label},
		],
		xTitle: 'Seasons',
		callouts: (f, l) => {
			const gl = (p: Point) => share(p, 'Global kitchens') + share(p, 'Mexican & Latin');
			return [
				{at: 0, text: `${ratio(share(f, 'Diner'), gl(f))}x more`, name: 'Diners', color: DINER.color},
				{at: 1, text: `${ratio(gl(l), share(l, 'Diner'))}x more`, name: 'Global & Latin', color: GLOBAL_LATIN.color},
			];
		},
	},
	season: {
		points: SEASONS,
		lines: [gray('Drive-In'), gray('BBQ & smokehouses'), DINER, GLOBAL],
		labels: [GRAY_PAIR, labelFor(DINER, 'Diner'), labelFor(GLOBAL, 'Global')],
		units: 'percent',
		yMax: 60,
		x: [PLOT.left + 30, 780],
		twoPoint: false,
		xTicks: (xAt) => [1, 10, 20, 30, 40].map((s) => ({at: xAt(s - 1), label: String(s)})),
		xTitle: 'Season',
		callouts: () => [],
	},
	endpoints: {
		points: [SEASONS[0], SEASONS[SEASONS.length - 1]],
		lines: [gray('BBQ & smokehouses'), DINER, GLOBAL, LATIN],
		labels: [
			{name: 'BBQ', categories: ['BBQ & smokehouses'], color: INK.gray},
			{...labelFor(DINER, 'Diners'), singular: 'Diner'},
			labelFor(GLOBAL, 'Global'),
			labelFor(LATIN, 'Mexican/Latin'),
		],
		units: 'count',
		yMax: 24,
		x: [420, 720],
		twoPoint: true,
		xTicks: (xAt) => [
			{at: xAt(0), label: 'Season 1'},
			{at: xAt(1), label: 'Season 43'},
		],
		xTitle: '',
		callouts: (f, l) => [
			{at: 0, text: `${count(f, 'Diner')} to ${count(f, 'Global kitchens')}`, name: 'Diners', color: DINER.color},
			{at: 1, text: `${count(l, 'Global kitchens')} to ${count(l, 'Diner')}`, name: 'Global', color: GLOBAL.color},
		],
	},
};

// Space labels at least LABEL_GAP apart, keeping their order and staying above `limit`.
const spread = (ys: number[], limit: number) => {
	const order = ys.map((y, i) => ({y, i})).sort((a, b) => a.y - b.y);
	for (let k = 1; k < order.length; k++) order[k].y = Math.max(order[k].y, order[k - 1].y + LABEL_GAP);
	for (let k = order.length - 1; k >= 0; k--) {
		order[k].y = Math.min(order[k].y, k === order.length - 1 ? limit : order[k + 1].y - LABEL_GAP);
	}
	const out = [...ys];
	order.forEach((o) => (out[o.i] = o.y));
	return out;
};

export type ThenNowLinesProps = {title: string; mode: keyof typeof VARIANTS};

export const ThenNowLines: React.FC<ThenNowLinesProps> = ({title, mode}) => {
	const frame = useCurrentFrame();
	const v = VARIANTS[mode];
	const {points} = v;
	const [x0, x1] = v.x;
	const xAt = (i: number) => x0 + (i / (points.length - 1)) * (x1 - x0);
	const value = (p: Point, c: string) => (v.units === 'percent' ? share(p, c) : count(p, c));
	const y = (val: number) => scaleY(PLOT, val, v.yMax);

	const lines = useMemo(
		() =>
			v.lines.map((l, j) =>
				ink.path(
					points.map((p, i) => [xAt(i), y((l.sumOf ?? [l.category]).reduce((t, c) => t + value(p, c), 0))] as [number, number]),
					{seed: 600 + j, stroke: l.color, strokeWidth: l.hero ? 13 : 7, roughness: v.twoPoint ? 0.9 : 0.6},
				),
			),
		// eslint-disable-next-line react-hooks/exhaustive-deps
		[mode],
	);

	const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
	const fadeIn = interpolate(frame, [0, 10], [0, 1], clamp);
	const grayP = interpolate(frame, [GRAY_START, GRAY_START + 24], [0, 1], clamp);
	const heroP = interpolate(frame, [HERO_START, HERO_START + HERO_FRAMES], [0, 1], clamp);
	const callout = interpolate(frame, [CALLOUT_START, CALLOUT_START + 10], [0, 1], clamp);

	const first = points[0];
	const last = points[points.length - 1];
	const fmt = (val: number) => (v.units === 'percent' ? `${Math.round(val)}%` : String(Math.round(val)));
	const labelValue = (p: Point, l: Label) => l.categories.reduce((s, c) => s + value(p, c), 0) / (l.sum ? 1 : l.categories.length);
	// A label appears with its line: early for flat (non-hero) lines, with the hero lines otherwise.
	const isGray = (l: Label) => v.lines.some((line) => !line.hero && l.categories.includes(line.category));
	const nameAt = (p: Point, l: Label) => (l.singular && Math.round(labelValue(p, l)) === 1 ? l.singular : l.name);
	const calloutY = PLOT.bottom + (v.xTitle ? 235 : 150);
	const limit = PLOT.bottom - 24;
	const leftYs = spread(v.labels.map((l) => y(labelValue(first, l))), limit);
	const rightYs = spread(v.labels.map((l) => y(labelValue(last, l))), limit);

	return (
		<Page>
			<Title opacity={fadeIn}>{title}</Title>
			<Axes
				frame={frame}
				plot={PLOT}
				yTicks={v.twoPoint ? [] : [0, 30, 60].map((t) => ({at: y(t), label: `${t}%`}))}
				hideYAxis={v.twoPoint}
				xTicks={v.xTicks(xAt)}
				yTitle={v.twoPoint ? '' : 'Share of restaurants'}
				xTitle={v.xTitle}
			/>
			{v.lines.map((l, j) => (
				<Ink key={l.category} drawable={lines[j]} progress={l.hero ? heroP : grayP} connect />
			))}
			{v.twoPoint &&
				v.labels.map((l, k) => (
					<Scrawl key={`L${k}`} x={x0 - 22} y={leftYs[k]} size={34} color={l.color} anchor="end" opacity={isGray(l) ? grayP : heroP > 0 ? 1 : 0} seed={`L${k}`}>
						{`${nameAt(first, l)} ${fmt(labelValue(first, l))}`}
					</Scrawl>
				))}
			{v.labels.map((l, k) => (
				<Scrawl key={`R${k}`} x={x1 + 22} y={rightYs[k]} size={34} color={l.color} anchor="start" opacity={isGray(l) ? grayP : heroP >= 1 ? 1 : 0} seed={`R${k}`}>
					{v.twoPoint ? `${fmt(labelValue(last, l))} ${nameAt(last, l)}` : l.name}
				</Scrawl>
			))}
			<g opacity={callout}>
				{v.callouts(first, last).map((c, k) => (
					<g key={k}>
						<Scrawl x={c.at === 0 ? x0 : x1} y={calloutY} size={46} color={c.color} seed={`c${k}`}>
							{c.text}
						</Scrawl>
						<Scrawl x={c.at === 0 ? x0 : x1} y={calloutY + 50} size={46} color={c.color} seed={`cb${k}`}>
							{c.name}
						</Scrawl>
					</g>
				))}
			</g>
		</Page>
	);
};
