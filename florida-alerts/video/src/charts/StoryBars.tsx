// Cards 6 and 7: FDLE's 197 Silver Alert success stories (2014–2022), as horizontal bars.
//   Card 6 (1:42:23–1:52:19): who spotted the missing person. All five labels, as David chose.
//   Card 7 (1:52:19–2:00:20): how they knew, public vs. police (David chose this framing 2026-10-08).
//   Public alerts are one bar stacked from highway signs (49) and lottery terminals (14) = 63, against the
//   police BOLO's 54. The plate-reader story (1) and the 79 that don't name a channel aren't shown. Most of
//   those 79 are citizen finds, which is why the BOLO alone looked like the top channel.
// Bars draw in over the first ~2 seconds and then hold for the rest of the card.
import React, {useMemo} from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import data from '../data/silver.json';
import {COLOR, HBars, Ink, Page, Scrawl, ScopeNote, ZONES, clamp, ink, type HBarRow} from '../sharpie';

const FOUND_BY: HBarRow[] = [
	{label: 'A citizen', value: data.foundBy.citizen, color: COLOR.public},
	{label: 'Police', value: data.foundBy.law_enforcement, color: COLOR.police},
	{label: 'The person themself', value: data.foundBy.self, color: COLOR.other},
	{label: 'Unclear', value: data.foundBy.unclear, color: COLOR.other},
	{label: 'A family member', value: data.foundBy.family, color: COLOR.other},
];

const SIGNS = data.channels.highway_sign;
const LOTTERY = data.channels.lottery;
const BOLO = data.channels.bolo_teletype;
const LOTTERY_GREEN = '#7cc796'; // a lighter green: still "the public", but a separate piece of the bar

export const FoundByBars: React.FC = () => {
	const frame = useCurrentFrame();
	return (
		<Page>
			<HBars frame={frame} rows={FOUND_BY} max={120} top={ZONES.chart.top + 30} bottom={ZONES.chart.bottom - 90} />
			<ScopeNote opacity={interpolate(frame, [30, 45], [0, 1], clamp)}>{`${data.stories} FDLE success stories, 2014–2022`}</ScopeNote>
		</Page>
	);
};

// Layout: bar label above each bar, value at its end, the two public pieces labeled beneath their segments.
const LEFT = ZONES.chart.left + 10;
const RIGHT = ZONES.chart.right - 110;
const MAX = 70;
const BAR_H = 80;
const ROW_Y = {public: ZONES.chart.top + 200, police: ZONES.chart.top + 560};
const px = (v: number) => ((RIGHT - LEFT) * v) / MAX;

export const ChannelBars: React.FC = () => {
	const frame = useCurrentFrame();
	const bars = useMemo(
		() => ({
			signs: ink.rect(LEFT, ROW_Y.public, px(SIGNS), BAR_H, {seed: 401, stroke: COLOR.public, fill: COLOR.public}),
			lottery: ink.rect(LEFT + px(SIGNS) + 6, ROW_Y.public, px(LOTTERY) - 6, BAR_H, {seed: 402, stroke: COLOR.public, fill: LOTTERY_GREEN, hachureAngle: 60}),
			bolo: ink.rect(LEFT, ROW_Y.police, px(BOLO), BAR_H, {seed: 403, stroke: COLOR.police, fill: COLOR.police}),
		}),
		[],
	);
	const grow = (start: number) => interpolate(frame, [start, start + 24], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	const fade = (start: number) => interpolate(frame, [start, start + 8], [0, 1], clamp);
	const pub = grow(6);
	const pol = grow(16);
	const clip = (id: string, y: number, w: number) => (
		<clipPath id={id}>
			<rect x={LEFT - 20} y={y - 20} width={(w + 40)} height={BAR_H + 40} />
		</clipPath>
	);
	return (
		<Page>
			{clip('ch-pub', ROW_Y.public, px(SIGNS + LOTTERY) * pub)}
			{clip('ch-pol', ROW_Y.police, px(BOLO) * pol)}
			<Scrawl x={LEFT} y={ROW_Y.public - 44} size={50} anchor="start" opacity={fade(6)} seed="c7a">
				Public alerts
			</Scrawl>
			<g clipPath="url(#ch-pub)">
				<Ink drawable={bars.signs} />
				<Ink drawable={bars.lottery} />
			</g>
			<Scrawl x={LEFT + px(SIGNS + LOTTERY) + 24} y={ROW_Y.public + BAR_H / 2} size={56} anchor="start" opacity={fade(26)} seed="c7b">
				{SIGNS + LOTTERY}
			</Scrawl>
			<Scrawl x={LEFT} y={ROW_Y.public + BAR_H + 44} size={36} anchor="start" opacity={fade(28)} seed="c7c">
				{`highway signs ${SIGNS}`}
			</Scrawl>
			<Scrawl x={LEFT + px(SIGNS + LOTTERY)} y={ROW_Y.public + BAR_H + 44} size={36} anchor="end" opacity={fade(32)} seed="c7d">
				{`lottery ${LOTTERY}`}
			</Scrawl>
			<Scrawl x={LEFT} y={ROW_Y.police - 44} size={50} anchor="start" opacity={fade(16)} seed="c7e">
				Police BOLO
			</Scrawl>
			<g clipPath="url(#ch-pol)">
				<Ink drawable={bars.bolo} />
			</g>
			<Scrawl x={LEFT + px(BOLO) + 24} y={ROW_Y.police + BAR_H / 2} size={56} anchor="start" opacity={fade(36)} seed="c7f">
				{BOLO}
			</Scrawl>
			<ScopeNote opacity={fade(40)}>FDLE success stories that name a channel</ScopeNote>
		</Page>
	);
};
