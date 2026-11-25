// Chart pieces for the Thanksgiving Reel. Every number is Checked or Source in docs/the-case.md
// and passed the spot checks (docs/spot-checks.md, cleared 2026-11-24).
// Titles are the Sheet's On-Screen Text, word for word. Row labels in the factors list and the
// survey receipt are Claude's draft data labels, flagged for David's review.
import React from 'react';
import {Easing, interpolate} from 'remotion';
import {C, Dotted, MONO, PH, PW, Receipt, Title} from './look';

export const ramp = (f: number, a: number, b: number) =>
	interpolate(f, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});

const T: React.FC<React.SVGProps<SVGTextElement> & {children: React.ReactNode}> = ({children, ...p}) => (
	<text fontFamily={MONO} fontWeight={700} fill={C.ink} textAnchor="middle" {...p}>
		{children}
	</text>
);

// ---------- Hook chart: USDA ERS household food insecurity, 2001-2024 (data/raw/ers/trends.xlsx)
const FI: [number, number][] = [
	[2001, 10.7], [2002, 11.1], [2003, 11.2], [2004, 11.9], [2005, 11.0], [2006, 10.9], [2007, 11.1],
	[2008, 14.6], [2009, 14.7], [2010, 14.5], [2011, 14.9], [2012, 14.5], [2013, 14.3], [2014, 14.0],
	[2015, 12.7], [2016, 12.3], [2017, 11.8], [2018, 11.1], [2019, 10.5], [2020, 10.5], [2021, 10.2],
	[2022, 12.8], [2023, 13.5], [2024, 13.7],
];
export const HookChart: React.FC<{draw?: number; labels?: number; slots?: number; qmarks?: number; title?: boolean}> = ({
	draw = 1, labels = 0, slots = 0, qmarks = 0, title = false,
}) => {
	const x0 = 80, x1 = PW - 56, yTop = title ? 200 : 120, yBot = PH - 110;
	const X = (yr: number) => x0 + ((yr - 2001) / 25) * (x1 - x0);
	const Y = (v: number) => yBot - ((v - 8) / 8) * (yBot - yTop);
	const pts = FI.map(([yr, v]) => [X(yr), Y(v)] as const);
	// draw the line progressively along its x extent
	const xEnd = x0 + draw * (X(2024) - x0);
	const d = pts.map(([x, y], i) => `${i ? 'L' : 'M'}${x},${y}`).join(' ');
	const marks: [number, number, number][] = [[2001, 10.7, -26], [2011, 14.9, -26], [2021, 10.2, 54], [2024, 13.7, -26]];
	const dx = (yr: number) => (yr === 2024 ? -20 : 0);
	const anchor = (yr: number) => (yr === 2024 ? 'end' : 'middle');
	return (
		<Receipt>
			{title && <Title text="USDA Food Insecurity Rate" opacity={labels} />}
			<svg width={PW} height={PH} style={{position: 'absolute', left: 0, top: 0}}>
				<defs>
					<clipPath id="drawclip"><rect x={0} y={0} width={xEnd + 12} height={PH} /></clipPath>
				</defs>
				<line x1={x0} x2={x1} y1={yBot} y2={yBot} stroke={C.rule} strokeWidth={3} />
				<g clipPath="url(#drawclip)">
					<path d={d} fill="none" stroke={C.red} strokeWidth={8} strokeLinejoin="round" strokeLinecap="round" />
				</g>
				{[2025, 2026].map((yr) => (
					<g key={yr} opacity={slots}>
						<rect x={X(yr) - 10} y={yTop} width={20} height={yBot - yTop} fill={C.track} opacity={0.7} />
						<line x1={X(yr)} x2={X(yr)} y1={yTop} y2={yBot} stroke={C.muted} strokeWidth={4} strokeDasharray="12 10" />
						<T x={X(yr)} y={yTop - 14} fontSize={46} fill={C.muted} opacity={qmarks} transform={`translate(0 ${(1 - qmarks) * 20})`}>?</T>
					</g>
				))}
				<g opacity={labels}>
					{marks.map(([yr, v, dy]) => (
						<g key={yr}>
							<circle cx={X(yr)} cy={Y(v)} r={10} fill={C.red} stroke={C.paper} strokeWidth={3} />
							<T x={X(yr) + dx(yr)} y={Y(v) + dy} fontSize={34} textAnchor={anchor(yr)}>{`${v}%`}</T>
						</g>
					))}
					{[2001, 2006, 2011, 2016, 2021, 2026].map((yr) => (
						<T key={yr} x={X(yr)} y={yBot + 50} fontSize={30} fontWeight={600} fill={yr > 2024 ? C.muted : C.ink}>{`'${String(yr).slice(2)}`}</T>
					))}
				</g>
			</svg>
		</Receipt>
	);
};

