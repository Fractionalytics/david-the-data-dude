// Every video is a <Composition>. Its id is what you pass to `npx remotion render`.
// Each chart's storyboard card is noted in README.md's composition table.
import React from 'react';
import {Composition} from 'remotion';
import {VIDEO} from './sharpie';
import {ERA_DURATION, ServicesByEra} from './charts/ServicesByEra';
import {STRIP_DURATION, DailyStrip} from './charts/DailyStrip';
import {SEESAW_DURATION, Seesaw} from './charts/Seesaw';
import {CONVEYOR_DURATION, Conveyor} from './charts/Conveyor';

export const RemotionRoot: React.FC = () => (
	<>
		<Composition id="services-by-era" component={ServicesByEra} durationInFrames={ERA_DURATION} {...VIDEO} />
		<Composition id="daily-strip" component={DailyStrip} durationInFrames={STRIP_DURATION} {...VIDEO} />
		<Composition id="conveyor" component={Conveyor} durationInFrames={CONVEYOR_DURATION} {...VIDEO} />
		<Composition id="seesaw" component={Seesaw} durationInFrames={SEESAW_DURATION} {...VIDEO} />
	</>
);
