// One composition per storyboard card, timed to David's Start column (Sheet, read 2026-11-24).
// Start times are MM:SS:FF-style at 30 fps; "SS:FF" when there's no minute part.
// Each card runs until the next included card starts, and opens on the previous card's end state
// so back-to-back clips cut together cleanly.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {
	Acronym, Bills, BigNumber, Definition, DinnerChart, Demand, Donations, Employment, Factors, HookChart,
	IneligibleBar, MealRatio, PaidWith, Slope, Surveys, Tefap, UtilityDebt, ramp,
} from './charts';
import {C} from './look';

const tc = (s: string) => {
	const p = s.split(':').map(Number);
	const [m, ss, ff] = p.length === 3 ? p : [0, p[0], p[1]];
	return (m * 60 + ss) * 30 + ff;
};

// Included cards in Sheet order: [card, Start]. Card 68 (no script) only marks the end.
const STARTS: [number, string][] = [
	[1, '0:00:00'], [2, '01:14'], [3, '04:05'], [4, '06:09'], [5, '09:13'], [6, '12:07'], [7, '16:01'], [8, '18:03'],
	[9, '18:19'], [10, '20:16'], [11, '24:05'], [12, '28:20'], [13, '29:17'], [14, '32:19'], [15, '35:19'], [16, '36:07'],
	[19, '38:00'], [20, '38:24'], [21, '39:23'], [23, '40:26'], [24, '41:20'], [25, '43:17'], [27, '48:18'], [28, '49:29'],
	[29, '51:21'], [30, '55:09'], [31, '57:27'], [32, '1:01:02'], [33, '1:04:17'], [34, '1:07:20'], [36, '1:08:29'],
	[38, '1:12:05'], [40, '1:17:13'], [42, '1:18:25'], [43, '1:22:23'], [44, '1:26:10'], [45, '1:29:14'], [46, '1:33:10'],
	[47, '1:34:27'], [48, '1:36:19'], [49, '1:39:16'], [50, '1:40:29'], [51, '1:45:24'], [52, '1:48:29'], [54, '1:52:20'],
	[55, '1:56:12'], [56, '2:01:05'], [57, '2:04:29'], [58, '2:08:29'], [59, '2:13:18'], [60, '2:16:12'], [61, '2:18:21'],
	[62, '2:20:15'], [63, '2:21:16'], [64, '2:24:27'], [65, '2:28:25'], [66, '2:31:22'], [67, '2:33:01'], [68, '2:37:00'],
];

export const TIMING: Record<number, {start: number; dur: number}> = {};
STARTS.forEach(([card, s], i) => {
	if (i < STARTS.length - 1) TIMING[card] = {start: tc(s), dur: tc(STARTS[i + 1][1]) - tc(s)};
});

const all = (n: number, v = 1) => Array(n).fill(v);
// rows appearing one after another, `step` frames apart, starting at `from`
const seq = (f: number, n: number, from: number, step: number, len = 10) =>
	Array.from({length: n}, (_, i) => ramp(f, from + i * step, from + i * step + len));

