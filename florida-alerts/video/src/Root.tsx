// Every video is a <Composition>. Its id is what you pass to `npx remotion render`.
// Each composition runs exactly as long as its storyboard card in David's recording (src/sharpie.tsx CARD).
import React from 'react';
import {Composition} from 'remotion';
import {VIDEO, durationOf} from './sharpie';
import {AlertsYearsDots} from './charts/AlertsYearsDots';
import {ChannelBars, FoundByBars} from './charts/StoryBars';
import {RecoveryMap} from './charts/RecoveryMap';
import {Takeaways} from './charts/Takeaways';
import {CAROUSEL, DifficultyScorecard} from '@kit/scorecard';
import difficulty from './data/difficulty.json';
import {ArchiveBeforeAfter} from './carousel/ArchiveBeforeAfter';
import {ReelQr} from './carousel/ReelQr';

export const RemotionRoot: React.FC = () => (
	<>
		<Composition id="card5-years-dots" component={AlertsYearsDots} durationInFrames={durationOf(5)} {...VIDEO} />
		<Composition id="card6-found-by" component={FoundByBars} durationInFrames={durationOf(6)} {...VIDEO} />
		<Composition id="card7-channels" component={ChannelBars} durationInFrames={durationOf(7)} {...VIDEO} />
		<Composition id="card8-map" component={RecoveryMap} durationInFrames={durationOf(8)} {...VIDEO} />
		<Composition id="card9-takeaways" component={Takeaways} durationInFrames={durationOf(9)} {...VIDEO} />
		{/* "How I did it" carousel slides (1080×1350 stills). */}
		<Composition id="carousel-difficulty" component={DifficultyScorecard} durationInFrames={1} {...CAROUSEL} defaultProps={{difficulty}} />
		<Composition id="carousel-04-archive" component={ArchiveBeforeAfter} durationInFrames={1} {...CAROUSEL} />
		<Composition id="carousel-09-reel" component={ReelQr} durationInFrames={1} {...CAROUSEL} />
	</>
);
