// Pieces shared by Amara's charts. Colors: AI-exposed / office jobs red, everything else gray,
// the same on every card. Text is level (setScrawlTilt(0) in ../sharpie).
import type {Options} from 'roughjs/bin/core';
import {INK, ZONES, ink} from '../sharpie';

// rough.js ignores strokeLineDash when its paths are rendered by Ink, so dashed lines are built
// from short segments. Returns one drawable per dash.
export const dashedLine = (x1: number, y1: number, x2: number, y2: number, dash: number, gap: number, o: Options) => {
	const len = Math.hypot(x2 - x1, y2 - y1);
	const ux = (x2 - x1) / len;
	const uy = (y2 - y1) / len;
	const out = [];
	for (let s = 0, i = 0; s < len; s += dash + gap, i++) {
		const e = Math.min(len, s + dash);
		out.push(ink.line(x1 + ux * s, y1 + uy * s, x1 + ux * e, y1 + uy * e, {...o, seed: (o.seed ?? 1) + i}));
	}
	return out;
};

export const HOT = INK.red; // AI-exposed / fast lane / office & admin
export const COOL = INK.blue; // slow lane
export const OTHER = INK.gray; // everything else / removed
export const CX = (ZONES.chart.left + ZONES.chart.right) / 2;

// "1.8M", "870K", "-284K": the rounding the script uses.
// `stepK` rounds thousands (10 = nearest 10K, as in "about 870K").
export const fmtJobs = (n: number, signed = false, stepK = 1) => {
	const a = Math.abs(n);
	const s = a >= 1e6 ? `${(a / 1e6).toFixed(1)}M` : `${Math.round(a / 1e3 / stepK) * stepK}K`;
	return signed ? `${n < 0 ? '−' : '+'}${s}` : s;
};
