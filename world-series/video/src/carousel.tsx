// The World Series of Last Names carousel: seven 1080×1350 slides in the Reel's look (cream, Graduate,
// the team logos). Slide list and every sentence are David's (2026-10-14). Roster rows are data:
// position, player, the surname's meaning (docs/name-meanings.md, or David's on-screen wording where
// the Reel used one) and 2026 bWAR. Lines David hasn't written yet show as [TBD: David].
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {loadFont as loadGraduate} from '@remotion/google-fonts/Graduate';
import {loadFont as loadYellowtail} from '@remotion/google-fonts/Yellowtail';
import {loadFont as loadRye} from '@remotion/google-fonts/Rye';
import {loadFont as loadAlfa} from '@remotion/google-fonts/AlfaSlabOne';
import data from './data/video.json';

const {fontFamily: GRADUATE} = loadGraduate();
loadYellowtail();
loadRye();
loadAlfa();

export const SLIDE = {width: 1080, height: 1350, fps: 30};
const BG = '#F3EBD8';
const INK = '#20262B';
const BROWN = '#6b5a2e';
const M = 90; // side margin

type TeamKey = 'jobs' | 'sons' | 'nicknames' | 'places';
type Team = {key: TeamKey; name: string; color: string; rosterWar: number; roster: Record<string, {name: string; war: number}[]>};
const TEAMS = data.teams as Team[];
const LOGOS = data.logos as Record<TeamKey, string>;
const team = (k: TeamKey) => TEAMS.find((t) => t.key === k)!;
const POS = ['P', 'C', '1B', '2B', '3B', 'SS', 'OF', 'DH'];

// What each rostered surname means, from docs/name-meanings.md. Where the Reel put a meaning on
// screen, David's wording is used.
const MEANING: Record<string, string> = {
	// The Jobs
	'Cam Schlittler': 'sled maker',
	'Zack Wheeler': 'wheel maker',
	'Tarik Skubal': 'feather plucker',
	'Cade Cavalli': 'horse groom',
	'Dillon Dingler': 'blade sharpener',
	'Jake Bauers': 'farmer',
	'Bryson Stott': 'cattleman',
	'Junior Caminero': 'traveler, peddler',
	'José Caballero': 'knight',
	'Andy Pages': 'agricultural laborer',
	'Jordan Walker': 'cloth fuller',
	'Ian Happ': 'sickle maker',
	'Iván Herrera': 'ironworker',
	// The Sons of Somebody
	'Cristopher Sánchez': 'son of Sancho',
	'Eduardo Rodriguez': 'son of Rodrigo',
	'Drew Rasmussen': 'son of Rasmus',
	'Michael Wacha': 'son of Wenceslaus',
	'Drake Baldwin': 'son of Baldwin',
	'Pete Alonso': 'son of Alonso',
	'Xavier Edwards': 'son of Edward',
	'José Ramírez': 'son of Ramiro',
	'Kevin McGonigle': 'son of Congal',
	'Michael Harris II': 'son of Harry',
	'Corbin Carroll': 'son of Cearbhall',
	'Cody Bellinger': 'son of Berenger',
	'Yordan Alvarez': 'son of Álvaro',
	// The Nicknames
	'Jesús Luzardo': 'light',
	'Jacob Misiorowski': 'bear (or mouse)',
	'Sonny Gray': 'gray-haired',
	'Michael King': 'acted like a king',
	'Gabriel Moreno': 'dark',
	'Ty France': 'the Frenchman',
	'Cole Young': 'the younger',
	'Ezequiel Duran': 'enduring',
	'Bobby Witt Jr.': 'white',
	'Pete Crow-Armstrong': 'bird-strong',
	'Mike Trout': 'the fish',
	'Henry Bolte': 'bold',
	'Kyle Schwarber': 'unknown (black?)',
	// The Places
	'Parker Messick': 'a place in France',
	'Yoshinobu Yamamoto': 'base of the mountain',
	'Chris Sale': 'willow tree',
	'Chase Burns': 'stream',
	'William Contreras': 'a town in Spain',
	'Willson Contreras': 'a town in Spain',
	'Brandon Lowe': 'hill',
	'Alex Bregman': 'by the riverbank',
	'Jeremy Peña': 'boulder/cliff',
	'Wilyer Abreu': 'a place in Portugal',
	'Randy Arozarena': "the smith's house",
	'Seiya Suzuki': 'bell tree',
	'Shohei Ohtani': 'large valley',
};

