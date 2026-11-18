// What's on screen at global frame g of Reel 2. Card clips render their slice of this, so a clip always starts
// from the previous card's end state. Titles come from the Sheet (DDD16, Script v3, On-Screen Text).
// In-card cues marked "est." are estimates from where the words fall in the line (no word-level timecodes).
import React from 'react';
import {AbsoluteFill, Easing} from 'remotion';
import {GapBars, MethMap} from './charts';
import {DeadlyPairSign, DotGrids, EuropeMeth, ListSign, MixGrid, Potency, Seesaw, ShareBars, SplitBar, StatWaffle, Strengths, Trend, UseBars} from './charts2';
import {END, S} from './cues';
import {prog} from './kit';

const In: React.FC<{g: number; at: number; frames?: number; children: React.ReactNode}> = ({g, at, frames = 8, children}) => (
	<AbsoluteFill style={{opacity: prog(g, at, at + frames, Easing.linear)}}>{children}</AbsoluteFill>
);

// Frame at a share of a card's length (est.).
const at = (card: number, share: number) => S(card) + Math.round((END(card) - S(card)) * share);
const tc = (m: number, s: number, f: number) => (m * 60 + s) * 30 + f;
const pop = Easing.out(Easing.quad);

const DEATHS = 'Drug-Induced Deaths: US vs. Europe'; // cards 2-3, 6, 34, 46
const USE = 'Drug Usage Rates: US vs. Europe';
const DIFF = 'What Makes the US Different from Europe';