// ---------- Turkey dinner price, AFBF classic dinner for 10, price each year (not inflation-adjusted)
const DINNER: [number, number][] = [
	[2019, 48.91], [2020, 46.9], [2021, 53.31], [2022, 64.05], [2023, 61.17], [2024, 58.08], [2025, 55.18], [2026, 58.63],
];
export const DinnerChart: React.FC<{draw: number; labels: number}> = ({draw, labels}) => {
	const x0 = 90, x1 = PW - 80, yTop = 200, yBot = PH - 110;
	const X = (yr: number) => x0 + ((yr - 2019) / 7) * (x1 - x0);
	const Y = (v: number) => yBot - ((v - 40) / 30) * (yBot - yTop);
	const d = DINNER.map(([yr, v], i) => `${i ? 'L' : 'M'}${X(yr)},${Y(v)}`).join(' ');
	const xEnd = x0 + draw * (x1 - x0);
	const marks: [number, number, string][] = [[2019, 48.91, '$48.91'], [2022, 64.05, '$64.05'], [2026, 58.63, '$58.63']];
	return (
		<Receipt>
			<Title text="Price of Turkey Dinner" />
			<svg width={PW} height={PH} style={{position: 'absolute', left: 0, top: 0}}>
				<defs><clipPath id="dclip"><rect x={0} y={0} width={xEnd + 12} height={PH} /></clipPath></defs>
				<line x1={x0} x2={x1} y1={yBot} y2={yBot} stroke={C.rule} strokeWidth={3} />
				<g clipPath="url(#dclip)">
					<path d={d} fill="none" stroke={C.red} strokeWidth={8} strokeLinejoin="round" strokeLinecap="round" />
					{DINNER.map(([yr, v]) => <circle key={yr} cx={X(yr)} cy={Y(v)} r={8} fill={C.red} stroke={C.paper} strokeWidth={3} />)}
				</g>
				{DINNER.map(([yr]) => (
					<T key={yr} x={X(yr)} y={yBot + 50} fontSize={28} fontWeight={600}>{`'${String(yr).slice(2)}`}</T>
				))}
				<g opacity={labels}>
					{marks.map(([yr, v, s]) => (
						<T key={yr} x={X(yr)} y={Y(v) - 26} fontSize={36}>{s}</T>
					))}
				</g>
			</svg>
		</Receipt>
	);
};

// ---------- Receipt-style list rows
const Row: React.FC<{top: number; left: string; right?: string; rightColor?: string; opacity?: number; size?: number; weight?: number}> = ({
	top, left, right, rightColor = C.ink, opacity = 1, size = 36, weight = 600,
}) => (
	<div style={{position: 'absolute', left: 44, right: 44, top, display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontSize: size, fontWeight: weight, opacity, transform: `translateY(${(1 - opacity) * 12}px)`}}>
		<span>{left}</span>
		{right !== undefined && <span style={{color: rightColor, fontWeight: 700}}>{right}</span>}
	</div>
);

// Cards 5-6: other government surveys and their status (docs/research/food-insecurity-sources-*.md)
const SURVEYS: [string, string][] = [
	['CDC HEALTH SURVEY (NHIS)', 'ENDED 2024'],
	['CENSUS PULSE (HTOPS)', '1 QUESTION'],
	['CENSUS SIPP', 'NO RATE'],
	['CDC NHANES', 'NO RATE'],
	['AHRQ MEPS', 'NO RATE'],
	['FED SHED', '1 QUESTION'],
];
export const Surveys: React.FC<{rows: number[]; status: number[]}> = ({rows, status}) => (
	<Receipt>
		<Title text="Other Governmental Reports" />
		<Dotted top={96} />
		{SURVEYS.map(([name, st], i) => (
			<Row key={name} top={140 + i * 96} left={name} size={34} opacity={rows[i] ?? 0}
				right={(status[i] ?? 0) > 0 ? st : ''} rightColor={C.red} />
		))}
	</Receipt>
);