const Logo: React.FC<{k: TeamKey; cx: number; cy: number; size: number}> = ({k, cx, cy, size}) => (
	<g transform={`translate(${cx - size / 2} ${cy - size / 2}) scale(${size / 600})`} dangerouslySetInnerHTML={{__html: LOGOS[k]}} />
);

const Frame: React.FC<{children: React.ReactNode}> = ({children}) => (
	<AbsoluteFill style={{backgroundColor: BG}}>
		<svg width={SLIDE.width} height={SLIDE.height} viewBox={`0 0 ${SLIDE.width} ${SLIDE.height}`} fontFamily={GRADUATE}>
			<rect x={24} y={24} width={SLIDE.width - 48} height={SLIDE.height - 48} rx={28} fill="none" stroke={INK} strokeWidth={6} />
			{children}
		</svg>
	</AbsoluteFill>
);

// Wrap text to lines of at most `max` characters.
const wrap = (text: string, max: number) => {
	const lines: string[] = [];
	let line = '';
	for (const w of text.split(' ')) {
		if ((line + ' ' + w).trim().length > max) {
			lines.push(line.trim());
			line = w;
		} else line = `${line} ${w}`;
	}
	if (line.trim()) lines.push(line.trim());
	return lines;
};

// ---------- 1. cover ----------
export const Slide1: React.FC = () => {
	const q = wrap('Who won the 2026 World Series of Last Names?', 16);
	return (
		<Frame>
			{q.map((l, i) => (
				<text key={i} x={540} y={210 + i * 112} textAnchor="middle" fontSize={92} fill={INK}>
					{l}
				</text>
			))}
			{(['jobs', 'sons', 'nicknames', 'places'] as TeamKey[]).map((k, i) => (
				<Logo key={k} k={k} cx={300 + (i % 2) * 480} cy={(q.length > 3 ? 820 : 760) + Math.floor(i / 2) * 330} size={300} />
			))}
		</Frame>
	);
};

// ---------- 2. the four teams ----------
// David's own definitions from the Reel's script (cards 5, 7, 8). Card 6 has none.
const DEFS: Record<TeamKey, string> = {
	jobs: 'Your last name is an old-style occupation',
	sons: 'Your last name relates to a long-ago father-son or mother-son relationship',
	nicknames: 'Your last name is how others once described a person',
	places: 'Your last name has to do with a place name or geographic feature',
};

export const Slide2: React.FC = () => (
	<Frame>
		{(['places', 'nicknames', 'sons', 'jobs'] as TeamKey[]).map((k, i) => {
			const y = 80 + i * 300;
			const lines = wrap(DEFS[k], 24);
			const t = team(k);
			return (
				<g key={k}>
					<Logo k={k} cx={M + 120} cy={y + 140} size={230} />
					<text x={M + 270} y={y + 90} fontSize={50} fill={INK}>
						{t.name}
					</text>
					{lines.map((l, j) => (
						<text key={j} x={M + 270} y={y + 150 + j * 46} fontSize={36} fill={BROWN}>
							{l}
						</text>
					))}
				</g>
			);
		})}
	</Frame>
);

