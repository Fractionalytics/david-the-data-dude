// Reel 2 (DDD16) compositions, a separate entry point so Reels 1 and 3 stay as posted:
//   npx remotion studio src/reel2/index.ts
//   r2-card-NN   one transparent clip per graphic card, for CapCut (node render-cards.mjs --reel2)
//   r2-preview   the whole Reel: every built card's graphic over a still of that card's speaker
//                (Reel 3's stills; David filmed Reel 2 in the same setup)
import React from 'react';
import {AbsoluteFill, Composition, Img, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {VIDEO} from '@kit/zones';
import {CARDS, END, GRAPHIC_CARDS, S, STILL, TOTAL} from './cues';
import {Graphic} from './timeline';

const pad = (n: number) => String(n).padStart(2, '0');

const CardClip: React.FC<{card: number}> = ({card}) => {
	const f = useCurrentFrame();
	return (
		<AbsoluteFill>
			<Graphic g={S(card) + f} card={card} />
		</AbsoluteFill>
	);
};

const Preview: React.FC = () => (
	<AbsoluteFill style={{background: '#000'}}>
		{CARDS.filter((c) => c < 49).map((c) => (
			<Sequence key={c} from={S(c)} durationInFrames={END(c) - S(c)}>
				<Img src={staticFile(`reel3/speaker-${STILL(c)}.png`)} style={{position: 'absolute', width: 1080, height: 1920}} />
				{GRAPHIC_CARDS.includes(c) && <CardClip card={c} />}
				<div style={{position: 'absolute', right: 20, bottom: 20, fontFamily: 'sans-serif', fontSize: 28, color: '#fff', background: 'rgba(0,0,0,0.45)', padding: '4px 10px', borderRadius: 6}}>card {c}</div>
			</Sequence>
		))}
	</AbsoluteFill>
);

export const RemotionRoot: React.FC = () => (
	<>
		{GRAPHIC_CARDS.map((c) => (
			<Composition key={c} id={`r2-card-${pad(c)}`} component={() => <CardClip card={c} />} durationInFrames={END(c) - S(c)} {...VIDEO} />
		))}
		<Composition id="r2-preview" component={Preview} durationInFrames={TOTAL} {...VIDEO} />
	</>
);
