// The World Series of Last Names: one full-screen composition for the whole Reel (cards 1–12).
// Deliberate rule-break (David, 2026-10-14): uses the whole frame, not just ZONES.chart; David's
// face moves around it in the edit. Everything stays inside the side margins and below the
// keep-out band. All words are in Graduate, the collegiate face from the team logos.
import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {loadFont as loadGraduate} from '@remotion/google-fonts/Graduate';
import {loadFont as loadYellowtail} from '@remotion/google-fonts/Yellowtail';
import {loadFont as loadRye} from '@remotion/google-fonts/Rye';
import {loadFont as loadAlfa} from '@remotion/google-fonts/AlfaSlabOne';
import {SIDE_MARGIN, VIDEO, ZoneGuide} from '@kit/zones';
import data from './data/video.json';
import {CARD, RANK_AT, TEAM_CUES, ZOOM_FRAMES, type Def} from './timing';

const {fontFamily: GRADUATE} = loadGraduate();
loadYellowtail();
loadRye();
loadAlfa();

const BG = '#F3EBD8';
const INK = '#20262B';
const GRAY_IN = '#8F8F8F'; // unsorted players waiting in the hopper
const OTHER = '#B8AE9C'; // everyone outside the four teams

type TeamKey = 'jobs' | 'sons' | 'nicknames' | 'places';
const TEAMS = data.teams as {key: TeamKey; name: string; balls: number; color: string; rosterWar: number; roster: Record<string, {name: string; war: number}[]>}[];
const LOGOS = data.logos as Record<TeamKey, string>;

// ---------- layout (px, 1080×1920) ----------
const L = SIDE_MARGIN; // 120
const R = VIDEO.width - SIDE_MARGIN; // 960
const HOPPER = {top: 250, bottom: 440, topHalf: 240, bottomHalf: 50};
const MACHINE = {left: 380, right: 700, top: 440, bottom: 580};
const MANIFOLD_Y = 615;
const BIN = {top: 655, bottom: 870, w: 152};
const BIN_X = [0, 1, 2, 3, 4].map((i) => L + 84 + i * 168); // centers: jobs, sons, nicknames, places, other
const BADGE = {y: 920, size: 84};
const BALL_R = 6;
const STEP = 13;
const PER_ROW = Math.floor((BIN.w - 10) / STEP);

// Lower stage (under the machine): zoomed logos, then name cards.
const STAGE = {cx: 540, cy: 1345, size: 640};

