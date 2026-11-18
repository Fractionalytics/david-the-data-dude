// Reel 3 (DDD15, Script v6) card start times from David's storyboard Sheet, Start column, read 2026-11-17.
// The Sheet writes SS:FF under a minute and MM:SS:FF after (30 fps). Cards 20-21 were cut, so a card runs
// to the next card that exists. Card 52 marks the end of the video.
const START: Record<number, string> = {
	1: '0:00:00', 2: '02:15', 3: '03:08', 4: '09:09', 5: '13:08', 6: '15:19', 7: '16:19', 8: '20:27', 9: '25:19',
	10: '27:12', 11: '31:15', 12: '34:24', 13: '35:27', 14: '38:08', 15: '39:01', 16: '43:22', 17: '47:23',
	18: '49:25', 19: '51:12', 22: '55:26', 23: '59:13', 24: '01:04:09', 25: '01:09:14', 26: '01:14:16',
	27: '01:23:05', 28: '01:25:02', 29: '01:27:16', 30: '01:28:14', 31: '01:38:04', 32: '01:39:04', 33: '01:44:15',
	34: '01:45:29', 35: '01:51:15', 36: '01:52:23', 37: '01:54:19', 38: '02:02:11', 39: '02:03:19', 40: '02:04:10',
	41: '02:09:22', 42: '02:13:17', 43: '02:16:19', 44: '02:18:11', 45: '02:25:09', 46: '02:26:13', 47: '02:35:15',
	48: '02:36:28', 49: '02:43:14', 50: '02:49:11', 51: '02:50:13', 52: '02:53:24',
};

const toFrames = (tc: string) => {
	const p = tc.split(':').map(Number);
	const [mm, ss, ff] = p.length === 3 ? p : [0, ...p];
	return (mm * 60 + ss) * 30 + ff;
};

export const CARDS = Object.keys(START).map(Number).sort((a, b) => a - b);
export const S = (card: number) => toFrames(START[card]);
export const END = (card: number) => S(CARDS[CARDS.indexOf(card) + 1]);
export const TOTAL = S(52);

// Character column: A = glasses, B = cap.
const B_CARDS = [1, 3, 5, 7, 9, 12, 14, 17, 22, 24, 27, 29, 31, 33, 35, 38, 43, 45, 47, 50];
export const SPEAKER = (card: number): 'a' | 'b' => (B_CARDS.includes(card) ? 'b' : 'a');

// Cards with a graphic (the rest are talking head, or David's own on-screen emojis on card 11).
export const GRAPHIC_CARDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 16, 17, 18, 19, 22, 23, 24, 25, 26, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
	41, 42, 44, 46, 48, 49];

// In-card cues that are ESTIMATES from where words fall in the card (no word-level timecodes).
// Card 46: "truck sizes" ~ word 3 of 22, "smartphones" ~ word 5, "Being hit got deadlier" ~ word 6.
const at = (card: number, share: number) => S(card) + Math.round((END(card) - S(card)) * share);
export const EST = {
	trucks: at(46, 0.12),
	phones: at(46, 0.22),
	deadlier: at(46, 0.3),
};
