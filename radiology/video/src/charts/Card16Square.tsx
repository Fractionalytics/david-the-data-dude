// Revised card 16 (00:07:18 = 228 frames): the takeaway number again, in card 3's square
// format. It is the card 14 chart itself ("RADIOLOGY PREMIUM", PayPremium), not a redraw:
// the 1080×1920 page is scaled so its chart content (y 240-1120) fills the 1080 square.
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {PayPremium} from './PayPremium';

export const CARD16_DURATION = 228;

const S = 1.13; // 840px-wide chart zone -> ~950px
const CENTER_Y = 680; // middle of the chart's drawn content on the tall page

export const Card16Square: React.FC = () => (
	<AbsoluteFill style={{backgroundColor: 'white'}}>
		<div
			style={{
				position: 'absolute',
				width: 1080,
				height: 1920,
				transformOrigin: '0 0',
				transform: `translate(${540 * (1 - S)}px, ${540 - CENTER_Y * S}px) scale(${S})`,
			}}
		>
			<PayPremium />
		</div>
	</AbsoluteFill>
);
