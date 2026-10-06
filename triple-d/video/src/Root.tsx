// Every video is a <Composition>. Its id is what you pass to `npx remotion render`.
import React from 'react';
import {Composition} from 'remotion';
import {VIDEO} from './sharpie';
import {HOOK_DURATION, HookLine} from './charts/HookLine';
import {HOOK_STEPS_DURATION, HookSteps} from './charts/HookSteps';
import {DDD_STRIKE_DURATION, DddStrike} from './charts/DddStrike';
import {D_WORDS_DURATION, DWords} from './charts/DWords';
import {CATEGORY_MORPH_DURATION, CategoryMorph} from './charts/CategoryMorph';
import {BARS_DURATION, CategoryBars} from './charts/CategoryBars';
import {STACK_DURATION, SeasonStack} from './charts/SeasonStack';
import {DETAILED_DURATION, DetailedBars} from './charts/DetailedBars';
import {DETAILED_STACK_DURATION, DetailedSeasonStack} from './charts/DetailedSeasonStack';
import {THEN_NOW_DURATION, ThenNowLines} from './charts/ThenNowLines';

export const RemotionRoot: React.FC = () => (
	<>
		<Composition id="hook-line" component={HookLine} durationInFrames={HOOK_DURATION} {...VIDEO} />
		<Composition
			id="category-bars-jev"
			component={CategoryBars}
			durationInFrames={BARS_DURATION}
			{...VIDEO}
			defaultProps={{policy: 'strict' as const, title: '', xTitle: 'Category'}}
		/>
		<Composition
			id="category-bars-forced"
			component={CategoryBars}
			durationInFrames={BARS_DURATION}
			{...VIDEO}
			defaultProps={{policy: 'forced' as const, title: 'If Guy had to pick', xTitle: 'Category'}}
		/>
		<Composition
			id="category-bars-detailed"
			component={DetailedBars}
			durationInFrames={DETAILED_DURATION}
			{...VIDEO}
			defaultProps={{title: ''}}
		/>
		<Composition
			id="season-stack"
			component={SeasonStack}
			durationInFrames={STACK_DURATION}
			{...VIDEO}
			defaultProps={{mode: 'count' as const, title: 'Restaurants per season'}}
		/>
		<Composition
			id="season-stack-100"
			component={SeasonStack}
			durationInFrames={STACK_DURATION}
			{...VIDEO}
			defaultProps={{mode: 'percent' as const, title: 'Share per season'}}
		/>
		<Composition
			id="season-stack-100-detailed"
			component={DetailedSeasonStack}
			durationInFrames={DETAILED_STACK_DURATION}
			{...VIDEO}
			defaultProps={{title: 'Share per season, unpacked', layers: 'full' as const, groupBy: 'season' as const}}
		/>
		<Composition
			id="season-stack-100-simple"
			component={DetailedSeasonStack}
			durationInFrames={DETAILED_STACK_DURATION}
			{...VIDEO}
			defaultProps={{title: 'Share per season, simplified', layers: 'simple' as const, groupBy: 'season' as const}}
		/>
		<Composition
			id="era-stack-100-simple"
			component={DetailedSeasonStack}
			durationInFrames={DETAILED_STACK_DURATION}
			{...VIDEO}
			defaultProps={{title: 'Then vs. now', layers: 'simple' as const, groupBy: 'era' as const}}
		/>
		<Composition
			id="then-now-slope"
			component={ThenNowLines}
			durationInFrames={THEN_NOW_DURATION}
			{...VIDEO}
			defaultProps={{title: 'Diners out, global in', mode: 'slope' as const}}
		/>
		<Composition
			id="then-now-seasons"
			component={ThenNowLines}
			durationInFrames={THEN_NOW_DURATION}
			{...VIDEO}
			defaultProps={{title: 'Diners out, global in', mode: 'season' as const}}
		/>
		<Composition
			id="then-now-endpoints"
			component={ThenNowLines}
			durationInFrames={THEN_NOW_DURATION}
			{...VIDEO}
			defaultProps={{title: 'Season 1 vs. season 43', mode: 'endpoints' as const}}
		/>
		<Composition
			id="then-now-slope-combined"
			component={ThenNowLines}
			durationInFrames={THEN_NOW_DURATION}
			{...VIDEO}
			defaultProps={{title: 'Diners out, global in', mode: 'combined' as const}}
		/>
		<Composition id="hook-line-steps" component={HookSteps} durationInFrames={HOOK_STEPS_DURATION} {...VIDEO} />
		<Composition id="ddd-strike" component={DddStrike} durationInFrames={DDD_STRIKE_DURATION} {...VIDEO} />
		<Composition id="d-words" component={DWords} durationInFrames={D_WORDS_DURATION} {...VIDEO} />
		<Composition id="category-morph" component={CategoryMorph} durationInFrames={CATEGORY_MORPH_DURATION} {...VIDEO} />
	</>
);
