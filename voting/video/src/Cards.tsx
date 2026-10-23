// Card clips for Voting (Script v2 tab). Transparent; laid out in this video's narrow chart area (look.tsx Z)
// so everything sits on David's shirt. Each card starts from the previous card's end state where the two
// share a chart, so clips cut together. Cue frames are within the card. Card 2's cues are David's; the rest
// are estimates from where the phrase falls in the line, and are easy to nudge.
import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame} from 'remotion';
import {VIDEO} from '@kit/zones';
import {COLOR, Label, Num, PERSON_W, Person, Z, mix, t} from './look';
import {ADULTS, ADULT_YEARS, DROP, RATIO, YOUNG_MIDTERM} from './data';

const Svg: React.FC<{children: React.ReactNode}> = ({children}) => (
	<AbsoluteFill>
		<svg width={VIDEO.width} height={VIDEO.height} viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`}>
			{children}
		</svg>
	</AbsoluteFill>
);

const pop = (f: number, at: number) => spring({frame: f - at, fps: VIDEO.fps, config: {damping: 11, stiffness: 140}});
// A quick 1 -> 1.12 -> 1 bump, for pointing at something already on screen.
const bump = (f: number, at: number) => 1 + 0.12 * Math.sin(Math.PI * t(f, at, at + 10));
const LINE = 6; // thinnest stroke anywhere: thinner lines go soft over video

// Up to three left-aligned title lines from the top of the chart area.
const Title: React.FC<{lines: string[]; o?: number; size?: number}> = ({lines, o = 1, size = 52}) => (
	<g opacity={o}>
		{lines.map((l, i) => (
			<Label key={i} x={Z.left} y={Z.top + 45 + i * (size + 8)} size={size} anchor="start">{l}</Label>
		))}
	</g>
);

// --- cards 1-2: one young voter against the voters 65+ ------------------------------------------------
const FIG_H = 190;
const FIG_STEP = 92;
const FIG_X0 = Z.left + 40;
const YOUNG_Y = Z.top + 390;
const OLD_Y = Z.top + 700;
const BODY_W = FIG_H * PERSON_W;
const GROUP_LABEL = (rowBottom: number) => rowBottom - FIG_H - 30; // each group's label sits above its row

// Card 1: a year counter runs through the midterms while the seniors' row fills to each year's ratio.
const C1 = {start: 12, perElection: 9}; // 13 midterms in ~3.6 s, landing at frame 120; holds to 184
const ratioAt = (f: number) => {
	const k = interpolate(f, [C1.start, C1.start + C1.perElection * (RATIO.length - 1)], [0, RATIO.length - 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const i = Math.min(Math.floor(k), RATIO.length - 2);
	const p = t(k - i, 0, 1);
	return {ratio: mix(p, RATIO[i][1], RATIO[i + 1][1]), year: RATIO[Math.round(k)][0]};
};

// Slots fill left to right; a partly filled slot shows its empty part as a faint figure.
// Fills under 0.08 of a figure (2022's 5.03 leaves 0.03) aren't drawn: a 3px sliver reads as a glitch.
const SeniorRow: React.FC<{ratio: number; scales?: number[]}> = ({ratio, scales = []}) => (
	<g>
		{Array.from({length: 6}, (_, i) => {
			const fill = Math.max(0, Math.min(1, ratio - i));
			if (fill < 0.08) return null;
			const x = FIG_X0 + i * FIG_STEP;
			return (
				<g key={i}>
					<defs>
						<clipPath id={`slot-${i}`}>
							<rect x={x - BODY_W / 2 - 4} y={OLD_Y - FIG_H - 10} width={(BODY_W + 8) * fill} height={FIG_H + 20} />
						</clipPath>
					</defs>
					{fill < 1 && <Person x={x} y={OLD_Y} h={FIG_H} fill={COLOR.off} opacity={0.3} />}
					<g clipPath={`url(#slot-${i})`}>
						<Person x={x} y={OLD_Y} h={FIG_H} fill={COLOR.old} scale={scales[i] ?? 1} />
					</g>
				</g>
			);
		})}
	</g>
);

