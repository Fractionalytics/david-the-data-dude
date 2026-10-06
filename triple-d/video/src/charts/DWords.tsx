// Title card: "D-WORDS" scoreboard. Two columns (DAVID | TRIPLE-D) fill with D-words at set
// times; each word adds a point to its column's red score. Partway through, TRIPLE-D's words
// are erased and its score resets, then the column is filled again.
// ("DIVE-INS" is intentionally misspelled to match the taped voiceover.)
//
// Timing is in the editor's SS:FF timecode at 30 fps: each word starts writing on its frame.
import React, {useEffect, useMemo, useRef, useState} from 'react';
import {continueRender, delayRender, interpolate, useCurrentFrame} from 'remotion';
import {INK, Ink, MARKER_FONT, Page, VIDEO, ink, markerFontReady} from '../sharpie';

const FPS = 30;
const tc = (ss: number, ff: number) => ss * FPS + ff; // SS:FF -> frame number
const WRITE_FRAMES = 8; // each word writes out left to right over this many frames
const ERASE_FRAMES = 10;
const POP_FRAMES = 6; // score "pop" when it changes

type Col = 'L' | 'R';
type Event = {t: number; col: Col; word?: string; erase?: boolean};
const EVENTS: Event[] = [
	{t: tc(1, 8), col: 'L', word: 'DAVID'},
	{t: tc(1, 17), col: 'L', word: 'DATA'},
	{t: tc(1, 21), col: 'L', word: 'DUDE'},
	{t: tc(2, 25), col: 'L', word: 'DOING'},
	{t: tc(3, 6), col: 'L', word: 'DEEP'},
	{t: tc(3, 14), col: 'L', word: 'DIVE'},
	{t: tc(4, 2), col: 'R', word: 'DINERS'},
	{t: tc(4, 21), col: 'R', word: 'DIVE-INS'},
	{t: tc(5, 16), col: 'R', word: 'DIVES'},
	{t: tc(6, 14), col: 'R', erase: true},
	{t: tc(7, 9), col: 'R', word: 'DINERS'},
	{t: tc(7, 26), col: 'R', word: 'DRIVE-INS'},
	{t: tc(8, 15), col: 'R', word: 'DIVES'},
];
const LAST = Math.max(...EVENTS.map((e) => e.t));
export const D_WORDS_DURATION = LAST + WRITE_FRAMES + 2 * FPS; // hold 2 s after the last word

// Each word with its column, row (rows restart after an erase) and when (if ever) it is erased.
type Placed = {word: string; col: Col; row: number; t: number; erasedAt: number | null};
const PLACED: Placed[] = (() => {
	const out: Placed[] = [];
	const row = {L: 0, R: 0};
	for (const e of EVENTS) {
		if (e.erase) {
			out.filter((p) => p.col === e.col && p.erasedAt === null).forEach((p) => (p.erasedAt = e.t));
			row[e.col] = 0;
		} else if (e.word) {
			out.push({word: e.word, col: e.col, row: row[e.col]++, t: e.t, erasedAt: null});
		}
	}
	return out;
})();

const score = (col: Col, frame: number) =>
	PLACED.filter((p) => p.col === col && p.t <= frame && (p.erasedAt === null || frame < p.erasedAt)).length;
const lastChange = (col: Col, frame: number) =>
	Math.max(-Infinity, ...EVENTS.filter((e) => e.col === col && e.t <= frame).map((e) => e.t));

// Layout: everything sits in the top ~1300px, leaving the bottom free for a talking head.
const COL_X = {L: VIDEO.width * 0.25, R: VIDEO.width * 0.75};
const TITLE_Y = 95;
const NAME_Y = 205;
const SCORE_Y = 300;
const RULE_Y = 370;
const ROW_Y0 = 455;
const ROW_STEP = 150;
const DIVIDER_BOTTOM = 1280;
const WORD_SIZE = 84;

export const DWords: React.FC = () => {
	const frame = useCurrentFrame();
	const refs = useRef<(SVGTextElement | null)[]>([]);
	const [widths, setWidths] = useState<number[] | null>(null);
	const [handle] = useState(() => delayRender('measure words'));

	// Measure each word once the marker font has loaded, so the write-out wipe fits the real text.
	useEffect(() => {
		markerFontReady().then(() => {
			setWidths(PLACED.map((_, i) => refs.current[i]!.getBBox().width));
			continueRender(handle);
		});
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	const lines = useMemo(
		() => [
			ink.line(VIDEO.width / 2, NAME_Y - 50, VIDEO.width / 2, DIVIDER_BOTTOM, {seed: 61, strokeWidth: 9}),
			ink.line(60, RULE_Y, VIDEO.width - 60, RULE_Y, {seed: 62, strokeWidth: 9}),
		],
		[],
	);
	const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

	const text = (x: number, y: number, size: number, color: string, children: React.ReactNode, scale = 1) => (
		<text
			x={x}
			y={y}
			fontFamily={MARKER_FONT}
			fontSize={size}
			fill={color}
			textAnchor="middle"
			dominantBaseline="middle"
			transform={scale === 1 ? undefined : `translate(${x} ${y}) scale(${scale}) translate(${-x} ${-y})`}
		>
			{children}
		</text>
	);

	return (
		<Page>
			{text(VIDEO.width / 2, TITLE_Y, 76, INK.black, 'D-WORDS')}
			<Ink drawable={lines[0]} />
			<Ink drawable={lines[1]} />
			{(['L', 'R'] as Col[]).map((col) => {
				const pop = interpolate(frame - lastChange(col, frame), [0, POP_FRAMES], [1.35, 1], clamp);
				return (
					<g key={col}>
						{text(COL_X[col], NAME_Y, 64, INK.black, col === 'L' ? 'DAVID' : 'TRIPLE-D')}
						{text(COL_X[col], SCORE_Y, 104, INK.red, score(col, frame), pop)}
					</g>
				);
			})}
			{PLACED.map((p, i) => {
				const w = widths?.[i] ?? 0;
				const written = interpolate(frame, [p.t - 1, p.t + WRITE_FRAMES - 1], [0, 1], clamp);
				// Erasing wipes the word away left to right.
				const erased = p.erasedAt === null ? 0 : interpolate(frame, [p.erasedAt - 1, p.erasedAt + ERASE_FRAMES - 1], [0, 1], clamp);
				const x0 = COL_X[p.col] - w / 2 - 10;
				const y = ROW_Y0 + p.row * ROW_STEP;
				return (
					<g key={i}>
						<clipPath id={`dw-${i}`}>
							<rect x={x0 + (w + 20) * erased} y={y - WORD_SIZE} width={(w + 20) * Math.max(0, written - erased)} height={WORD_SIZE * 2} />
						</clipPath>
						<text
							ref={(el) => {
								refs.current[i] = el;
							}}
							x={COL_X[p.col]}
							y={y}
							fontFamily={MARKER_FONT}
							fontSize={WORD_SIZE}
							fill={INK.black}
							textAnchor="middle"
							dominantBaseline="middle"
							clipPath={widths ? `url(#dw-${i})` : undefined}
							opacity={widths ? 1 : 0}
						>
							{p.word}
						</text>
					</g>
				);
			})}
		</Page>
	);
};
