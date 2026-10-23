// One composition per storyboard card (Script v2 tab), named card-NN. Each lasts from its card's Start
// to the next card's Start, read as m:ss:ff at 30 fps. Cards 3, 5 and 11 are David's talking head (no clip).
// `preview` plays the whole timeline over public/mock-bg.png (a stand-in for David's frame), for review.
import React from 'react';
import {AbsoluteFill, Composition, Img, Series, staticFile} from 'remotion';
import {VIDEO} from '@kit/zones';
import {Card01, Card02, Card04, Card06, Card07, Card08, Card09, Card10} from './Cards';

const tc = (s: string) => {
	const [m, ss, ff] = s.split(':').map(Number);
	return (m * 60 + ss) * 30 + ff;
};
// Script v2, Start column (2026-10-22). Card 11 ends at 1:17:14 (Video column).
const START = ['0:00:00', '0:06:04', '0:12:15', '0:18:05', '0:29:11', '0:32:28', '0:42:08', '0:47:27', '0:57:15', '1:03:11', '1:11:11', '1:17:14'].map(tc);
const len = (card: number) => START[card] - START[card - 1];

const CARDS: {n: number; el: React.ReactNode | null}[] = [
	{n: 1, el: <Card01 />},
	{n: 2, el: <Card02 />},
	{n: 3, el: null},
	{n: 4, el: <Card04 />},
	{n: 5, el: null},
	{n: 6, el: <Card06 />},
	{n: 7, el: <Card07 />},
	{n: 8, el: <Card08 />},
	{n: 9, el: <Card09 />},
	{n: 10, el: <Card10 />},
	{n: 11, el: null},
];
const id = (n: number) => `card-${String(n).padStart(2, '0')}`;

const Preview: React.FC = () => (
	<AbsoluteFill>
		<Img src={staticFile('mock-bg.png')} style={{width: VIDEO.width, height: VIDEO.height}} />
		<Series>
			{CARDS.map((c) => (
				<Series.Sequence key={c.n} durationInFrames={len(c.n)}>
					{c.el ?? <AbsoluteFill />}
				</Series.Sequence>
			))}
		</Series>
	</AbsoluteFill>
);

// The visual cards back to back on black, without David: the public repo's `videos/` copy.
const VISUAL = CARDS.filter((c) => c.el);
const Animation: React.FC = () => (
	<AbsoluteFill style={{backgroundColor: 'black'}}>
		<Series>
			{VISUAL.map((c) => (
				<Series.Sequence key={c.n} durationInFrames={len(c.n)}>
					{c.el}
				</Series.Sequence>
			))}
		</Series>
	</AbsoluteFill>
);

export const RemotionRoot: React.FC = () => (
	<>
		{VISUAL.map((c) => (
			<Composition key={c.n} id={id(c.n)} component={() => <>{c.el}</>} durationInFrames={len(c.n)} {...VIDEO} />
		))}
		<Composition id="preview" component={Preview} durationInFrames={START[START.length - 1]} {...VIDEO} />
		<Composition id="animation" component={Animation} durationInFrames={VISUAL.reduce((a, c) => a + len(c.n), 0)} {...VIDEO} />
	</>
);