// ---------- 3–6. rosters ----------
export const RosterSlide: React.FC<{k: TeamKey}> = ({k}) => {
	const t = team(k);
	const rows = POS.flatMap((pos) => (t.roster[pos] ?? []).map((p) => ({pos, ...p})));
	const top = 330;
	const rowH = 70;
	return (
		<Frame>
			<Logo k={k} cx={M + 120} cy={175} size={230} />
			<text x={SLIDE.width - M} y={180} textAnchor="end" fontSize={120} fill={INK}>
				{t.rosterWar.toFixed(2)}
			</text>
			<text x={SLIDE.width - M} y={240} textAnchor="end" fontSize={44} fill={BROWN}>
				Total WAR
			</text>
			{/* header */}
			<g fontSize={26} fill={BROWN}>
				<text x={M} y={top - 14}>Pos</text>
				<text x={M + 80} y={top - 14}>Player</text>
				<text x={M + 490} y={top - 14}>Name means</text>
				<text x={SLIDE.width - M} y={top - 14} textAnchor="end">
					WAR
				</text>
			</g>
			<line x1={M} x2={SLIDE.width - M} y1={top} y2={top} stroke={INK} strokeWidth={4} />
			{rows.map((r, i) => {
				const y = top + i * rowH;
				return (
					<g key={r.name}>
						{i % 2 === 1 && <rect x={M - 10} y={y} width={SLIDE.width - 2 * M + 20} height={rowH} fill="rgba(32,38,43,0.05)" />}
						<rect x={M} y={y + 18} width={56} height={36} rx={8} fill={t.color} />
						<text x={M + 28} y={y + 46} textAnchor="middle" fontSize={24} fill={k === 'jobs' ? INK : '#fff'}>
							{r.pos}
						</text>
						<text x={M + 80} y={y + 46} fontSize={28} fill={INK}>
							{r.name}
						</text>
						<text x={M + 490} y={y + 46} fontSize={24} fill={BROWN}>
							{MEANING[r.name] ?? '??'}
						</text>
						<text x={SLIDE.width - M} y={y + 46} textAnchor="end" fontSize={30} fill={INK}>
							{r.war.toFixed(2)}
						</text>
					</g>
				);
			})}
		</Frame>
	);
};

// ---------- 8. everyone else ----------
// The four best players outside the named teams, and the categories that couldn't field a team.
// Headline, subhead and the "no other category" line: Claude's draft from David's brief
// (2026-10-15); David to approve.
const OTHERS = [
	{pos: '2B', name: 'Brice Turang', cat: 'Origin unknown', meaning: 'unknown', war: 7.34},
	{pos: 'OF', name: 'Ceddanne Rafaela', cat: 'Acquired/assigned', meaning: 'name given at emancipation', war: 5.7},
	{pos: 'SS', name: 'Elly De La Cruz', cat: 'Patronage', meaning: 'of the cross', war: 5.63},
	{pos: 'P', name: 'Dylan Cease', cat: 'Origin unknown', meaning: 'from German Zies', war: 5.52},
];
const SMALL = [
	{cat: 'Patronage', n: 14, note: 'no C, 2B or DH'},
	{cat: 'Acquired/assigned', n: 4, note: ''},
	{cat: 'Compound (two surnames)', n: 4, note: ''},
	{cat: 'Ornamental/artificial', n: 2, note: ''},
	{cat: 'Origin unknown', n: 219, note: ''},
];

export const Slide8: React.FC = () => (
	<Frame>
		<text x={540} y={150} textAnchor="middle" fontSize={84} fill={INK}>
			Everyone Else
		</text>
		<text x={540} y={210} textAnchor="middle" fontSize={34} fill={BROWN}>
			243 players outside the four teams
		</text>
		{OTHERS.map((o, i) => {
			const y = 260 + i * 120;
			return (
				<g key={o.name}>
					{i % 2 === 0 && <rect x={M - 10} y={y} width={SLIDE.width - 2 * M + 20} height={120} fill="rgba(32,38,43,0.05)" />}
					<rect x={M} y={y + 22} width={56} height={36} rx={8} fill="#8F8F8F" />
					<text x={M + 28} y={y + 50} textAnchor="middle" fontSize={24} fill="#fff">
						{o.pos}
					</text>
					<text x={M + 80} y={y + 52} fontSize={34} fill={INK}>
						{o.name}
					</text>
					<text x={M + 80} y={y + 96} fontSize={26} fill={BROWN}>
						{o.meaning === 'unknown' ? o.cat : `${o.cat}: ${o.meaning}`}
					</text>
					<text x={SLIDE.width - M} y={y + 52} textAnchor="end" fontSize={34} fill={INK}>
						{o.war.toFixed(2)}
					</text>
				</g>
			);
		})}
		<line x1={M} x2={SLIDE.width - M} y1={780} y2={780} stroke={INK} strokeWidth={4} />
		<text x={M} y={840} fontSize={36} fill={INK}>
			No other category could field a whole team:
		</text>
		{SMALL.map((s, i) => (
			<g key={s.cat}>
				<text x={M + 20} y={910 + i * 62} fontSize={30} fill={INK}>
					{s.cat}
				</text>
				<text x={SLIDE.width - M} y={910 + i * 62} textAnchor="end" fontSize={30} fill={BROWN}>
					{s.n} players{s.note ? `, ${s.note}` : ''}
				</text>
			</g>
		))}
		<text x={540} y={1260} textAnchor="middle" fontSize={26} fill={BROWN}>
			Matronymic names (2) joined the Sons of Somebody
		</text>
	</Frame>
);