const YearCounter: React.FC<{year: number; opacity?: number}> = ({year, opacity = 1}) => (
	<g opacity={opacity}>
		<Num x={Z.left} y={Z.top + 70} size={100} anchor="start">{year}</Num>
		<Label x={Z.left + 215} y={Z.top + 66} size={60} anchor="start">midterm</Label>
	</g>
);

export const Card01: React.FC = () => {
	const f = useCurrentFrame();
	const {ratio, year} = ratioAt(f);
	return (
		<Svg>
			<YearCounter year={year} opacity={t(f, 0, 8)} />
			<Person x={FIG_X0} y={YOUNG_Y} h={FIG_H} fill={COLOR.young} scale={pop(f, 0)} />
			<g opacity={t(f, 4, 12)}>
				<SeniorRow ratio={ratio} />
			</g>
		</Svg>
	);
};

// Card 2 opens on card 1's last frame and adds the labels on David's cues:
// "for every one of you" at 0:08:03 and "about 5 grandparents" at 0:09:28 (card starts 0:06:04).
export const CUE2 = {young: 59, seniors: 114};
export const Card02: React.FC = () => {
	const f = useCurrentFrame();
	const end = RATIO[RATIO.length - 1];
	return (
		<Svg>
			<YearCounter year={end[0]} />
			<Num x={Z.left} y={GROUP_LABEL(YOUNG_Y)} size={76} anchor="start" fill={COLOR.young} opacity={t(f, CUE2.young, CUE2.young + 10)}>18–24</Num>
			<Person x={FIG_X0} y={YOUNG_Y} h={FIG_H} fill={COLOR.young} scale={bump(f, CUE2.young)} />
			<Num x={Z.left} y={GROUP_LABEL(OLD_Y)} size={76} anchor="start" fill={COLOR.old} opacity={t(f, CUE2.seniors, CUE2.seniors + 10)}>65+</Num>
			<SeniorRow ratio={end[1]} scales={[0, 1, 2, 3, 4].map((i) => bump(f, CUE2.seniors + i * 8))} />
		</Svg>
	);
};

// --- card 4: adults 18-24 vs 65+, 1972-2024 ----------------------------------------------------------
// Estimated cues: the gold line on "the number of young people has stayed roughly constant", the orchid
// line on "the grandparent-aged population has steadily grown", 2011 on "especially since 2011".
const C4 = {axes: [0, 12], young: [20, 120], old: [130, 250], mark: 235};
const AX = {x0: Z.left + 90, x1: Z.right - 150, y0: Z.bottom - 90, y1: Z.top + 180, max: 70};
const ax = (yr: number) => AX.x0 + ((yr - 1972) / (2024 - 1972)) * (AX.x1 - AX.x0);
const ay = (m: number) => AX.y0 - (m / AX.max) * (AX.y0 - AX.y1);
const linePath = (vals: readonly number[]) => vals.map((v, i) => `${i ? 'L' : 'M'}${ax(ADULT_YEARS[i])} ${ay(v)}`).join(' ');

