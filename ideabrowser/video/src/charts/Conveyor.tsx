// Card 3 ("Gmail to classified in an hour"): envelopes ride a conveyor through two stations.
// Claude Code turns each email into a card; Jev tags it and it drops into its bin. The items are
// 25 real newsletter-era ideas sampled in proportion to that era's mix (data.conveyor), so the
// bins fill in true proportions: services narrowly ahead of software.
// A clock sweeps 50 minutes: raw emails on disk to all 1,433 ideas classified (git timestamps).
// Length is fixed by the edit: 34:20 to 39:09 (SS:FF at 30 fps) = 139 frames.
// The stations show the tool names until logo files are added (see LOGOS).
import React, {useMemo} from 'react';
import {Easing, interpolate, staticFile, useCurrentFrame} from 'remotion';
import data from '../data/ideabrowser.json';
import {INK, Ink, Page, Scrawl, TYPE_INK, ZONES, ink, ramp} from '../sharpie';

export const CONVEYOR_DURATION = 139;

// Drop logo files in video/public/logos/ and set their names here; null shows the tool name.
const LOGOS: {claude: string | null; jev: string | null} = {claude: 'claude.webp', jev: 'typesafe.png'};

const BELT_Y = 720; // top surface of the belt
const BELT = {from: ZONES.chart.left, to: 770};
const BOX = 190;
const STATIONS = [
	{x: 330, name: 'Claude Code', logo: LOGOS.claude},
	{x: 595, name: 'Jev', logo: LOGOS.jev},
];
const ITEM = {w: 58, h: 40};
const SPAWN = {first: 4, every: 3.2}; // frames: the 25th card lands by frame 137 of 139
const TRAVEL = 40; // frames from belt start to belt end
const FALL = 16; // frames from belt end into a bin
const BIN = {w: 170, h: 150, top: 880};
const BIN_ORDER = ['service', 'software', 'marketplace', 'other'] as const;
const BIN_LABEL = {service: 'Services', software: 'Software', marketplace: 'Marketplace', other: 'Other'};
const BIN_INK = {service: TYPE_INK.service, software: TYPE_INK.software, marketplace: INK.green, other: INK.gray};
const binX = (i: number) => ZONES.chart.left + 105 + i * 210;
const CLOCK = {x: ZONES.chart.right - 70, y: ZONES.chart.top + 90, r: 62, minutes: 50};

