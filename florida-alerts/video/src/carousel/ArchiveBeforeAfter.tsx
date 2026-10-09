// Carousel slide 4 (1080×1350): the vanished reports, before and after.
//   Top: a real screenshot of FDLE's Silver Alert "Monthly Reports" page as it is today (captured 2026-10-08 with
//   headless Chrome; public/fdle-monthly-reports.png), with the empty space circled.
//   Bottom: every month 2011–2020, one cell each, checked if its report was recovered from the Internet Archive
//   (119) and crossed if not (October 2012). Data: silver.json reportMonths, from the pipeline.
// The only words are labels and source notes; any headline is David's caption.
import React, {useMemo} from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import data from '../data/silver.json';
import {CAROUSEL} from '@kit/scorecard';
import {INK, Ink, Scrawl, ink} from '../sharpie';

const W = CAROUSEL.width;
const M = 70;
// Screenshot: show its top 690px (header through the empty content area), scaled to the slide width.
const SHOT = {src: 'fdle-monthly-reports.png', w: 1080, h: 1500, show: 690};
const SHOT_TOP = 50;
const SHOT_W = W - 2 * M;
const SHOT_H = (SHOT.show * SHOT_W) / SHOT.w;
const scale = SHOT_W / SHOT.w;

const GRID_TOP = SHOT_TOP + SHOT_H + 120;
const LABEL_W = 110;
const BOTTOM = CAROUSEL.height - 70; // room for the source note under the grid
const CELL = Math.min((W - 2 * M - LABEL_W) / 12, (BOTTOM - GRID_TOP) / 10);
const YEARS = Array.from({length: 10}, (_, i) => 2011 + i);
const MONTHS = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'];
const HAVE = new Set(data.reportMonths.map(([y, m]) => `${y}-${m}`));

export const ArchiveBeforeAfter: React.FC = () => {
	const marks = useMemo(
		() =>
			YEARS.flatMap((y, r) =>
				MONTHS.map((_, c) => {
					const x = M + LABEL_W + c * ((W - 2 * M - LABEL_W) / 12) + (W - 2 * M - LABEL_W) / 24;
					const yy = GRID_TOP + r * CELL + CELL / 2;
					const s = CELL * 0.28;
					const seed = 1000 + r * 12 + c;
					return HAVE.has(`${y}-${c + 1}`)
						? [ink.path([[x - s, yy], [x - s / 3, yy + s * 0.8], [x + s, yy - s * 0.8]], {seed, stroke: INK.green, strokeWidth: 5})]
						: [ink.line(x - s, yy - s, x + s, yy + s, {seed, stroke: INK.red, strokeWidth: 6}), ink.line(x + s, yy - s, x - s, yy + s, {seed: seed + 500, stroke: INK.red, strokeWidth: 6})];
				}),
			),
		[],
	);
	// The empty content area in the screenshot (page px): right of the side menu, below the heading.
	const empty = useMemo(() => ink.rect(M + 370 * scale, SHOT_TOP + 380 * scale, 660 * scale, 300 * scale, {seed: 1900, stroke: INK.red, strokeWidth: 7, roughness: 2}), []);
	return (
		<AbsoluteFill style={{backgroundColor: 'white'}}>
			<div style={{position: 'absolute', left: M, top: SHOT_TOP, width: SHOT_W, height: SHOT_H, overflow: 'hidden', border: `3px solid ${INK.black}`}}>
				<Img src={staticFile(SHOT.src)} style={{width: SHOT_W, display: 'block'}} />
			</div>
			<svg width={W} height={CAROUSEL.height} viewBox={`0 0 ${W} ${CAROUSEL.height}`} style={{position: 'absolute', left: 0, top: 0}}>
				<defs>
					<filter id="marker-edge" filterUnits="userSpaceOnUse" x={0} y={0} width={W} height={CAROUSEL.height}>
						<feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves={1} seed={3} result="noise" />
						<feDisplacementMap in="SourceGraphic" in2="noise" scale={2.5} />
					</filter>
				</defs>
				<Ink drawable={empty} />
				<Scrawl x={W / 2} y={SHOT_TOP + SHOT_H + 36} size={26} color={INK.gray} seed="src1">
					FDLE's Silver Alert Monthly Reports page, October 2026
				</Scrawl>
				{MONTHS.map((m, c) => (
					<Scrawl key={`m${c}`} x={M + LABEL_W + c * ((W - 2 * M - LABEL_W) / 12) + (W - 2 * M - LABEL_W) / 24} y={GRID_TOP - 24} size={28} seed={`gm${c}`}>
						{m}
					</Scrawl>
				))}
				{YEARS.map((y, r) => (
					<Scrawl key={`y${y}`} x={M} y={GRID_TOP + r * CELL + CELL / 2} size={32} anchor="start" seed={`gy${r}`}>
						{String(y)}
					</Scrawl>
				))}
				{marks.flat().map((d, i) => (
					<Ink key={i} drawable={d} connect />
				))}
				<Scrawl x={W / 2} y={GRID_TOP + 10 * CELL + 36} size={26} color={INK.gray} seed="src2">
					{`${data.reportMonths.length} of 120 monthly reports, recovered from the Internet Archive`}
				</Scrawl>
			</svg>
		</AbsoluteFill>
	);
};
