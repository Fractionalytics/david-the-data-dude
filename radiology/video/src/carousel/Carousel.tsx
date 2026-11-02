// Iteration 3: the Reel's story as eleven 1080×1440 (3:4) slides, in an X-ray film look with
// grease-pencil colors, the way a radiologist marks up a scan. Captions are David's words, copied
// from carousel/slides.md by scripts/carousel_build.py. Numbers come from the Reel's data files.
// The chest is drawn from curves, not a photo, and runs across the seam from slide 1 into slide 2.
import React from 'react';
import {AbsoluteFill, getInputProps, Img, staticFile} from 'remotion';
import {MARKER_FONT} from '../sharpie';
import captions from '../data/carousel.json';
import cards from '../data/cards.json';
import pay from '../data/card9.json';

export const CAROUSEL = {width: 1080, height: 1440, fps: 30};
const {width: W, height: H} = CAROUSEL;
const FILM = '#070c13';
const BONE = '#dfe9f2';
const GREASE = '#ffd23f';
const RED = '#ff4d5e';
const RAD = '#6db7ff';
const GRAY = '#aab6c2';
const CHEST_X = 760;

const Film: React.FC<{glowX?: number; glowY?: number; children: React.ReactNode}> = ({glowX = W / 2, glowY = 500, children}) => (
	<AbsoluteFill style={{backgroundColor: FILM}}>
		<div style={{position: 'absolute', inset: 0, background: `radial-gradient(ellipse 700px 800px at ${glowX}px ${glowY}px, #2a3c50 0%, #141f2c 50%, ${FILM} 100%)`}} />
		{children}
		<svg width={W} height={H} style={{position: 'absolute', inset: 0, mixBlendMode: 'overlay', opacity: 0.35}}>
			<filter id="grain">
				<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={4} />
				<feColorMatrix type="saturate" values="0" />
			</filter>
			<rect width={W} height={H} filter="url(#grain)" />
		</svg>
	</AbsoluteFill>
);

// The real-scan version (build with --real-scan): Nevit Dilmen's chest radiograph, spine centered on cx.
const RealChest: React.FC<{cx: number; opacity: number}> = ({cx, opacity}) => {
	const width = 1180;
	return (
		<Img
			src={staticFile('carousel/chest-real.jpg')}
			style={{
				position: 'absolute',
				left: cx - 0.494 * width,
				top: 0,
				width,
				opacity: opacity * 0.9,
				WebkitMaskImage: 'radial-gradient(ellipse 48% 58% at 49.4% 44%, black 62%, transparent 100%)',
			}}
		/>
	);
};

const Chest: React.FC<{cx: number; opacity?: number}> = ({cx, opacity = 1}) => {
	if (getInputProps().scan === 'real') return <RealChest cx={cx} opacity={opacity} />;
	const ribs = Array.from({length: 11}, (_, i) => {
		const y = 210 + i * 62;
		const reach = 250 + Math.sin(((i + 1) / 11) * Math.PI) * 215;
		const drop = 92 + i * 7;
		const side = (s: number) =>
			`M ${cx + s * 24} ${y} C ${cx + s * reach * 0.5} ${y - 52}, ${cx + s * reach * 0.98} ${y - 14}, ${cx + s * reach} ${y + drop * 0.62} C ${cx + s * reach} ${y + drop * 0.8}, ${cx + s * reach * 0.95} ${y + drop * 0.96}, ${cx + s * reach * 0.86} ${y + drop * 1.08}`;
		return {l: side(-1), r: side(1), o: 0.95 - i * 0.045, w: 19 - i * 0.55};
	});
	const clavicle = (s: number) => `M ${cx + s * 30} 150 C ${cx + s * 130} 112, ${cx + s * 250} 120, ${cx + s * 370} 92`;
	const vertebrae = Array.from({length: 17}, (_, i) => 70 + i * 52);
	return (
		<svg width={W} height={H} style={{position: 'absolute', inset: 0, opacity}}>
			<defs>
				<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3.5" /></filter>
				<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="16" /></filter>
				<filter id="heart" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="44" /></filter>
			</defs>
			<ellipse cx={cx + 62} cy={640} rx={165} ry={205} fill={BONE} opacity={0.34} filter="url(#heart)" />
			{['glow', 'soft'].map((f, pass) => (
				<g key={f} filter={`url(#${f})`} fill="none" stroke={BONE} strokeLinecap="round" opacity={pass === 0 ? 0.42 : 0.9}>
					{ribs.map((r, i) => (
						<g key={i} opacity={r.o} strokeWidth={r.w}>
							<path d={r.l} />
							<path d={r.r} />
						</g>
					))}
					<path d={clavicle(-1)} strokeWidth={24} />
					<path d={clavicle(1)} strokeWidth={24} />
					{vertebrae.map((y) => (
						<rect key={y} x={cx - 27} y={y} width={54} height={38} rx={10} fill={BONE} stroke="none" opacity={0.5} />
					))}
				</g>
			))}
		</svg>
	);
};