export const Conveyor: React.FC = () => {
	const frame = useCurrentFrame();
	const items = data.conveyor as (typeof BIN_ORDER)[number][];

	const belt = useMemo(() => ink.line(BELT.from, BELT_Y + 6, BELT.to, BELT_Y + 6, {seed: 1, strokeWidth: 10}), []);
	const rollers = useMemo(
		() => Array.from({length: 7}, (_, i) => ink.dot(BELT.from + 20 + i * ((BELT.to - BELT.from - 40) / 6), BELT_Y + 32, 34, {seed: 2 + i, fill: 'white', fillStyle: 'solid'})),
		[],
	);
	const boxes = useMemo(
		() => STATIONS.map((s, i) => ink.rect(s.x - BOX / 2, BELT_Y - BOX, BOX, BOX, {seed: 20 + i, fill: 'white', fillStyle: 'solid'})),
		[],
	);
	const bins = useMemo(
		() => BIN_ORDER.map((b, i) => ink.path([[binX(i) - BIN.w / 2, BIN.top], [binX(i) - BIN.w / 2 + 12, BIN.top + BIN.h], [binX(i) + BIN.w / 2 - 12, BIN.top + BIN.h], [binX(i) + BIN.w / 2, BIN.top]], {seed: 30 + i, stroke: BIN_INK[b]})),
		[],
	);
	const clockFace = useMemo(() => ink.dot(CLOCK.x, CLOCK.y, CLOCK.r * 2, {seed: 40, fill: 'white', fillStyle: 'solid', strokeWidth: 6}), []);
	const clockSweep = interpolate(frame, [SPAWN.first, CONVEYOR_DURATION - 6], [0, (CLOCK.minutes / 60) * 360], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	const handRad = ((clockSweep - 90) * Math.PI) / 180;
	const hand = ink.line(CLOCK.x, CLOCK.y, CLOCK.x + (CLOCK.r - 14) * Math.cos(handRad), CLOCK.y + (CLOCK.r - 14) * Math.sin(handRad), {seed: 41, strokeWidth: 7, stroke: INK.red});
	const appear = ramp(frame, 0, 8);

	// Each item: where it is, what it looks like, and whether it has landed.
	const landed: Record<string, number> = {service: 0, software: 0, marketplace: 0, other: 0};
	const drawn = items.map((type, i) => {
		const t = frame - (SPAWN.first + i * SPAWN.every);
		if (t < 0) return null;
		const bin = BIN_ORDER.indexOf(type);
		let x: number;
		let y: number;
		if (t <= TRAVEL) {
			x = interpolate(t, [0, TRAVEL], [BELT.from - 20, BELT.to]);
			y = BELT_Y - ITEM.h;
		} else {
			// Drop off the belt's end first, then glide across above the bins, so no card cuts under the belt.
			const f = Math.min(1, (t - TRAVEL) / FALL);
			const LANE = BELT_Y + 120; // between the rollers and the bin rims
			const drop = Math.min(1, f / 0.35);
			const glide = Math.max(0, (f - 0.35) / 0.65);
			x = f < 0.35 ? BELT.to + 30 * drop : interpolate(glide, [0, 1], [BELT.to + 30, binX(bin)], {easing: Easing.inOut(Easing.quad)});
			y = f < 0.35 ? interpolate(drop, [0, 1], [BELT_Y - ITEM.h, LANE], {easing: Easing.in(Easing.quad)}) : interpolate(glide, [0, 1], [LANE, BIN.top + BIN.h - ITEM.h - 10], {easing: Easing.in(Easing.quad)});
			if (f >= 1) {
				landed[type] += 1;
				return null; // counted in the bin's fill instead
			}
		}
		const stage = x < STATIONS[0].x ? 'email' : x < STATIONS[1].x ? 'card' : 'tagged';
		const left = x - ITEM.w / 2;
		const seed = 100 + i * 5;
		const color = BIN_INK[type];
		return (
			<g key={i}>
				<Ink drawable={ink.rect(left, y, ITEM.w, ITEM.h, {seed, strokeWidth: 4, fill: 'white', fillStyle: 'solid'})} />
				{stage === 'email' ? (
					<Ink drawable={ink.path([[left + 2, y + 2], [x, y + ITEM.h * 0.55], [left + ITEM.w - 2, y + 2]], {seed: seed + 1, strokeWidth: 3})} />
				) : (
					<>
						<Ink drawable={ink.line(left + 14, y + 13, left + ITEM.w - 8, y + 13, {seed: seed + 2, strokeWidth: 3, stroke: INK.gray})} />
						<Ink drawable={ink.line(left + 14, y + 26, left + ITEM.w - 16, y + 26, {seed: seed + 3, strokeWidth: 3, stroke: INK.gray})} />
						{stage === 'tagged' && <rect x={left + 3} y={y + 3} width={8} height={ITEM.h - 6} fill={color} />}
					</>
				)}
			</g>
		);
	});
	const maxFill = Math.max(...BIN_ORDER.map((b) => items.filter((t) => t === b).length));

	return (
		<Page>
			<g opacity={appear}>
				<Ink drawable={belt} />
				{rollers.map((r, i) => (
					<Ink key={i} drawable={r} />
				))}
				<Ink drawable={clockFace} />
				{[0, 90, 180, 270].map((a) => (
					<circle key={a} cx={CLOCK.x + (CLOCK.r - 12) * Math.cos(((a - 90) * Math.PI) / 180)} cy={CLOCK.y + (CLOCK.r - 12) * Math.sin(((a - 90) * Math.PI) / 180)} r={4} fill={INK.black} />
				))}
				<Ink drawable={hand} />
			</g>
			{drawn}
			{STATIONS.map((s, i) => (
				<g key={i} opacity={appear}>
					<Ink drawable={boxes[i]} />
					{s.logo ? (
						<image href={staticFile(`logos/${s.logo}`)} x={s.x - 70} y={BELT_Y - BOX / 2 - 70} width={140} height={140} preserveAspectRatio="xMidYMid meet" />
					) : (
						s.name.split(' ').map((word, w, words) => (
							<Scrawl key={w} x={s.x} y={BELT_Y - BOX / 2 + (w - (words.length - 1) / 2) * 50} size={48} seed={`st${i}${w}`}>
								{word}
							</Scrawl>
						))
					)}
				</g>
			))}
			{BIN_ORDER.map((b, i) => {
				const n = landed[b];
				const fillH = (n / maxFill) * (BIN.h - 16);
				return (
					<g key={b} opacity={appear}>
						{n > 0 && (
							<rect x={binX(i) - BIN.w / 2 + 16} y={BIN.top + BIN.h - 6 - fillH} width={BIN.w - 32} height={fillH} fill={BIN_INK[b]} opacity={0.85} rx={4} />
						)}
						<Ink drawable={bins[i]} />
						<Scrawl x={binX(i)} y={BIN.top + BIN.h + 45} size={b === 'marketplace' ? 30 : 36} color={BIN_INK[b]} seed={`b${i}`}>
							{BIN_LABEL[b]}
						</Scrawl>
					</g>
				);
			})}
		</Page>
	);
};
