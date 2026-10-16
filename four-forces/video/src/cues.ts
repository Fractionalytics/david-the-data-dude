// Timing for every composition. One composition per storyboard card (David: "Do not make one
// monolithic remotion video"), each as long as its card: from its Start timecode to the next
// card's. Timecodes are David's (Sheet "Start" column, MM:SS:FF at 30 fps, 2026-10-16).
// Inside a card, cues David gave are exact; the rest are ESTIMATES from where the phrase falls in
// the script (frames per word = card length / card words), marked "est."
export const tc = (s: string) => {
	const [mm, ss, ff] = s.split(':').map(Number);
	return (mm * 60 + ss) * 30 + ff;
};

const START = {
	c07: tc('0:28:03'),
	c08: tc('0:51:19'),
	c09: tc('0:59:24'),
	c10: tc('1:08:25'),
	c11: tc('1:16:03'),
	c13: tc('1:33:27'),
	c14: tc('1:36:08'),
	c15: tc('2:05:00'),
	c16: tc('2:14:14'),
	c17: tc('2:23:28'),
	c19: tc('2:38:11'),
	c20: tc('2:49:15'),
};
const len = (a: number, b: number) => b - a;

export const CUE = {
	// Card 7 (706 f, 61 words): ceiling first (David), bar lands on "1.8M" (word 31, est. f 360).
	c07: {dur: len(START.c07, START.c08), ceiling: 0, bar: 330, barFrames: 30},
	// Card 8 (245 f): the pre-2022 decline drops out on "already in decline" (est. f 70).
	c08: {dur: len(START.c08, START.c09), bar: 50, barFrames: 30},
	// Card 9 (271 f): loan processing drops out on "loan processing" (est. f 60).
	c09: {dur: len(START.c09, START.c10), bar: 35, barFrames: 30},
	// Card 10 (218 f): the remaining bar grows and is labelled on "870K" (est. f 55).
	c10: {dur: len(START.c10, START.c11), bar: 25, barFrames: 30},
	// Card 11 (534 f, 45 words): customer service lands on "customer service" (word 10, est. f 120);
	// the other three follow.
	c11: {dur: len(START.c11, START.c13), rows: [95, 140, 165, 190]},
	// Card 13 (71 f): the title.
	c13: {dur: len(START.c13, START.c14)},
	// Card 14: each force is fully on screen at David's timecode (Video column).
	c14: {dur: len(START.c14, START.c15), items: ['1:41:25', '1:47:13', '1:53:18', '1:58:17'].map((t) => tc(t) - START.c14)},
	// Card 15 (284 f, 26 words): list moves into the table; FAST header on "fast lane" (word 16,
	// est. f 175), SLOW on "slow lane" (word 22, est. f 240).
	c15: {dur: len(START.c15, START.c16), move: 0, fast: 165, slow: 230},
	// Card 16 (284 f, 33 words): line chart, then the table on "The four forces are weak" (word 23, est. f 195).
	c16a: {dur: 195},
	c16b: {dur: len(START.c16, START.c17) - 195},
	// Card 17 (433 f, 35 words): radiology grid until "law" (word 14, est. f 175); paralegals until
	// "That's office work too" (word 25, est. f 310), bar landing on "14%" (word 22, est. f 275);
	// then the table with SLOW meters.
	c17a: {dur: 175},
	c17b: {dur: 135, paralegals: 100},
	c17c: {dur: len(START.c17, START.c19) - 175 - 135},
	// Card 19 (334 f, 40 words): "-31%" lands on "31%" (word 17, est. f 142).
	c19: {dur: len(START.c19, START.c20), pct: 130},
};