type Render = (f: number, dur: number) => React.ReactNode;
const R: Record<number, Render> = {
	// Hook chart
	1: (f, d) => <HookChart draw={ramp(f, 0, d - 4)} />,
	2: (f) => <HookChart title labels={ramp(f, 0, 14)} />,
	3: (f) => <HookChart title labels={1} slots={ramp(f, 0, 14)} />,
	// Other surveys
	5: (f, d) => <Surveys rows={seq(f, 6, 4, Math.floor((d - 16) / 6))} status={[]} />,
	6: (f, d) => <Surveys rows={all(6)} status={seq(f, 6, 6, Math.floor((d - 24) / 6))} />,
	7: () => <HookChart title labels={1} slots={1} />,
	8: () => <HookChart title labels={1} slots={1} />,
	9: (f) => <HookChart title labels={1} slots={1} qmarks={ramp(f, 4, 18)} />,
	// Dinner price
	11: (f) => <DinnerChart draw={ramp(f, 4, 64)} labels={ramp(f, 56, 72)} />,
	12: () => <DinnerChart draw={1} labels={1} />,
	13: () => <DinnerChart draw={1} labels={1} />,
	14: () => <DinnerChart draw={1} labels={1} />,
	15: () => <DinnerChart draw={1} labels={1} />,
	// Important bills: one line per spoken word
	16: () => <Bills rows={[]} pay={0} />,
	19: (f) => <Bills rows={[ramp(f, 0, 10)]} pay={0} />,
	20: (f) => <Bills rows={[1, ramp(f, 0, 10)]} pay={0} />,
	21: (f) => <Bills rows={[1, 1, ramp(f, 0, 10)]} pay={0} />,
	23: (f) => <Bills rows={[1, 1, 1, ramp(f, 0, 10)]} pay={0} />,
	24: () => <Bills rows={all(4)} pay={0} />,
	25: () => <Bills rows={all(4)} pay={0} />,
	27: (f) => <Definition o={ramp(f, 2, 14)} />,
	28: (f) => <BigNumber o={ramp(f, 4, 20)} />,
	29: (f) => <HookChart title labels={1} slots={1} qmarks={ramp(f, 0, 12)} />,
	30: () => <HookChart title labels={1} slots={1} qmarks={1} />,
	31: () => <Bills rows={all(4)} pay={0} />,
	32: (f) => <Bills rows={all(4)} pay={ramp(f, 6, 20)} />,
	33: (f, d) => <Employment rows={seq(f, 3, 4, Math.floor((d - 16) / 3), 12)} />,
	34: (f, d) => <Acronym rows={seq(f, 4, 2, Math.floor((d - 12) / 4), 8)} />,
	36: (f) => (
		<Slope title="SNAP Participants" sub="Aug 2025 - Aug 2026" a={['AUG 2025', 41.4, '41.4M']} b={['AUG 2026', 35.9, '35.9M']}
			color={C.blue} max={45} draw={ramp(f, 6, 46)} />
	),
	38: (f) => <IneligibleBar grow={ramp(f, 8, 50)} />,
	40: () => <IneligibleBar grow={1} />,
	42: (f) => <MealRatio snap={ramp(f, 4, 60)} bank={ramp(f, 66, 80)} />,
	43: (f) => <Tefap grow={ramp(f, 10, 50)} />,
	44: (f, d) => <Donations rows={seq(f, 2, 4, Math.floor(d / 3), 12)} />,
	45: () => <Donations rows={all(2)} />,
	46: (f) => <Demand o={ramp(f, 0, 12)} />,
	47: () => <PaidWith strike={0} credit={0} bnpl={0} />,
	48: (f) => <PaidWith strike={ramp(f, 4, 16)} credit={ramp(f, 14, 26)} bnpl={ramp(f, 30, 42)} />,
	49: (f) => <UtilityDebt grow={ramp(f, 2, 40)} />,
	50: (f) => (
		<Slope title="Credit Card Delinquencies Up" a={['Q3 2022', 6.2, '6.2%']} b={['Q3 2026', 10.3, '10.3%']}
			color={C.red} max={12} draw={ramp(f, 30, 80)} note="LOWEST-INCOME ZIP CODES" />
	),
	51: () => <Slope title="BNPL Grocery Usage Rates Up" a={['2024', 14, '14%']} b={['2026', 29, '29%']} color={C.red} max={35} draw={0} />,
	52: (f) => <Slope title="BNPL Grocery Usage Rates Up" a={['2024', 14, '14%']} b={['2026', 29, '29%']} color={C.red} max={35} draw={ramp(f, 16, 70)} />,
	// Factors list
	54: (f) => <Factors rows={seq(f, 8, 4, 11, 10)} />,
	55: (f) => <Factors rows={[...all(8), ramp(f, 30, 42)]} />,
	56: () => <Factors rows={all(9)} />,
	57: (f) => <Factors rows={[...all(9), ramp(f, 20, 32)]} />,
	58: (f) => <HookChart title labels={1} slots={1} qmarks={1} draw={1} />,
	59: () => <HookChart title labels={1} slots={1} qmarks={1} />,
	60: (f) => <Factors rows={[...all(10), ramp(f, 20, 32)]} />,
	61: () => <Factors rows={all(11)} />,
};

export const CARDS = Object.keys(R).map(Number);

export const Card: React.FC<{card: number}> = ({card}) => {
	const f = useCurrentFrame();
	return <>{R[card](f, TIMING[card].dur)}</>;
};
