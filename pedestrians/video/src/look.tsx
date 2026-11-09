// Sedans to SUVs look: road-sign plates above David's head.
// Layout ("head-low"): both speakers' heads start at about y 844 in the 1080x1920 frame
// (speaker A's hair at x 515-870, B's cap at x 130-520; measured 2026-11-09 from
// public/speaker-a.png and speaker-b.png). Captions go below the chin, so the band above
// the heads is free: y 250-800, x 120-960 (a 44px gap above the hair).
// Colors validated with the dataviz validator (2026-11-09): US red and Europe blue pass every
// check on the wall (#D6DEBA) and on the white plate; the ochre third color passes on the plate.
import React from 'react';
import {barlow} from '@kit/fonts';

export const BAND = {left: 120, right: 960, top: 250, bottom: 800};
export const BAND_W = BAND.right - BAND.left;
export const BAND_H = BAND.bottom - BAND.top;

export const C = {
	plate: 'rgba(251,251,247,0.95)', // white regulatory-sign plate
	border: '#1A1C1E',
	ink: '#1A1C1E',
	muted: '#5E6368',
	grid: '#D9DCD4',
	track: '#E4E6E0',
	us: '#B3261E', // stop-sign red
	eu: '#1F4E9C', // European road-sign blue
	meth: '#7A5A00', // dark ochre
	go: '#1E7B34', // highway-sign green, for checkmarks (David, 2026-11-09); 5.1:1 on the plate
};

export const FONT = barlow; // Barlow Condensed: drawn from California highway signs and plates

// The plate: a white sign with a black inset border, filling the band.
export const Plate: React.FC<{children: React.ReactNode}> = ({children}) => (
	<div
		style={{
			position: 'absolute',
			left: BAND.left,
			top: BAND.top,
			width: BAND_W,
			height: BAND_H,
			background: C.plate,
			borderRadius: 30,
			boxShadow: `inset 0 0 0 7px ${C.border}`,
			fontFamily: FONT,
			color: C.ink,
			overflow: 'hidden',
		}}
	>
		{children}
	</div>
);

// Titles are David's words from the Sheet's On-Screen Text column, in caps. Fit rule (2026-11-09):
// one line at 58px if it fits the 760px text width, 54px if that makes it fit, otherwise two lines
// at 58px (text split with "\n") and no gray subtitle, so the chart keeps the same space.
export const Title: React.FC<{text: string; size?: number}> = ({text, size = 58}) => (
	<div
		style={{
			position: 'absolute',
			left: 40,
			right: 40,
			top: 26,
			fontSize: size,
			fontWeight: 800,
			lineHeight: 1.0,
			whiteSpace: 'pre-line',
			textTransform: 'uppercase',
			letterSpacing: 1,
			color: text.startsWith('[TBD') ? C.muted : C.ink,
		}}
	>
		{text}
	</div>
);
