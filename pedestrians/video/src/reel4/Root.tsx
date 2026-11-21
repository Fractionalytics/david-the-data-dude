// Reel 4 (DDD17 4 Waves) compositions, a separate entry point so the earlier Reels stay as posted:
//   npx remotion studio src/reel4/index.ts
//   r4-card-NN   one transparent clip per card, for CapCut (node render-cards.mjs --reel4)
//   r4-preview   the whole Reel over David's hedge still (public/reel4/speaker.png)
import React from 'react';
import {AbsoluteFill, Composition, Img, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {CARDS, END, GRAPHIC_CARDS, S, TOTAL} from './cues';
import {Graphic} from './timeline';

const VIDEO = {width: 1080, height: 1920, fps: 30};
const pad = (n: number) => String(n).padStart(2, '0');

const CardClip: React.FC<{card: number}> = ({card}) => {
	const f = useCurrentFrame();
	return <Graphic g={S(card) + f} />;
};

const Preview: React.FC = () => (
	<AbsoluteFill style={{background: '#000'}}>
		<Img src={staticFile('reel4/speaker.png')} style={{position: 'absolute', width: 1080, height: 1920}} />
		{CARDS.filter((c) => c < 39).map((c) => (
			<Sequence key={c} from={S(c)} durationInFrames={END(c) - S(c)}>
				<CardClip card={c} />
				<div style={{position: 'absolute', right: 20, bottom: 20, fontFamily: 'sans-serif', fontSize: 28, color: '#fff', background: 'rgba(0,0,0,0.45)', padding: '4px 10px', borderRadius: 6}}>card {c}</div>
			</Sequence>
		))}
	</AbsoluteFill>
);

export const RemotionRoot: React.FC = () => (
	<>
		{GRAPHIC_CARDS.map((c) => (
			<Composition key={c} id={`r4-card-${pad(c)}`} component={() => <CardClip card={c} />} durationInFrames={END(c) - S(c)} {...VIDEO} />
		))}
		<Composition id="r4-preview" component={Preview} durationInFrames={TOTAL} {...VIDEO} />
	</>
);
