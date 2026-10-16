// Card 16: office & admin jobs vs. all other jobs, indexed to May 2019 = 100 (BLS OEWS official
// totals; May 2019, 2022-2025. May 2020 and 2021 aren't in the project's files, so the segment from
// 2019 to 2022 is drawn straight and the 2022 dot marks the last pre-ChatGPT reading). Ends:
// office 90.9 (-9.1% since 2019), other jobs 108.2. Line labels are series labels.
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import data from '../data/charts.json';
import {INK, Ink, Page, Scrawl, ZONES, ink, ramp} from '../sharpie';
import {CUE} from '../cues';
import {HOT, OTHER, dashedLine} from './parts';

const PTS = data.officeVsRest;
const PLOT = {left: ZONES.chart.left + 60, right: ZONES.chart.right - 210, top: ZONES.chart.top + 120, bottom: ZONES.chart.bottom - 150};
const YMIN = 85;
const YMAX = 112;
const px = (yr: number) => PLOT.left + ((yr - 2019) / (2025 - 2019)) * (PLOT.right - PLOT.left);
const py = (v: number) => PLOT.bottom - ((v - YMIN) / (YMAX - YMIN)) * (PLOT.bottom - PLOT.top);
export const OFFICE_DURATION = CUE.c16a.dur;

export const OfficeVsRest: React.FC = () => {
	const frame = useCurrentFrame();
	const base = useMemo(() => dashedLine(PLOT.left - 20, py(100), PLOT.right + 20, py(100), 16, 14, {seed: 200, stroke: INK.gray, strokeWidth: 3}), []);
	const axis = useMemo(() => ink.line(PLOT.left - 20, PLOT.bottom, PLOT.right + 20, PLOT.bottom, {seed: 3, stroke: INK.black, strokeWidth: 6}), []);
	const chatgpt = useMemo(() => dashedLine(px(2022.9), PLOT.top - 20, px(2022.9), PLOT.bottom, 12, 12, {seed: 250, stroke: INK.gray, strokeWidth: 3}), []);
	const lines = useMemo(
		() => ({
			rest: ink.path(PTS.map((p) => [px(p.year), py(p.rest)] as [number, number]), {seed: 5, stroke: OTHER, strokeWidth: 10}),
			office: ink.path(PTS.map((p) => [px(p.year), py(p.office)] as [number, number]), {seed: 6, stroke: HOT, strokeWidth: 12}),
		}),
		[],
	);
	const draw = ramp(frame, 10, 100);
	const end = PTS[PTS.length - 1];
	return (
		<Page>
			<Ink drawable={axis} />
			{base.map((d, i) => (
				<Ink key={i} drawable={d} />
			))}
			<Scrawl x={PLOT.right + 20} y={py(100) - 28} size={30} anchor="end" color={INK.gray} seed="b">
				2019 = 100
			</Scrawl>
			{chatgpt.map((d, i) => (
				<Ink key={i} drawable={d} />
			))}
			<Scrawl x={px(2022.9)} y={PLOT.top - 45} size={32} color={INK.gray} seed="c">
				ChatGPT
			</Scrawl>
			{[2019, 2022, 2025].map((yr) => (
				<Scrawl key={yr} x={px(yr)} y={PLOT.bottom + 50} size={40} seed={`x${yr}`}>
					{yr}
				</Scrawl>
			))}
			<Ink drawable={lines.rest} progress={draw} connect />
			<Ink drawable={lines.office} progress={draw} connect />
			<g opacity={ramp(frame, 110, 10)}>
				<Scrawl x={px(2025) + 20} y={py(end.rest)} size={40} anchor="start" color={OTHER} seed="lr">
					Other jobs
				</Scrawl>
				<Scrawl x={px(2025) + 20} y={py(end.rest) + 46} size={40} anchor="start" color={OTHER} seed="vr">
					{`+${(end.rest - 100).toFixed(1)}%`}
				</Scrawl>
				<Scrawl x={px(2025) + 20} y={py(end.office) - 20} size={40} anchor="start" color={HOT} seed="lo">
					Office &amp;
				</Scrawl>
				<Scrawl x={px(2025) + 20} y={py(end.office) + 24} size={40} anchor="start" color={HOT} seed="lo2">
					admin
				</Scrawl>
				<Scrawl x={px(2025) + 20} y={py(end.office) + 70} size={40} anchor="start" color={HOT} seed="vo">
					{`${(end.office - 100).toFixed(1)}%`}
				</Scrawl>
			</g>
		</Page>
	);
};