// Cards 16-32: important bills, Oct 2022 -> Oct 2026 (BLS CPI), plus low-end pay (BLS, Q3 to Q3)
const BILLS: [string, string][] = [
	['SHELTER', '+19.5%'],
	['ELECTRICITY', '+17.4%'],
	['WATER, SEWER & TRASH', '+21.9%'],
	['CHILD CARE', '+20.6%'],
];
export const Bills: React.FC<{rows: number[]; pay: number}> = ({rows, pay}) => (
	<Receipt>
		<Title text="Important Bills" />
		<Dotted top={96} />
		{BILLS.map(([k, v], i) => <Row key={k} top={140 + i * 96} left={k} right={v} rightColor={C.red} opacity={rows[i] ?? 0} size={40} />)}
		<div style={{opacity: pay}}>
			<Dotted top={540} />
			<Row top={568} left="PAY, LOWEST 10%" right="+13.2%" size={40} weight={700} opacity={pay} />
			<div style={{position: 'absolute', left: 44, top: 620, fontSize: 24, color: C.muted, opacity: pay}}>FULL-TIME WAGE & SALARY WORKERS</div>
		</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 100, textAlign: 'right', paddingRight: 44, fontSize: 24, color: C.muted}}>2022 → 2026</div>
	</Receipt>
);

// Card 27: USDA's definition (ERS: "a household-level economic and social condition of limited or uncertain access to adequate food")
export const Definition: React.FC<{o: number}> = ({o}) => (
	<Receipt>
		<Title text="Definition of Food Insecurity" />
		<Dotted top={130} />
		<div style={{position: 'absolute', left: 60, right: 60, top: 200, fontSize: 52, fontWeight: 700, lineHeight: 1.25, opacity: o}}>
			“Limited or uncertain access to adequate food”
		</div>
		<div style={{position: 'absolute', right: 60, top: 520, fontSize: 32, fontWeight: 600, color: C.muted, opacity: o}}>— USDA</div>
	</Receipt>
);

// Card 28: 47.9 million people in food-insecure households, 2024 (Map the Meal Gap / USDA)
export const BigNumber: React.FC<{o: number}> = ({o}) => (
	<Receipt>
		<Title text="Estimated People with Food Insecurity" />
		<div style={{position: 'absolute', left: 0, right: 0, top: 230, textAlign: 'center', fontSize: 210, fontWeight: 700, color: C.red, opacity: o, transform: `scale(${0.9 + 0.1 * o})`}}>47.9M</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 500, textAlign: 'center', fontSize: 34, fontWeight: 600, color: C.muted, opacity: o}}>2024</div>
	</Receipt>
);

// Card 33: David's own lines from the Sheet's Video column
const EMP = [['Long-term jobless', '▲62%'], ['Part-time workers who want full-time', '▲32%'], ['Underemployment', '▲18%']];
export const Employment: React.FC<{rows: number[]}> = ({rows}) => (
	<Receipt>
		<Title text="Employment Numbers" sub="October 2022 - October 2026" />
		<Dotted top={140} />
		{EMP.map(([s, v], i) => (
			<div key={s} style={{position: 'absolute', left: 50, right: 50, top: 190 + i * 150, display: 'flex', alignItems: 'center', gap: 24, fontSize: 40, fontWeight: 600, lineHeight: 1.25, opacity: rows[i] ?? 0}}>
				<span style={{flex: 1}}>{s}</span>
				<span style={{color: C.red, fontWeight: 700, fontSize: 52, whiteSpace: 'nowrap'}}>{v}</span>
			</div>
		))}
	</Receipt>
);

// Card 34: the acronym
export const Acronym: React.FC<{rows: number[]}> = ({rows}) => (
	<Receipt>
		<Title text="S.N.A.P." />
		{['Supplemental', 'Nutrition', 'Assistance', 'Program'].map((w, i) => (
			<div key={w} style={{position: 'absolute', left: 110, top: 150 + i * 120, fontSize: 76, fontWeight: 700, opacity: rows[i] ?? 0}}>
				<span style={{color: C.red}}>{w[0]}</span>{w.slice(1)}
			</div>
		))}
	</Receipt>
);

