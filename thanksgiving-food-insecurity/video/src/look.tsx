// Thanksgiving look: grocery-receipt panels (David picked it, 2026-11-23).
// Layout measured on this Reel's own footage (2026-11-24, public/speaker-a.png and speaker-b.png,
// 1080x1920): head tops at y 1045 (A, black shirt) and y 1073 (B, orange cap). David: leave 60px
// above the heads for captions, so the caption band is y 985-1045 and the receipt panel fills
// y 260-980, x 160-920 (inside the 120px side margins).
// Colors validated with the dataviz validator on the paper (#FBF8F1), 2026-11-24, all pairs:
// red #B3261E, blue #1F5FA8, green #00936F pass every check (worst CVD dE 10.7, contrast >= 3:1).
import React from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';

export const PANEL = {left: 160, right: 920, top: 260, bottom: 980};
export const PW = PANEL.right - PANEL.left; // 760
export const PH = PANEL.bottom - PANEL.top; // 720

export const C = {
	paper: '#FBF8F1',
	ink: '#1F1F1F',
	muted: '#77736A',
	rule: '#B9B3A6',
	red: '#B3261E', // rose / bad news
	blue: '#1F5FA8', // fell
	green: '#00936F', // good news (factors list only)
	track: '#E7E2D6',
};

export const MONO = 'IBM Plex Mono';

const fontHandle = typeof window !== 'undefined' ? delayRender('IBM Plex Mono') : null;
if (typeof window !== 'undefined') {
	Promise.all(
		['400', '600', '700'].map((w) =>
			new FontFace(MONO, `url(${staticFile(`fonts/IBMPlexMono-${w}.woff2`)})`, {weight: w})
				.load()
				.then((f) => document.fonts.add(f)),
		),
	)
		.catch((e) => console.error('font load failed', e))
		.finally(() => fontHandle !== null && continueRender(fontHandle));
}

// Paper receipt filling the panel, with a subtle torn bottom edge (David, 2026-11-23).
export const Receipt: React.FC<{children: React.ReactNode; opacity?: number}> = ({children, opacity = 1}) => {
	const teeth = 76;
	const depth = 5;
	const pts = ['0% 0%', '100% 0%', `100% ${PH - depth}px`];
	for (let i = teeth; i >= 0; i--) pts.push(`${(i / teeth) * 100}% ${i % 2 === 0 ? PH - depth : PH}px`);
	return (
		<div
			style={{
				position: 'absolute',
				left: PANEL.left,
				top: PANEL.top,
				width: PW,
				height: PH,
				background: C.paper,
				clipPath: `polygon(${pts.join(',')})`,
				fontFamily: MONO,
				color: C.ink,
				opacity,
				overflow: 'hidden',
			}}
		>
			{children}
		</div>
	);
};

export const Dotted: React.FC<{top: number}> = ({top}) => (
	<div style={{position: 'absolute', left: 36, right: 36, top, borderTop: `3px dashed ${C.rule}`}} />
);

// Titles are David's words from the Sheet's On-Screen Text column, set in caps.
export const Title: React.FC<{text: string; sub?: string; opacity?: number}> = ({text, sub, opacity = 1}) => (
	<div style={{position: 'absolute', left: 30, right: 30, top: 26, textAlign: 'center', opacity}}>
		<div style={{fontSize: 42, fontWeight: 700, textTransform: 'uppercase', lineHeight: 1.1}}>{text}</div>
		{sub && <div style={{fontSize: 28, fontWeight: 600, color: C.muted, marginTop: 6}}>{sub}</div>}
	</div>
);