// ---------- the balls: 1 ball = 5 players, real proportions ----------
const rng = (seed: number) => () => {
	seed |= 0;
	seed = (seed + 0x6d2b79f5) | 0;
	let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
	t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
	return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

type Ball = {bin: number; color: string; k: number; birth: number; pile: {x: number; y: number}};
const EMIT_START = 15;
const EMIT_END = CARD.c10 + 250; // the machine keeps processing through card 10 (Sheet, card 9)
const BALLS: Ball[] = (() => {
	const r = rng(2026);
	const bins: number[] = [];
	TEAMS.forEach((t, i) => {
		for (let j = 0; j < t.balls; j++) bins.push(i);
	});
	for (let j = 0; j < data.other.balls; j++) bins.push(4);
	for (let i = bins.length - 1; i > 0; i--) {
		const j = Math.floor(r() * (i + 1));
		[bins[i], bins[j]] = [bins[j], bins[i]];
	}
	// Pile slots in the hopper, bottom row first; the top of the pile leaves first.
	const slots: {x: number; y: number}[] = [];
	for (let row = 0; slots.length < bins.length; row++) {
		const y = HOPPER.bottom - 12 - row * (STEP - 1);
		const half = HOPPER.bottomHalf + ((HOPPER.bottom - y) / (HOPPER.bottom - HOPPER.top)) * (HOPPER.topHalf - HOPPER.bottomHalf) - 10;
		const n = Math.max(1, Math.floor((2 * half) / STEP));
		for (let c = 0; c < n && slots.length < bins.length; c++) slots.push({x: 540 - ((n - 1) * STEP) / 2 + c * STEP, y});
	}
	const counts = [0, 0, 0, 0, 0];
	const n = bins.length;
	return bins.map((bin, i) => ({
		bin,
		color: bin < 4 ? TEAMS[bin].color : OTHER,
		k: counts[bin]++,
		birth: EMIT_START + Math.round((i / (n - 1)) * (EMIT_END - EMIT_START)),
		pile: slots[n - 1 - i],
	}));
})();

const slotOf = (bin: number, k: number) => {
	const row = Math.floor(k / PER_ROW);
	const col = k % PER_ROW;
	const left = BIN_X[bin] - BIN.w / 2 + 5 + BALL_R + (BIN.w - 10 - PER_ROW * STEP) / 2;
	return {x: left + col * STEP, y: BIN.bottom - 6 - BALL_R - row * STEP};
};

// Walk a polyline at fraction t (0..1) of its length.
const along = (pts: {x: number; y: number}[], t: number) => {
	const segs = pts.slice(1).map((p, i) => Math.hypot(p.x - pts[i].x, p.y - pts[i].y));
	let d = Math.min(1, Math.max(0, t)) * segs.reduce((a, b) => a + b, 0);
	for (let i = 0; i < segs.length; i++) {
		if (d <= segs[i] || i === segs.length - 1) {
			const u = segs[i] ? Math.min(1, d / segs[i]) : 1;
			return {x: pts[i].x + (pts[i + 1].x - pts[i].x) * u, y: pts[i].y + (pts[i + 1].y - pts[i].y) * u};
		}
		d -= segs[i];
	}
	return pts[pts.length - 1];
};

const FALL = 16; // pile → throat
const INSIDE = 14; // hidden in the machine
const OUT = 34; // nozzle → bin slot

const Balls: React.FC<{frame: number}> = ({frame}) => (
	<g>
		{BALLS.map((b, i) => {
			const a = frame - b.birth;
			const slot = slotOf(b.bin, b.k);
			let p = b.pile;
			let fill = GRAY_IN;
			if (a >= 0 && a < FALL) p = along([b.pile, {x: 540, y: HOPPER.bottom}], Easing.in(Easing.quad)(a / FALL));
			else if (a >= FALL && a < FALL + INSIDE) return null;
			else if (a >= FALL + INSIDE) {
				fill = b.color;
				const t = (a - FALL - INSIDE) / OUT;
				p = along([{x: 540, y: MACHINE.bottom}, {x: 540, y: MANIFOLD_Y}, {x: BIN_X[b.bin], y: MANIFOLD_Y}, {x: BIN_X[b.bin], y: BIN.top}, slot], t);
			}
			const stroke = b.bin === 0 && a >= FALL + INSIDE ? '#5c4700' : 'rgba(0,0,0,0.35)';
			return <circle key={i} cx={p.x} cy={p.y} r={BALL_R} fill={fill} stroke={stroke} strokeWidth={1.2} />;
		})}
	</g>
);

// ---------- the machine ----------
const Gear: React.FC<{x: number; y: number; r: number; angle: number}> = ({x, y, r, angle}) => (
	<g transform={`translate(${x} ${y}) rotate(${angle})`}>
		{Array.from({length: 8}, (_, i) => (
			<rect key={i} x={-r * 0.18} y={-r * 1.25} width={r * 0.36} height={r * 0.5} fill="#C9C1AE" transform={`rotate(${i * 45})`} />
		))}
		<circle r={r} fill="#C9C1AE" />
		<circle r={r * 0.38} fill={INK} />
	</g>
);

const Machine: React.FC<{frame: number}> = ({frame}) => {
	const blink = Math.floor(frame / 8) % 2 === 0;
	return (
		<g>
			{/* hopper */}
			<path
				d={`M${540 - HOPPER.topHalf},${HOPPER.top} L${540 + HOPPER.topHalf},${HOPPER.top} L${540 + HOPPER.bottomHalf},${HOPPER.bottom} L${540 - HOPPER.bottomHalf},${HOPPER.bottom} Z`}
				fill="rgba(32,38,43,0.06)"
				stroke={INK}
				strokeWidth={6}
				strokeLinejoin="round"
			/>
			{/* pipes: nozzle → manifold → five bins */}
			<g fill="none" stroke="#9C9384" strokeWidth={20} strokeLinecap="round" strokeLinejoin="round" opacity={0.55}>
				<path d={`M540,${MACHINE.bottom} L540,${MANIFOLD_Y} M${BIN_X[0]},${MANIFOLD_Y} L${BIN_X[4]},${MANIFOLD_Y}`} />
				{BIN_X.map((x) => (
					<path key={x} d={`M${x},${MANIFOLD_Y} L${x},${BIN.top}`} />
				))}
			</g>
			{/* body */}
			<rect x={MACHINE.left} y={MACHINE.top} width={MACHINE.right - MACHINE.left} height={MACHINE.bottom - MACHINE.top} rx={22} fill={INK} />
			<Gear x={MACHINE.left + 42} y={MACHINE.top + 44} r={18} angle={frame * 6} />
			<Gear x={MACHINE.right - 42} y={MACHINE.top + 44} r={18} angle={-frame * 6} />
			{/* placeholder badges: swap for the real Claude and Jev logos when David supplies them */}
			<g fontFamily={GRADUATE} textAnchor="middle">
				<rect x={MACHINE.left + 40} y={MACHINE.top + 78} width={110} height={44} rx={10} fill="#D97757" />
				<text x={MACHINE.left + 95} y={MACHINE.top + 109} fontSize={24} fill="#fff">
					Claude
				</text>
				<rect x={MACHINE.right - 150} y={MACHINE.top + 78} width={110} height={44} rx={10} fill="#F3EBD8" />
				<text x={MACHINE.right - 95} y={MACHINE.top + 109} fontSize={24} fill={INK}>
					Jev
				</text>
			</g>
			{[0, 1, 2].map((i) => (
				<circle key={i} cx={510 + i * 30} cy={MACHINE.top + 30} r={7} fill={blink === (i % 2 === 0) ? '#F2B705' : '#4a5258'} />
			))}
			<rect x={520} y={MACHINE.bottom - 4} width={40} height={12} rx={4} fill={INK} />
		</g>
	);
};

const Bins: React.FC = () => (
	<g>
		{BIN_X.map((x, i) => (
			<path
				key={i}
				d={`M${x - BIN.w / 2},${BIN.top} L${x - BIN.w / 2},${BIN.bottom} Q${x - BIN.w / 2},${BIN.bottom + 6} ${x - BIN.w / 2 + 8},${BIN.bottom + 6} L${x + BIN.w / 2 - 8},${BIN.bottom + 6} Q${x + BIN.w / 2},${BIN.bottom + 6} ${x + BIN.w / 2},${BIN.bottom} L${x + BIN.w / 2},${BIN.top}`}
				fill="rgba(255,255,255,0.45)"
				stroke={INK}
				strokeWidth={5}
				strokeLinejoin="round"
			/>
		))}
		<text x={BIN_X[4]} y={BADGE.y + 12} textAnchor="middle" fontFamily={GRADUATE} fontSize={30} fill={INK}>
			OTHER
		</text>
	</g>
);

// ---------- logos ----------
const Logo: React.FC<{team: TeamKey; cx: number; cy: number; size: number; opacity?: number}> = ({team, cx, cy, size, opacity = 1}) => (
	<g transform={`translate(${cx - size / 2} ${cy - size / 2}) scale(${size / 600})`} opacity={opacity} dangerouslySetInnerHTML={{__html: LOGOS[team]}} />
);

// The badge under each bin; zooms to the lower stage when its team is named (6 s, Sheet cards 5–8).
const BinLogos: React.FC<{frame: number; fps: number}> = ({frame, fps}) => (
	<g>
		{TEAMS.map((t, i) => {
			const cue = TEAM_CUES.find((c) => c.key === t.key)!;
			const a = frame - cue.zoomAt;
			const out = spring({frame: a, fps, config: {damping: 16, stiffness: 120}, durationInFrames: 18});
			const back = spring({frame: a - (ZOOM_FRAMES - 18), fps, config: {damping: 18, stiffness: 140}, durationInFrames: 18});
			const z = a < 0 ? 0 : Math.max(0, out - back);
			const cx = interpolate(z, [0, 1], [BIN_X[i], STAGE.cx]);
			const cy = interpolate(z, [0, 1], [BADGE.y, STAGE.cy]);
			const size = interpolate(z, [0, 1], [BADGE.size, STAGE.size]);
			return <Logo key={t.key} team={t.key} cx={cx} cy={cy} size={size} />;
		})}
	</g>
);

// ---------- words ----------
const ExampleBanner: React.FC<{d: Def; y: number; frame: number; until: number}> = ({d, y, frame, until}) => {
	const a = frame - d.at;
	if (a < 0 || frame >= until) return null;
	const pop = Math.min(1, a / 8);
	const fade = interpolate(frame, [until - 8, until], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	return (
		<g opacity={pop * fade} transform={`translate(540 ${y}) scale(${0.85 + 0.15 * pop})`} fontFamily={GRADUATE} textAnchor="middle">
			<rect x={-400} y={-62} width={800} height={124} rx={18} fill={INK} opacity={0.9} />
			<text y={-8} fontSize={56} fill="#F3EBD8">
				{d.name} =
			</text>
			<text y={44} fontSize={42} fill="#F2B705">
				{d.meaning}
			</text>
		</g>
	);
};

const PlayerCard: React.FC<{d: Def; y: number; color: string; frame: number; until: number}> = ({d, y, color, frame, until}) => {
	const a = frame - d.at;
	if (a < 0 || frame >= until) return null;
	const slide = Easing.out(Easing.cubic)(Math.min(1, a / 12));
	const fade = interpolate(frame, [until - 10, until], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	return (
		<g opacity={fade} transform={`translate(${interpolate(slide, [0, 1], [-900, 0])} ${y})`} fontFamily={GRADUATE}>
			<rect x={L} y={0} width={R - L} height={112} rx={16} fill="#FFFDF7" stroke={INK} strokeWidth={4} />
			<rect x={L} y={0} width={22} height={112} rx={8} fill={color} />
			<text x={L + 48} y={50} fontSize={48} fill={INK}>
				{d.name} =
			</text>
			<text x={L + 48} y={96} fontSize={36} fill="#6b5a2e">
				{d.meaning}
			</text>
		</g>
	);
};

const Words: React.FC<{frame: number}> = ({frame}) => (
	<g>
		{TEAM_CUES.map((c) => {
			const color = TEAMS.find((t) => t.key === c.key)!.color;
			const zoomEnd = c.zoomAt + ZOOM_FRAMES;
			return (
				<g key={c.key}>
					{c.examples.map((d, i) => (
						<ExampleBanner key={d.name} d={d} y={STAGE.cy - 70 + i * 150} frame={frame} until={zoomEnd - 10} />
					))}
					{c.players.map((d, i) => (
						<PlayerCard key={d.name} d={d} y={1000 + i * 130} color={color} frame={frame} until={c.clearAt} />
					))}
				</g>
			);
		})}
	</g>
);

// ---------- cards 9–10: pipes to the positions, filled by WAR ----------
const POS = ['P', 'C', '1B', '2B', '3B', 'SS', 'OF', 'DH'];
const BOX = {w: 190, h: 250, rows: [1080, 1380], xs: [130, 335, 540, 745].map((x) => x + 0)};
const POS_MANIFOLD = 1010;
const boxOf = (i: number) => ({x: BOX.xs[i % 4], y: BOX.rows[Math.floor(i / 4)]});
const DOT_R = 15;

type Dot = {team: number; pos: number; k: number; at: number; war: number};
const DOTS: Dot[] = (() => {
	const all: Omit<Dot, 'k' | 'at'>[] = [];
	POS.forEach((pos, pi) =>
		TEAMS.forEach((t, ti) => (t.roster[pos] ?? []).forEach((p) => all.push({team: ti, pos: pi, war: p.war}))),
	);
	// Highest WAR first within each position: the best players claim the spots.
	all.sort((a, b) => a.pos - b.pos || b.war - a.war);
	const counts = POS.map(() => 0);
	const start = CARD.c10 + 20;
	const span = CARD.c11 - 40 - start;
	return all.map((d, i) => ({...d, k: counts[d.pos]++, at: start + Math.round((i / (all.length - 1)) * span)}));
})();

const dotSlot = (pos: number, k: number) => {
	const b = boxOf(pos);
	const perRow = 5;
	const step = 34;
	const left = b.x + (BOX.w - (perRow - 1) * step) / 2;
	return {x: left + (k % perRow) * step, y: b.y + BOX.h - 26 - Math.floor(k / perRow) * step};
};

const Positions: React.FC<{frame: number}> = ({frame}) => {
	if (frame < CARD.c9) return null;
	const draw = interpolate(frame, [CARD.c9, CARD.c9 + 90], [0, 1], {extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
	const boxesIn = interpolate(frame, [CARD.c9 + 60, CARD.c9 + 110], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const pipe = (d: string, key: string) => (
		<path key={key} d={d} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} />
	);
	return (
		<g>
			<g fill="none" stroke="#9C9384" strokeWidth={16} strokeLinecap="round" strokeLinejoin="round" opacity={0.6}>
				{BIN_X.slice(0, 4).map((x, i) => pipe(`M${x},${BADGE.y + 44} L${x},${POS_MANIFOLD}`, `t${i}`))}
				{pipe(`M${BOX.xs[0] + BOX.w / 2},${POS_MANIFOLD} L${BOX.xs[3] + BOX.w / 2},${POS_MANIFOLD}`, 'm')}
				{POS.map((_, i) => {
					const b = boxOf(i);
					const x = b.x + BOX.w / 2;
					return pipe(i < 4 ? `M${x},${POS_MANIFOLD} L${x},${b.y}` : `M${x},${POS_MANIFOLD} L${x},${POS_MANIFOLD + 30} L${b.x - 8},${POS_MANIFOLD + 30} L${b.x - 8},${b.y + 20}`, `p${i}`);
				})}
			</g>
			<g opacity={boxesIn} fontFamily={GRADUATE}>
				{POS.map((p, i) => {
					const b = boxOf(i);
					return (
						<g key={p}>
							<rect x={b.x} y={b.y} width={BOX.w} height={BOX.h} rx={16} fill="rgba(255,255,255,0.55)" stroke={INK} strokeWidth={5} />
							<text x={b.x + BOX.w / 2} y={b.y + 62} textAnchor="middle" fontSize={54} fill={INK}>
								{p}
							</text>
						</g>
					);
				})}
			</g>
			{DOTS.map((d, i) => {
				const a = frame - d.at;
				if (a < 0) return null;
				const b = boxOf(d.pos);
				const target = dotSlot(d.pos, d.k);
				const route =
					d.pos < 4
						? [{x: BIN_X[d.team], y: BIN.bottom}, {x: BIN_X[d.team], y: POS_MANIFOLD}, {x: b.x + BOX.w / 2, y: POS_MANIFOLD}, {x: b.x + BOX.w / 2, y: b.y + 80}, target]
						: [{x: BIN_X[d.team], y: BIN.bottom}, {x: BIN_X[d.team], y: POS_MANIFOLD}, {x: b.x + BOX.w / 2, y: POS_MANIFOLD}, {x: b.x + BOX.w / 2, y: POS_MANIFOLD + 30}, {x: b.x - 8, y: POS_MANIFOLD + 30}, {x: b.x - 8, y: b.y + 20}, {x: b.x + 30, y: b.y + 80}, target];
				const p = along(route, Easing.inOut(Easing.quad)(Math.min(1, a / 30)));
				const t = TEAMS[d.team];
				return <circle key={i} cx={p.x} cy={p.y} r={DOT_R} fill={t.color} stroke={t.key === 'jobs' ? '#5c4700' : 'rgba(0,0,0,0.4)'} strokeWidth={2} />;
			})}
		</g>
	);
};

// ---------- card 11–12: the ranking, built from the bottom ----------
const Ranking: React.FC<{frame: number; fps: number}> = ({frame, fps}) => {
	if (frame < CARD.c11) return null;
	const order = data.ranking as TeamKey[]; // best first
	return (
		<g fontFamily={GRADUATE}>
			{order.map((key, i) => {
				const at = RANK_AT[key];
				const s = spring({frame: frame - at, fps, config: {damping: 12, stiffness: 110}});
				if (frame < at) return null;
				const y = 330 + i * 330;
				return (
					<g key={key} opacity={Math.min(1, s * 1.5)} transform={`translate(0 ${(1 - s) * 60})`}>
						<text x={L + 70} y={y + 175} textAnchor="middle" fontSize={190} fill={INK}>
							{i + 1}
						</text>
						<Logo team={key} cx={460} cy={y + 125} size={280 * (0.6 + 0.4 * s)} />
						{/* the team's total roster WAR (data label) */}
						<text x={R} y={y + 140} textAnchor="end" fontSize={104} fill={INK}>
							{TEAMS.find((t) => t.key === key)!.rosterWar.toFixed(2)}
						</text>
						<text x={R} y={y + 196} textAnchor="end" fontSize={44} fill="#6b5a2e">
							WAR
						</text>
					</g>
				);
			})}
		</g>
	);
};

export const WorldSeries: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const machineOut = interpolate(frame, [CARD.c11, CARD.c11 + 20], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const intro = interpolate(frame, [0, 12], [0, 1], {extrapolateRight: 'clamp'});
	return (
		<AbsoluteFill style={{backgroundColor: BG}}>
			<svg width={VIDEO.width} height={VIDEO.height} viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`}>
				{machineOut > 0 && (
					<g opacity={machineOut * intro}>
						<Machine frame={frame} />
						<Bins />
						<Balls frame={frame} />
						<Positions frame={frame} />
						<BinLogos frame={frame} fps={fps} />
						<Words frame={frame} />
					</g>
				)}
				<Ranking frame={frame} fps={fps} />
			</svg>
			<ZoneGuide />
		</AbsoluteFill>
	);
};
