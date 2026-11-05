// One composition per data card on the Sheet's "Original Script" tab. Each lasts from its card's Start to the next
// card's Start (M:SS:FF at 30 fps; the Sheet writes the first minute as SS:FF). Animated; cue estimates are in Charts.tsx.
// `card-NN-over` puts a card over a still of David's frame (public/mock-bg.png, from his 2026-11-04 screenshot).
import React from 'react';
import {AbsoluteFill, Composition, Img, Sequence, staticFile} from 'remotion';
import {VIDEO} from '@kit/zones';
import {Card02, Card03, Card04, Card05, Card09, Card10, Card11, Card12, Card15} from './Charts';

const tc = (s: string) => {
	const p = s.split(':').map(Number);
	const [m, ss, ff] = p.length === 3 ? p : [0, ...p];
	return (m * 60 + ss) * 30 + ff;
};
// Sheet Start column, 2026-11-04.
const S = {
	c2: tc('06:08'), c3: tc('13:02'), c4: tc('18:29'), c5: tc('28:15'), c6: tc('34:17'),
	c9: tc('42:23'), c10: tc('49:20'), c11: tc('54:05'), c12: tc('1:03:13'), c13: tc('1:06:27'),
	c15: tc('1:17:29'), c16: tc('1:20:24'),
};

const CARDS = [
	{id: 'card-02', start: S.c2, len: S.c3 - S.c2, el: <Card02 />},
	{id: 'card-03', start: S.c3, len: S.c4 - S.c3, el: <Card03 />},
	{id: 'card-04', start: S.c4, len: S.c5 - S.c4, el: <Card04 />},
	{id: 'card-05', start: S.c5, len: S.c6 - S.c5, el: <Card05 />},
	{id: 'card-09', start: S.c9, len: S.c10 - S.c9, el: <Card09 />},
	{id: 'card-10', start: S.c10, len: S.c11 - S.c10, el: <Card10 />},
	{id: 'card-11', start: S.c11, len: S.c12 - S.c11, el: <Card11 />},
	{id: 'card-12', start: S.c12, len: S.c13 - S.c12, el: <Card12 />},
	{id: 'card-15', start: S.c15, len: S.c16 - S.c15, el: <Card15 />},
];

const OverDavid: React.FC<{children: React.ReactNode}> = ({children}) => (
	<AbsoluteFill>
		<Img src={staticFile('mock-bg.png')} style={{width: VIDEO.width, height: VIDEO.height}} />
		{children}
	</AbsoluteFill>
);

// Every card at its real Start over David's still, from 0:00 to card 16. Review only (render-cards writes it as preview.mp4).
const Preview: React.FC = () => (
	<OverDavid>
		{CARDS.map((c) => (
			<Sequence key={c.id} from={c.start} durationInFrames={c.len}>
				{c.el}
			</Sequence>
		))}
	</OverDavid>
);

export const RemotionRoot: React.FC = () => (
	<>
		{CARDS.map((c) => (
			<Composition key={c.id} id={c.id} component={() => c.el} durationInFrames={c.len} {...VIDEO} />
		))}
		{CARDS.map((c) => (
			<Composition key={`${c.id}-over`} id={`${c.id}-over`} component={() => <OverDavid>{c.el}</OverDavid>} durationInFrames={c.len} {...VIDEO} />
		))}
		<Composition id="preview" component={Preview} durationInFrames={S.c16} {...VIDEO} />
	</>
);
