// Every video is a <Composition>. Its id is what you pass to `npx remotion render`.
// One composition per storyboard card (Script v2 tab); each lasts from its card's Start to the next
// card's Start, read as m:ss:ff at 30 fps. Card 15's end isn't in the Sheet, so it runs 8 s.
// `preview` plays every card in order over a still of David's frame, for review only.
import React from 'react';
import {AbsoluteFill, Composition, Img, Series, staticFile} from 'remotion';
import {VIDEO} from '@kit/zones';
import {Comparisons, FullFunnel, MergeCard, SplitCard, layoutChildren} from './Anim';

const ON_SCREEN_1 = '1-in-70 serve on 4+ day trial'; // Sheet, cards 1 and 15
const COMPARISONS = ['civil > criminal', 'felonies > misdemeanors', 'federal > state (less common)']; // Sheet, card 12

const tc = (s: string) => {
	const [m, ss, ff] = s.split(':').map(Number);
	return (m * 60 + ss) * 30 + ff;
};
const START = {c1: tc('0:00:00'), c5: tc('0:05:09'), c6: tc('0:17:04'), c8: tc('0:32:12'), c9: tc('0:43:16'), c11: tc('0:59:26'), c12: tc('1:20:09'), c15: tc('1:32:17')};

const k5 = [
	{value: 449, label: 'eligible', kind: 'stay' as const},
	{value: 551, label: 'postponed, no reply or excused', kind: 'out' as const},
];
const k8 = [
	{value: 155, label: 'sent to a courtroom', kind: 'stay' as const},
	{value: 92, label: 'sent home', kind: 'out' as const},
];
const k9 = [
	{value: 48, label: 'sworn', kind: 'stay' as const},
	{value: 107, label: 'not chosen', kind: 'out' as const},
];
const k11 = [
	{value: 8, label: '1 day', kind: 'days' as const},
	{value: 19, label: '2 days', kind: 'days' as const},
	{value: 7, label: '3 days', kind: 'days' as const},
	{value: 14, label: '4+ days', kind: 'days' as const},
];
// Where each card's continuing bar ended, so the next card can zoom in from exactly there.
const [r449, r551] = layoutChildren(1000, k5).map((r) => ({x0: r.x0, w: r.w}));
const r247 = {x0: 510 - (1000 * (r449.w / 449) + 60) / 2, w: 247 * (r449.w / 449)};
const r155 = layoutChildren(247, k8)[0];
const r48 = layoutChildren(155, k9)[0];

// David's cues within cards (2026-10-22), as absolute m:ss:ff, converted to frames within the card.
const at = (card: number, s: string) => tc(s) - card;
const CUE9 = [
	{at: at(START.c9, '0:51:03'), part: 48, total: 247, label: 'reported'}, // "1-in-5 of the people who showed up"
	{at: at(START.c9, '0:55:03'), part: 48, total: 1000, label: 'summoned'}, // "1-in-20 of the people who received a summons"
];
const CUE11 = ['1:08:02', '1:12:12', '1:14:21', '1:17:04'].map((s) => at(START.c11, s)); // 1 / 2 / 3 / 4+ days
const CUE12 = ['1:22:08', '1:25:11', '1:27:03'].map((s) => at(START.c12, s)); // the three comparison lines

const CARDS = [
	{id: 'card-01', len: START.c5 - START.c1, el: <FullFunnel onScreen={ON_SCREEN_1} />},
	{id: 'card-05', len: START.c6 - START.c5, el: <SplitCard parent={{value: 1000, label: 'summoned'}} kids={k5} upto={0} />},
	{id: 'card-06', len: START.c8 - START.c6, el: <MergeCard from449={r449} from551={r551} />},
	{id: 'card-08', len: START.c9 - START.c8, el: <SplitCard parent={{value: 247, label: 'reported'}} kids={k8} from={r247} upto={2} />},
	{id: 'card-09', len: START.c11 - START.c9, el: <SplitCard parent={{value: 155, label: 'sent to a courtroom'}} kids={k9} from={{x0: r155.x0, w: r155.w}} upto={3} compare={CUE9} />},
	{id: 'card-11', len: START.c12 - START.c11, el: <SplitCard parent={{value: 48, label: 'sworn'}} kids={k11} from={{x0: r48.x0, w: r48.w}} upto={4} cues={CUE11} crumbFinal={{value: 14, at: CUE11[3]}} />},
	// Card 12's lines appear on David's cues (CUE12).
	{id: 'card-12', len: START.c15 - START.c12, el: <Comparisons lines={COMPARISONS} at={CUE12} />},
	{id: 'card-15', len: 240, el: <FullFunnel onScreen={ON_SCREEN_1} hold />},
];

const Preview: React.FC = () => (
	<AbsoluteFill>
		<Img src={staticFile('mock-bg.png')} style={{width: VIDEO.width, height: VIDEO.height}} />
		<Series>
			{CARDS.map((c) => (
				<Series.Sequence key={c.id} durationInFrames={c.len}>
					{c.el}
				</Series.Sequence>
			))}
		</Series>
	</AbsoluteFill>
);

// Every card in order on black, without David: the public repo's `videos/` copy.
const Animation: React.FC = () => (
	<AbsoluteFill style={{backgroundColor: 'black'}}>
		<Series>
			{CARDS.map((c) => (
				<Series.Sequence key={c.id} durationInFrames={c.len}>
					{c.el}
				</Series.Sequence>
			))}
		</Series>
	</AbsoluteFill>
);

export const RemotionRoot: React.FC = () => (
	<>
		{CARDS.map((c) => (
			<Composition key={c.id} id={c.id} component={() => c.el} durationInFrames={c.len} {...VIDEO} />
		))}
		<Composition id="preview" component={Preview} durationInFrames={CARDS.reduce((a, c) => a + c.len, 0)} {...VIDEO} />
		<Composition id="animation" component={Animation} durationInFrames={CARDS.reduce((a, c) => a + c.len, 0)} {...VIDEO} />
	</>
);
