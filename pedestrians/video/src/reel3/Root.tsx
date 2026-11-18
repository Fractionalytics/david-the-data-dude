// Reel 3 (DDD15) compositions, a separate entry point so Reel 1's stay as posted:
//   npx remotion studio src/reel3/index.ts
//   r3-card-NN   one transparent clip per graphic card, for CapCut (node render-cards.mjs --reel3)
//   r3-preview   the whole Reel: every card's graphic over David's edited video (public/reel3/reel.mp4
//                when FOOTAGE is true) or over a still of that card's speaker
import React from 'react';
import {AbsoluteFill, Composition, Img, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {VIDEO} from '@kit/zones';
import {CARDS, END, GRAPHIC_CARDS, S, SPEAKER, TOTAL} from './cues';
import {Graphic} from './timeline';

// Set to true once David's edited Reel is copied to public/reel3/reel.mp4.
const FOOTAGE = false;

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
		{FOOTAGE && <OffthreadVideo src={staticFile('reel3/reel.mp4')} />}
		{CARDS.filter((c) => c < 52).map((c) => (
			<Sequence key={c} from={S(c)} durationInFrames={END(c) - S(c)}>
				{!FOOTAGE && <Img src={staticFile(`reel3/speaker-${SPEAKER(c)}.png`)} style={{position: 'absolute', width: 1080, height: 1920}} />}
				{GRAPHIC_CARDS.includes(c) && <CardClip card={c} />}
				<div style={{position: 'absolute', right: 20, bottom: 20, fontFamily: 'sans-serif', fontSize: 28, color: '#fff', background: 'rgba(0,0,0,0.45)', padding: '4px 10px', borderRadius: 6}}>card {c}</div>
			</Sequence>
		))}
	</AbsoluteFill>
);

export const RemotionRoot: React.FC = () => (
	<>
		{GRAPHIC_CARDS.map((c) => (
			<Composition key={c} id={`r3-card-${pad(c)}`} component={() => <CardClip card={c} />} durationInFrames={END(c) - S(c)} {...VIDEO} />
		))}
		<Composition id="r3-preview" component={Preview} durationInFrames={TOTAL} {...VIDEO} />
	</>
);
