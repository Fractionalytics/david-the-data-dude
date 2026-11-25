// card-NN: one transparent clip per storyboard card, timed to the Sheet's Start column (src/cards.tsx).
// preview-NN: the same card over this Reel's footage (speaker A or B), for review stills only.
import React from 'react';
import {AbsoluteFill, Composition, Img, staticFile} from 'remotion';
import {VIDEO} from '@kit/zones';
import {CARDS, Card, TIMING} from './cards';

// Speaker per card, from the Sheet's Character column.
const B_CARDS = new Set([1, 3, 5, 7, 9, 10, 12, 15, 24, 28, 30, 34, 40, 45, 47, 54, 58, 62, 66]);
const pad = (n: number) => String(n).padStart(2, '0');

const Preview: React.FC<{card: number}> = ({card}) => (
	<AbsoluteFill>
		<Img src={staticFile(B_CARDS.has(card) ? 'speaker-b.png' : 'speaker-a.png')} style={{width: 1080, height: 1920}} />
		<Card card={card} />
	</AbsoluteFill>
);

export const RemotionRoot: React.FC = () => (
	<>
		{CARDS.map((c) => (
			<Composition key={`card-${c}`} id={`card-${pad(c)}`} component={Card} defaultProps={{card: c}}
				durationInFrames={TIMING[c].dur} {...VIDEO} />
		))}
		{CARDS.map((c) => (
			<Composition key={`preview-${c}`} id={`preview-${pad(c)}`} component={Preview} defaultProps={{card: c}}
				durationInFrames={TIMING[c].dur} {...VIDEO} />
		))}
	</>
);