// Colors phrases of David's text without retyping it. A phrase that's gone from slides.md throws,
// so a caption edit can't silently lose its emphasis.
const marked = (text: string, marks: Record<string, string> = {}) => {
	let parts: React.ReactNode[] = [text];
	Object.entries(marks).forEach(([phrase, color]) => {
		if (!text.includes(phrase)) throw new Error(`"${phrase}" is not in: ${text}`);
		parts = parts.flatMap((p) => {
			if (typeof p !== 'string' || !p.includes(phrase)) return [p];
			const [before, ...rest] = p.split(phrase);
			return [before, <span key={phrase} style={{color}}>{phrase}</span>, rest.join(phrase)];
		});
	});
	return parts;
};

const Words: React.FC<{
	text: string;
	marks?: Record<string, string>;
	x?: number;
	y: number;
	size: number;
	color?: string;
	width?: number;
	lineHeight?: number;
}> = ({text, marks, x = 70, y, size, color = '#fff', width = W - 140, lineHeight = 1.16}) => (
	<div style={{position: 'absolute', left: x, top: y, width, fontFamily: MARKER_FONT, fontSize: size, lineHeight, color, textAlign: 'left', textShadow: `0 0 26px ${FILM}, 0 0 8px ${FILM}`}}>
		{marked(text, marks)}
	</div>
);

const Fade: React.FC<{height: number}> = ({height}) => (
	<div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height, background: `linear-gradient(to top, ${FILM} 62%, transparent)`}} />
);

const Label: React.FC<{x: number; y: number; size: number; color?: string; anchor?: 'start' | 'middle' | 'end'; children: React.ReactNode}> = ({x, y, size, color = '#fff', anchor = 'middle', children}) => (
	<text x={x} y={y} textAnchor={anchor} fontFamily={MARKER_FONT} fontSize={size} fill={color}>
		{children}
	</text>
);

const Slide1: React.FC = () => (
	<Film glowX={CHEST_X} glowY={520}>
		<Chest cx={CHEST_X} />
		<Fade height={760} />
		<Words text={captions['1'][0]} marks={{Jobpocalypse: RED}} y={820} size={102} />
	</Film>
);

const Slide2: React.FC = () => (
	<Film glowX={300} glowY={500}>
		<Chest cx={CHEST_X - W} />
		<Words text={captions['2'][0]} x={190} y={60} width={830} size={56} color={GREASE} />
		<Words text={captions['2'][1]} marks={{'People should stop training radiologists now': RAD, 'within 5 years': RED, 'it might be 10 years': RED}} x={190} y={140} width={830} size={58} lineHeight={1.2} />
		<Img
			src={staticFile('carousel/hinton.jpg')}
			style={{
				position: 'absolute',
				right: 0,
				bottom: 0,
				width: 500,
				filter: 'grayscale(1) contrast(1.08) brightness(1.05)',
				mixBlendMode: 'screen',
				WebkitMaskImage: 'linear-gradient(to bottom, black 78%, transparent 100%)',
			}}
		/>
		<Words text={captions['2'][2]} x={70} y={1010} width={510} size={44} color={GREASE} lineHeight={1.2} />
	</Film>
);

const Slide3: React.FC = () => {
	const base = 1150;
	const perPoint = 53;
	const bar = (x: number, pct: number, color: string, name: string) => (
		<g>
			<rect x={x} y={base - pct * perPoint} width={300} height={pct * perPoint} rx={8} fill={color} opacity={0.2} style={{filter: 'blur(22px)'}} />
			<rect x={x} y={base - pct * perPoint} width={300} height={pct * perPoint} rx={8} fill={color} opacity={0.92} />
			<Label x={x + 150} y={base - pct * perPoint - 34} size={pct > 10 ? 104 : 78} color={color}>+{pct}%</Label>
			<Label x={x + 150} y={base + 68} size={44} color={color}>{name}</Label>
		</g>
	);
	return (
		<Film glowY={880}>
			<Words text={captions['3'][0]} marks={{NOT: RED}} y={60} size={112} lineHeight={1.08} />
			<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
				{bar(140, cards.medicare.radiologists, RAD, 'Radiologists')}
				{bar(640, cards.medicare.physicians, GRAY, 'All doctors')}
				<line x1={90} x2={990} y1={base} y2={base} stroke="#fff" strokeWidth={7} strokeLinecap="round" />
			</svg>
			<Words text={captions['3'][1]} y={1260} size={40} color={GREASE} lineHeight={1.2} />
		</Film>
	);
};

