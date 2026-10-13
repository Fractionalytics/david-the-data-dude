// Card 6: "a task is only part of a job." Venn diagram, stacked vertically for a phone: AI on
// top, Radiologist below, overlapping in the tasks FDA-cleared tools aid with. All text is
// David's, word for word from card 6's Video column. DRAFT: final frame only (David asked
// for the final frame first); animation comes once the layout is approved.
import React, {useMemo} from 'react';
import {INK, Ink, Page, Scrawl, ink} from '../sharpie';
import {CX, RAD} from './parts';

const AI = {cy: 500, r: 260};
const RADIO = {cy: 820, r: 330};
const AI_COLOR = INK.red;
export const CARD6_DURATION = 30;

const OVERLAP = ['triage, measurement,', 'and image reconstruction', 'aids'];
const RAD_ONLY = ['review images', 'hands-on procedures', 'consult with doctor', 'legally sign the report'];

export const Card6Venn: React.FC = () => {
	const circles = useMemo(
		() => [
			ink.dot(CX, AI.cy, AI.r * 2, {seed: 61, stroke: AI_COLOR, strokeWidth: 9, fill: undefined}),
			ink.dot(CX, RADIO.cy, RADIO.r * 2, {seed: 62, stroke: RAD, strokeWidth: 9, fill: undefined}),
		],
		[],
	);
	return (
		<Page>
			{circles.map((c, i) => (
				<Ink key={i} drawable={c} />
			))}
			<Scrawl x={CX} y={AI.cy - 130} size={80} color={AI_COLOR} seed="ai">
				AI
			</Scrawl>
			{OVERLAP.map((t, i) => (
				<Scrawl key={t} x={CX} y={570 + i * 44} size={30} seed={`o${i}`}>
					{t}
				</Scrawl>
			))}
			<Scrawl x={CX} y={805} size={58} color={RAD} seed="rad">
				Radiologist
			</Scrawl>
			{RAD_ONLY.map((t, i) => (
				<Scrawl key={t} x={CX} y={870 + i * 50} size={36} color={RAD} seed={`r${i}`}>
					{t}
				</Scrawl>
			))}
		</Page>
	);
};