export const Graphic: React.FC<{g: number; card: number}> = ({g, card}) => {
	// Card 1: the bars draw in bare. Card 2: title, labels, numbers and the 13x stamp from the start
	// (David, 2026-11-18). Card 3 holds.
	if (card >= 1 && card <= 3)
		return (
			<In g={g} at={S(1)} frames={4}>
				<GapBars title={DEATHS} usP={prog(g, S(1) + 3, S(1) + 40)} euP={prog(g, S(1) + 10, S(1) + 30)} headP={prog(g, S(2), S(2) + 10, Easing.linear)} stampP={prog(g, S(2) + 6, S(2) + 16, pop)} />
			</In>
		);
	// Cards 4-5: cocaine and amphetamines while "stimulant use is about the same" (est.); opioids at the
	// start of card 5, cannabis on "cannabis" (est.).
	if (card === 4 || card === 5) {
		const r = (a: number) => prog(g, a, a + 18);
		return (
			<In g={g} at={S(4)}>
				<UseBars title={USE} ps={[r(at(4, 0.3)), r(at(4, 0.55)), r(S(5) + 2), r(at(5, 0.22))]} />
			</In>
		);
	}
	// Card 6: back to the bars; the 13x restamps larger as he says "13x" (est.).
	if (card === 6)
		return (
			<In g={g} at={S(6)}>
				<GapBars title={DEATHS} usP={1} euP={1} headP={1} stampP={1} focusP={prog(g, at(6, 0.72), at(6, 0.86))} />
			</In>
		);
	// Cards 7-8: the three factors at David's cues (0:23:11, 0:25:27, 0:28:16).
	if (card === 7 || card === 8)
		return (
			<In g={g} at={S(7)}>
				<ListSign title="What Explains the Difference" items={['Mix', 'Heavy users', 'Usage patterns']} shown={[tc(0, 23, 11), tc(0, 25, 27), tc(0, 28, 16)].map((a) => prog(g, a, a + 10))} />
			</In>
		);
	// Cards 9-10: Europe fills on "Europe has very little fentanyl", the US on "commonplace" (est.).
	if (card === 9 || card === 10)
		return (
			<In g={g} at={S(9)}>
				<ShareBars title="Fentanyl's Share of Deaths: US vs. Europe" euP={prog(g, at(9, 0.3), at(9, 0.3) + 20)} usP={prog(g, at(9, 0.72), at(9, 0.72) + 30)} />
			</In>
		);
	// Card 11: the map, the cities, then the exceptions light up.
	if (card === 11)
		return (
			<In g={g} at={S(11)}>
				<EuropeMeth title="Meth in Europe" sub="Czechia, Slovakia, Lithuania, and parts of Germany are exceptions." mapP={1} dotsP={prog(g, S(11) + 4, S(11) + 40)} hotP={prog(g, at(11, 0.5), at(11, 0.5) + 15)} />
			</In>
		);
	// Card 12: 2009, then 2016, then 2024, each held about a second and a half.
	if (card === 12) {
		const t = prog(g, S(12) + 40, S(12) + 60) + prog(g, S(12) + 95, S(12) + 115);
		return (
			<In g={g} at={S(12)}>
				<MethMap title="Meth in the US over Time" t={t} mapP={1} />
			</In>
		);
	}
	// Cards 14-15: the US column first (already said), then heroin and cocaine as he names them (est.).
	if (card === 14 || card === 15) {
		const c = (a: number) => prog(g, a, a + 12);
		return (
			<In g={g} at={S(14)}>
				<MixGrid title="Supply Mix: US vs. Europe" ps={[c(S(14) + 4), c(S(14) + 12), c(at(14, 0.36)), c(at(14, 0.86))]} />
			</In>
		);
	}
	// Cards 16-17: heroin's bar, then fentanyl's grows on "50 times stronger" (est.). Card 17 holds.
	if (card === 16 || card === 17)
		return (
			<In g={g} at={S(16)}>
				<Potency title="Fentanyl vs. Heroin" heroinP={prog(g, S(16) + 4, S(16) + 16)} fentP={prog(g, at(16, 0.18), at(16, 0.42))} />
			</In>
		);
	// Cards 22-23: the first line types, then "The Deadly Pair" stamps.
	if (card === 22 || card === 23)
		return (
			<In g={g} at={S(22)}>
				<DeadlyPairSign typeP={prog(g, S(22) + 4, S(22) + 40, Easing.linear)} stampP={prog(g, S(22) + 48, S(22) + 58, pop)} />
			</In>
		);
	// Cards 24-25: powder meth on "lacing is fairly rare", crystal on "crystal meth" (est.).
	if (card === 24 || card === 25)
		return (
			<In g={g} at={S(24)}>
				<DotGrids title="Meth Laced with Fentanyl is Rare" powderP={prog(g, at(24, 0.28), at(24, 0.28) + 18)} crystalP={prog(g, at(24, 0.6), at(24, 0.6) + 40)} />
			</In>
		);
	if (card === 26)
		return (
			<In g={g} at={S(26)}>
				<StatWaffle title="Syringe Program Clients" sub="University of Washington ADAI 2023 survey" p={prog(g, S(26) + 6, S(26) + 50)} />
			</In>
		);
	// Cards 30-32: fentanyl tips the seesaw on card 30; meth lands on "meth" and it levels on "an upper to
	// match the downer" (est.).
	if (card >= 30 && card <= 32)
		return (
			<In g={g} at={S(30)}>
				<Seesaw title="Counterbalancing Effects" downP={prog(g, S(30) + 4, S(30) + 22)} upP={prog(g, at(31, 0.12), at(31, 0.12) + 16)} levelP={prog(g, at(31, 0.68), at(31, 0.9))} />
			</In>
		);
	if (card === 33) {
		const r = (a: number) => prog(g, a, a + 16);
		return (
			<In g={g} at={S(33)}>
				<Strengths title="Relative Strengths" ps={[r(S(33) + 4), r(S(33) + 16), r(S(33) + 28)]} />
			</In>
		);
	}
	if (card === 34)
		return (
			<In g={g} at={S(34)}>
				<GapBars title={DEATHS} usP={1} euP={1} headP={1} stampP={1} />
			</In>
		);
	// Cards 35-36, 43: the Deadly Pair lights on "the Deadly Pair" (est.), the rest on card 36 as named;
	// "everything else" (on screen, not spoken) last. Card 43 holds.
	if (card === 35 || card === 36 || card === 43) {
		const r = (a: number) => prog(g, a, a + 18);
		return (
			<In g={g} at={S(35)}>
				<SplitBar title={DIFF} ps={[r(at(35, 0.2)), r(at(36, 0.04)), r(at(36, 0.5)), r(at(36, 0.85))]} />
			</In>
		);
	}
	// Cards 44-45: the climb to 2023, the 2024 drop on "dropped in 2024" (est.), then -33%.
	if (card === 44 || card === 45)
		return (
			<In g={g} at={S(44)}>
				<Trend title="Deadly Pair Overdoses Dropped in 2024" p={prog(g, S(44) + 4, at(44, 0.3), Easing.linear)} dropP={prog(g, at(44, 0.36), at(44, 0.48))} stampP={prog(g, at(44, 0.52), at(44, 0.52) + 10, pop)} />
			</In>
		);
	// Card 46: the bars again, the 13x enlarged on "13x" (est.).
	if (card === 46)
		return (
			<In g={g} at={S(46)}>
				<GapBars title={DEATHS} usP={1} euP={1} headP={1} stampP={1} focusP={prog(g, at(46, 0.36), at(46, 0.5))} />
			</In>
		);
	return null;
};
