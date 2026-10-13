// Card 4: radiologists vs all doctors on two measures. Panel 1: clinicians billing traditional
// Medicare, 2016-2024 (+12.8% vs +7.2%). Panel 2: average pay, Doximity 2017 vs 2026 reports
// (+49% vs +35%; "average doctor" = mean of 48 specialties). No title: card 4 has no
// On-Screen Text. Sources go in the post text.
//
// Cue ESTIMATES (no timecodes yet; ~175 words/min over card 4's 40 words, adjust in edit):
//   panel 1 at "Since 2016, the number of radiologists billing Medicare..." ~ word 10 -> 3.4 s
//   panel 2 at "An average radiologist's pay is up 49%..."               ~ word 27 -> 9.3 s
import React from 'react';
import {useCurrentFrame} from 'remotion';
import data from '../data/cards.json';
import {Page, ZONES} from '../sharpie';
import {BarPair, OTHER, RAD} from './parts';

const P1_AT = 100;
const P2_AT = 280;
export const CARD4_DURATION = 420;

export const Card4Growth: React.FC = () => {
	const frame = useCurrentFrame();
	return (
		<Page>
			<BarPair
				frame={frame}
				start={P1_AT}
				top={ZONES.chart.top + 40}
				label="Doctors billing Medicare, 2016–2024"
				rows={[
					{name: 'Radiologists', value: data.medicare.radiologists, color: RAD},
					{name: 'All doctors', value: data.medicare.physicians, color: OTHER},
				]}
				max={14}
				fmt={(v) => `+${v.toFixed(1)}%`}
				seed={400}
			/>
			<BarPair
				frame={frame}
				start={P2_AT}
				top={ZONES.chart.top + 470}
				label="Average pay, 2017–2025"
				rows={[
					{name: 'Radiologists', value: data.pay.radiologists, color: RAD},
					{name: 'Avg. doctor', value: data.pay.physicians, color: OTHER},
				]}
				max={52}
				fmt={(v) => `+${Math.round(v)}%`}
				seed={420}
			/>
		</Page>
	);
};
