// Every video is a <Composition>. Its id is what you pass to `npx remotion render`.
// One composition per storyboard card ("Original Script" tab); each is a window of the one Reel
// timeline (Reel.tsx), from its card's Start to the next card's Start, read as m:ss:ff at 30 fps.
// `preview` plays the whole timeline over a still of David's frame, for review only; `animation`
// plays it on black for the public repo.
import React from 'react';
import {AbsoluteFill, Composition, Img, staticFile, useCurrentFrame} from 'remotion';
import {VIDEO, ZoneGuide} from '@kit/zones';
import {END, Reel, START} from './Reel';

const starts = Object.values(START);
const CARDS = starts.map((from, i) => ({
	id: `card-${String(i + 1).padStart(2, '0')}`,
	from,
	len: (starts[i + 1] ?? END) - from,
}));

const Window: React.FC<{from: number}> = ({from}) => {
	const frame = useCurrentFrame();
	return (
		<AbsoluteFill>
			<Reel f={from + frame} />
		</AbsoluteFill>
	);
};

const Preview: React.FC<{bg: string}> = ({bg}) => (
	<AbsoluteFill>
		<Img src={staticFile(bg)} style={{width: VIDEO.width, height: VIDEO.height}} />
		<Window from={0} />
		<ZoneGuide layout="headTop" />
	</AbsoluteFill>
);

// The whole timeline on black, without David: the public repo's `videos/` copy.
const Animation: React.FC = () => (
	<AbsoluteFill style={{backgroundColor: 'black'}}>
		<Window from={0} />
	</AbsoluteFill>
);

export const RemotionRoot: React.FC = () => (
	<>
		{CARDS.map((c) => (
			<Composition key={c.id} id={c.id} component={Window} defaultProps={{from: c.from}} durationInFrames={c.len} {...VIDEO} />
		))}
		<Composition id="animation" component={Animation} durationInFrames={END} {...VIDEO} />
		<Composition id="preview" component={Preview} defaultProps={{bg: 'mock-bg.png'}} durationInFrames={END} {...VIDEO} />
	</>
);
