// Card 9 (2:16:21–2:44:02): David's five takeaway lines, word for word from the storyboard's Video column.
// Each line writes in (left-to-right wipe) as David says it, and they stay up to the end of the card.
// No line wraps: once the marker font loads, every line is measured and one shared font size is picked
// so the widest line fits the chart zone.
//
// The cue times are estimates: each line's phrase position in the card 9 script, scaled to the card's
// length. If a line lands early or late, change its timecode here (MM:SS:FF, 30 fps).
import React, {useEffect, useRef, useState} from 'react';
import {continueRender, delayRender, interpolate, useCurrentFrame} from 'remotion';
import {INK, MARKER_FONT, Page, ZONES, clamp, cue, markerFontReady} from '../sharpie';

const LINES: {text: string; emoji?: string; at: number; color: string}[] = [
	{text: 'Yes, they work', at: cue(9, 2, 18, 23), color: INK.black}, // "yes, Silver Alerts work"
	{text: 'Not the only solution', at: cue(9, 2, 20, 13), color: INK.black}, // "They aren't the only solution"
	{text: '11% of cases', emoji: '✅', at: cue(9, 2, 22, 13), color: INK.red}, // "in 11% of cases"
	{text: 'Public > police', at: cue(9, 2, 29, 3), color: INK.green}, // "the public seems to be even more effective than the police"
	{text: '98% of Silver Alerts', emoji: '👍', at: cue(9, 2, 40, 14), color: INK.black}, // "the 98% success rate"
];
const WRITE = 12; // frames for a line to write in, finishing on its cue
const EMOJI_FONT = '"Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif';
const MAX_WIDTH = ZONES.chart.right - ZONES.chart.left - 20;
const MAX_SIZE = 130;
const GAP = 0.3; // em between the text and its emoji

export const Takeaways: React.FC = () => {
	const frame = useCurrentFrame();
	const probe = useRef<(SVGTextElement | null)[]>([]);
	const [widths, setWidths] = useState<number[] | null>(null);
	const [handle] = useState(() => delayRender('measure takeaway lines'));

	// Measure every line at 100px once the marker font has loaded.
	useEffect(() => {
		markerFontReady().then(() => {
			setWidths(LINES.map((_, i) => probe.current[i]!.getBBox().width));
			continueRender(handle);
		});
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	const size = widths ? Math.min(MAX_SIZE, Math.floor((MAX_WIDTH / Math.max(...widths)) * 100)) : MAX_SIZE;
	const rowStep = (ZONES.chart.bottom - ZONES.chart.top) / LINES.length;
	const x0 = ZONES.chart.left + 10;

	return (
		<Page>
			{/* Hidden probes at 100px: the text plus its emoji, for measuring. */}
			<g opacity={0}>
				{LINES.map((l, i) => (
					<text
						key={i}
						ref={(el) => {
							probe.current[i] = el;
						}}
						x={0}
						y={-500}
						fontSize={100}
					>
						<tspan fontFamily={MARKER_FONT}>{l.text}</tspan>
						{l.emoji && (
							<tspan fontFamily={EMOJI_FONT} dx={GAP * 100}>
								{l.emoji}
							</tspan>
						)}
					</text>
				))}
			</g>
			{widths &&
				LINES.map((l, i) => {
					const y = ZONES.chart.top + rowStep * (i + 0.5);
					const written = interpolate(frame, [l.at - WRITE, l.at], [0, 1], clamp);
					const w = (widths[i] * size) / 100;
					return (
						<g key={i}>
							<clipPath id={`tk-${i}`}>
								<rect x={x0 - 10} y={y - size} width={(w + 30) * written} height={size * 2} />
							</clipPath>
							<text x={x0} y={y} fontSize={size} fill={l.color} dominantBaseline="middle" clipPath={`url(#tk-${i})`}>
								<tspan fontFamily={MARKER_FONT}>{l.text}</tspan>
								{l.emoji && (
									<tspan fontFamily={EMOJI_FONT} dx={GAP * size}>
										{l.emoji}
									</tspan>
								)}
							</text>
						</g>
					);
				})}
		</Page>
	);
};
