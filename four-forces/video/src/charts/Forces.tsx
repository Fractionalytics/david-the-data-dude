// Cards 13-17: the four forces. Words on screen are David's, word for word (Video column, 2026-10-16):
// title "FOUR FORCES", the list "1. TASK VS. JOB / 2. GATEKEEPERS / 3. DEMAND / 4. CHECKING", and the
// table headers "FORCE", "FAST", "SLOW". Each force's strength in a lane is a three-segment meter (no
// words): weak = one segment, strong = three. "The stronger the force, the more secure the job."
// One component, one composition per card (playbook: repeat a chart, don't redraw it):
//   title - card 13, the title alone
//   list  - card 14, each force fully on screen at David's timecode
//   table - card 15, the list shrinks into the table; FAST and SLOW headers appear as each lane is named
//   fast  - card 16's second half, FAST meters fill (all weak)
//   slow  - card 17's last beat, SLOW meters fill (all strong)
// Timing: ../cues.ts.
import React, {useMemo} from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {CUE} from '../cues';
import {INK, Ink, Page, Scrawl, ZONES, ink, ramp} from '../sharpie';
import {COOL, CX, HOT} from './parts';

const FORCES = ['TASK VS. JOB', 'GATEKEEPERS', 'DEMAND', 'CHECKING'];
// Meter level (out of 3) per lane, from the rubric (docs/rubric-table.md).
const LEVEL = {fast: [1, 1, 1, 1], slow: [3, 3, 3, 3]};
export type ForcesMode = 'title' | 'list' | 'table' | 'fast' | 'slow';
export const FORCES_DURATION: Record<ForcesMode, number> = {
	title: CUE.c13.dur,
	list: CUE.c14.dur,
	table: CUE.c15.dur,
	fast: CUE.c16b.dur,
	slow: CUE.c17c.dur,
};

const TITLE_Y = ZONES.chart.top + 50;
const ROW0 = ZONES.chart.top + 260;
const ROW_H = 165;
const COL_FORCE = ZONES.chart.left + 10;
const COL_FAST = ZONES.chart.left + 560;
const COL_SLOW = ZONES.chart.left + 740;
const SEG_W = 42;
const SEG_GAP = 10;
const LIST_SIZE = 64;
const TABLE_SIZE = 50;
const MOVE_FRAMES = 20;

const Meter: React.FC<{cx: number; cy: number; level: number; color: string; seed: number; on: number}> = ({cx, cy, level, color, seed, on}) => {
	const segs = useMemo(
		() =>
			[0, 1, 2].map((k) => {
				const x0 = cx - (3 * SEG_W + 2 * SEG_GAP) / 2 + k * (SEG_W + SEG_GAP);
				const filled = k < level;
				return ink.rect(x0, cy - 30, SEG_W, 60, {seed: seed + k, stroke: filled ? color : INK.gray, strokeWidth: 4, fill: filled ? color : undefined, hachureGap: 7});
			}),
		[cx, cy, level, color, seed],
	);
	return (
		<g opacity={on}>
			{segs.map((s, k) => (
				<Ink key={k} drawable={s} />
			))}
		</g>
	);
};

export const Forces: React.FC<{mode: ForcesMode}> = ({mode}) => {
	const frame = useCurrentFrame();
	const rule = useMemo(() => ink.line(ZONES.chart.left, ROW0 - 95, ZONES.chart.right, ROW0 - 95, {seed: 7, stroke: INK.black, strokeWidth: 5}), []);
	const isTable = mode === 'table' || mode === 'fast' || mode === 'slow';
	// Card 15 shrinks the list into the table; later cards start in the table.
	const shrink = mode === 'table' ? interpolate(frame, [CUE.c15.move, CUE.c15.move + MOVE_FRAMES], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : isTable ? 1 : 0;
	const size = interpolate(shrink, [0, 1], [LIST_SIZE, TABLE_SIZE]);
	const headers = {
		force: mode === 'table' ? ramp(frame, CUE.c15.move + 6, 10) : 1,
		fast: mode === 'table' ? ramp(frame, CUE.c15.fast, 10) : 1,
		slow: mode === 'table' ? ramp(frame, CUE.c15.slow, 10) : 1,
	};
	// A force is fully on screen at its cue: the fade ends on the cue frame.
	const itemOn = (i: number) => {
		if (mode === 'title') return 0;
		if (mode === 'list') return ramp(frame, CUE.c14.items[i] - 10, 10);
		return 1;
	};
	return (
		<Page>
			<Scrawl x={CX} y={TITLE_Y} size={84} opacity={mode === 'title' ? ramp(frame, 0, 10) : 1} seed="title">
				FOUR FORCES
			</Scrawl>
			{isTable && (
				<g>
					<Scrawl x={COL_FORCE} y={ROW0 - 140} size={44} anchor="start" color={INK.gray} opacity={headers.force} seed="hf">
						FORCE
					</Scrawl>
					<Scrawl x={COL_FAST} y={ROW0 - 140} size={44} color={HOT} opacity={headers.fast} seed="hfa">
						FAST
					</Scrawl>
					<Scrawl x={COL_SLOW} y={ROW0 - 140} size={44} color={COOL} opacity={headers.slow} seed="hs">
						SLOW
					</Scrawl>
					<Ink drawable={rule} progress={mode === 'table' ? ramp(frame, CUE.c15.move + 6, 14) : 1} />
				</g>
			)}
			{FORCES.map((f, i) => (
				<g key={f}>
					<Scrawl x={COL_FORCE} y={ROW0 + i * ROW_H} size={size} anchor="start" opacity={itemOn(i)} seed={`f${i}`}>
						{`${i + 1}. ${f}`}
					</Scrawl>
					{(mode === 'fast' || mode === 'slow') && (
						<Meter cx={COL_FAST} cy={ROW0 + i * ROW_H} level={LEVEL.fast[i]} color={HOT} seed={60 + i * 5} on={mode === 'fast' ? ramp(frame, 8 + i * 12, 8) : 1} />
					)}
					{mode === 'slow' && <Meter cx={COL_SLOW} cy={ROW0 + i * ROW_H} level={LEVEL.slow[i]} color={COOL} seed={90 + i * 5} on={ramp(frame, 8 + i * 12, 8)} />}
				</g>
			))}
		</Page>
	);
};