export const Card04: React.FC = () => {
	const f = useCurrentFrame();
	const lines = [
		{key: 'young', vals: ADULTS.young, col: COLOR.young, win: C4.young, label: '18–24'},
		{key: 'old', vals: ADULTS.old, col: COLOR.old, win: C4.old, label: '65+'},
	];
	return (
		<Svg>
			<g opacity={t(f, C4.axes[0], C4.axes[1])}>
				<Title lines={['Adults, millions']} size={60} />
				<line x1={AX.x0} y1={AX.y0} x2={AX.x1} y2={AX.y0} stroke="white" strokeWidth={LINE} strokeLinecap="round" />
				{[0, 20, 40, 60].map((v) => (
					<Label key={v} x={AX.x0 - 18} y={ay(v) + 20} size={52} anchor="end">{v}</Label>
				))}
				{[1972, 2024].map((yr) => (
					<Label key={yr} x={ax(yr)} y={AX.y0 + 66} size={52}>{yr}</Label>
				))}
			</g>
			<g opacity={t(f, C4.mark, C4.mark + 10)}>
				<line x1={ax(2011)} y1={AX.y0} x2={ax(2011)} y2={AX.y1 - 10} stroke="white" strokeOpacity={0.8} strokeWidth={LINE} strokeDasharray="14 12" />
				<Label x={ax(2011)} y={AX.y1 - 26} size={52}>2011</Label>
			</g>
			{lines.map((l) => {
				const p = t(f, l.win[0], l.win[1]);
				const last = l.vals[l.vals.length - 1];
				return (
					<g key={l.key}>
						<defs>
							<clipPath id={`reveal-${l.key}`}>
								<rect x={0} y={0} width={AX.x0 + (AX.x1 - AX.x0) * p + 10} height={VIDEO.height} />
							</clipPath>
						</defs>
						<path d={linePath(l.vals)} fill="none" stroke={l.col} strokeWidth={16} strokeLinejoin="round" strokeLinecap="round" clipPath={`url(#reveal-${l.key})`} />
						<g opacity={t(f, l.win[1] - 8, l.win[1] + 4)}>
							<Num x={ax(2024) + 18} y={ay(last) + 20} size={72} anchor="start" fill={l.col}>{`${Math.round(last)}M`}</Num>
							<Num x={ax(2024) + 18} y={ay(last) + 80} size={60} anchor="start" fill={l.col}>{l.label}</Num>
						</g>
					</g>
				);
			})}
		</Svg>
	);
};

// --- cards 6-8: vertical turnout bars on one 0-100% axis -----------------------------------------------
// No raw percentages (David, 2026-10-23): the axis gives the scale, the bars carry the change, and only
// the change is labeled. The lost turnout drains from the top of each bar and stays as a faint ghost.
const BAR = {y0: Z.bottom - 90, y1: Z.top + 250, w: 120, axisX: Z.left + 120};
// `max` is the value at the top of the axis: 100 on cards 6-7; card 8 rescales it to 2018's 32.4 (David, 2026-10-23).
const by = (v: number, max = 100) => BAR.y0 - (v / max) * (BAR.y0 - BAR.y1);
const COL_X = {old: Z.left + 290, young: Z.left + 470, single: Z.left + 300};
type Timing = {grow: [number, number]; drain: [number, number]; delta: number};

// Ticks 0/50/100 on the full axis; card 8 crossfades them to 0/10/20/30 as the axis rescales.
const PctAxis: React.FC<{opacity: number; max?: number; fullTicks?: number; zoomTicks?: number}> = ({opacity, max = 100, fullTicks = 1, zoomTicks = 0}) => (
	<g opacity={opacity}>
		<line x1={BAR.axisX} y1={BAR.y0} x2={BAR.axisX} y2={BAR.y1} stroke="white" strokeWidth={LINE} strokeLinecap="round" />
		<line x1={BAR.axisX} y1={BAR.y0} x2={Z.right - 20} y2={BAR.y0} stroke="white" strokeWidth={LINE} strokeLinecap="round" />
		{[
			{vals: [0, 50, 100], o: fullTicks},
			{vals: [0, 10, 20, 30], o: zoomTicks},
		].map(({vals, o}, k) =>
			vals
				.filter((v) => v <= max + 0.5 && o > 0)
				.map((v) => (
					<Label key={`${k}-${v}`} x={BAR.axisX - 18} y={by(v, max) + 18} size={52} anchor="end" opacity={o}>{v}</Label>
				)),
		)}
	</g>
);

