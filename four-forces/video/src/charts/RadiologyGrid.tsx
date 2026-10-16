// Card 17, first beat: "the aforementioned radiology" and force #1 (task vs. job). The same
// 100-square grid as the Radiology Reel's rev11-13-reasons (projects/radiology/video), same numbers
// and labels: a radiologist's working time starts all blue, then drains to the 36% spent reading
// scans (VALUE study: Dhanoa et al., J Am Coll Radiol 2013;10(10):764-769; 36.4% rounded as in that
// Reel). Copied rather than imported because that composition is one long multi-card clip.
// Color: the slow lane's blue. Timing: ../cues.ts (drain finishes on "radiology", est.).
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {CUE} from '../cues';
import {Page, Scrawl, ZONES, ramp} from '../sharpie';
import {COOL, CX, OTHER} from './parts';

export const RAD_GRID_DURATION = CUE.c17a.dur;
const READING = 36;
const COLS = 10;
const ROWS = 10;
const CELL = 52;
const GRID_LEFT = CX - (COLS * CELL) / 2;
const GRID_TOP = ZONES.chart.top + 120;
const DRAIN_AT = 40;
const DRAIN_FRAMES = 60;

export const RadiologyGrid: React.FC = () => {
	const frame = useCurrentFrame();
	// Squares turn gray from the end, one at a time, until 36 blue are left.
	const blue = 100 - Math.round(ramp(frame, DRAIN_AT, DRAIN_FRAMES) * (100 - READING));
	return (
		<Page>
			<g opacity={ramp(frame, 0, 10)}>
				{Array.from({length: COLS * ROWS}, (_, i) => (
					<rect
						key={i}
						x={GRID_LEFT + (i % COLS) * CELL + 4}
						y={GRID_TOP + Math.floor(i / COLS) * CELL + 4}
						width={CELL - 8}
						height={CELL - 8}
						rx={5}
						fill={i < blue ? COOL : '#dcdcd8'}
					/>
				))}
			</g>
			<Scrawl x={CX} y={GRID_TOP + ROWS * CELL + 60} size={60} color={COOL} opacity={ramp(frame, DRAIN_AT + DRAIN_FRAMES, 10)} seed="read">
				{`${READING}% reading scans`}
			</Scrawl>
			<Scrawl x={CX} y={GRID_TOP + ROWS * CELL + 135} size={52} color={OTHER} opacity={ramp(frame, DRAIN_AT + DRAIN_FRAMES + 12, 10)} seed="rest">
				{`${100 - READING}% everything else`}
			</Scrawl>
		</Page>
	);
};
