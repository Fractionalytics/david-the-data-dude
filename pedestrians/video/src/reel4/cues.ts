// Reel 4 (DDD17 4 Waves, tab Script v2) card start times from David's storyboard Sheet, Start column, read
// 2026-11-21. SS:FF under a minute, M:SS:FF after (30 fps). Card 39 marks the end of the video.
const START: Record<number, string> = {
	1: '0:00:00', 2: '05:07', 3: '07:02', 4: '09:25', 5: '15:12', 6: '19:27', 7: '23:25', 8: '27:14', 9: '34:08',
	10: '42:07', 11: '47:21', 12: '49:07', 13: '54:04', 14: '59:28', 15: '1:04:29', 16: '1:08:23', 17: '1:10:24',
	18: '1:15:22', 19: '1:20:28', 20: '1:24:19', 21: '1:31:01', 22: '1:35:22', 23: '1:38:23', 24: '1:43:29',
	25: '1:49:17', 26: '1:52:26', 27: '1:56:19', 28: '2:02:17', 29: '2:06:15', 30: '2:10:04', 31: '2:17:04',
	32: '2:19:27', 33: '2:26:06', 34: '2:30:25', 35: '2:36:06', 36: '2:43:05', 37: '2:47:19', 38: '2:54:18',
	39: '2:58:28',
};

const toFrames = (tc: string) => {
	const p = tc.split(':').map(Number);
	const [mm, ss, ff] = p.length === 3 ? p : [0, ...p];
	return (mm * 60 + ss) * 30 + ff;
};

export const CARDS = Object.keys(START).map(Number).sort((a, b) => a - b);
export const S = (card: number) => toFrames(START[card]);
export const END = (card: number) => S(CARDS[CARDS.indexOf(card) + 1]);
export const TOTAL = S(39);
// Every card from 1 to 38 has a graphic (the waves, or the OxyContin slopegraph on cards 4-6).
export const GRAPHIC_CARDS = CARDS.filter((c) => c < 39);