const Slide3b: React.FC = () => (
	<Film glowY={780}>
		<Chest cx={W / 2} opacity={0.16} />
		<Words text={captions['3.5'][0]} y={110} size={92} />
		<Words text={captions['3.5'][1]} marks={{Capability: RAD, Prescription: RED}} y={520} size={158} lineHeight={1.34} />
	</Film>
);

const Slide4: React.FC = () => (
	<Film glowY={420}>
		<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
			<Label x={W / 2} y={230} size={130} color={GRAY}>5 years</Label>
			<line x1={270} y1={225} x2={810} y2={160} stroke={RED} strokeWidth={14} strokeLinecap="round" />
			<text x={W / 2} y={490} textAnchor="middle" fontFamily={MARKER_FONT} fontSize={210} fill={RAD} style={{filter: `drop-shadow(0 0 26px ${RAD}88)`}}>15 years</text>
		</svg>
		<Words text={captions['4'][0]} marks={{'CAPABILITY:': RAD, '76%': GREASE, 'a factor of three': RED}} y={640} size={56} lineHeight={1.24} />
	</Film>
);

const Slide5: React.FC = () => {
	const L = 120;
	const R = 960;
	const T = 90;
	const B = 660;
	return (
		<Film glowY={380}>
			<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
				<path d={`M ${L} ${T} L ${L} ${B} L ${R} ${B}`} fill="none" stroke="#fff" strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" />
				<path d={`M ${L} ${B} C ${L + 110} ${T + 240}, ${L + 280} ${T + 170}, ${R} ${T + 140}`} fill="none" stroke={GRAY} strokeWidth={12} strokeLinecap="round" />
				<path d={`M ${L} ${B} C ${L + 460} ${B}, ${L + 700} ${B - 120}, ${R - 20} ${T}`} fill="none" stroke={RAD} strokeWidth={14} strokeLinecap="round" style={{filter: `drop-shadow(0 0 14px ${RAD})`}} />
				<Label x={L + 300} y={T + 120} size={44} color={GRAY}>What we expect</Label>
				<Label x={L + 610} y={B - 110} size={44} color={RAD} anchor="start">What happens</Label>
				<Label x={L + 130} y={B + 62} size={40}>Short run</Label>
				<Label x={R - 130} y={B + 62} size={40}>Long run</Label>
			</svg>
			<Words text={captions['5'][0]} marks={{"Amara's Law:": GREASE}} y={790} size={52} lineHeight={1.22} />
			<Words text={captions['5'][1]} y={1250} size={50} color={GREASE} />
		</Film>
	);
};

const Slide6: React.FC = () => (
	<Film glowY={320}>
		<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
			<g fill="none" stroke="#fff" strokeWidth={7} strokeLinejoin="round">
				<rect x={80} y={70} width={410} height={430} rx={6} />
				<rect x={590} y={70} width={410} height={430} rx={6} />
			</g>
			<g stroke={GREASE} strokeWidth={10} strokeLinecap="round">
				<line x1={540} y1={40} x2={540} y2={530} />
				<line x1={500} y1={170} x2={580} y2={170} />
				<line x1={500} y1={290} x2={580} y2={290} />
				<line x1={500} y1={410} x2={580} y2={410} />
			</g>
			<path d="M 270 390 C 390 180, 620 110, 800 370" fill="none" stroke={RED} strokeWidth={11} strokeLinecap="round" style={{filter: `drop-shadow(0 0 12px ${RED})`}} />
			<circle cx={802} cy={374} r={21} fill={RED} />
			<Label x={285} y={160} size={84}>AI</Label>
			<Label x={795} y={140} size={46}>Labor</Label>
			<Label x={795} y={195} size={46}>Economics</Label>
		</svg>
		<Words text={captions['6'][0]} marks={{'PRESCRIPTION:': RED}} y={590} size={70} lineHeight={1.18} />
		<Words text={captions['6'][1]} marks={{'"epistemic trespassing,"': RED}} y={880} size={58} lineHeight={1.24} />
	</Film>
);

