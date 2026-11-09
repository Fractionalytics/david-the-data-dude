// Non-chart signs: the Vision Zero city grid (card 6), the question-mark warning sign (cards 15-17) and
// list signs (cards 26 and 46). All take animation progress so cards hand off cleanly.
import React from 'react';
import {BAND, BAND_H, BAND_W, C, FONT, Plate, Title} from '../look';

const clamp = (v: number) => Math.max(0, Math.min(1, v));

// Card 6: the 18 early US Vision Zero cities (pledged 2012-2016) in Ferenchak (2023, Transportation
// Letters). Only New York had a statistically significant drop in pedestrian deaths after its pledge
// (before/after, 2007-2019). Alphabetical; New York highlighted on "outside of NYC".
const VZ_CITIES = ['Anchorage', 'Austin', 'Boston', 'Chicago', 'Denver', 'Fort Lauderdale', 'Fremont', 'Los Angeles',
	'New York', 'Philadelphia', 'Portland', 'Richmond', 'San Antonio', 'San Diego', 'San Francisco', 'San Jose', 'Seattle', 'Washington'];

export const VisionZeroGrid: React.FC<{title: string; tilesP: number; nycP: number}> = ({title, tilesP, nycP}) => {
	const COLS = 3, TOP = 160, CW = (BAND_W - 80) / COLS, RH = 62;
	return (
		<Plate>
			<Title text={title} />
			<div style={{position: 'absolute', left: 40, top: 98, fontSize: 36, fontWeight: 700, color: C.muted, whiteSpace: 'nowrap'}}>
				Significant drop in pedestrian deaths after Vision Zero
			</div>
			{VZ_CITIES.map((c, i) => {
				const hit = c === 'New York';
				const t = clamp(tilesP * VZ_CITIES.length - i);
				const lit = hit ? nycP : 0;
				return (
					<div
						key={c}
						style={{
							position: 'absolute',
							left: 40 + (i % COLS) * CW,
							top: TOP + Math.floor(i / COLS) * RH,
							width: CW - 14,
							height: RH - 10,
							borderRadius: 8,
							background: lit > 0.5 ? C.eu : C.track,
							color: lit > 0.5 ? '#FFFFFF' : C.muted,
							fontSize: 38,
							fontWeight: lit > 0.5 ? 800 : 700,
							display: 'flex',
							alignItems: 'center',
							paddingLeft: 14,
							opacity: t,
							transform: `scale(${hit ? 1 + 0.08 * Math.sin(Math.PI * lit) : 1})`,
						}}
					>
						{lit > 0.5 ? `✓ ${c}` : c}
					</div>
				);
			})}
		</Plate>
	);
};

// Cards 15-17: a yellow diamond warning sign with a question mark, centered in the band. `p` scales it in.
export const QuestionSign: React.FC<{p: number}> = ({p}) => {
	const D = 520; // the diamond's diagonal, inside the 550px band
	const S = D / Math.SQRT2;
	const scale = p >= 1 ? 1 : p * (1.08 - 0.08 * p); // slight overshoot as it lands
	return (
		<div style={{position: 'absolute', left: BAND.left + (BAND_W - D) / 2, top: BAND.top + (BAND_H - D) / 2, width: D, height: D, transform: `scale(${scale})`, opacity: clamp(p * 3)}}>
			<div
				style={{
					position: 'absolute',
					left: (D - S) / 2,
					top: (D - S) / 2,
					width: S,
					height: S,
					transform: 'rotate(45deg)',
					background: '#FDB913',
					borderRadius: 26,
					boxShadow: `inset 0 0 0 10px #FDB913, inset 0 0 0 20px ${C.border}`,
				}}
			/>
			<div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT, fontWeight: 800, fontSize: 330, color: C.ink, lineHeight: 1, paddingTop: 20}}>
				?
			</div>
		</div>
	);
};

// Cards 38-39 and 52-54: Hill's nine viewpoints (Hill 1965, Proc. R. Soc. Med. 58:295-300, in his order),
// each with a mark: '' unchecked, 'check', or 'half' (partly met). `marks` progress fades each mark in.
export const HILL = ['Strength', 'Consistency', 'Specificity', 'Temporality', 'Biological gradient', 'Plausibility', 'Coherence', 'Experiment', 'Analogy'];

export const HillSign: React.FC<{title: string; sub?: string; marks: Array<'' | 'check' | 'half'>; markP: number[]; listP?: number}> = ({title, sub, marks, markP, listP = 1}) => {
	const COLS = 3, TOP = sub ? 190 : 150, CW = (BAND_W - 80) / COLS, RH = 112;
	return (
		<Plate>
			<Title text={title} />
			{sub && <div style={{position: 'absolute', left: 40, top: 98, fontSize: 36, fontWeight: 700, color: C.muted, whiteSpace: 'nowrap'}}>{sub}</div>}
			{HILL.map((h, i) => {
				const m = marks[i], p = clamp(markP[i] ?? 0), on = m !== '' && p > 0;
				const left = 40 + (i % COLS) * CW, top = TOP + Math.floor(i / COLS) * RH;
				return (
					<div key={h} style={{position: 'absolute', left, top, width: CW - 10, opacity: clamp(listP * HILL.length - i)}}>
						<div
							style={{
								position: 'absolute', left: 0, top: 0, width: 48, height: 48, borderRadius: 9,
								boxShadow: `inset 0 0 0 5px ${on ? (m === 'check' ? C.go : C.muted) : C.grid}`,
								background: on ? `rgba(${m === 'check' ? '30,123,52' : '94,99,104'},${0.12 * p})` : 'transparent',
							}}
						>
							{on && (
								<div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 42, fontWeight: 800, color: m === 'check' ? C.go : C.muted, opacity: p, transform: `scale(${0.6 + 0.4 * p})`}}>
									{m === 'check' ? '✓' : '½'}
								</div>
							)}
						</div>
						<div style={{position: 'absolute', left: 58, top: 3, right: 0, fontSize: h.length > 14 ? 33 : 36, fontWeight: 800, lineHeight: 1.05, color: on ? C.ink : C.muted}}>{h}</div>
					</div>
				);
			})}
		</Plate>
	);
};

// A sign listing items, each fading in with its own progress (0-1). Words are David's (Sheet).
export const ListSign: React.FC<{items: string[]; shown: number[]; size?: number; top?: number; gap?: number}> = ({items, shown, size = 52, top = 40, gap}) => {
	const step = gap ?? (BAND_H - top * 2) / items.length;
	return (
		<Plate>
			{items.map((it, i) => (
				<div
					key={it}
					style={{
						position: 'absolute',
						left: 50,
						right: 40,
						top: top + i * step,
						fontSize: size,
						fontWeight: 800,
						textTransform: 'uppercase',
						letterSpacing: 1,
						lineHeight: 1,
						whiteSpace: 'nowrap',
						opacity: clamp(shown[i]),
						transform: `translateX(${(1 - clamp(shown[i])) * -30}px)`,
					}}
				>
					{it}
				</div>
			))}
		</Plate>
	);
};
