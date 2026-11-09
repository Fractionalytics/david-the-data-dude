// Card start times from David's storyboard Sheet (Start column, MM:SS:FF at 30 fps), read 2026-11-09.
// Card 59 is the end of the video. A card runs from its start to the next card's start.
const START: Record<number, string> = {
	1: '00:00:00', 2: '00:01:13', 3: '00:05:10', 4: '00:09:00', 5: '00:12:19', 6: '00:17:13', 7: '00:23:06',
	8: '00:26:29', 9: '00:30:11', 10: '00:33:20', 11: '00:40:07', 12: '00:41:25', 13: '00:43:05', 14: '00:45:13',
	15: '00:50:09', 16: '00:52:08', 17: '00:55:08', 18: '00:56:15', 19: '01:00:20', 20: '01:02:00', 21: '01:04:16',
	22: '01:06:29', 23: '01:09:10', 24: '01:10:12', 25: '01:12:19', 26: '01:17:13', 27: '01:20:05', 28: '01:22:06',
	29: '01:23:15', 30: '01:27:12', 31: '01:32:23', 32: '01:33:18', 33: '01:35:00', 34: '01:36:01', 35: '01:42:21',
	36: '01:47:27', 37: '01:49:22', 38: '01:52:00', 39: '01:54:15', 40: '01:55:03', 41: '01:58:09', 42: '01:59:02',
	43: '02:02:24', 44: '02:03:16', 45: '02:05:14', 46: '02:06:15', 47: '02:12:24', 48: '02:14:27', 49: '02:20:28',
	50: '02:21:28', 51: '02:23:04', 52: '02:27:00', 53: '02:27:17', 54: '02:32:06', 55: '02:34:29', 56: '02:37:01',
	57: '02:44:19', 58: '02:45:18', 59: '02:48:00',
};

const toFrames = (tc: string) => {
	const [mm, ss, ff] = tc.split(':').map(Number);
	return (mm * 60 + ss) * 30 + ff;
};

export const S = (card: number) => toFrames(START[card]);
export const END = (card: number) => S(card + 1);

// Cards that get a graphics clip (the rest are talking head or David's b-roll).
export const GRAPHIC_CARDS = [1, 2, 3, 4, 5, 6, 8, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 29, 30, 31, 32, 33,
	34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 46, 48, 49, 50, 51, 52, 53, 54, 56];

export const SPEAKER: Record<number, 'a' | 'b'> = {
	1: 'b', 2: 'a', 3: 'b', 4: 'a', 5: 'b', 6: 'a', 8: 'a', 15: 'b', 16: 'a', 17: 'b', 18: 'a', 19: 'a', 20: 'a', 21: 'a',
	22: 'a', 23: 'a', 24: 'a', 25: 'a', 26: 'b', 29: 'a', 30: 'a', 31: 'b', 32: 'a', 33: 'b', 34: 'a', 35: 'b', 36: 'a',
	37: 'b', 38: 'a', 39: 'b', 52: 'b', 53: 'a', 54: 'a', 40: 'a', 41: 'b', 42: 'a', 43: 'b', 46: 'a', 48: 'a', 49: 'b', 50: 'a', 51: 'a', 56: 'a',
};

// In-card cues that are ESTIMATES from where the phrase falls in the script (no word-level timecodes):
// card 6 "outside of NYC" ~ 55% into the card; card 46 "sleeplessness" / "risk-taking" / "crash effect"
// ~ words 4, 5 and 8 of 17 over the card's first sentence.
export const EST = {
	nycLights: S(6) + Math.round((END(6) - S(6)) * 0.55),
	sleepless: S(46) + 30,
	risk: S(46) + 48,
	crash: S(46) + 78,
};
