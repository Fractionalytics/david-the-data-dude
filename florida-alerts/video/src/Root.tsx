// Every video is a <Composition>. Its id is what you pass to `npx remotion render`.
// Each composition runs exactly as long as its storyboard card in David's recording (src/sharpie.tsx CARD).
import React from 'react';
import {Composition} from 'remotion';
import {VIDEO, durationOf} from './sharpie';
import {AlertsYearsDots} from './charts/AlertsYearsDots';
import {ChannelBars, FoundByBars} from './charts/StoryBars';
import {RecoveryMap} from './charts/RecoveryMap';
import {Takeaways} from './charts/Takeaways';

export const RemotionRoot: React.FC = () => (
	<>
		<Composition id="card5-years-dots" component={AlertsYearsDots} durationInFrames={durationOf(5)} {...VIDEO} />
		<Composition id="card6-found-by" component={FoundByBars} durationInFrames={durationOf(6)} {...VIDEO} />
		<Composition id="card7-channels" component={ChannelBars} durationInFrames={durationOf(7)} {...VIDEO} />
		<Composition id="card8-map" component={RecoveryMap} durationInFrames={durationOf(8)} {...VIDEO} />
		<Composition id="card9-takeaways" component={Takeaways} durationInFrames={durationOf(9)} {...VIDEO} />
	</>
);