// Slopegraph (cards 36, 50, 51-52)
export const Slope: React.FC<{title: string; sub?: string; a: [string, number, string]; b: [string, number, string]; color: string; max: number; draw: number; note?: string}> = ({
	title, sub, a, b, color, max, draw, note,
}) => {
	const yTop = sub ? 260 : 230, yBot = PH - 130, xa = 200, xb = 560;
	const Y = (v: number) => yBot - (v / max) * (yBot - yTop);
	const xe = xa + draw * (xb - xa);
	const ye = Y(a[1]) + draw * (Y(b[1]) - Y(a[1]));
	return (
		<Receipt>
			<Title text={title} sub={sub} />
			<svg width={PW} height={PH} style={{position: 'absolute', left: 0, top: 0}}>
				<line x1={120} x2={640} y1={yBot + 22} y2={yBot + 22} stroke={C.rule} strokeWidth={3} strokeDasharray="8 8" />
				<line x1={xa} x2={xe} y1={Y(a[1])} y2={ye} stroke={color} strokeWidth={9} strokeLinecap="round" />
				<circle cx={xa} cy={Y(a[1])} r={13} fill={color} stroke={C.paper} strokeWidth={3} />
				<T x={xa} y={Y(a[1]) - 32} fontSize={50}>{a[2]}</T>
				<T x={xa} y={yBot + 70} fontSize={30} fontWeight={600}>{a[0]}</T>
				<g opacity={draw >= 0.98 ? 1 : 0}>
					<circle cx={xb} cy={Y(b[1])} r={13} fill={color} stroke={C.paper} strokeWidth={3} />
					<T x={xb} y={Y(b[1]) - 32} fontSize={50}>{b[2]}</T>
				</g>
				<T x={xb} y={yBot + 70} fontSize={30} fontWeight={600}>{b[0]}</T>
				{note && <T x={PW / 2} y={yBot + 118} fontSize={24} fontWeight={600} fill={C.muted}>{note}</T>}
			</svg>
		</Receipt>
	);
};

// Card 38-40: 25M of 47.9M food-insecure people earn too much for federal nutrition aid (MMG 2026, 2024 data)
export const IneligibleBar: React.FC<{grow: number}> = ({grow}) => {
	const left = 60, width = PW - 120, share = 25 / 47.9;
	return (
		<Receipt>
			<Title text="Food Insecure, Ineligible for SNAP" />
			<div style={{position: 'absolute', left, width, top: 340, height: 140, background: C.track, borderRadius: 6}}>
				<div style={{width: `${share * 100 * grow}%`, height: '100%', background: C.red, borderRadius: 6}} />
			</div>
			<div style={{position: 'absolute', left, top: 250, fontSize: 64, fontWeight: 700, color: C.red, opacity: grow}}>25M</div>
			<div style={{position: 'absolute', left, width, top: 510, fontSize: 32, fontWeight: 600, opacity: grow}}>EARN TOO MUCH FOR FEDERAL AID</div>
			<div style={{position: 'absolute', left, width, top: 262, textAlign: 'right', fontSize: 48, fontWeight: 700, color: C.muted}}>47.9M</div>
			<div style={{position: 'absolute', left, width, top: 580, textAlign: 'right', fontSize: 28, color: C.muted}}>ALL FOOD INSECURE, 2024</div>
		</Receipt>
	);
};

// Card 42: for every meal from the Feeding America network, SNAP provides nine
const Plate: React.FC<{x: number; y: number; color: string; s: number}> = ({x, y, color, s}) => (
	<g transform={`translate(${x} ${y}) scale(${s})`} opacity={s > 0.05 ? 1 : 0}>
		<circle r={54} fill={color} />
		<circle r={36} fill="none" stroke={C.paper} strokeWidth={4} opacity={0.85} />
	</g>
);
export const MealRatio: React.FC<{snap: number; bank: number}> = ({snap, bank}) => (
	<Receipt>
		<Title text="SNAP to Food Banks Meal Ratio" />
		<svg width={PW} height={PH} style={{position: 'absolute', left: 0, top: 0}}>
			{Array.from({length: 9}, (_, i) => {
				const col = i % 3, row = Math.floor(i / 3);
				return <Plate key={i} x={100 + col * 120} y={250 + row * 120} color={C.blue} s={Math.min(1, Math.max(0, snap * 9 - i))} />;
			})}
			<T x={220} y={660} fontSize={42}>SNAP: 9</T>
			<Plate x={590} y={370} color={C.red} s={bank} />
			<T x={540} y={660} fontSize={40} opacity={bank}>FOOD BANKS: 1</T>
		</svg>
	</Receipt>
);

