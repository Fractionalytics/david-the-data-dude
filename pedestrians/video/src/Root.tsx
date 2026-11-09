// One transparent clip per storyboard card (card-NN), each rendering its slice of the whole-Reel timeline
// (src/timeline.tsx), so clips cut together cleanly. `preview` plays every graphic card over a still of
// the speaker for review; `still-NN` shows card NN at a chosen frame over the speaker.
import React from 'react';
import {AbsoluteFill, Composition, Img, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {VIDEO} from '@kit/zones';
import {END, GRAPHIC_CARDS, S, SPEAKER} from './cues';
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
		{GRAPHIC_CARDS.map((c, i) => {
			const from = GRAPHIC_CARDS.slice(0, i).reduce((a, k) => a + (END(k) - S(k)), 0);
			return (
				<Sequence key={c} from={from} durationInFrames={END(c) - S(c)}>
					<Img src={staticFile(`speaker-${SPEAKER[c]}.png`)} style={{position: 'absolute', width: 1080, height: 1920}} />
					<CardClip card={c} />
				</Sequence>
			);
		})}
	</AbsoluteFill>
);

const previewLen = GRAPHIC_CARDS.reduce((a, k) => a + (END(k) - S(k)), 0);

export const RemotionRoot: React.FC = () => (
	<>
		{GRAPHIC_CARDS.map((c) => (
			<Composition key={c} id={`card-${pad(c)}`} component={() => <CardClip card={c} />} durationInFrames={END(c) - S(c)} {...VIDEO} />
		))}
		{GRAPHIC_CARDS.map((c) => (
			<Composition
				key={`s${c}`}
				id={`still-${pad(c)}`}
				component={() => (
					<AbsoluteFill>
						<Img src={staticFile(`speaker-${SPEAKER[c]}.png`)} style={{width: 1080, height: 1920}} />
						<CardClip card={c} />
					</AbsoluteFill>
				)}
				durationInFrames={END(c) - S(c)}
				{...VIDEO}
			/>
		))}
		<Composition id="preview" component={Preview} durationInFrames={previewLen} {...VIDEO} />
	</>
);
