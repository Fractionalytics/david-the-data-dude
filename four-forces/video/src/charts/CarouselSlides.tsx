// Four Forces carousel slides (1080x1350, 4:5). Every word is David's: slide 1 is his title, word for
// word (2026-10-16); slides 3-6 are the force names (his Video column) and his Reel definitions (Sheet
// card 14), word for word, only broken onto lines. Slide 2 is the Reel's final table frame, cropped by
// shared/video-kit/carousel_frame.py, so it isn't here. See carousel/slides.md.
import React, {useMemo} from 'react';
import {AbsoluteFill} from 'remotion';
import {INK, Ink, Scrawl, ink} from '../sharpie';
import {COOL, HOT} from './parts';

export const CAROUSEL = {width: 1080, height: 1350, fps: 30};
const CX = 540;

const SlidePage: React.FC<{children: React.ReactNode}> = ({children}) => (
	<AbsoluteFill style={{backgroundColor: 'white'}}>
		<svg width={1080} height={1350} viewBox="0 0 1080 1350">
			<defs>
				<filter id="marker-edge" filterUnits="userSpaceOnUse" x={0} y={0} width={1080} height={1350}>
					<feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves={1} seed={3} result="noise" />
					<feDisplacementMap in="SourceGraphic" in2="noise" scale={2.5} />
				</filter>
			</defs>
			{children}
		</svg>
	</AbsoluteFill>
);

// Slide 1: David's title, one word group per line.
const TITLE_LINES = ['My framework', 'for AI-driven', 'job loss risks'];
export const CarouselTitle: React.FC = () => {
	const underline = useMemo(() => ink.line(200, 860, 880, 860, {seed: 21, stroke: HOT, strokeWidth: 12}), []);
	return (
		<SlidePage>
			{TITLE_LINES.map((t, i) => (
				<Scrawl key={t} x={CX} y={480 + i * 150} size={124} seed={`t${i}`}>
					{t}
				</Scrawl>
			))}
			<Ink drawable={underline} />
		</SlidePage>
	);
};

// Slides 3-6: one force each. Definition lines are David's card 14 words, broken for width.
const FORCES = [
	{name: '1. TASK VS. JOB', lines: ['is the automatable task', 'most of the job,', 'or just one slice?']},
	{name: '2. GATEKEEPERS', lines: ['regulations, liability,', 'licensing,', 'who has to sign?']},
	{name: '3. DEMAND', lines: ['does cheaper work', 'create more or less', 'demand for it?']},
	{name: '4. CHECKING', lines: ['is the AI work', 'cheap to check,', 'or do mistakes', 'surface late?']},
];

const SEG_W = 70;
const SEG_GAP = 16;
const Meter: React.FC<{cx: number; cy: number; level: number; color: string; seed: number}> = ({cx, cy, level, color, seed}) => {
	const segs = useMemo(
		() =>
			[0, 1, 2].map((k) => {
				const x0 = cx - (3 * SEG_W + 2 * SEG_GAP) / 2 + k * (SEG_W + SEG_GAP);
				const filled = k < level;
				return ink.rect(x0, cy - 50, SEG_W, 100, {seed: seed + k, stroke: filled ? color : INK.gray, strokeWidth: 5, fill: filled ? color : undefined, hachureGap: 9});
			}),
		[cx, cy, level, color, seed],
	);
	return (
		<g>
			{segs.map((s, k) => (
				<Ink key={k} drawable={s} />
			))}
		</g>
	);
};

export const CarouselForce: React.FC<{index: number}> = ({index}) => {
	const f = FORCES[index];
	const rule = useMemo(() => ink.line(120, 400, 960, 400, {seed: 50 + index, stroke: INK.black, strokeWidth: 6}), [index]);
	const defTop = 530;
	const meterY = defTop + f.lines.length * 95 + 210;
	return (
		<SlidePage>
			<Scrawl x={CX} y={310} size={104} seed={`n${index}`}>
				{f.name}
			</Scrawl>
			<Ink drawable={rule} />
			{f.lines.map((l, i) => (
				<Scrawl key={i} x={CX} y={defTop + i * 95} size={72} seed={`d${index}${i}`}>
					{l}
				</Scrawl>
			))}
			{/* The force's row from the table: FAST weak, SLOW strong (docs/rubric-table.md). */}
			<Scrawl x={330} y={meterY - 110} size={60} color={HOT} seed={`fa${index}`}>
				FAST
			</Scrawl>
			<Scrawl x={750} y={meterY - 110} size={60} color={COOL} seed={`sl${index}`}>
				SLOW
			</Scrawl>
			<Meter cx={330} cy={meterY} level={1} color={HOT} seed={300 + index * 10} />
			<Meter cx={750} cy={meterY} level={3} color={COOL} seed={400 + index * 10} />
		</SlidePage>
	);
};