// Card 43: TEFAP food by weight, FY2024 -> FY2026, -30% (Feeding America fact sheet, July 2026)
export const Tefap: React.FC<{grow: number}> = ({grow}) => {
	const left = 230, width = PW - 290;
	const bar = (top: number, frac: number, color: string) => (
		<div style={{position: 'absolute', left, top, width: width * frac, height: 120, background: color, borderRadius: 6}} />
	);
	return (
		<Receipt>
			<Title text="TEFAP Reduced" />
			<div style={{position: 'absolute', left: 40, top: 180, fontSize: 38, fontWeight: 700}}>FY2024</div>
			{bar(150, 1, C.muted)}
			<div style={{position: 'absolute', left: 40, top: 360, fontSize: 38, fontWeight: 700}}>FY2026</div>
			{bar(330, 1 - 0.3 * grow, C.blue)}
			<div style={{position: 'absolute', left: left + width * 0.7 + 20, top: 352, fontSize: 48, fontWeight: 700, color: C.blue, opacity: grow}}>−30%</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 495, textAlign: 'center', fontSize: 28, color: C.muted}}>FEDERAL FOOD BY WEIGHT</div>
			<Dotted top={555} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 580, textAlign: 'center', fontSize: 30, fontWeight: 600, lineHeight: 1.3}}>TEFAP = THE EMERGENCY FOOD<br />ASSISTANCE PROGRAM</div>
		</Receipt>
	);
};

// Cards 44-45: two local reports of donations down (KOLD 2026-11-13; KWCH 2026-11-12)
export const Donations: React.FC<{rows: number[]}> = ({rows}) => (
	<Receipt>
		<Title text="Private Donations" />
		<Dotted top={96} />
		{[
			['SOUTHERN ARIZONA', 'FOOD BANK', '▼15%'],
			['KANSAS', 'FOOD BANK', '▼20%'],
		].map(([a, b, v], i) => (
			<div key={a} style={{opacity: rows[i] ?? 0}}>
				<Row top={170 + i * 230} left={a} right={v} rightColor={C.blue} size={46} />
				<Row top={228 + i * 230} left={b} size={36} />
			</div>
		))}
		<div style={{position: 'absolute', left: 0, right: 0, top: PH - 70, textAlign: 'center', fontSize: 26, color: C.muted}}>DONATIONS, NOV 2026 VS. 2025</div>
	</Receipt>
);

// Card 46: NBC News survey, Oct 2026: nearly three-quarters of 48 responding food banks (of 90 surveyed) saw more visitors
export const Demand: React.FC<{o: number}> = ({o}) => (
	<Receipt>
		<Title text="Demand for Food Banks Up" />
		<div style={{position: 'absolute', left: 0, right: 0, top: 190, textAlign: 'center', fontSize: 190, fontWeight: 700, color: C.red, opacity: o}}>≈75%</div>
		<div style={{position: 'absolute', left: 120, right: 120, top: 440, display: 'flex', gap: 16, opacity: o}}>
			{[0, 1, 2, 3].map((i) => (
				<div key={i} style={{flex: 1, height: 90, borderRadius: 6, background: i < 3 ? C.red : C.track}} />
			))}
		</div>
		<div style={{position: 'absolute', left: 40, right: 40, top: 560, textAlign: 'center', fontSize: 32, fontWeight: 600, lineHeight: 1.3}}>REPORTED MORE VISITORS THIS YEAR</div>
		<div style={{position: 'absolute', left: 40, right: 40, top: 630, textAlign: 'center', fontSize: 26, color: C.muted}}>48 OF THE 90 LARGEST FOOD BANKS RESPONDED</div>
	</Receipt>
);

// Cards 47-48: a receipt's "paid with" lines switching from cash to borrowing
export const PaidWith: React.FC<{strike: number; credit: number; bnpl: number}> = ({strike, credit, bnpl}) => (
	<Receipt>
		<Title text="Receipt" />
		<Dotted top={96} />
		<Row top={130} left="TURKEY DINNER (10)" right="$58.63" size={36} />
		<Dotted top={200} />
		<div style={{position: 'absolute', left: 44, top: 232, fontSize: 30, color: C.muted, fontWeight: 600}}>PAID WITH</div>
		<div style={{position: 'absolute', left: 44, top: 320, fontSize: 52, fontWeight: 700}}>
			CASH
			<div style={{position: 'absolute', left: -6, top: 34, height: 7, width: 175 * strike, background: C.red}} />
		</div>
		<div style={{position: 'absolute', left: 44, top: 430, fontSize: 52, fontWeight: 700, color: C.red, opacity: credit}}>CREDIT CARD</div>
		<div style={{position: 'absolute', left: 44, top: 540, fontSize: 52, fontWeight: 700, color: C.red, opacity: bnpl}}>BUY NOW, PAY LATER</div>
	</Receipt>
);

