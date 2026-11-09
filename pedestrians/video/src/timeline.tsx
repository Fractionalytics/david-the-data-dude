// What's on screen at global frame g of the whole Reel. Card clips render their slice of this, so a clip
// always starts from the previous card's end state. Words on screen come from the Sheet.
import React from 'react';
import {AbsoluteFill, Easing, interpolate} from 'remotion';
import {EST, S} from './cues';
import {MethChart, MethScatter, PovertyBars, RatesChart, RoadChart, Slope, StatSign, StimIndexChart, StimulantChart, SuvChart} from './charts/Charts';
import {HILL, HillSign, ListSign, QuestionSign, VisionZeroGrid} from './charts/Signs';

const ease = Easing.inOut(Easing.cubic);
// Progress 0-1 between frames a and b.
const prog = (g: number, a: number, b: number, e = ease) =>
	interpolate(g, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});

// Fade a run's graphic in at its first card.
const In: React.FC<{g: number; at: number; frames?: number; children: React.ReactNode}> = ({g, at, frames = 8, children}) => (
	<AbsoluteFill style={{opacity: prog(g, at, at + frames, Easing.linear)}}>{children}</AbsoluteFill>
);

// Cards 18-24: On-Screen Text, split into number and words.
const STATS: Record<number, [number, string]> = {
	18: [99, 'urban or suburban'],
	19: [84, 'after dark'],
	20: [84, 'middle of the block'],
	21: [71, 'arterial roads'],
	22: [75, 'adults'],
	23: [72, 'men'],
	24: [84, 'in south and west'],
};

