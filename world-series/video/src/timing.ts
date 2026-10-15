// Cues for the World Series of Last Names, from David's storyboard (Start Time and Video columns).
// David's timecodes are M:SS:FF at 30 fps: frame = (m * 60 + s) * 30 + ff.
//
// Every cue below is David's (Ohtani's 1:08:29 and card 11's rows confirmed 2026-10-14).
export const tc = (m: number, s: number, f: number) => (m * 60 + s) * 30 + f;

export const CARD = {
	c1: tc(0, 0, 0), // hook: the sorting machine starts
	c2: tc(0, 4, 13),
	c3: tc(0, 8, 16),
	c4: tc(0, 15, 7),
	c5: tc(0, 20, 9), // The Jobs
	c6: tc(0, 33, 0), // The Sons of Somebody
	c7: tc(0, 43, 16), // The Nicknames
	c8: tc(0, 59, 9), // The Places
	c9: tc(1, 13, 3), // pipes to positions
	c10: tc(1, 19, 19), // WAR sorts players into positions
	c11: tc(1, 32, 8), // ranking
	c12: tc(1, 49, 14), // close
	end: tc(1, 55, 3),
};

export const TOTAL_FRAMES = CARD.end;

// How long a team logo stays zoomed out of its bin (Sheet: 6 seconds).
export const ZOOM_FRAMES = 6 * 30;

// Words on screen come word for word from the Sheet's Video column (David's on-screen text).
export type Def = {at: number; name: string; meaning: string};
export type TeamCues = {key: 'jobs' | 'sons' | 'nicknames' | 'places'; zoomAt: number; examples: Def[]; players: Def[]; clearAt: number};

export const TEAM_CUES: TeamCues[] = [
	{
		key: 'jobs',
		zoomAt: CARD.c5,
		examples: [
			{at: tc(0, 23, 26), name: 'Miller', meaning: 'grain grinder'},
			{at: tc(0, 25, 6), name: 'Herrera', meaning: 'ironworker'},
		],
		players: [
			{at: tc(0, 28, 12), name: 'Schlittler', meaning: 'sled maker'},
			{at: tc(0, 29, 19), name: 'Wheeler', meaning: 'wheel maker'},
			{at: tc(0, 30, 28), name: 'Pages', meaning: 'agricultural laborer'},
		],
		clearAt: CARD.c6,
	},
	{
		key: 'sons',
		zoomAt: CARD.c6,
		examples: [
			{at: tc(0, 36, 7), name: 'Wilson', meaning: 'son of William'},
			{at: tc(0, 37, 17), name: 'Rodriguez', meaning: 'son of Rodrigo'},
		],
		players: [
			{at: tc(0, 39, 17), name: 'Sánchez', meaning: 'son of Sancho'},
			{at: tc(0, 40, 25), name: 'McGonigle', meaning: 'son of Congal'},
			{at: tc(0, 41, 27), name: 'Rasmussen', meaning: 'son of Rasmus'},
		],
		clearAt: CARD.c7,
	},
	{
		key: 'nicknames',
		zoomAt: CARD.c7,
		examples: [
			{at: tc(0, 47, 25), name: 'Brown', meaning: 'brown'},
			{at: tc(0, 48, 1), name: 'Flores', meaning: 'flowers'},
		],
		players: [
			{at: tc(0, 50, 19), name: 'Crow-Armstrong', meaning: 'bird-strong'},
			{at: tc(0, 55, 15), name: 'Witt', meaning: 'white'},
			{at: tc(0, 57, 7), name: 'Moreno', meaning: 'dark'},
		],
		clearAt: CARD.c8,
	},
	{
		key: 'places',
		zoomAt: CARD.c8,
		examples: [
			{at: tc(1, 3, 23), name: 'Hill', meaning: 'hill'},
			{at: tc(1, 4, 2), name: 'Torres', meaning: 'towers'},
		],
		players: [
			{at: tc(1, 8, 29), name: 'Ohtani', meaning: 'large valley'},
			{at: tc(1, 10, 4), name: 'Messick', meaning: 'a place in France'},
			{at: tc(1, 11, 12), name: 'Peña', meaning: 'boulder/cliff'},
		],
		clearAt: CARD.c9,
	},
];

// Card 11 ranking rows, built from the bottom (Sheet cues).
export const RANK_AT = {
	jobs: tc(1, 35, 8),
	sons: tc(1, 37, 19),
	nicknames: tc(1, 40, 1),
	places: tc(1, 43, 23),
};