// Card 49: household utility debt (NEADA): $16.1B Aug 2022 -> $23-25B 2026 (NEADA's own figures disagree)
export const UtilityDebt: React.FC<{grow: number}> = ({grow}) => {
	const left = 60, width = PW - 120, max = 25;
	return (
		<Receipt>
			<Title text="Utility Debt Up" />
			<div style={{position: 'absolute', left, top: 190, fontSize: 34, fontWeight: 700}}>AUG 2022</div>
			<div style={{position: 'absolute', left, top: 240, width: width * (16.1 / max), height: 120, background: C.muted, borderRadius: 6}} />
			<div style={{position: 'absolute', left: left + width * (16.1 / max) + 16, top: 270, fontSize: 48, fontWeight: 700}}>$16.1B</div>
			<div style={{position: 'absolute', left, top: 410, fontSize: 34, fontWeight: 700}}>2026</div>
			<div style={{position: 'absolute', left, top: 460, width: width * (23 / max) * grow, height: 120, background: C.red, borderRadius: '6px 0 0 6px'}} />
			<div style={{position: 'absolute', left: left + width * (23 / max) * grow, top: 460, width: width * (2 / max) * grow, height: 120, background: C.red, opacity: 0.4, borderRadius: '0 6px 6px 0'}} />
			<div style={{position: 'absolute', left, width, top: 600, textAlign: 'right', fontSize: 50, fontWeight: 700, color: C.red, opacity: grow}}>$23–25B</div>
		</Receipt>
	);
};

// Cards 54-61: factors list. Arrow = direction; color = good (green) or bad (red) news (David, 2026-11-24).
export type Factor = {label: string; up: boolean; good: boolean; value?: string};
export const FACTORS: Factor[] = [
	{label: 'FOOD INSECURITY (USDA, TO 2024)', up: true, good: false},
	{label: 'MUST-PAY BILLS', up: true, good: false},
	{label: 'JOBLESS & UNDEREMPLOYED', up: true, good: false},
	{label: 'SNAP PARTICIPANTS', up: false, good: false},
	{label: 'GOV’T FOOD TO FOOD BANKS', up: false, good: false},
	{label: 'FOOD BANK DEMAND', up: true, good: false},
	{label: 'DEBT & LATE PAYMENTS', up: true, good: false},
	{label: 'BNPL FOR GROCERIES', up: true, good: false},
	{label: 'CENSUS HUNGER MEASURE', up: false, good: true, value: '11.5% → 6.7%'},
	{label: 'OFFICIAL POVERTY', up: false, good: true, value: '10.2%, −0.5 PTS'},
	{label: 'PURDUE SURVEY', up: true, good: false, value: '12.5% → 14.2%'},
];
export const Factors: React.FC<{rows: number[]}> = ({rows}) => (
	<Receipt>
		<Title text="Food Insecurity Factors" />
		<div style={{position: 'absolute', left: 44, right: 44, top: 84, display: 'flex', justifyContent: 'center', gap: 28, fontSize: 24, fontWeight: 600, color: C.muted}}>
			<span><span style={{color: C.red}}>■</span> BAD NEWS</span>
			<span><span style={{color: C.green}}>■</span> GOOD NEWS</span>
		</div>
		<Dotted top={122} />
		{FACTORS.map((f, i) => {
			const o = rows[i] ?? 0;
			const col = f.good ? C.green : C.red;
			return (
				<div key={f.label} style={{position: 'absolute', left: 36, right: 36, top: 140 + i * 52, height: 50, display: 'flex', alignItems: 'center', gap: 12, fontSize: 29, fontWeight: 600, opacity: o, transform: `translateX(${(1 - o) * -16}px)`}}>
					<span style={{color: col, fontSize: 30, width: 30, textAlign: 'center'}}>{f.up ? '▲' : '▼'}</span>
					<span style={{flex: 1, whiteSpace: 'nowrap'}}>{f.label}</span>
					{f.value && <span style={{color: col, fontWeight: 700, whiteSpace: 'nowrap'}}>{f.value}</span>}
				</div>
			);
		})}
	</Receipt>
);
