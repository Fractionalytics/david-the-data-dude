// Every video is a <Composition>. Its id is what you pass to `npx remotion render`.
// Note each chart's storyboard card in README.md's composition table.
// Lengths are David's recorded card lengths (2026-10-30), 30 fps.
import React from 'react';
import {Composition} from 'remotion';
import {VIDEO} from '@kit/zones';
import {Card06} from './charts/Card06';
import {CARD08, Card08} from './charts/Card08';
import {Card15, Card17, Card18} from './charts/Scorecard';

export const RemotionRoot: React.FC = () => (
	<>
		{/* 02:27 (SS:FF); full screen, animation done by frame 30. */}
		<Composition id="card-06" component={Card06} durationInFrames={87} {...VIDEO} />
		{/* A PNG still for the band above David's head (840 x 410); render with remotion still. */}
		<Composition id="card-08" component={Card08} durationInFrames={1} fps={30} {...CARD08} />
		{/* Cards 15 + 16 in one clip: 254 + 163 frames. */}
		<Composition id="card-15" component={Card15} durationInFrames={417} {...VIDEO} />
		<Composition id="card-17" component={Card17} durationInFrames={271} {...VIDEO} />
		{/* Its last frame is the still for cards 19 (135 frames) and 20 (155 frames). */}
		<Composition id="card-18" component={Card18} durationInFrames={274} {...VIDEO} />
	</>
);
