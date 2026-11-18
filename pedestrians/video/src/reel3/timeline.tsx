// What's on screen at global frame g of Reel 3. Card clips render their slice of this, so a clip always starts
// from the previous card's end state. Words on screen come from the Sheet (DDD15, Script v6).
import React from 'react';
import {AbsoluteFill, Easing} from 'remotion';
import {AreaChart, BucketBars, EuropeMap, ListSign, MethOnlyChart, RatesChart, ReportPage, SlopeChart, StateGrid, StimIndexChart, StimulantChart, View, WordSign} from './charts';
import {END, EST, S} from './cues';
import {C, prog, W} from './kit';
import assets from './assets.json';

const In: React.FC<{g: number; at: number; frames?: number; children: React.ReactNode}> = ({g, at, frames = 8, children}) => (
	<AbsoluteFill style={{opacity: prog(g, at, at + frames, Easing.linear)}}>{children}</AbsoluteFill>
);

const RATES = 'Pedestrian Deaths: US vs. Europe'; // Reel 1's title
const SAFER = 'Czechia got safer'; // Sheet, cards 22-26
const CREDIT = 'Matthew Brumbelow\nresearcher at the Insurance Institute for Highway Safety'; // per David

// Report views (page pixels at 2x; a page is 1224 x 1584).
// Text runs x 72-1152, so a passage view spans the full text width, centered on the passage's lines.
const hlCenter = (k: keyof typeof assets.highlights): View => {
	const h = assets.highlights[k];
	const ys = h.rects.flatMap((r) => [r[1], r[3]]);
	return {page: h.page, cx: 612, cy: (Math.min(...ys) + Math.max(...ys)) / 2, w: 1110};
};
const lerpView = (a: View, b: View, t: number): View =>
	a.page !== b.page ? (t < 0.5 ? a : b) : {page: a.page, cx: a.cx + (b.cx - a.cx) * t, cy: a.cy + (b.cy - a.cy) * t, w: a.w + (b.w - a.w) * t};