export const Graphic: React.FC<{g: number; card: number}> = ({g, card}) => {
	// Cards 1-5: US line (card 1, quick), title (card 2), Europe line and new title (card 4).
	if (card >= 1 && card <= 5) {
		const eu = card >= 4;
		return (
			<In g={g} at={S(1)} frames={5}>
				<RatesChart
					title={eu ? 'Pedestrian Deaths: US vs. Europe' : 'US Pedestrian Deaths'}
					titleSize={eu ? 54 : undefined}
					titleOp={eu ? 1 : prog(g, S(2), S(2) + 10, Easing.linear)}
					usP={prog(g, S(1) + 2, S(1) + 38)}
					euP={eu ? prog(g, S(4) + 10, S(4) + 70) : 0}
				/>
			</In>
		);
	}
	if (card === 6)
		return (
			<In g={g} at={S(6)}>
				<VisionZeroGrid title="Vision Zero Cities" tilesP={prog(g, S(6) + 4, S(6) + 40, Easing.linear)} nycP={prog(g, EST.nycLights, EST.nycLights + 12)} />
			</In>
		);
	if (card === 8)
		return (
			<In g={g} at={S(8)}>
				<SuvChart title="SUV Adoption in Europe" p={prog(g, S(8) + 6, S(8) + 66)} />
			</In>
		);
	if (card >= 15 && card <= 17) return <QuestionSign p={prog(g, S(15), S(15) + 12, Easing.out(Easing.back(1.6)))} />;
	if (card >= 18 && card <= 24) {
		const [pct, label] = STATS[card];
		return (
			<In g={g} at={S(18)}>
				<StatSign
					pct={pct}
					label={label}
					p={prog(g, S(card) + 2, S(card) + 22)}
					pop={card === 24 ? 62 : undefined}
					popP={card === 24 ? prog(g, S(24) + 26, S(24) + 46) : 0}
				/>
			</In>
		);
	}
	if (card === 25)
		return (
			<In g={g} at={S(25)}>
				<PovertyBars title={'Pedestrian Deaths by\nNeighborhood Type'} p={prog(g, S(25) + 6, S(25) + 50)} />
			</In>
		);
	if (card === 26) {
		const items = Object.values(STATS).map(([n, w]) => `${n}% ${w}`);
		return (
			<In g={g} at={S(26)}>
				<ListSign items={items} shown={items.map((_, i) => prog(g, S(26) + 4 + i * 6, S(26) + 14 + i * 6))} size={54} top={34} gap={70} />
			</In>
		);
	}
	if (card >= 29 && card <= 31)
		return (
			<In g={g} at={S(29)}>
				<StimulantChart title={'Stimulant-Positive\nPedestrian Victims'} p={prog(g, S(30) + 6, S(31) - 6, Easing.linear)} />
			</In>
		);
	if (card >= 32 && card <= 37)
		return (
			<In g={g} at={S(32)}>
				<MethScatter title="Crystal Meth vs. Pedestrians" dotsP={prog(g, S(32) + 4, S(32) + 40, Easing.linear)} fitP={prog(g, S(34) + 10, S(34) + 50)} />
			</In>
		);
	// Cards 38-39: Hill's nine viewpoints, unchecked. Cards 52-54: the same sign with marks filling in,
	// in story order (PROPOSED marks, pending David: see docs/bradford-hill.md).
	if (card === 38 || card === 39)
		return (
			<In g={g} at={S(38)}>
				<HillSign title="Bradford Hill Criteria" sub="for judging whether a correlation is likely causal" marks={HILL.map(() => '')} markP={[]} listP={prog(g, S(38) + 4, S(38) + 40, Easing.linear)} />
			</In>
		);
	if (card >= 52 && card <= 54) {
		const order = ['Temporality', 'Biological gradient', 'Plausibility', 'Consistency', 'Experiment'];
		const marks = HILL.map((h) => (h === 'Experiment' ? 'half' : order.includes(h) ? 'check' : '')) as Array<'' | 'check' | 'half'>;
		const markP = HILL.map((h) => (order.includes(h) ? prog(g, S(52) + 6 + order.indexOf(h) * 9, S(52) + 14 + order.indexOf(h) * 9) : 0));
		return (
			<In g={g} at={S(52)}>
				<HillSign title="Bradford Hill Criteria" sub="for judging whether a correlation is likely causal" marks={marks} markP={markP} />
			</In>
		);
	}
	if (card === 40 || card === 41)
		return (
			<In g={g} at={S(40)}>
				<StimulantChart title="Stimulant-Positive Victims" p={1} />
			</In>
		);
	if (card === 42 || card === 43) {
		const x = prog(g, S(42), S(42) + 10, Easing.linear);
		return (
			<>
				<AbsoluteFill style={{opacity: 1 - x}}>
					<StimulantChart title="Stimulant-Positive Victims" p={1} />
				</AbsoluteFill>
				<AbsoluteFill style={{opacity: x}}>
					<StimIndexChart title={'Stimulant-Positive Victims\nwith Pedestrian Deaths'} pedP={prog(g, S(42) + 12, S(42) + 80)} />
				</AbsoluteFill>
			</>
		);
	}
	if (card === 46) {
		const items = ['Sleeplessness', 'Risk-taking', 'Crash phase'];
		const at = [EST.sleepless, EST.risk, EST.crash];
		return (
			<In g={g} at={S(46)}>
				<ListSign items={items} shown={at.map((a) => prog(g, a, a + 8))} size={110} top={50} gap={160} />
			</In>
		);
	}
	if (card >= 48 && card <= 50)
		return (
			<In g={g} at={S(48)}>
				<MethChart title="Meth Overdoses" p={prog(g, S(48) + 6, S(48) + 90)} />
			</In>
		);
	if (card === 51)
		return (
			<In g={g} at={S(51)}>
				<RoadChart title="Pedestrian Deaths" p={prog(g, S(51) + 6, S(51) + 90)} />
			</In>
		);
	if (card === 56)
		return (
			<In g={g} at={S(56)}>
				<Slope title="Pedestrian Likelihood of Death" leftNote="1.0x" rightNote="2.9x" p={prog(g, S(56) + 8, S(56) + 110)} />
			</In>
		);
	return null;
};
