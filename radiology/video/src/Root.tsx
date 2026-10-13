// Every video is a <Composition>. Its id is what you pass to `npx remotion render`.
// Note each chart's storyboard card in README.md's composition table.
import React from 'react';
import {Composition} from 'remotion';
import {VIDEO} from '@kit/zones';
import {CARD4_DURATION, Card4Growth} from './charts/Card4Growth';
import {CARD5_DURATION, Card5Arrived} from './charts/Card5Arrived';
import {CARD6_DURATION, Card6Venn} from './charts/Card6Venn';
import {CARD8_DURATION, Card8Facts} from './charts/Card8Facts';
import {PAY_DURATION, PayPremium} from './charts/PayPremium';
import {CARD11_DURATION, Card11Takeaway} from './charts/Card11Takeaway';
import {CARD03_DURATION, Card03Square, SQUARE} from './charts/Card03Square';
import {CARD0607_DURATION, Card0607Capability} from './charts/Card0607Capability';
import {CARD08_DURATION, Card08Amara} from './charts/Card08Amara';
import {CARD0910_DURATION, Card0910Prescription} from './charts/Card0910Prescription';
import {CARD1113_DURATION, Card1113Reasons} from './charts/Card1113Reasons';
import {CARD16_DURATION, Card16Square} from './charts/Card16Square';

export const RemotionRoot: React.FC = () => (
	<>
		{/* "Revised Script" tab (2026-10-13) card numbers. */}
		<Composition id="rev03-headline-square" component={Card03Square} durationInFrames={CARD03_DURATION} {...SQUARE} />
		<Composition id="rev06-07-capability" component={Card0607Capability} durationInFrames={CARD0607_DURATION} {...VIDEO} />
		<Composition id="rev08-amara" component={Card08Amara} durationInFrames={CARD08_DURATION} {...VIDEO} />
		<Composition id="rev09-10-prescription" component={Card0910Prescription} durationInFrames={CARD0910_DURATION} {...VIDEO} />
		<Composition id="rev11-13-reasons" component={Card1113Reasons} durationInFrames={CARD1113_DURATION} {...VIDEO} />
		{/* Card 14 reuses the card 9 pay-premium chart at David's length (00:21:15). */}
		<Composition id="rev14-pay-premium" component={PayPremium} durationInFrames={645} {...VIDEO} />
		<Composition id="rev16-takeaway-square" component={Card16Square} durationInFrames={CARD16_DURATION} {...SQUARE} />
		{/* Earlier "Sheet1" card numbers; superseded where the revised script differs. */}
		<Composition id="card4-growth" component={Card4Growth} durationInFrames={CARD4_DURATION} {...VIDEO} />
		<Composition id="card5-ai-arrived" component={Card5Arrived} durationInFrames={CARD5_DURATION} {...VIDEO} />
		<Composition id="card6-venn" component={Card6Venn} durationInFrames={CARD6_DURATION} {...VIDEO} />
		<Composition id="card8-facts" component={Card8Facts} durationInFrames={CARD8_DURATION} {...VIDEO} />
		<Composition id="card9-pay-premium" component={PayPremium} durationInFrames={PAY_DURATION} {...VIDEO} />
		<Composition id="card11-takeaway" component={Card11Takeaway} durationInFrames={CARD11_DURATION} {...VIDEO} />
	</>
);
