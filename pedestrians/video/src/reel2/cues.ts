// Reel 2 (DDD16, Script v3) card start times from David's storyboard Sheet, Start column, read 2026-11-18.
// The Sheet writes SS:FF under a minute (David: no minutes means 0) and M:SS:FF after (30 fps). Cards 37-42
// don't exist, so card 36 runs to card 43. Card 49 marks the end of the video.
const START: Record<number, string> = {
	1: '0:00:00', 2: '01:28', 3: '06:10', 4: '09:12', 5: '14:22', 6: '18:08', 7: '23:11', 8: '30:25', 9: '31:15',
	10: '36:06', 11: '37:20', 12: '42:06', 13: '47:22', 14: '49:01', 15: '53:25', 16: '55:15', 17: '1:00:21',
	18: '1:01:15', 19: '1:07:01', 20: '1:14:14', 21: '1:21:08', 22: '1:22:25', 23: '1:27:03', 24: '1:30:08',
	25: '1:36:07', 26: '1:38:08', 27: '1:43:23', 28: '1:45:02', 29: '1:46:14', 30: '1:49:28', 31: '1:50:28',
	32: '1:55:16', 33: '1:58:04', 34: '2:02:21', 35: '2:04:20', 36: '2:12:07', 43: '2:18:20', 44: '2:20:03',
	45: '2:27:29', 46: '2:29:13', 47: '2:36:20', 48: '2:37:17', 49: '2:40:14',
};

const toFrames = (tc: string) => {
	const p = tc.split(':').map(Number);
	const [mm, ss, ff] = p.length === 3 ? p : [0, ...p];
	return (mm * 60 + ss) * 30 + ff;
};

export const CARDS = Object.keys(START).map(Number).sort((a, b) => a - b);
export const S = (card: number) => toFrames(START[card]);
export const END = (card: number) => S(CARDS[CARDS.indexOf(card) + 1]);
export const TOTAL = S(49);

// Character column. In Reel 2, A wears the orange cap and B the glasses; Reel 3's stills are named the other
// way round (public/reel3/speaker-a.png = glasses), so the preview swaps them.
const B_CARDS = [1, 3, 6, 8, 10, 13, 15, 17, 19, 21, 23, 25, 28, 30, 32, 34, 43, 45, 47];
export const STILL = (card: number): 'a' | 'b' => (B_CARDS.includes(card) ? 'a' : 'b');

// Cards with a graphic (the plan: docs/reel2-visual-plan.md). Empty Video cells (13, 19, 47-48) and
// [DO NOT RENDER] cards (18, 20-21, 27-29) get no clip.
export const GRAPHIC_CARDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 22, 23, 24, 25, 26, 30, 31, 32, 33, 34, 35, 36, 43, 44, 45, 46];