// One bar: grows to `from`, then its top drains (or rises) to `to`. A fall leaves a faint ghost of what was
// lost; a rise marks the old level with a white line across the bar.
const ChangeBar: React.FC<{f: number; x: number; col: string; label: string; from: number; to: number; delta: string; timing: Timing; hold?: boolean; max?: number; deltaBeside?: boolean}> = ({f: frame, x, col, label, from, to, delta, timing, hold, max = 100, deltaBeside}) => {
	const f = hold ? 9999 : frame;
	const grow = t(f, timing.grow[0], timing.grow[1]);
	const move = t(f, timing.drain[0], timing.drain[1]);
	const level = mix(move, from, to) * grow;
	const fall = to < from;
	const top = Math.max(from, to);
	return (
		<g opacity={t(f, timing.grow[0] - 6, timing.grow[0] + 4)}>
			{fall && <rect x={x - BAR.w / 2} y={by(from * grow, max)} width={BAR.w} height={BAR.y0 - by(from * grow, max)} rx={10} fill={col} opacity={0.28} />}
			<rect x={x - BAR.w / 2} y={by(level, max)} width={BAR.w} height={BAR.y0 - by(level, max)} rx={10} fill={col} />
			{!fall && move > 0 && <line x1={x - BAR.w / 2} y1={by(from, max)} x2={x + BAR.w / 2} y2={by(from, max)} stroke="white" strokeWidth={LINE} />}
			<Num x={x} y={BAR.y0 + 70} size={64} fill={col}>{label}</Num>
			{deltaBeside ? (
				<Num x={x + BAR.w / 2 + 20} y={by(top, max) + 24} size={68} anchor="start" fill={col} opacity={t(f, timing.delta, timing.delta + 12)}>{delta}</Num>
			) : (
				<Num x={x} y={by(top, max) - 24} size={68} fill={col} opacity={t(f, timing.delta, timing.delta + 12)}>{delta}</Num>
			)}
		</g>
	);
};

const TURNOUT_TITLE = ['% of citizens', 'who say they voted'];
const oldBar = (f: number, timing: Timing, hold?: boolean, max?: number) => (
	<ChangeBar f={f} x={COL_X.old} col={COLOR.old} label="65+" {...DROP.old} delta={`−${Math.round(DROP.old.from - DROP.old.to)} pts`} timing={timing} hold={hold} max={max} />
);
const youngBar = (f: number, timing: Timing, hold?: boolean, max?: number) => (
	<ChangeBar f={f} x={COL_X.young} col={COLOR.young} label="18–24" {...DROP.young} delta={`−${Math.round(DROP.young.from - DROP.young.to)} pts`} timing={timing} hold={hold} max={max} />
);

// Card 6 estimates: the bar rises as the line starts; it drains on "just 8 percentage points under".
const C6: Timing = {grow: [14, 40], drain: [150, 200], delta: 200};
// Card 7 estimates: the drain on "dropped 24 points".
const C7: Timing = {grow: [6, 30], drain: [55, 110], delta: 110};

export const Card06: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<Svg>
			<Title lines={[...TURNOUT_TITLE, '2020 → 2022']} o={t(f, 0, 12)} />
			<PctAxis opacity={t(f, 0, 12)} />
			{oldBar(f, C6)}
		</Svg>
	);
};

export const Card07: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<Svg>
			<Title lines={[...TURNOUT_TITLE, '2020 → 2022']} />
			<PctAxis opacity={1} />
			{oldBar(f, C6, true)}
			{youngBar(f, C7)}
		</Svg>
	);
};

// Card 8: card 7's bars and period fade out while the axis rescales so its top is 2018's turnout (32.4),
// then one 18-24 bar for midterm turnout rises 2014 -> 2018 to the top of the axis.
// Estimates: the rise on "Young people TURNED OUT", +89% right after.
const C8: Timing = {grow: [34, 58], drain: [135, 185], delta: 190};
const C8_ZOOM: [number, number] = [6, 30];
export const Card08: React.FC = () => {
	const f = useCurrentFrame();
	const out = 1 - t(f, 0, 18);
	const max = mix(t(f, C8_ZOOM[0], C8_ZOOM[1]), 100, YOUNG_MIDTERM.to);
	const gain = Math.round((YOUNG_MIDTERM.to / YOUNG_MIDTERM.from - 1) * 100);
	return (
		<Svg>
			<defs>
				<clipPath id="plot8">
					<rect x={0} y={BAR.y1 - 4} width={VIDEO.width} height={BAR.y0 - BAR.y1 + 8} />
				</clipPath>
			</defs>
			<Title lines={TURNOUT_TITLE} />
			<Label x={Z.left} y={Z.top + 45 + 2 * 60} size={52} anchor="start" opacity={out}>2020 → 2022</Label>
			<Label x={Z.left} y={Z.top + 45 + 2 * 60} size={52} anchor="start" opacity={t(f, 18, 30)}>Midterms, 2014 → 2018</Label>
			<PctAxis opacity={1} max={max} fullTicks={1 - t(f, 2, 12)} zoomTicks={t(f, 12, 24)} />
			<g opacity={out} clipPath="url(#plot8)">
				{oldBar(f, C6, true, max)}
				{youngBar(f, C7, true, max)}
			</g>
			<ChangeBar f={f} x={COL_X.single} col={COLOR.young} label="18–24" {...YOUNG_MIDTERM} delta={`+${gain}%`} timing={C8} max={max} deltaBeside />
		</Svg>
	);
};

