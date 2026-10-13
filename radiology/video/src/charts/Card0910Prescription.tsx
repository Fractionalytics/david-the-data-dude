// Revised cards 9-10 (00:22:20 = 680 frames): "2. PRESCRIPTION" (David's words), matching the
// "1. CAPABILITY" card, then it moves up and the frame turns into a picture of epistemic
// trespassing: two fenced fields, "AI" (Hinton's expertise) and "labor economics" (where the
// prescription landed, David's framing), with a trail stepping over the fence, labelled
// "EPISTEMIC TRESPASSING".
//
// Cue ESTIMATES (David gave only the 22.7 s total; cards 9+10 = 60 words, ~2.65 words/s):
//   card 10 starts ("It seems Dr. Hinton...")  ~ word 24 -> 9 s    -> fields at frame 255
//   "epistemic trespassing"                    ~ word 31 -> 11.7 s -> trail 300-370, label 350
import React, {useMemo} from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {INK, Ink, Page, Scrawl, ZONES, ink, ramp} from '../sharpie';
import {CX} from './parts';

export const CARD0910_DURATION = 680;
const MOVE_AT = 230;
const FIELDS_AT = 255;
const TRAIL_AT = 300;
const LABEL_AT = 350;

const TOP = ZONES.chart.top + 230;
const BOTTOM = ZONES.chart.top + 640;
const FENCE_X = CX;
const TRAIL: [number, number][] = Array.from({length: 21}, (_, i) => {
	const t = i / 20;
	return [ZONES.chart.left + 190 + t * 460, BOTTOM - 120 - Math.sin(Math.PI * t) * 170];
});

export const Card0910Prescription: React.FC = () => {
	const frame = useCurrentFrame();
	const move = interpolate(frame, [MOVE_AT, MOVE_AT + 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const titleY = interpolate(move, [0, 1], [ZONES.chart.top + 420, ZONES.chart.top + 40]);
	// 96 is the largest size at which "2. PRESCRIPTION" fits the 840px safe width.
	const titleSize = interpolate(move, [0, 1], [96, 72]);
	const shapes = useMemo(
		() => [
			ink.rect(ZONES.chart.left, TOP, FENCE_X - ZONES.chart.left - 30, BOTTOM - TOP, {seed: 91, strokeWidth: 6}),
			ink.rect(FENCE_X + 30, TOP, ZONES.chart.right - FENCE_X - 30, BOTTOM - TOP, {seed: 92, strokeWidth: 6}),
			// The fence: a post line with three rails.
			ink.line(FENCE_X, TOP - 30, FENCE_X, BOTTOM + 30, {seed: 93, strokeWidth: 10}),
			...[0.25, 0.5, 0.75].map((f, i) => ink.line(FENCE_X - 40, TOP + f * (BOTTOM - TOP), FENCE_X + 40, TOP + f * (BOTTOM - TOP), {seed: 94 + i, strokeWidth: 8})),
		],
		[],
	);
	const trail = useMemo(() => ink.path(TRAIL, {seed: 98, stroke: INK.red, strokeWidth: 8, strokeLineDash: [18, 16]}), []);
	const end = TRAIL[TRAIL.length - 1];
	const dot = useMemo(() => ink.dot(end[0], end[1], 40, {seed: 99, stroke: INK.red, fill: INK.red}), [end]);
	const fields = ramp(frame, FIELDS_AT, 12);
	return (
		<Page>
			<Scrawl x={CX} y={titleY} size={titleSize} opacity={ramp(frame, 0, 10)} seed="rx">
				2. PRESCRIPTION
			</Scrawl>
			<g opacity={fields}>
				{shapes.map((s, i) => (
					<Ink key={i} drawable={s} />
				))}
				<Scrawl x={(ZONES.chart.left + FENCE_X) / 2} y={TOP + 70} size={72} seed="ai">
					AI
				</Scrawl>
				<Scrawl x={(FENCE_X + ZONES.chart.right) / 2} y={TOP + 60} size={46} seed="le1">
					labor
				</Scrawl>
				<Scrawl x={(FENCE_X + ZONES.chart.right) / 2} y={TOP + 112} size={46} seed="le2">
					economics
				</Scrawl>
			</g>
			<Ink drawable={trail} progress={ramp(frame, TRAIL_AT, 60)} connect />
			{frame >= TRAIL_AT + 60 && <Ink drawable={dot} />}
			<Scrawl x={CX} y={BOTTOM + 120} size={64} color={INK.red} opacity={ramp(frame, LABEL_AT, 10)} seed="et1">
				EPISTEMIC
			</Scrawl>
			<Scrawl x={CX} y={BOTTOM + 195} size={64} color={INK.red} opacity={ramp(frame, LABEL_AT, 10)} seed="et2">
				TRESPASSING
			</Scrawl>
		</Page>
	);
};
