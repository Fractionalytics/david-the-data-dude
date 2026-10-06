// Title card: DINERS / DRIVE-INS / DIVES are written out one per line, then each gets a red
// marker strike-through, left to right. No chart. The three lines are centered in the same top
// area the charts use, leaving the bottom of the frame free for a talking head.
//
// Timing is in the editor's HH:MM:SS:FF timecode at 30 fps. Each animation starts on its first
// frame and is complete on its last frame (inclusive).
import React, {useEffect, useMemo, useRef, useState} from 'react';
import {continueRender, delayRender, interpolate, useCurrentFrame} from 'remotion';
import {INK, Ink, MARKER_FONT, Page, VIDEO, ink, markerFontReady} from '../sharpie';

const FPS = 30;
const tc = (ss: number, ff: number) => ss * FPS + ff; // SS:FF -> frame number

const WORDS = [
	{text: 'DINERS', write: [tc(1, 23), tc(2, 13)], strike: [tc(4, 25), tc(5, 16)]},
	{text: 'DRIVE-INS', write: [tc(2, 15), tc(3, 6)], strike: [tc(6, 4), tc(6, 27)]},
	{text: 'DIVES', write: [tc(3, 13), tc(4, 1)], strike: [tc(7, 14), tc(8, 3)]},
] as const;
// Hold everything still for 2 s after the last strike's final frame.
export const DDD_STRIKE_DURATION = tc(8, 3) + 1 + 2 * FPS;

const FONT_SIZE = 165; // largest size that keeps DRIVE-INS and its strike-through inside the frame
const LINE_Y = [400, 700, 1000]; // centers of the three lines, within the charts' top area
const CENTER_X = VIDEO.width / 2;

export const DddStrike: React.FC = () => {
	const frame = useCurrentFrame();
	const refs = [useRef<SVGTextElement>(null), useRef<SVGTextElement>(null), useRef<SVGTextElement>(null)];
	const [widths, setWidths] = useState<number[] | null>(null);
	const [handle] = useState(() => delayRender('measure words'));

	// Measure each word once the marker font has loaded, so wipes and strikes fit the real text.
	useEffect(() => {
		markerFontReady().then(() => {
			setWidths(refs.map((r) => r.current!.getBBox().width));
			continueRender(handle);
		});
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	const strikes = useMemo(
		() =>
			widths
				? WORDS.map((_, i) => {
						const half = widths[i] / 2 + 24;
						const y = LINE_Y[i] - 4;
						return ink.line(CENTER_X - half, y + 6, CENTER_X + half, y - 6, {seed: 40 + i, stroke: INK.red, strokeWidth: 22, roughness: 0.8});
					})
				: [],
		[widths],
	);

	// 0 before the first frame, 1 on (and after) the last frame.
	const progress = ([start, end]: readonly [number, number]) =>
		interpolate(frame, [start - 1, end], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

	return (
		<Page>
			{WORDS.map((w, i) => {
				const width = widths?.[i] ?? 0;
				const written = progress(w.write);
				return (
					<g key={w.text}>
						{/* "Writing" = the word is revealed left to right by a growing clip. */}
						<clipPath id={`write-${i}`}>
							<rect x={CENTER_X - width / 2 - 10} y={LINE_Y[i] - FONT_SIZE} width={(width + 20) * written} height={FONT_SIZE * 2} />
						</clipPath>
						<text
							ref={refs[i]}
							x={CENTER_X}
							y={LINE_Y[i]}
							fontFamily={MARKER_FONT}
							fontSize={FONT_SIZE}
							fill={INK.black}
							textAnchor="middle"
							dominantBaseline="middle"
							clipPath={widths ? `url(#write-${i})` : undefined}
							opacity={widths ? 1 : 0}
						>
							{w.text}
						</text>
						{widths && <Ink drawable={strikes[i]} progress={progress(w.strike)} />}
					</g>
				);
			})}
		</Page>
	);
};
