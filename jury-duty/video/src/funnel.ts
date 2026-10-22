// The jury funnel per 1,000 summoned. Source: docs/funnel-ranges.md ("Wisconsin spine", revised
// 2026-10-19): median of Milwaukee 2024, Racine 2015-25 and Waukesha 2025; called off is the
// remainder (eligible - reported); the sworn split by days on trial is estimated from Massachusetts
// FY2015 days served and its 2025 share sworn. Labels are data labels only; titles and callouts
// come from the storyboard's On-Screen Text column.
export type Kind = 'stay' | 'out' | 'days';
export type Node = {value: number; label: string; kind: Kind};
export type Step = {card: number; parent: Node; children: Node[]};

export const PATH: Node[] = [
	{value: 1000, label: 'summoned', kind: 'stay'},
	{value: 449, label: 'eligible', kind: 'stay'},
	{value: 247, label: 'reported', kind: 'stay'},
	{value: 155, label: 'sent to a courtroom', kind: 'stay'},
	{value: 48, label: 'sworn', kind: 'stay'},
];

export const STEPS: Step[] = [
	{card: 5, parent: PATH[0], children: [PATH[1], {value: 551, label: 'postponed, no reply or excused', kind: 'out'}]},
	{card: 6, parent: PATH[1], children: [PATH[2], {value: 202, label: 'called off', kind: 'out'}]},
	{card: 7, parent: PATH[2], children: [PATH[3], {value: 92, label: 'sent home', kind: 'out'}]},
	{card: 8, parent: PATH[3], children: [PATH[4], {value: 107, label: 'not chosen', kind: 'out'}]},
	{
		card: 9,
		parent: PATH[4],
		children: [
			{value: 8, label: '1 day', kind: 'days'},
			{value: 19, label: '2 days', kind: 'days'},
			{value: 7, label: '3 days', kind: 'days'},
			{value: 14, label: '4+ days', kind: 'days'},
		],
	},
];

// Each split must add up; a typo here would silently break the Sankey.
for (const s of STEPS) {
	const sum = s.children.reduce((a, c) => a + c.value, 0);
	if (sum !== s.parent.value) throw new Error(`card ${s.card}: children sum ${sum} != ${s.parent.value}`);
}

export const SOURCE = [
	'Per 1,000 summoned · Milwaukee, Racine & Waukesha (WI), 2015–2025',
	'Days on trial: estimated from Massachusetts FY2015',
];