const Slide7: React.FC = () => {
	const cell = 52;
	const gap = 6;
	const left = 70;
	const top = 70;
	const lit = 36;
	return (
		<Film glowX={300} glowY={340}>
			<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
				{Array.from({length: 100}, (_, i) => (
					<rect key={i} x={left + (i % 10) * (cell + gap)} y={top + Math.floor(i / 10) * (cell + gap)} width={cell} height={cell} rx={7} fill={i < lit ? RAD : '#2c3a4a'} style={i < lit ? {filter: `drop-shadow(0 0 8px ${RAD}aa)`} : undefined} />
				))}
				<text x={690} y={290} fontFamily={MARKER_FONT} fontSize={146} fill={RAD}>36%</text>
				<Label x={690} y={350} size={40} color={RAD} anchor="start">reading scans</Label>
				<text x={690} y={500} fontFamily={MARKER_FONT} fontSize={100} fill={GRAY}>64%</text>
				<Label x={690} y={556} size={40} color={GRAY} anchor="start">everything else</Label>
			</svg>
			<Words text={captions['7'][0]} marks={{NOT: RED, '36%': RAD}} y={720} size={56} lineHeight={1.22} />
		</Film>
	);
};

// The Reel's three on-screen lines, with the doctor-services figure corrected from 27% to 26%.
const Slide8: React.FC = () => {
	const rows: [string, string, string, boolean][] = [
		['24%', '65+ population', RAD, true],
		['38%', 'Imaging services per Medicare patient, vs. 26% for doctor services overall', RAD, true],
		['9%', 'Radiologists per 100k Americans 65+', RED, false],
	];
	return (
		<Film glowY={350}>
			{rows.map(([num, line, color, up], i) => (
				<React.Fragment key={num}>
					<div style={{position: 'absolute', left: 60, top: 60 + i * 215, width: 350, display: 'flex', alignItems: 'center', gap: 10, fontFamily: MARKER_FONT, fontSize: 112, color, lineHeight: 1.2}}>
						{num}
						<svg width={54} height={96} viewBox="0 0 54 96" style={{transform: up ? undefined : 'rotate(180deg)', flexShrink: 0}}>
							<path d="M 27 90 L 27 10 M 6 34 L 27 8 L 48 34" fill="none" stroke={color} strokeWidth={11} strokeLinecap="round" strokeLinejoin="round" />
						</svg>
					</div>
					<div style={{position: 'absolute', left: 400, top: 80 + i * 215, width: 620, height: 150, display: 'flex', alignItems: 'center', fontFamily: MARKER_FONT, fontSize: 42, lineHeight: 1.2, color: '#fff'}}>{line}</div>
				</React.Fragment>
			))}
			<Words text={captions['8'][0]} marks={{"hasn't kept pace.": RED}} y={760} size={58} lineHeight={1.24} />
		</Film>
	);
};

const Slide9: React.FC = () => {
	const [p0, p1] = pay.surveys.find((s) => s.source === 'Doximity')!.points;
	const L = 240;
	const R = 840;
	const yOf = (m: number) => 700 - (m - 1) * 800;
	return (
		<Film glowY={350}>
			<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
				<Label x={W / 2} y={105} size={84}>Radiology Premium</Label>
				<line x1={L} x2={R} y1={yOf(p0.multiple)} y2={yOf(p1.multiple)} stroke={RAD} strokeWidth={14} strokeLinecap="round" style={{filter: `drop-shadow(0 0 14px ${RAD})`}} />
				<circle cx={L} cy={yOf(p0.multiple)} r={22} fill={RAD} />
				<circle cx={R} cy={yOf(p1.multiple)} r={22} fill={RAD} />
				<Label x={L + 10} y={yOf(p0.multiple) - 50} size={92} color={RAD}>{p0.multiple.toFixed(2)}x</Label>
				<Label x={R - 10} y={yOf(p1.multiple) - 50} size={120} color={RAD}>{p1.multiple.toFixed(2)}x</Label>
				<line x1={L} x2={R} y1={yOf(1)} y2={yOf(1)} stroke={GRAY} strokeWidth={8} strokeLinecap="round" />
				<Label x={W / 2} y={yOf(1) - 26} size={40} color={GRAY}>Average doctor = 1.0x</Label>
				<Label x={L} y={yOf(1) + 70} size={50}>2017</Label>
				<Label x={R} y={yOf(1) + 70} size={50}>2025</Label>
			</svg>
			<Words text={captions['9'][0]} marks={{'the opposite happened.': RED}} y={825} size={56} lineHeight={1.24} />
		</Film>
	);
};

const Slide10: React.FC = () => (
	<Film glowY={520}>
		<Chest cx={W / 2} />
		<Fade height={820} />
		<Words text={captions['10'][0]} marks={{'Follow for more.': GREASE}} y={860} size={118} lineHeight={1.14} />
	</Film>
);

export const SLIDES = [Slide1, Slide2, Slide3, Slide3b, Slide4, Slide5, Slide6, Slide7, Slide8, Slide9, Slide10];