// ---------- 9. data sources ----------
const SOURCES = [
	{what: 'Baseball-Reference', why: '2026 WAR for all 1,472 players'},
	{what: 'MLB Stats API', why: 'positions and birthplaces'},
	{what: 'Wikipedia, "Surname"', why: 'the surname categories'},
	{what: 'Wiktionary + surname dictionaries', why: 'what each name means'},
	{what: 'Claude + Jev', why: 'sorting every name'},
];

export const Slide9: React.FC = () => (
	<Frame>
		<text x={540} y={170} textAnchor="middle" fontSize={84} fill={INK}>
			Data Sources
		</text>
		{SOURCES.map((s, i) => (
			<g key={s.what}>
				<circle cx={M + 22} cy={290 + i * 190} r={14} fill={['#1F4D3A', '#B3272D', '#13294B', '#F2B705', '#8F8F8F'][i]} />
				<text x={M + 60} y={302 + i * 190} fontSize={40} fill={INK}>
					{s.what}
				</text>
				<text x={M + 60} y={360 + i * 190} fontSize={34} fill={BROWN}>
					{s.why}
				</text>
			</g>
		))}
	</Frame>
);

// ---------- 10. watch the Reel ----------
// Claude's draft from David's brief (2026-10-15); David to approve.
export const Slide10: React.FC = () => (
	<Frame>
		<text x={540} y={230} textAnchor="middle" fontSize={96} fill={INK}>
			Watch the Reel
		</text>
		{/* Instagram's Reels glyph, single-color outline, pointing viewers to the Reels tab (not a button) */}
		<g transform="translate(540 640)" fill="none" stroke={INK} strokeWidth={26} strokeLinejoin="round" strokeLinecap="round">
			<rect x={-170} y={-170} width={340} height={340} rx={90} />
			<line x1={-170} y1={-80} x2={170} y2={-80} />
			<line x1={-70} y1={-166} x2={-25} y2={-84} />
			<line x1={40} y1={-166} x2={85} y2={-84} />
			<path d="M-40,-5 L-40,105 L55,50 Z" fill={INK} strokeWidth={14} />
		</g>
		{(['jobs', 'sons', 'nicknames', 'places'] as TeamKey[]).map((k, i) => (
			<Logo key={k} k={k} cx={195 + i * 230} cy={1060} size={200} />
		))}
	</Frame>
);

// ---------- 7. the champions ----------
const confetti = Array.from({length: 70}, (_, i) => {
	const r = Math.sin(i * 12.9898) * 43758.5453;
	const f = r - Math.floor(r);
	const g = Math.sin(i * 78.233) * 12345.678;
	const h = g - Math.floor(g);
	return {x: 70 + f * 940, y: 60 + h * 1230, rot: f * 360, c: ['#1F4D3A', '#D9A520', '#B3272D', '#13294B'][i % 4]};
});

export const Slide7: React.FC = () => {
	const t = team('places');
	return (
		<Frame>
			{confetti
				.filter((c) => Math.hypot(c.x - 540, c.y - 640) > 340 && c.y > 310 && !(c.y > 990 && c.y < 1170 && Math.abs(c.x - 540) < 230))
				.map((c, i) => (
					<rect key={i} x={c.x} y={c.y} width={14} height={26} rx={3} fill={c.c} transform={`rotate(${c.rot} ${c.x} ${c.y})`} />
				))}
			<text x={540} y={160} textAnchor="middle" fontSize={92} fill={INK}>
				World Series
			</text>
			<text x={540} y={265} textAnchor="middle" fontSize={92} fill={INK}>
				Champs!
			</text>
			<Logo k="places" cx={540} cy={640} size={600} />
			<text x={540} y={1080} textAnchor="middle" fontSize={120} fill={INK}>
				{t.rosterWar.toFixed(2)}
			</text>
			<text x={540} y={1140} textAnchor="middle" fontSize={44} fill={BROWN}>
				Total WAR
			</text>
		</Frame>
	);
};
