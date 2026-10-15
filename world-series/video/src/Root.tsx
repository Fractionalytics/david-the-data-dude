// Every video is a <Composition>. Its id is what you pass to `npx remotion render`.
// Note each one's storyboard card in README.md's composition table.
import React from 'react';
import {Composition} from 'remotion';
import {VIDEO} from '@kit/zones';
import {WorldSeries} from './WorldSeries';
import {TOTAL_FRAMES} from './timing';
import {RosterSlide, SLIDE, Slide1, Slide10, Slide2, Slide7, Slide8, Slide9} from './carousel';

export const RemotionRoot: React.FC = () => (
	<>
		<Composition id="world-series" component={WorldSeries} durationInFrames={TOTAL_FRAMES} {...VIDEO} />
		<Composition id="carousel-01" component={Slide1} durationInFrames={1} {...SLIDE} />
		<Composition id="carousel-02" component={Slide2} durationInFrames={1} {...SLIDE} />
		<Composition id="carousel-03" component={RosterSlide} durationInFrames={1} {...SLIDE} defaultProps={{k: 'jobs' as const}} />
		<Composition id="carousel-04" component={RosterSlide} durationInFrames={1} {...SLIDE} defaultProps={{k: 'sons' as const}} />
		<Composition id="carousel-05" component={RosterSlide} durationInFrames={1} {...SLIDE} defaultProps={{k: 'nicknames' as const}} />
		<Composition id="carousel-06" component={RosterSlide} durationInFrames={1} {...SLIDE} defaultProps={{k: 'places' as const}} />
		<Composition id="carousel-07" component={Slide7} durationInFrames={1} {...SLIDE} />
		<Composition id="carousel-08" component={Slide8} durationInFrames={1} {...SLIDE} />
		<Composition id="carousel-09" component={Slide9} durationInFrames={1} {...SLIDE} />
		<Composition id="carousel-10" component={Slide10} durationInFrames={1} {...SLIDE} />
	</>
);
