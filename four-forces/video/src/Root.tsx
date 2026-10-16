// Every video is a <Composition>. Its id is what you pass to `npx remotion render`.
// One composition per storyboard card (or per beat, where a card has two visuals), each as long as
// its card in David's edit. Card numbers and timecodes: the Sheet's "Original Script" tab
// (2026-10-16); timing lives in cues.ts.
import React from 'react';
import {Composition} from 'remotion';
import {VIDEO} from '@kit/zones';
import {CUE} from './cues';
import {Waterfall} from './charts/Waterfall';
import {TOP_DECLINES_DURATION, TopDeclines} from './charts/TopDeclines';
import {FORCES_DURATION, Forces} from './charts/Forces';
import {OFFICE_DURATION, OfficeVsRest} from './charts/OfficeVsRest';
import {RAD_GRID_DURATION, RadiologyGrid} from './charts/RadiologyGrid';
import {SLOW_DURATION, SlowLane} from './charts/SlowLane';
import {CALL_DURATION, CallCenters, SQUARE} from './charts/CallCenters';
import {CAROUSEL, CarouselForce, CarouselTitle} from './charts/CarouselSlides';

export const RemotionRoot: React.FC = () => (
	<>
		<Composition id="c07-waterfall-ceiling" component={Waterfall} durationInFrames={CUE.c07.dur} defaultProps={{card: 7 as const}} {...VIDEO} />
		<Composition id="c08-waterfall-pretrend" component={Waterfall} durationInFrames={CUE.c08.dur} defaultProps={{card: 8 as const}} {...VIDEO} />
		<Composition id="c09-waterfall-loans" component={Waterfall} durationInFrames={CUE.c09.dur} defaultProps={{card: 9 as const}} {...VIDEO} />
		<Composition id="c10-waterfall-remaining" component={Waterfall} durationInFrames={CUE.c10.dur} defaultProps={{card: 10 as const}} {...VIDEO} />
		<Composition id="c11-top-declines" component={TopDeclines} durationInFrames={TOP_DECLINES_DURATION} {...VIDEO} />
		<Composition id="c13-forces-title" component={Forces} durationInFrames={FORCES_DURATION.title} defaultProps={{mode: 'title' as const}} {...VIDEO} />
		<Composition id="c14-forces-list" component={Forces} durationInFrames={FORCES_DURATION.list} defaultProps={{mode: 'list' as const}} {...VIDEO} />
		<Composition id="c15-forces-table" component={Forces} durationInFrames={FORCES_DURATION.table} defaultProps={{mode: 'table' as const}} {...VIDEO} />
		<Composition id="c16a-office-vs-rest" component={OfficeVsRest} durationInFrames={OFFICE_DURATION} {...VIDEO} />
		<Composition id="c16b-forces-fast" component={Forces} durationInFrames={FORCES_DURATION.fast} defaultProps={{mode: 'fast' as const}} {...VIDEO} />
		<Composition id="c17a-radiology-grid" component={RadiologyGrid} durationInFrames={RAD_GRID_DURATION} {...VIDEO} />
		<Composition id="c17b-paralegals" component={SlowLane} durationInFrames={SLOW_DURATION} {...VIDEO} />
		<Composition id="c17c-forces-slow" component={Forces} durationInFrames={FORCES_DURATION.slow} defaultProps={{mode: 'slow' as const}} {...VIDEO} />
		<Composition id="c19-call-centers-square" component={CallCenters} durationInFrames={CALL_DURATION} {...SQUARE} />
		{/* Carousel slides (stills, 1080x1350). See carousel/slides.md. */}
		<Composition id="carousel-01-title" component={CarouselTitle} durationInFrames={1} {...CAROUSEL} />
		{[0, 1, 2, 3].map((i) => (
			<Composition key={i} id={`carousel-0${i + 3}-force-${i + 1}`} component={CarouselForce} durationInFrames={1} defaultProps={{index: i}} {...CAROUSEL} />
		))}
	</>
);
