// Card 11: the takeaway number. Clinicians billing traditional Medicare, physicians only,
// 2016-2024: radiologists +12.8% vs all doctors +7.2% (1.78x). Same bars and colors as card 4's
// first panel, larger. No title or callout: card 11 has no On-Screen Text.
//
// Cue ESTIMATE (~175 words/min over card 11's 23 words): bars at "Since 2016..." ~ word 6 -> 2 s
import React from 'react';
import {useCurrentFrame} from 'remotion';
import data from '../data/cards.json';
import {Page, ZONES} from '../sharpie';
import {BarPair, OTHER, RAD} from './parts';

const BARS_AT = 60;
export const CARD11_DURATION = 240;

export const Card11Takeaway: React.FC = () => {
	const frame = useCurrentFrame();
	return (
		<Page>
			<BarPair
				frame={frame}
				start={BARS_AT}
				top={ZONES.chart.top + 250}
				label="Doctors billing Medicare, 2016–2024"
				rows={[
					{name: 'Radiologists', value: data.medicare.radiologists, color: RAD},
					{name: 'All doctors', value: data.medicare.physicians, color: OTHER},
				]}
				max={14}
				fmt={(v) => `+${v.toFixed(1)}%`}
				seed={1100}
			/>
		</Page>
	);
};