// --- cards 9-10: slopegraph of voters 65+ per voter 18-24 ----------------------------------------------
const SLOPE_YEARS = [2014, 2018, 2022];
const SX = [Z.left + 75, (Z.left + Z.right) / 2, Z.right - 75];
const SY = (r: number) => Z.bottom - 90 - (r / 6) * (Z.bottom - 90 - (Z.top + 320));
const ratioOf = (yr: number) => RATIO.find(([y]) => y === yr)![1];

const SlopeColumn: React.FC<{i: number; o: number; dot: number}> = ({i, o, dot}) => {
	const r = ratioOf(SLOPE_YEARS[i]);
	return (
		<g>
			<g opacity={o}>
				<line x1={SX[i]} y1={SY(0)} x2={SX[i]} y2={SY(6)} stroke="white" strokeOpacity={0.4} strokeWidth={LINE} strokeLinecap="round" />
				<Label x={SX[i]} y={SY(0) + 66} size={52}>{SLOPE_YEARS[i]}</Label>
			</g>
			<g opacity={dot}>
				<circle cx={SX[i]} cy={SY(r)} r={24} fill={COLOR.old} />
				{/* the 2018 low point is labeled below its dot so the lines on both sides never cross the label */}
				<Num x={SX[i]} y={i === 1 ? SY(r) + 96 : SY(r) - 42} size={84}>{r.toFixed(1)}</Num>
			</g>
		</g>
	);
};

const Segment: React.FC<{i: number; p: number}> = ({i, p}) => {
	const [x0, y0] = [SX[i], SY(ratioOf(SLOPE_YEARS[i]))];
	const [x1, y1] = [SX[i + 1], SY(ratioOf(SLOPE_YEARS[i + 1]))];
	return <line x1={x0} y1={y0} x2={mix(p, x0, x1)} y2={mix(p, y0, y1)} stroke={COLOR.old} strokeWidth={14} strokeLinecap="round" opacity={p > 0 ? 1 : 0} />;
};

const SLOPE_TITLE = ['Voters 65+', 'per voter 18–24,', 'midterms'];

// Card 9 estimates: 2014's 5.6 on "from 5.6", the line down to 3.8 on "to 3.8".
const C9 = {cols: [0, 12], dot0: 30, line: [70, 110] as [number, number]};
export const Card09: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<Svg>
			<Title lines={SLOPE_TITLE} o={t(f, C9.cols[0], C9.cols[1])} />
			<SlopeColumn i={0} o={t(f, C9.cols[0], C9.cols[1])} dot={t(f, C9.dot0, C9.dot0 + 10)} />
			<SlopeColumn i={1} o={t(f, C9.cols[0], C9.cols[1])} dot={t(f, C9.line[1] - 4, C9.line[1] + 6)} />
			<Segment i={0} p={t(f, C9.line[0], C9.line[1])} />
		</Svg>
	);
};

// Card 10 opens on card 9's end; estimate: 2022's rise to 5.0 on "not let it slip like in 2022".
const C10 = {col: [10, 22], line: [170, 210] as [number, number]};
export const Card10: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<Svg>
			<Title lines={SLOPE_TITLE} />
			<SlopeColumn i={0} o={1} dot={1} />
			<SlopeColumn i={1} o={1} dot={1} />
			<Segment i={0} p={1} />
			<SlopeColumn i={2} o={t(f, C10.col[0], C10.col[1])} dot={t(f, C10.line[1] - 4, C10.line[1] + 6)} />
			<Segment i={1} p={t(f, C10.line[0], C10.line[1])} />
		</Svg>
	);
};
