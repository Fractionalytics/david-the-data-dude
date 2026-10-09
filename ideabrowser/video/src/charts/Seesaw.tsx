// Card 6: Services vs Software as stacks of blocks on a seesaw, one block per featured idea.
// August's stacks build (services 15, software 8) and the heavier side sinks; then 7 blocks
// leave the services stack as 7 land on software (September: 8 vs 15), and the plank tips over.
// The tilt follows the live difference between the stacks, so the weight drives the motion.
// Everything is drawn in page coordinates: the kit's marker-edge filter covers the page, so
// strokes inside a translated or rotated <g> would be clipped left of or above its origin.
import React, {useMemo} from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import data from '../data/ideabrowser.json';
import {Ink, Page, Scrawl, TYPE_INK, ZONES, ink, ramp} from '../sharpie';

const CX = (ZONES.chart.left + ZONES.chart.right) / 2;
const PIVOT_Y = ZONES.chart.bottom - 190;
const HALF = 300; // half the plank's length; the stacks sit this far from the pivot
const TILT = 13; // degrees at a full 7-block difference
const COLS = 3; // blocks per row in a stack
const BLOCK = 40;
const LABEL_Y = ZONES.chart.top + 205; // side labels: below the month title, above the tallest stack
const LABEL_DX = 270; // label centers; keeps "Software" inside the 120px side margin
const GAP = 5;
const BUILD = [8, 3]; // August stacks: start frame, frames per block
const MOVE = [100, 4]; // September: start frame, frames per block moved
export const SEESAW_DURATION = MOVE[0] + 7 * MOVE[1] + 55;

const MONTH = (m: string) => new Date(m + '-15T12:00').toLocaleDateString('en-US', {month: 'long'});
const smooth = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const, easing: Easing.inOut(Easing.quad)};

// Continuous block count at a frame: builds to `aug`, then moves to `sep`.
const countAt = (frame: number, aug: number, sep: number) => {
	const built = interpolate(frame, [BUILD[0], BUILD[0] + aug * BUILD[1]], [0, aug], smooth);
	const moves = Math.abs(sep - aug);
	return frame < MOVE[0] ? built : interpolate(frame, [MOVE[0], MOVE[0] + moves * MOVE[1]], [aug, sep], smooth);
};

export const Seesaw: React.FC = () => {
	const frame = useCurrentFrame();
	const [aug, sep] = data.seesaw;
	const counts = [countAt(frame, aug.service, sep.service), countAt(frame, aug.software, sep.software)];
	const shown = counts.map((c) => Math.round(c));
	// + tips the right (software) side down; a full TILT at the 7-block gap between the months.
	const angle = Math.max(-1, Math.min(1, (counts[1] - counts[0]) / Math.abs(aug.service - aug.software))) * TILT;
	const rad = (angle * Math.PI) / 180;
	const top = PIVOT_Y - 8; // the plank rests on the pivot's tip
	const at = (d: number) => ({x: CX + d * Math.cos(rad), y: top + d * Math.sin(rad)});
	const ends = [at(-HALF), at(HALF)];
	const tips = [at(-HALF - 110), at(HALF + 110)];
	const month = frame < MOVE[0] + 14 ? aug : sep;

	const pivot = useMemo(() => ink.path([[CX - 70, PIVOT_Y + 90], [CX, PIVOT_Y - 6], [CX + 70, PIVOT_Y + 90], [CX - 70, PIVOT_Y + 90]], {seed: 1}), []);
	const ground = useMemo(() => ink.line(ZONES.chart.left, PIVOT_Y + 92, ZONES.chart.right, PIVOT_Y + 92, {seed: 2, strokeWidth: 5}), []);
	const plank = ink.line(tips[0].x, tips[0].y, tips[1].x, tips[1].y, {seed: 3, strokeWidth: 20, roughness: 0.4});
	const sides = [
		{label: 'Services', color: TYPE_INK.service},
		{label: 'Software', color: TYPE_INK.software},
	];
	const appear = ramp(frame, 0, 10);
	// August fades out as the blocks start moving; September fades in halfway through.
	const monthOpacity = frame < MOVE[0] + 14 ? appear * (1 - ramp(frame, MOVE[0] + 4, 10)) : ramp(frame, MOVE[0] + 14, 8);
	const stackWidth = COLS * BLOCK + (COLS - 1) * GAP;

	return (
		<Page>
			<Scrawl x={CX} y={ZONES.chart.top + 70} size={84} opacity={monthOpacity} seed={month.month}>
				{MONTH(month.month)}
			</Scrawl>
			<Ink drawable={ground} progress={appear} />
			<Ink drawable={pivot} progress={appear} />
			<g opacity={appear}>
				<Ink drawable={plank} />
			</g>
			{ends.map((e, s) => {
				const base = e.y - 12; // stacks stand on the plank's top edge
				const rows = Math.ceil(Math.max(shown[s], 1) / COLS);
				return (
					<g key={s}>
						{Array.from({length: shown[s]}, (_, b) => {
							const col = b % COLS;
							const row = Math.floor(b / COLS);
							const x = e.x - stackWidth / 2 + col * (BLOCK + GAP);
							const y = base - (row + 1) * (BLOCK + GAP);
							return (
								<Ink
									key={b}
									drawable={ink.rect(x, y, BLOCK, BLOCK, {seed: 100 * s + b, stroke: sides[s].color, fill: sides[s].color, strokeWidth: 4, hachureGap: 6})}
								/>
							);
						})}
						<Scrawl x={e.x} y={base - rows * (BLOCK + GAP) - 60} size={96} color={sides[s].color} opacity={appear} seed={`n${s}`}>
							{String(shown[s])}
						</Scrawl>
						{/* Fixed between the month title and the tallest stack's count, so it never moves. */}
						<Scrawl x={CX + (s ? LABEL_DX : -LABEL_DX)} y={LABEL_Y} size={64} color={sides[s].color} opacity={appear} seed={`l${s}`}>
							{sides[s].label}
						</Scrawl>
					</g>
				);
			})}
			<Scrawl x={CX} y={ZONES.chart.bottom - 2} size={28} color="#8f8f8f" opacity={appear} seed="foot">
				{`One block per featured idea (${aug.total} in Aug, ${sep.total} in Sep)`}
			</Scrawl>
		</Page>
	);
};