export const Graphic: React.FC<{g: number; card: number}> = ({g, card}) => {
	// Cards 1-2: the hook, US and Europe drawing in together. Card 5-7: back to it, finished.
	if (card === 1 || card === 2)
		return (
			<In g={g} at={S(1)} frames={4}>
				<RatesChart title={RATES} usP={prog(g, S(1) + 2, S(1) + 60)} euP={prog(g, S(1) + 12, S(1) + 70)} />
			</In>
		);
	if (card === 3)
		return (
			<In g={g} at={S(3)}>
				<StimIndexChart title={'Stimulant-Positive Victims\nwith Pedestrian Deaths'} pedP={prog(g, S(3) + 6, S(3) + 60)} stimP={prog(g, S(3) + 50, S(3) + 120)} />
			</In>
		);
	if (card === 4)
		return (
			<In g={g} at={S(4)}>
				<StimulantChart title={'Stimulant-Positive\nPedestrian Victims'} p={prog(g, S(4) + 6, S(4) + 90, Easing.linear)} />
			</In>
		);
	if (card >= 5 && card <= 7)
		return (
			<In g={g} at={S(5)}>
				<RatesChart title={RATES} usP={1} euP={1} />
			</In>
		);
	if (card >= 8 && card <= 10)
		return (
			<In g={g} at={S(8)}>
				<EuropeMap
					mapP={prog(g, S(8), S(8) + 15, Easing.linear)}
					czP={prog(g, S(8) + 20, S(8) + 40)}
					flagP={prog(g, S(8) + 30, S(8) + 42, Easing.linear)}
					citiesP={prog(g, S(10) + 4, S(10) + 50)}
				/>
			</In>
		);
	if (card >= 15 && card <= 19)
		return (
			<In g={g} at={S(15)}>
				<AreaChart
					title="US vs. Czechia"
					czP={prog(g, S(15) + 6, S(15) + 20, Easing.linear)}
					usersP={prog(g, S(15) + 24, S(15) + 70)}
					areaP={prog(g, S(16) + 6, S(16) + 50)}
					riskP={prog(g, S(17) + 4, S(17) + 20)}
					zoomP={prog(g, S(18) + 2, S(18) + 30)}
					rangeP={prog(g, S(18) + 26, S(18) + 56)}
				/>
			</In>
		);
	// Card 22: the 2016-21 bars, then the stimulant pair fades back as B asks about the rest.
	if (card === 22)
		return (
			<In g={g} at={S(22)}>
				<BucketBars title={SAFER} barsP={prog(g, S(22) + 6, S(22) + 40)} focusP={prog(g, S(22) + 50, S(22) + 70)} />
			</In>
		);
	// Card 23: "In Czechia, that rate fell quite a bit, while it rose slightly in the US": the no-stimulant
	// rates over time, 2003-05 -> 2016-21. Card 25 adds the stimulant-positive pair to this same chart.
	if (card === 23) {
		const B = assets.numbers.buckets.slope;
		const pct = (v: number[]) => `${v[1] > v[0] ? '+' : '−'}${Math.round(Math.abs(v[1] / v[0] - 1) * 100)}%`;
		return (
			<In g={g} at={S(23)}>
				<SlopeChart title={SAFER} sub="Tested, no stimulants found, per million a year" max={11} ticks={[0, 5, 10]} p={prog(g, S(23) + 8, S(23) + 60)}
					series={[
						{label: 'US, none found', v: B.usNo, color: C.us, change: pct(B.usNo)},
						{label: 'Czechia, none found', v: B.czNo, color: C.eu, change: pct(B.czNo)},
					]} />
			</In>
		);
	}
	if (card === 24)
		return (
			<In g={g} at={S(24)}>
				<WordSign before="Vehicle size is about" num="10%" after="of the rise in the US" color={C.us} p={prog(g, S(24) + 6, S(24) + 30)} range={[0, 10]} />
			</In>
		);
	if (card === 25) {
		const B = assets.numbers.buckets.slope;
		return (
			<In g={g} at={S(25)}>
				<SlopeChart
					title={SAFER}
					sub="Tested, per million a year; dashed = stimulants found"
					max={11}
					ticks={[0, 5, 10]}
					p={1}
					series={[
						{label: 'US, none found', v: B.usNo, color: C.us},
						{label: 'Czechia, none found', v: B.czNo, color: C.eu},
						{label: 'US, stimulants', v: B.usStim, color: C.us, dash: '14 12', nudge: -18, p: prog(g, S(25) + 10, S(25) + 50)},
						{label: 'Czechia, stimulants', v: B.czStim, color: C.eu, dash: '14 12', nudge: 16, p: prog(g, S(25) + 10, S(25) + 50)},
					]}
				/>
			</In>
		);
	}
	if (card === 26) {
		const T = assets.numbers.buckets.total;
		return (
			<In g={g} at={S(26)}>
				<SlopeChart title={SAFER} sub="All dead pedestrians per million people a year" max={31} ticks={[0, 10, 20, 30]} x1={W - 250} p={prog(g, S(26) + 8, S(26) + 50)}
					series={[{label: 'US', v: T.us, color: C.us}, {label: 'Czechia', v: T.cz, color: C.eu}]} />
			</In>
		);
	}
	// Cards 30-31: "Same as Card 17" (Sheet): chart E's best-estimate state, held through card 31.
	if (card === 30 || card === 31)
		return (
			<In g={g} at={S(30)}>
				<AreaChart title="US vs. Czechia" czP={1} usersP={1} areaP={1} riskP={1} zoomP={0} rangeP={0} focusP={prog(g, S(30) + 15, S(30) + 35)} />
			</In>
		);
	// Cards 32-33: meth-only overdose deaths, 2009-2024, held through card 33. Title from the Sheet ("heaver" read as "heavier").
	if (card === 32 || card === 33)
		return (
			<In g={g} at={S(32)}>
				<MethOnlyChart title="A sign of heavier meth use" p={prog(g, S(32) + 8, S(32) + 100)} />
			</In>
		);
	// Cards 34-36: card 1's chart, accenting the US rise from the 2009 low; held through card 36.
	if (card >= 34 && card <= 36)
		return (
			<In g={g} at={S(34)}>
				<RatesChart title={RATES} usP={1} euP={1} accentP={prog(g, S(34) + 10, S(34) + 30)} riseP={prog(g, S(34) + 30, S(34) + 100)} />
			</In>
		);
	if (card >= 37 && card <= 42) {
		// 37: title, then the factors list, then "almost none shifted"; 38 holds; 39 the two exceptions;
		// 40 arterials at night; 41 the drug test rise; 42 pedestrians, not drivers.
		const full: View = {page: 1, cx: 612, cy: 300, w: 1224};
		const factors: View = {page: 1, cx: 612, cy: 1180, w: 1000};
		const segs: Array<[number, View, Array<[keyof typeof assets.highlights, number]>]> = [
			[S(37), full, [['title', prog(g, S(37) + 10, S(37) + 30)]]],
			[S(37) + Math.round((END(37) - S(37)) * 0.3), factors, [['factors', prog(g, S(37) + 90, S(37) + 110)]]],
			[S(37) + Math.round((END(37) - S(37)) * 0.72), hlCenter('noShift'), [['noShift', prog(g, S(37) + 175, S(37) + 205)]]],
			[S(39), hlCenter('twoExceptions'), [['noShift', 1], ['twoExceptions', prog(g, S(39) + 6, S(39) + 22)]]],
			[S(40), hlCenter('arterials'), [['twoExceptions', 1], ['arterials', prog(g, S(40) + 20, S(40) + 50)]]],
			[S(41), hlCenter('drugRise'), [['drugRise', prog(g, S(41) + 15, S(41) + 50)]]],
			[S(42), hlCenter('notDrivers'), [['drugRise', 1], ['notDrivers', prog(g, S(42) + 10, S(42) + 50)]]],
		];
		let i = 0;
		while (i + 1 < segs.length && g >= segs[i + 1][0]) i++;
		const prev = segs[Math.max(0, i - 1)][1];
		const t = i === 0 ? 1 : prog(g, segs[i][0], segs[i][0] + 18);
		const view = lerpView(prev, segs[i][1], t);
		const pageFade = prev.page !== segs[i][1].page ? Math.abs(t - 0.5) * 2 : 1;
		return (
			<In g={g} at={S(37)}>
				<ReportPage view={view} marks={segs[i][2]} credit={CREDIT} opacity={pageFade} />
			</In>
		);
	}
	if (card === 44 || card === 48 || card === 49) {
		const at = card === 44 ? S(44) : S(48);
		return (
			card === 44 ? (
				// Card 44: the state tandem test (P25). Title from the Sheet.
				<In g={g} at={at}>
					<StateGrid title="Working in Tandem" ps={[prog(g, S(44) + 8, S(44) + 30), prog(g, S(44) + 45, S(44) + 75), prog(g, S(44) + 95, S(44) + 135)]} />
				</In>
			) : (
				// Cards 48-49: the 13x rectangle from card 17 ("two systemic failures multiplying each other").
				<In g={g} at={at}>
					<AreaChart title="US vs. Czechia" czP={1} usersP={1} areaP={1} riskP={1} zoomP={0} rangeP={0} />
				</In>
			)
		);
	}
	if (card === 46) {
		const at = [EST.trucks, EST.phones, EST.deadlier];
		return (
			<In g={g} at={S(46)}>
				<ListSign items={['Truck sizes', 'Smartphones', 'Being hit got deadlier']} shown={at.map((a) => prog(g, a, a + 8))} />
			</In>
		);
	}
	return null;
};
